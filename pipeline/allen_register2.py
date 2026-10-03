#!/usr/bin/env python3
"""Second pass on the Allen plates: non-rigid refinement per plate and shape-based interpolation between plates.

    pipeline/.venv/bin/python pipeline/allen_register2.py <scratch/allen>

Starts from register_result.npz (plates already placed in MNI by a 2D similarity transform, nearest-plate
filled). For each placed plate y:
  1. moving = the plate's common-label map (Allen ids), fixed = NextBrain's slice at that y (same ids);
     a multi-label B-spline registration on the labels' signed distance maps (SimpleITK), smoothed with
     a coarse control grid so small nuclei follow the big neighbours instead of jumping;
  2. the full plate (all Allen ids) is warped with that field.
Then every label is interpolated between consecutive plates with distance-transform morphing, which turns
the slab stack into smooth shapes. Output: register2_result.npz + register2_report.json.
Research/educational use only (Allen terms of use).
"""
import json
import sys
from pathlib import Path

import numpy as np
import SimpleITK as sitk
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_pipeline.build import NextBrain  # noqa: E402

S = Path(sys.argv[1])
r = np.load(S / "register_result.npz")
vol, MM, origin = r["vol"], float(r["mm"]), r["origin"]
rep = [x for x in json.loads((S / "register_report.json").read_text()) if "y_index" in x and "dice" in x]
pairs = json.loads((S / "name_pairs.json").read_text())
N2A = {n: a for a, n, _, _ in pairs}
common = set(N2A.values())

nb = NextBrain()
step = int(round(MM / nb.spacing))  # 0.5 mm -> every 2.5th voxel is not integer: use 0.4 mm grid then resample
nbv = np.asarray(nb.data)
lut = np.zeros(int(nbv.max()) + 1, dtype=np.int32)
for n, a in N2A.items():
    lut[n] = a


def nb_slice_A(y_mm):
    """NextBrain slice at y (mm), relabelled to Allen ids, on the output grid (x, z) at MM."""
    j = int(round((y_mm - origin[1]) / nb.spacing))
    j = min(max(j, 0), nbv.shape[1] - 1)
    sl = lut[nbv[:, j, :]]
    # resample 0.2 mm -> MM by nearest
    xs = np.clip(np.round(np.arange(vol.shape[0]) * MM / nb.spacing).astype(int), 0, sl.shape[0] - 1)
    zs = np.clip(np.round(np.arange(vol.shape[2]) * MM / nb.spacing).astype(int), 0, sl.shape[1] - 1)
    return sl[np.ix_(xs, zs)]


def sdm(mask):
    """signed distance (mm): negative inside"""
    if not mask.any():
        return None
    inside = ndimage.distance_transform_edt(mask) * MM
    outside = ndimage.distance_transform_edt(~mask) * MM
    return (outside - inside).astype(np.float32)


def register_plate(moving_lab, fixed_lab, ids):
    """B-spline field aligning the stacked signed-distance maps of `ids` (moving -> fixed). Returns a
    displacement field (sitk) or None."""
    chans_m, chans_f = [], []
    for i in ids:
        a, b = sdm(moving_lab == i), sdm(fixed_lab == i)
        if a is None or b is None:
            continue
        chans_m.append(np.clip(a, -8, 8)); chans_f.append(np.clip(b, -8, 8))
    if len(chans_m) < 3:
        return None
    # average the clipped distance maps into one scalar image each: a cheap multi-label similarity
    m = sitk.GetImageFromArray(np.mean(chans_m, axis=0))
    f = sitk.GetImageFromArray(np.mean(chans_f, axis=0))
    for im in (m, f):
        im.SetSpacing((MM, MM))
    tx0 = sitk.BSplineTransformInitializer(f, [6, 6])  # coarse grid: ~15-20 mm control spacing
    reg = sitk.ImageRegistrationMethod()
    reg.SetMetricAsMeanSquares()
    reg.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5, numberOfIterations=60)
    reg.SetInitialTransform(tx0, inPlace=True)
    reg.SetInterpolator(sitk.sitkLinear)
    reg.SetShrinkFactorsPerLevel([4, 2, 1]); reg.SetSmoothingSigmasPerLevel([2, 1, 0])
    try:
        tx = reg.Execute(f, m)
    except RuntimeError as e:
        print("   registration failed:", str(e)[:80]); return None
    return tx


plates = {}  # yi -> warped plate (all labels)
report = []
ys = sorted({int(round(x["y_index"] * 1.0 / MM)) for x in rep})  # y_index was on the 1 mm grid
for x in rep:
    yi = int(round(x["y_index"] * 1.0 / MM))
    moving = vol[:, yi, :]
    if not moving.any():
        continue
    fixed = nb_slice_A(origin[1] + yi * MM)
    ids = [i for i in (set(np.unique(moving)) & set(np.unique(fixed)) & common) if (moving == i).sum() > 20 and (fixed == i).sum() > 20]
    tx = register_plate(moving, fixed, ids)
    if tx is None:
        plates[yi] = moving; report.append({"y_mm": origin[1] + yi * MM, "refined": False}); continue
    mv = sitk.GetImageFromArray(moving.astype(np.int32)); mv.SetSpacing((MM, MM))
    warped = sitk.Resample(mv, mv, tx, sitk.sitkNearestNeighbor, 0, sitk.sitkInt32)
    w = sitk.GetArrayFromImage(warped).astype(np.uint16)
    d0 = np.median([2 * ((moving == i) & (fixed == i)).sum() / max(1, (moving == i).sum() + (fixed == i).sum()) for i in ids])
    d1 = np.median([2 * ((w == i) & (fixed == i)).sum() / max(1, (w == i).sum() + (fixed == i).sum()) for i in ids])
    # keep the refinement only where it actually helped; the averaged distance-map similarity can drift
    accepted = d1 > d0 + 0.01
    plates[yi] = w if accepted else moving
    report.append({"y_mm": origin[1] + yi * MM, "refined": bool(accepted), "labels": len(ids), "dice_before": round(float(d0), 3), "dice_after": round(float(d1 if accepted else d0), 3)})
    print(f"y={origin[1] + yi * MM:7.1f}  labels={len(ids):3d}  dice {d0:.2f} -> {d1:.2f}", flush=True)

# shape-based interpolation between consecutive plates, label by label
ys = sorted(plates)
out = np.zeros_like(vol)
for yi in ys:
    out[:, yi, :] = plates[yi]
all_ids = sorted(set(np.unique(np.stack([plates[y] for y in ys]))) - {0})
print("interpolating", len(all_ids), "labels between", len(ys), "plates", flush=True)
for i in all_ids:
    present = [y for y in ys if (plates[y] == i).any()]
    for a, b in zip(present, present[1:]):
        if b - a <= 1 or (b - a) * MM > 6.0:
            continue  # neighbours, or too far apart to be the same object
        da, db = sdm(plates[a] == i), sdm(plates[b] == i)
        for y in range(a + 1, b):
            t = (y - a) / (b - a)
            d = (1 - t) * da + t * db
            m = d < 0
            sl = out[:, y, :]
            sl[m & (sl == 0)] = i  # earlier labels keep precedence
    # a label on one plate only: give it the plate thickness (+-1 slice) so it is not a sheet
    for y in present:
        for yy in (y - 1, y + 1):
            if 0 <= yy < out.shape[1] and yy not in plates:
                sl = out[:, yy, :]
                m = (plates[y] == i) & (sl == 0)
                sl[m] = i
np.savez_compressed(S / "register2_result.npz", vol=out, origin=origin, mm=MM)
(S / "register2_report.json").write_text(json.dumps(report, indent=1))
ref = [x for x in report if x.get("refined")]
print(f"refined {len(ref)}/{len(report)} plates; median dice before {np.median([x['dice_before'] for x in ref]):.2f} after {np.median([x['dice_after'] for x in ref]):.2f}")
