#!/usr/bin/env python3
"""Derive sub-structure masks from the Visible-Human-segmented organs (MNI space).

    pipeline/.venv/bin/python pipeline/vhp_derive.py

The cryosections show the eyeball and the pituitary gland as wholes; their parts are not separable at
0.33 mm/px but their positions on the organ are textbook geometry, so they are cut from the organ mask:

  so-eyeball.{R,L}  ->  so-cornea          anterior cap of the wall, half-angle 30 deg about the +y axis
                        so-retina          the wall behind 60 deg from the anterior pole (ora serrata)
                        so-nasal-retina    the retina medial to the globe's centre
                        so-temporal-retina the retina lateral to the globe's centre
  pituitary.M       ->  end-ant-pituitary  anterior 3/4 of the gland along y
                        end-post-pituitary posterior 1/4 (the neurohypophysis is about a quarter of the gland)

The wall is 1.5 mm thick (the real retina is ~0.3 mm; a thinner shell does not survive the 1 mm smoothing
in the mesh step) and the eye parts are written at 0.5 mm. Output: data/derived/vhp/<id>.<side>.mni.nii.gz,
picked up by integrate_vhp.py like the segmented organs. These are approximations of the part boundary on
a real shape, not segmentations: the manifest marks them `derived`.
"""
import json
from pathlib import Path

import numpy as np
import SimpleITK as sitk

ROOT = Path(__file__).resolve().parent.parent
DER = ROOT / "data" / "derived" / "vhp"
WALL_MM = 1.5
FINE_MM = 0.5


def load_fine(path):
    """binary mask -> 0.5 mm grid, linear interpolation then threshold so the voxel steps round off"""
    img = sitk.ReadImage(str(path), sitk.sitkFloat32)
    size = [int(round(s * sp / FINE_MM)) for s, sp in zip(img.GetSize(), img.GetSpacing())]
    ref = sitk.Image(size, sitk.sitkFloat32)
    ref.SetSpacing((FINE_MM,) * 3); ref.SetDirection(img.GetDirection())
    ref.SetOrigin(tuple(np.array(img.GetOrigin()) + (FINE_MM - img.GetSpacing()[0]) / 2 * np.array(img.GetDirection()).reshape(3, 3).sum(axis=1)))
    sm = sitk.SmoothingRecursiveGaussian(img, 0.7)
    fine = sitk.Resample(sm, ref, sitk.Transform(), sitk.sitkLinear, 0.0)
    return sitk.Cast(fine > 0.5, sitk.sitkUInt8)


def ras_grid(img):
    """RAS physical coordinates of every voxel, shape (z, y, x, 3) — ITK gives LPS, so x and y are negated"""
    a = sitk.GetArrayFromImage(img)
    zz, yy, xx = np.indices(a.shape)
    idx = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3).astype(float)
    o = np.array(img.GetOrigin()); d = np.array(img.GetDirection()).reshape(3, 3); sp = np.array(img.GetSpacing())
    lps = (d @ (idx * sp).T).T + o
    ras = lps * np.array([-1, -1, 1])
    return a > 0, ras.reshape(a.shape + (3,))


def write_like(ref, arr, path):
    out = sitk.GetImageFromArray(arr.astype(np.uint8))
    out.CopyInformation(ref)
    sitk.WriteImage(out, str(path))
    print(f"  {path.name}: {arr.sum() * np.prod(ref.GetSpacing()) / 1000:.2f} mL")


def eye_parts(side):
    src = DER / f"so-eyeball.{side}.mni.nii.gz"
    if not src.exists():
        return
    img = load_fine(src)
    mask, ras = ras_grid(img)
    wall = mask & ~(sitk.GetArrayFromImage(sitk.BinaryErode(img, [int(round(WALL_MM / FINE_MM))] * 3)) > 0)
    c = ras[mask].mean(axis=0)
    v = ras - c
    r = np.linalg.norm(v, axis=-1) + 1e-9
    theta = np.degrees(np.arccos(np.clip(v[..., 1] / r, -1, 1)))  # angle from the anterior (+y) pole
    cornea = wall & (theta < 30)
    retina = wall & (theta > 60)
    medial = (ras[..., 0] < c[0]) if side == "R" else (ras[..., 0] > c[0])
    print(f"so-eyeball.{side}: centre RAS {c.round(1)}, radius {np.cbrt(3 * mask.sum() * FINE_MM**3 / (4 * np.pi)):.1f} mm")
    write_like(img, cornea, DER / f"so-cornea.{side}.mni.nii.gz")
    write_like(img, retina, DER / f"so-retina.{side}.mni.nii.gz")
    write_like(img, retina & medial, DER / f"so-nasal-retina.{side}.mni.nii.gz")
    write_like(img, retina & ~medial, DER / f"so-temporal-retina.{side}.mni.nii.gz")
    return ["so-cornea", "so-retina", "so-nasal-retina", "so-temporal-retina"]


def pituitary_parts():
    src = DER / "pituitary.M.mni.nii.gz"
    if not src.exists():
        return
    img = load_fine(src)
    mask, ras = ras_grid(img)
    y = ras[..., 1]
    ys = y[mask]
    cut = ys.min() + 0.25 * (ys.max() - ys.min())
    print(f"pituitary: y RAS {ys.min():.1f}..{ys.max():.1f}, cut at {cut:.1f}")
    write_like(img, mask & (y >= cut), DER / "end-ant-pituitary.M.mni.nii.gz")
    write_like(img, mask & (y < cut), DER / "end-post-pituitary.M.mni.nii.gz")
    return ["end-ant-pituitary", "end-post-pituitary"]


CORD_NOTE = ("자세 보정: Visible Human 표본은 목이 젖혀져 있어 척수가 뒤쪽으로 기울어 내려간다. "
             "큰구멍 아래의 척수를 그 축이 수직이 되도록 돌려 놓았다(모양·굵기는 분할 결과 그대로).")


def straighten_cord():
    """The specimen's neck is extended, so under the affine the cervical cord leaves the foramen magnum
    heading 25 degrees backwards. Rotate the part below the foramen magnum about a pivot there so its
    principal axis is vertical, blending over 20 mm so there is no kink. Shape and calibre are untouched."""
    src = DER / "sp-cord.M.mni.nii.gz"
    if not src.exists():
        return
    img = sitk.ReadImage(str(src))
    mask, ras = ras_grid(img)
    pts = ras[mask]
    z0 = -62.0  # foramen magnum level in MNI
    below = pts[pts[:, 2] < z0 - 10]
    c = below.mean(axis=0)
    _, _, vt = np.linalg.svd(below - c, full_matrices=False)
    d = vt[0] / np.linalg.norm(vt[0])
    if d[2] > 0:
        d = -d
    pivot = pts[np.abs(pts[:, 2] - z0) < 3].mean(axis=0)
    target = np.array([0.0, 0.0, -1.0])
    v = np.cross(d, target); s = np.linalg.norm(v); cth = float(d @ target)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + k + k @ k * ((1 - cth) / (s * s)) if s > 1e-9 else np.eye(3)
    angle = np.degrees(np.arccos(np.clip(cth, -1, 1)))
    print(f"sp-cord: axis below the foramen magnum tilted {angle:.1f} deg (RAS dir {d.round(2)}); pivot RAS {pivot.round(1)}")
    w = np.clip((z0 - pts[:, 2]) / 20.0, 0, 1)[:, None]  # 0 at/above the pivot, 1 from 20 mm below
    rotated = pivot + (R @ (pts - pivot).T).T
    moved = pts * (1 - w) + rotated * w
    # rasterise the moved points onto the same grid (extended downwards as needed), fill the few gaps
    o = np.array(img.GetOrigin()); dmat = np.array(img.GetDirection()).reshape(3, 3); sp = np.array(img.GetSpacing())
    lps = moved * np.array([-1, -1, 1])
    idx = np.rint(np.linalg.solve(dmat, (lps - o).T).T / sp).astype(int)
    lo = idx.min(axis=0) - 2; hi = idx.max(axis=0) + 3
    size = hi - lo
    arr = np.zeros(size[::-1], dtype=np.uint8)
    ii = idx - lo
    arr[ii[:, 2], ii[:, 1], ii[:, 0]] = 1
    out = sitk.GetImageFromArray(arr)
    out.SetSpacing(tuple(sp)); out.SetDirection(tuple(dmat.ravel()))
    out.SetOrigin(tuple(o + dmat @ (lo * sp)))
    out = sitk.BinaryMorphologicalClosing(out, [1, 1, 1])
    soft = sitk.SmoothingRecursiveGaussian(sitk.Cast(out, sitk.sitkFloat32), 1.0)
    out = sitk.Cast(soft > 0.5, sitk.sitkUInt8)
    sitk.WriteImage(out, str(src))
    print(f"  sp-cord.M.mni.nii.gz re-posed: {sitk.GetArrayFromImage(out).sum() / 1000:.2f} mL (was {mask.sum() / 1000:.2f} mL)")
    return angle


def main():
    derived = {}  # part id -> {"organ": Korean name of the organ it was cut from} or {"note": free text}
    for side in ("R", "L"):
        ids = eye_parts(side)
        if ids:
            for i in ids:
                derived[i] = {"organ": "안구"}
    ids = pituitary_parts()
    if ids:
        for i in ids:
            derived[i] = {"organ": "뇌하수체"}
    if straighten_cord() is not None:
        derived["sp-cord"] = {"note": CORD_NOTE}
    (DER / "derived.json").write_text(json.dumps(derived, indent=1) + "\n", encoding="utf-8")
    print("derived:", derived)


if __name__ == "__main__":
    main()
