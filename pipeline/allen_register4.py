#!/usr/bin/env python3
"""Fourth pass: per-plate non-rigid refinement driven by strong signals, then ITK contour interpolation.

    pipeline/.venv/bin/python pipeline/allen_register4.py <scratch/allen>

Starts from register3_sparse.npz (plates placed by the fitted spacing and a 2D similarity).
For each plate: fixed = NextBrain slice at that y, moving = the plate. The B-spline (SimpleITK) is driven
by three binary signals that are large and reliable on both sides — the whole tissue outline, the forebrain
white matter, and the union of common labels bigger than 100 mm^2 on the slice — turned into clipped signed
distance maps and summed. Small nuclei follow the smooth field. The refinement is kept only when the median
Dice of the common labels improves. Then ITK's MorphologicalContourInterpolator fills between plates.
Research/educational use only (Allen terms of use).
"""
import json
import sys
from pathlib import Path

import itk
import numpy as np
import SimpleITK as sitk
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_pipeline.build import NextBrain  # noqa: E402

S = Path(sys.argv[1])
r = np.load(S / "register3_sparse.npz")
vol, MM, origin = r["vol"], float(r["mm"]), r["origin"]
pairs = json.loads((S / "name_pairs.json").read_text())
N2A = {n: a for a, n, _, _ in pairs}
common = set(N2A.values())
onto = {s["id"]: s for s in json.loads((S / "ontology16.json").read_text())}
WM_ALLEN = next((a for a, n, name, _ in pairs if name == "white matter of forebrain"), None)

nb = NextBrain()
full = np.asarray(nb.data)
lut = np.zeros(int(full.max()) + 1, dtype=np.int32)
for n, a in N2A.items():
    lut[n] = a
idx = [np.clip(np.round(np.arange(vol.shape[d]) * MM / nb.spacing).astype(int), 0, full.shape[d] - 1) for d in range(3)]
nbA = lut[full[np.ix_(idx[0], idx[1], idx[2])]]
nbT = full[np.ix_(idx[0], idx[1], idx[2])] > 0  # tissue (any label)
del full


def sdm(mask, clip=10.0):
    if not mask.any():
        return None
    d = ndimage.distance_transform_edt(~mask) * MM - ndimage.distance_transform_edt(mask) * MM
    return np.clip(d, -clip, clip).astype(np.float32)


def signal(lab, tissue, big_ids):
    chans = [sdm(tissue)]
    if WM_ALLEN is not None:
        chans.append(sdm(lab == WM_ALLEN))
    u = np.isin(lab, list(big_ids))
    chans.append(sdm(u))
    chans = [c for c in chans if c is not None]
    return np.sum(chans, axis=0) / max(1, len(chans))


def dice_median(a, b, ids):
    vals = [2 * ((a == i) & (b == i)).sum() / max(1, (a == i).sum() + (b == i).sum()) for i in ids]
    return float(np.median(vals)) if vals else 0.0


out = np.zeros_like(vol)
report = []
for j in np.nonzero(vol.any(axis=(0, 2)))[0]:
    moving = vol[:, j, :]
    fixed = nbA[:, j, :]
    tissue_f = nbT[:, j, :]
    tissue_m = moving > 0
    ids = [i for i in (set(np.unique(moving)) & set(np.unique(fixed)) & common) if (moving == i).sum() > 8 and (fixed == i).sum() > 8]
    big = [i for i in ids if (fixed == i).sum() * MM * MM > 100]
    d0 = dice_median(moving, fixed, ids)
    f = sitk.GetImageFromArray(signal(fixed, tissue_f, big)); m = sitk.GetImageFromArray(signal(moving, tissue_m, big))
    for im in (f, m):
        im.SetSpacing((MM, MM))
    try:
        tx0 = sitk.BSplineTransformInitializer(f, [10, 10])
        reg = sitk.ImageRegistrationMethod()
        reg.SetMetricAsCorrelation()
        reg.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-6, numberOfIterations=80)
        reg.SetInitialTransform(tx0, inPlace=True)
        reg.SetInterpolator(sitk.sitkLinear)
        reg.SetShrinkFactorsPerLevel([4, 2, 1]); reg.SetSmoothingSigmasPerLevel([3, 1.5, 0])
        tx = reg.Execute(f, m)
        mv = sitk.GetImageFromArray(moving.astype(np.int32)); mv.SetSpacing((MM, MM))
        w = sitk.GetArrayFromImage(sitk.Resample(mv, mv, tx, sitk.sitkNearestNeighbor, 0, sitk.sitkInt32)).astype(np.uint16)
        d1 = dice_median(w, fixed, ids)
    except RuntimeError as e:
        w, d1 = moving, d0
    keep = d1 > d0 + 0.005
    out[:, j, :] = w if keep else moving
    report.append({"y_mm": float(origin[1] + j * MM), "labels": len(ids), "dice_before": round(d0, 3), "dice_after": round(d1 if keep else d0, 3), "refined": bool(keep)})
    print(f"y={origin[1] + j * MM:7.1f} labels={len(ids):3d} dice {d0:.2f} -> {d1:.2f} {'kept' if keep else 'rejected'}", flush=True)
ref = [x for x in report if x["refined"]]
print(f"refined {len(ref)}/{len(report)}; median dice before {np.median([x['dice_before'] for x in report]):.2f} after {np.median([x['dice_after'] for x in report]):.2f}", flush=True)
np.savez_compressed(S / "register4_sparse.npz", vol=out, origin=origin, mm=MM)

arr = np.ascontiguousarray(out.transpose(2, 1, 0).astype(np.uint16))
img = itk.image_from_array(arr); img.SetSpacing([MM, MM, MM])
interp = itk.MorphologicalContourInterpolator.New(img); interp.SetAxis(1); interp.SetUseDistanceTransform(True); interp.Update()
res = itk.array_from_image(interp.GetOutput()).transpose(2, 1, 0).astype(np.uint16)
np.savez_compressed(S / "register4_result.npz", vol=res, origin=origin, mm=MM)
dice = {}
for a in common:
    A = res == a; B = nbA == a
    if A.any() and B.any():
        dice[int(a)] = round(2 * (A & B).sum() / (A.sum() + B.sum()), 3)
vals = np.array(list(dice.values()))
stats = json.loads((S / "stack_stats.json").read_text())
print(f"3D dice on {len(dice)} common labels: median {np.median(vals):.2f}, >=0.5: {(vals >= 0.5).mean() * 100:.0f}%, >=0.7: {(vals >= 0.7).mean() * 100:.0f}%")
for key in ["putamen", "head of caudate", "red nucleus", "medial portion of STH", "lateral geniculate", "dentate nucleus", "superior colliculus", "inferior olivary"]:
    hits = [(stats[str(a)]["name"][:28], d) for a, d in dice.items() if key in (stats.get(str(a), {}).get("name") or "")]
    print("  ", key, hits[:2])
(S / "register4_report.json").write_text(json.dumps({"plates": report, "dice": dice}, indent=1))
