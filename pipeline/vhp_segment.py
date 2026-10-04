#!/usr/bin/env python3
"""Segment organ-level structures in the Visible Human male head cryosections with Segment Anything,
slice by slice, then push the masks into MNI space with the transform from vhp_stack_register.py.

    pipeline/.venv/bin/python pipeline/vhp_segment.py targets.json [--out data/derived/vhp]

targets.json: [ { "id": "so-eyeball", "side": "R", "slices": [1096, 1122], "seed": [950, 812],
                  "areaMm2": [150, 700], "prompt": "point" } , ... ]
  seed      : (x, y) pixel in the full-resolution image of the FIRST slice of the range
  areaMm2   : plausible 2D area band; the SAM candidate mask inside the band with the best score wins
Tracking: after each slice the accepted mask's centroid becomes the seed for the next slice; the previous
mask is also offered as a box prompt so SAM stays on the same object. A slice with no acceptable mask ends
the run in that direction (the range is walked outward from the seed slice both ways when the seed slice
is inside the range).
Output: <out>/<id>.<side>.npz (mask stack, slice numbers, pixel size) and, if the MNI transform exists,
<out>/<id>.<side>.mni.nii.gz (binary label resampled into the MNI152 grid) for the mesh pipeline.
Visible Human Project, U.S. National Library of Medicine — no licence required.
"""
import json
import sys
from pathlib import Path

import numpy as np
import SimpleITK as sitk
import torch
from PIL import Image
from segment_anything import SamPredictor, sam_model_registry

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "vhp" / "male-head"
PX = 0.33
OUT = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else ROOT / "data" / "derived" / "vhp"
TFM = ROOT / "data" / "raw" / "vhp" / "vhp_to_mni.tfm"
MNI = ROOT / "data" / "raw" / "mni" / "mni_icbm152_nlin_asym_09c" / "mni_icbm152_t1_tal_nlin_asym_09c.nii"
MNI_MASK = MNI.with_name("mni_icbm152_t1_tal_nlin_asym_09c_mask.nii")


def load_sam():
    sam = sam_model_registry["vit_b"](checkpoint=str(ROOT / "data" / "raw" / "sam" / "sam_vit_b_01ec64.pth"))
    sam.to("mps" if torch.backends.mps.is_available() else "cpu")
    return SamPredictor(sam)


def pick(masks, scores, band):
    lo, hi = band
    best = None
    for m, s in zip(masks, scores):
        area = m.sum() * PX * PX
        if lo <= area <= hi and (best is None or s > best[1]):
            best = (m, s, area)
    return best


def segment_target(pred, t):
    first, last = t["slices"]
    seed_slice = t.get("seedSlice", first)
    results = {}

    def run(direction):
        seed = np.array(t["seed"], float)
        n = seed_slice
        while first <= n <= last:
            p = SRC / f"a_vm{n}.png"
            if not p.exists():
                break
            im = np.asarray(Image.open(p).convert("RGB"))
            pred.set_image(im)
            # point prompt only: a box from the previous slice makes SAM lock onto the box rather than the
            # object and the track breaks within a few slices (measured on the spinal cord)
            masks, scores, _ = pred.predict(point_coords=seed[None], point_labels=np.array([1]), multimask_output=True)
            got = pick(masks, scores, t["areaMm2"])
            if got is None:
                break
            m, s, area = got
            results[n] = m
            ys, xs = np.nonzero(m)
            seed = np.array([xs.mean(), ys.mean()])
            print(f"  {t['id']}.{t.get('side','M')} slice {n}: area {area:.0f} mm2 score {s:.2f}", flush=True)
            n += direction
            if n == seed_slice:
                break

    run(+1)
    run(-1)
    return results


GREY = ROOT / "data" / "raw" / "vhp" / "vhp_head_grey.nii.gz"


def to_mni(stack, slices, shape_hw):
    """binary VHP-space volume -> MNI grid (nearest). The mask volume is built on exactly the grid the
    registration used (vhp_head_grey.nii.gz: its size, spacing, origin and LPS axis order, see
    vhp_stack_register.grey_volume), so the transform applies as is."""
    grey = sitk.ReadImage(str(GREY))
    nx, ny, nz = grey.GetSize()
    mm = grey.GetSpacing()[0]
    f = int(round(mm / PX))
    first = 1001
    vol = np.zeros((nz, ny, nx), dtype=np.uint8)  # (z, y, x) in the stack order (slice 1001 first)
    for n, m in zip(slices, stack):
        k = n - first
        if not (0 <= k < nz):
            continue  # slice outside the registered stack
        small = m[: ny * f, : nx * f].reshape(ny, f, nx, f).mean(axis=(1, 3)) > 0.5
        vol[k] = small
    lps = vol[::-1, ::-1, :]
    img = sitk.GetImageFromArray(lps.astype(np.float32))
    img.CopyInformation(grey)
    # SAM's outline jitters by a few pixels from slice to slice and the slices are 1 mm apart, which shows
    # as ridges on the mesh; smooth the binary volume a little and resample it as a soft mask, thresholding
    # after the transform instead of nearest-neighbour voxel copying
    img = sitk.SmoothingRecursiveGaussian(img, 1.2)
    mni = sitk.ReadImage(str(MNI))
    # output grid: the MNI grid extended 230 mm inferiorly (the template stops at z = -78 and the cord runs
    # on to C7), cropped to the mask afterwards so the files stay small
    ref = sitk.Image([mni.GetSize()[0], mni.GetSize()[1], mni.GetSize()[2] + 230], sitk.sitkUInt8)
    ref.SetSpacing(mni.GetSpacing()); ref.SetDirection(mni.GetDirection())
    ref.SetOrigin(tuple(np.array(mni.GetOrigin()) - np.array([0, 0, 230.0])))
    # The B-spline part of the transform was fitted inside the MNI brain mask only and drifts by >10 mm
    # when extrapolated to the eyes; outside the (dilated) brain mask the affine part alone is used.
    affine = sitk.CompositeTransform(sitk.ReadTransform(str(TFM))).GetNthTransform(0)

    def project(t):
        soft = sitk.Resample(img, ref, t, sitk.sitkLinear, 0.0, sitk.sitkFloat32)
        return sitk.Cast(soft > 0.5, sitk.sitkUInt8)

    out = project(affine)
    # well inside the brain (10 mm in from the mask edge) the B-spline part is used too, and only if it
    # keeps the volume: the pituitary sits at the mask edge where an early B-spline had a Jacobian of 0.1
    brain = sitk.BinaryErode(sitk.Cast(sitk.ReadImage(str(MNI_MASK)) > 0, sitk.sitkUInt8), [10, 10, 10])
    st = sitk.LabelShapeStatisticsImageFilter(); st.Execute(out)
    if 1 not in st.GetLabels():
        return out
    c = brain.TransformPhysicalPointToIndex(st.GetCentroid(1))
    inside = all(0 <= i < n for i, n in zip(c, brain.GetSize())) and brain[c] > 0
    if inside:
        vol_affine = st.GetPhysicalSize(1)
        full = project(sitk.ReadTransform(str(TFM)))
        st.Execute(full)
        if 1 in st.GetLabels() and 0.7 <= st.GetPhysicalSize(1) / vol_affine <= 1.4:
            out = full
        else:
            print(f"  B-spline changed the volume {vol_affine:.0f} -> {st.GetPhysicalSize(1) if 1 in st.GetLabels() else 0:.0f} mm3; using the affine", flush=True)
            st.Execute(out)
    bb = st.GetBoundingBox(1)  # (x0, y0, z0, sx, sy, sz)
    lo = [max(0, bb[i] - 2) for i in range(3)]
    hi = [min(out.GetSize()[i], bb[i] + bb[3 + i] + 2) for i in range(3)]
    return sitk.RegionOfInterest(out, [h - l for l, h in zip(lo, hi)], lo)


def main():
    targets = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    pred = load_sam()
    for t in targets:
        res = segment_target(pred, t)
        if not res:
            print("no mask for", t["id"]); continue
        slices = sorted(res)
        stack = np.stack([res[n] for n in slices])
        tag = f"{t['id']}.{t.get('side', 'M')}"
        np.savez_compressed(OUT / f"{tag}.npz", masks=stack, slices=np.array(slices), px=PX)
        vol_mm3 = stack.sum() * PX * PX * 1.0
        print(f"{tag}: {len(slices)} slices, {vol_mm3:.0f} mm3", flush=True)
        if TFM.exists():
            sitk.WriteImage(to_mni(stack, slices, stack.shape[1:]), str(OUT / f"{tag}.mni.nii.gz"))


if __name__ == "__main__":
    main()
