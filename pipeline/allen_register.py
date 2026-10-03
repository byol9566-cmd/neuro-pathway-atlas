#!/usr/bin/env python3
"""Register the Allen adult-human coronal plates to NextBrain (MNI space) plate by plate.

    pipeline/.venv/bin/python pipeline/allen_register.py <scratch/allen>

Both atlases use the Allen ontology, so the ~229 structures with identical names are the landmarks.
For every annotated plate:
  1. find its anterior-posterior position y in MNI: the y whose NextBrain slice shares the most labels
     with the plate (Jaccard over the common-label set), kept monotonic along the plate order;
  2. fit a 2D similarity transform (scale, rotation, translation) from the plate's label centroids to the
     centroids of the same labels in the NextBrain slice at that y (least squares, Umeyama);
  3. refine with a thin-plate spline on the same centroid pairs (smooth, so small nuclei do not jump);
  4. resample the plate into the MNI grid at 0.5 mm and record the per-label Dice against NextBrain.
Plates are then stacked along y (nearest plate fills the gaps). Output: register_result.npz (label volume
in MNI, uint16 Allen ids), register_report.json (y per plate, transform, Dice per label).
Research/educational use only: the Allen content is non-commercial without written permission.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.interpolate import RBFInterpolator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_pipeline.build import NextBrain  # noqa: E402

scratch = Path(sys.argv[1])
MM = 0.5
pairs = json.loads((scratch / "name_pairs.json").read_text())
A2N = {a: n for a, n, _, _ in pairs}
N2A = {n: a for a, n, _, _ in pairs}

print("loading NextBrain ...", flush=True)
nb = NextBrain()
# work at 1 mm for the search, full 0.2 mm data stays available for the final resampling target grid
step = int(round(1.0 / nb.spacing))
vol = np.asarray(nb.data)[::step, ::step, ::step]  # index order (x, y, z) in RAS (see build.NextBrain)
origin = nb.origin
sp = nb.spacing * step
print("nextbrain 1mm grid", vol.shape, "origin", origin, flush=True)
common_nb = np.array(sorted(N2A))
# relabel to Allen ids for common structures, 0 elsewhere
lut = np.zeros(int(vol.max()) + 1, dtype=np.int32)
for n, a in N2A.items():
    if n < len(lut):
        lut[n] = a
volA = lut[vol]

# label sets per NextBrain y-slice
ny = volA.shape[1]
slice_sets = [set(np.unique(volA[:, j, :]).tolist()) - {0} for j in range(ny)]

stack = np.load(scratch / "stack.npy")  # (plate z, rows, cols) at MM, Allen ids
plates = sorted(json.loads((scratch / "plates.json").read_text()), key=lambda p: p["section_number"])
secs = [p["section_number"] for p in plates]
z_of = {s: int(round((s - secs[0]) * 0.05 / MM)) for s in secs}


def centroids(lab2d, ids):
    out = {}
    for i in ids:
        m = lab2d == i
        if m.sum() >= 4:
            ys, xs = np.nonzero(m)
            out[i] = (xs.mean(), ys.mean(), int(m.sum()))
    return out


def umeyama(src, dst):
    """similarity transform dst ~ s R src + t (2D)"""
    mu_s, mu_d = src.mean(0), dst.mean(0)
    S, D = src - mu_s, dst - mu_d
    cov = D.T @ S / len(src)
    U, sig, Vt = np.linalg.svd(cov)
    d = np.sign(np.linalg.det(U @ Vt))
    R = U @ np.diag([1, d]) @ Vt
    s = (sig[0] + d * sig[1]) / (S**2).sum() * len(src)
    t = mu_d - s * R @ mu_s
    return s, R, t


report = []
out_vol = np.zeros((int(round(volA.shape[0] * sp / MM)), int(round(volA.shape[1] * sp / MM)), int(round(volA.shape[2] * sp / MM))), dtype=np.uint16)
placed_y = []
prev_j = -1
for k, sec in enumerate(secs):
    plate = stack[z_of[sec]]
    plate_ids = set(np.unique(plate).tolist()) - {0}
    plate_common = plate_ids & set(A2N)
    if len(plate_common) < 3:
        report.append({"section": sec, "skipped": "fewer than 3 common labels"})
        continue
    # 1. y search, monotonic (plates run anterior -> posterior or the reverse; detect direction once)
    scores = np.array([len(plate_common & s) / max(1, len(plate_common | s)) for s in slice_sets])
    if prev_j >= 0:
        lo, hi = max(0, prev_j - 14), min(ny - 1, prev_j + 2)  # at most ~14 mm further back, never ahead
        masked = np.full_like(scores, -1.0)
        masked[lo:hi + 1] = scores[lo:hi + 1]
        scores = masked
    j = int(np.argmax(scores))
    prev_j = j
    # 2. similarity from plate centroids (col,row) to NextBrain slice centroids (x,z) at y=j
    sl = volA[:, j, :]  # (x, z)
    c_p = centroids(plate, plate_common)
    c_n = {}
    for i in plate_common:
        m = sl == i
        if m.sum() >= 2:
            xs, zs = np.nonzero(m)
            c_n[i] = (origin[0] + xs.mean() * sp, origin[2] + zs.mean() * sp, int(m.sum()))
    ids = [i for i in c_p if i in c_n]
    if len(ids) < 3:
        report.append({"section": sec, "y_index": j, "skipped": "fewer than 3 centroid pairs"})
        continue
    src = np.array([c_p[i][:2] for i in ids], float)  # plate px (col, row): col ~ x, row ~ -z (image rows go down)
    dst = np.array([c_n[i][:2] for i in ids], float)  # MNI mm (x, z)
    # the plates are drawn mirrored relative to NextBrain (left hemisphere seen from the other side):
    # negate x; a similarity transform cannot absorb a reflection by itself
    src_mm = np.stack([-src[:, 0] * MM, -src[:, 1] * MM], 1)
    w = np.sqrt(np.array([c_p[i][2] for i in ids], float))
    s, R, t = umeyama(np.repeat(src_mm, np.clip(w.astype(int), 1, 30), axis=0), np.repeat(dst, np.clip(w.astype(int), 1, 30), axis=0))
    fitted = (s * (R @ src_mm.T)).T + t
    resid = np.linalg.norm(fitted - dst, axis=1)
    # 3. thin-plate spline on the residual, damped
    tps = RBFInterpolator(fitted, dst - fitted, kernel="thin_plate_spline", smoothing=25.0) if len(ids) >= 6 else None
    # 4. resample: for every output voxel (x,z) at y=j find plate pixel via inverse mapping
    xs = origin[0] + np.arange(out_vol.shape[0]) * MM
    zs = origin[2] + np.arange(out_vol.shape[2]) * MM
    gx, gz = np.meshgrid(xs, zs, indexing="ij")
    P = np.stack([gx.ravel(), gz.ravel()], 1)
    if tps is not None:
        P = P - tps(P)  # approximate inverse of the small residual warp
    Q = (R.T @ ((P - t) / s).T).T  # back to plate mm
    col = -Q[:, 0] / MM
    row = -Q[:, 1] / MM
    inside = (col >= 0) & (col < plate.shape[1] - 1) & (row >= 0) & (row < plate.shape[0] - 1)
    samp = np.zeros(len(P), dtype=np.uint16)
    samp[inside] = plate[np.round(row[inside]).astype(int), np.round(col[inside]).astype(int)]
    yi = int(round(j * sp / MM))
    out_vol[:, yi, :] = samp.reshape(gx.shape)
    placed_y.append(yi)
    # Dice per common label at this y
    nbs = volA[:, j, :]
    dice = {}
    for i in ids:
        a = samp.reshape(gx.shape) == i
        # compare on the 1 mm grid of NextBrain: downsample a
        a1 = a[:: int(1 / MM), :: int(1 / MM)][: nbs.shape[0], : nbs.shape[1]]
        b1 = nbs[: a1.shape[0], : a1.shape[1]] == i
        dice[int(i)] = round(2 * (a1 & b1).sum() / max(1, a1.sum() + b1.sum()), 3)
    report.append({"section": sec, "y_index": j, "y_mm": float(origin[1] + j * sp), "score": float(scores[j]), "pairs": len(ids), "scale": float(s), "rot_deg": float(np.degrees(np.arctan2(R[1, 0], R[0, 0]))), "resid_mm_median": float(np.median(resid)), "dice_median": float(np.median(list(dice.values()))), "dice": dice})
    print(f"plate {sec:5d}: y={origin[1] + j * sp:7.1f} mm score={scores[j]:.2f} pairs={len(ids):3d} scale={s:.3f} rot={np.degrees(np.arctan2(R[1, 0], R[0, 0])):6.1f} resid={np.median(resid):5.1f} mm dice={np.median(list(dice.values())):.2f}", flush=True)

# fill between placed plates with the nearest plate
placed_y = sorted(set(placed_y))
filled = np.zeros_like(out_vol)
for yi in range(out_vol.shape[1]):
    near = min(placed_y, key=lambda p: abs(p - yi))
    if abs(near - yi) * MM <= 6:
        filled[:, yi, :] = out_vol[:, near, :]
np.savez_compressed(scratch / "register_result.npz", vol=filled, origin=origin, mm=MM)
(scratch / "register_report.json").write_text(json.dumps(report, indent=1))
ok = [r for r in report if "dice_median" in r]
print(f"plates placed {len(ok)}/{len(secs)}; median dice {np.median([r['dice_median'] for r in ok]):.2f}; y range {min(r['y_mm'] for r in ok):.0f}..{max(r['y_mm'] for r in ok):.0f} mm")
