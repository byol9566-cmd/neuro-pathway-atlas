#!/usr/bin/env python3
"""Third pass: physical plate spacing + per-plate similarity + ITK morphological contour interpolation.

    pipeline/.venv/bin/python pipeline/allen_register3.py <scratch/allen>

1. Plate positions: y_i = y0 + k * (section_i - section_0). Only the offset y0 and the shrink-corrected
   spacing k are fitted (grid search maximising the label-set overlap with NextBrain slices), so the
   plates stay in their true order and spacing instead of collapsing onto the same y.
2. Per plate: 2D similarity (mirror, scale, rotation, translation) from common-label centroids to the
   NextBrain slice at y_i, area-weighted; resampled into the MNI grid at 0.5 mm.
3. The sparse stack is filled with ITK's MorphologicalContourInterpolator (the algorithm behind 3D
   Slicer's "Fill between slices"), which morphs every label between its neighbouring plates.
4. 3D Dice against NextBrain for every common label.
Research/educational use only (Allen terms of use).
"""
import json
import sys
from pathlib import Path

import itk
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_pipeline.build import NextBrain  # noqa: E402

S = Path(sys.argv[1])
MM = 0.5
pairs = json.loads((S / "name_pairs.json").read_text())
A2N = {a: n for a, n, _, _ in pairs}
N2A = {n: a for a, n, _, _ in pairs}
nb = NextBrain()
origin = nb.origin
full = np.asarray(nb.data)
lut = np.zeros(int(full.max()) + 1, dtype=np.int32)
for n, a in N2A.items():
    lut[n] = a
# NextBrain on the 0.5 mm grid, Allen ids on common labels (nearest sampling)
idx = [np.clip(np.round(np.arange(int(full.shape[d] * nb.spacing / MM)) * MM / nb.spacing).astype(int), 0, full.shape[d] - 1) for d in range(3)]
nbA = lut[full[np.ix_(idx[0], idx[1], idx[2])]]
del full
print("nextbrain 0.5 mm grid", nbA.shape, flush=True)
ny = nbA.shape[1]
slice_sets = [set(np.unique(nbA[:, j, :]).tolist()) - {0} for j in range(ny)]

stack = np.load(S / "stack.npy")
plates = sorted(json.loads((S / "plates.json").read_text()), key=lambda p: p["section_number"])
secs = np.array([p["section_number"] for p in plates])
z_of = {s: int(round((s - secs[0]) * 0.05 / MM)) for s in secs}
plate_sets = []
for s in secs:
    ids = set(np.unique(stack[z_of[s]]).tolist()) - {0}
    plate_sets.append(ids & set(A2N))

# 1. fit y0, k (plates run anterior -> posterior with the section number: k < 0 in RAS y)
best = None
for k in np.arange(-0.09, -0.035, 0.0025):
    for y0 in np.arange(40.0, 120.0, 1.0):
        tot = 0.0
        for s, ps in zip(secs, plate_sets):
            j = int(round((y0 + k * (s - secs[0]) - origin[1]) / MM))
            if 0 <= j < ny and ps:
                tot += len(ps & slice_sets[j]) / len(ps | slice_sets[j])
        if best is None or tot > best[0]:
            best = (tot, y0, k)
tot, y0, k = best
print(f"plate spacing fit: y0={y0:.1f} mm, k={k:.4f} mm/section (nominal -0.05 -> shrink factor {-k / 0.05:.2f}), score {tot:.1f}", flush=True)


def centroids(lab, ids, flip_x):
    out = {}
    for i in ids:
        m = lab == i
        n = int(m.sum())
        if n >= 4:
            r, c = np.nonzero(m)
            out[i] = (np.array([-c.mean() if flip_x else c.mean(), -r.mean()]), n)
    return out


def umeyama(src, dst):
    mu_s, mu_d = src.mean(0), dst.mean(0)
    Sx, D = src - mu_s, dst - mu_d
    cov = D.T @ Sx / len(src)
    U, sig, Vt = np.linalg.svd(cov)
    d = np.sign(np.linalg.det(U @ Vt))
    R = U @ np.diag([1, d]) @ Vt
    s = (sig[0] + d * sig[1]) / (Sx**2).sum() * len(src)
    return s, R, mu_d - s * R @ mu_s


vol = np.zeros(nbA.shape, dtype=np.uint16)
report = []
xs = origin[0] + np.arange(vol.shape[0]) * MM
zs = origin[2] + np.arange(vol.shape[2]) * MM
gx, gz = np.meshgrid(xs, zs, indexing="ij")
P = np.stack([gx.ravel(), gz.ravel()], 1)
for s, ps in zip(secs, plate_sets):
    y = y0 + k * (s - secs[0])
    j = int(round((y - origin[1]) / MM))
    if not (0 <= j < ny):
        continue
    plate = stack[z_of[s]]
    sl = nbA[:, j, :]
    c_p = centroids(plate, ps, flip_x=True)
    c_n = {}
    for i in ps:
        m = sl == i
        if m.sum() >= 2:
            a, b = np.nonzero(m)
            c_n[i] = (np.array([origin[0] + a.mean() * MM, origin[2] + b.mean() * MM]), int(m.sum()))
    ids = [i for i in c_p if i in c_n]
    if len(ids) < 3:
        report.append({"section": int(s), "y_mm": y, "skipped": len(ids)})
        continue
    src = np.array([c_p[i][0] * MM for i in ids])
    dst = np.array([c_n[i][0] for i in ids])
    w = np.clip(np.sqrt([c_p[i][1] for i in ids]).astype(int), 1, 30)
    sc, R, t = umeyama(np.repeat(src, w, axis=0), np.repeat(dst, w, axis=0))
    resid = np.linalg.norm((sc * (R @ src.T)).T + t - dst, axis=1)
    Q = (R.T @ ((P - t) / sc).T).T
    col = -Q[:, 0] / MM
    row = -Q[:, 1] / MM
    inside = (col >= 0) & (col < plate.shape[1] - 1) & (row >= 0) & (row < plate.shape[0] - 1)
    samp = np.zeros(len(P), dtype=np.uint16)
    samp[inside] = plate[np.round(row[inside]).astype(int), np.round(col[inside]).astype(int)]
    vol[:, j, :] = samp.reshape(gx.shape)
    report.append({"section": int(s), "y_mm": float(y), "pairs": len(ids), "scale": float(sc), "rot_deg": float(np.degrees(np.arctan2(R[1, 0], R[0, 0]))), "resid_mm_median": float(np.median(resid))})
placed = [r for r in report if "pairs" in r]
print(f"placed {len(placed)}/{len(secs)} plates, median residual {np.median([r['resid_mm_median'] for r in placed]):.1f} mm, scale {np.median([r['scale'] for r in placed]):.2f}", flush=True)
np.savez_compressed(S / "register3_sparse.npz", vol=vol, origin=origin, mm=MM)

# 3. morphological contour interpolation along y (ITK axis order is z,y,x -> our (x,y,z) array becomes (z,y,x) when transposed)
print("interpolating with ITK MorphologicalContourInterpolator ...", flush=True)
arr = np.ascontiguousarray(vol.transpose(2, 1, 0).astype(np.uint16))  # (z, y, x) for itk
img = itk.image_from_array(arr)
img.SetSpacing([MM, MM, MM])
interp = itk.MorphologicalContourInterpolator.New(img)
interp.SetAxis(1)  # interpolate along y
interp.SetUseDistanceTransform(True)
interp.Update()
out = itk.array_from_image(interp.GetOutput()).transpose(2, 1, 0).astype(np.uint16)
np.savez_compressed(S / "register3_result.npz", vol=out, origin=origin, mm=MM)

# 4. 3D Dice on common labels
dice = {}
for a in set(A2N):
    A = out == a
    B = nbA == a
    if A.any() and B.any():
        dice[int(a)] = round(2 * (A & B).sum() / (A.sum() + B.sum()), 3)
stats = json.loads((S / "stack_stats.json").read_text())
vals = np.array(list(dice.values()))
print(f"3D dice on {len(dice)} common labels: median {np.median(vals):.2f}, >=0.5: {(vals >= 0.5).mean() * 100:.0f}%, >=0.7: {(vals >= 0.7).mean() * 100:.0f}%")
big = sorted(dice.items(), key=lambda kv: -stats.get(str(kv[0]), {}).get("mm3", 0))[:12]
print("largest:", [(stats[str(a)]["name"][:22], d) for a, d in big])
(S / "register3_report.json").write_text(json.dumps({"y0": y0, "k": k, "plates": report, "dice": dice}, indent=1))
