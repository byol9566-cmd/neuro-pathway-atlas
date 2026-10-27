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

The cord re-posed onto the vertebral canal goes to its own file, sp-cord.M.mni-straight.nii.gz (read by the
build and prepare_tracts.py); the projected sp-cord.M.mni.nii.gz stays as vhp_to_mni_all.py wrote it, so
re-running this script gives the same output instead of closing and smoothing the cord once more.
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


CANAL = ROOT / "data" / "derived" / "bp3d" / "canal_axis.json"
CORD_STRAIGHT = DER / "sp-cord.M.mni-straight.nii.gz"  # not *.mni.nii.gz: integrate_vhp.py must not pick it up
CORD_NOTE = ("자세 보정: Visible Human 표본은 목이 젖혀져 있어 척수가 뒤로 기울어 내려간다. 큰구멍 아래의 척수를 "
             "BodyParts3D 전신 모델의 척추관 축(척추뼈마다 구한 척추구멍 중심)을 따라 옮겨 놓았다(모양·굵기는 분할 결과 그대로).")


def canal_curve():
    """z -> (x, y) of the vertebral canal from bp3d_canal_axis.py, smoothed and linearly extended"""
    pts = json.loads(CANAL.read_text())["points"]
    z = np.array([p["z"] for p in pts]); x = np.array([p["x"] for p in pts]); y = np.array([p["y"] for p in pts])
    order = np.argsort(-z); z, x, y = z[order], x[order], y[order]
    k = np.ones(3) / 3
    xs = np.convolve(np.pad(x, 1, mode="edge"), k, mode="valid"); ys = np.convolve(np.pad(y, 1, mode="edge"), k, mode="valid")
    def f(zq):
        zq = np.asarray(zq, float)
        return np.interp(-zq, -z, xs), np.interp(-zq, -z, ys)
    return f, float(z.min())


def straighten_cord():
    """Move the Visible Human cord (segmented with the specimen's neck extended) onto the body's vertebral
    canal: below the foramen magnum every slice is shifted to the canal centre, blending in over 40 mm so
    the medulla junction is untouched. Shape and calibre are kept."""
    src = DER / "sp-cord.M.mni.nii.gz"
    if not src.exists() or not CANAL.exists():
        return
    img = sitk.ReadImage(str(src))
    mask, ras = ras_grid(img)
    canal, _ = canal_curve()
    pts = ras[mask]
    z0 = -85.0
    zs = np.round(pts[:, 2])
    moved = pts.copy()
    for z in np.unique(zs):
        sel = zs == z
        w = float(np.clip((z0 - z) / 40.0, 0, 1))
        if w == 0:
            continue
        cx, cy = canal(z)
        here = pts[sel]
        shift = np.array([cx - here[:, 0].mean(), cy - here[:, 1].mean(), 0.0]) * w
        moved[sel] = here + shift
    print(f"sp-cord: re-posed onto the BodyParts3D canal (blend {z0} .. {z0 - 40})")
    o = np.array(img.GetOrigin()); dmat = np.array(img.GetDirection()).reshape(3, 3); sp = np.array(img.GetSpacing())
    lps = moved * np.array([-1, -1, 1])
    idx = np.rint(np.linalg.solve(dmat, (lps - o).T).T / sp).astype(int)
    lo = idx.min(axis=0) - 2; hi = idx.max(axis=0) + 3
    arr = np.zeros((hi - lo)[::-1], dtype=np.uint8)
    ii = idx - lo
    arr[ii[:, 2], ii[:, 1], ii[:, 0]] = 1
    out = sitk.GetImageFromArray(arr)
    out.SetSpacing(tuple(sp)); out.SetDirection(tuple(dmat.ravel()))
    out.SetOrigin(tuple(o + dmat @ (lo * sp)))
    out = sitk.BinaryMorphologicalClosing(out, [1, 1, 1])
    soft = sitk.SmoothingRecursiveGaussian(sitk.Cast(out, sitk.sitkFloat32), 1.0)
    out = sitk.Cast(soft > 0.5, sitk.sitkUInt8)
    sitk.WriteImage(out, str(CORD_STRAIGHT))
    print(f"  {CORD_STRAIGHT.name}: {sitk.GetArrayFromImage(out).sum() / 1000:.2f} mL (projected {mask.sum() / 1000:.2f} mL)")
    return True


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
        # the build meshes the re-posed file instead of the content's projected one
        derived["sp-cord"] = {"note": CORD_NOTE, "files": {"M": str(CORD_STRAIGHT.relative_to(ROOT))}}
    (DER / "derived.json").write_text(json.dumps(derived, indent=1) + "\n", encoding="utf-8")
    print("derived:", derived)


if __name__ == "__main__":
    main()
