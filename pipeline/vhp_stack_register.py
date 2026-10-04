#!/usr/bin/env python3
"""Stack the Visible Human male head cryosections and register them to MNI152.

    pipeline/.venv/bin/python pipeline/vhp_stack_register.py [--mm 1.0] [--skip-stack]

Input  data/raw/vhp/male-head/a_vm1001.png ... a_vm1377.png   (2048x1216 RGB, 0.33 mm/px, 1 mm apart)
Output data/raw/vhp/vhp_head_rgb.npz   RGB volume at --mm (z, y, x, 3) in photo order, plus a grey volume
       data/raw/vhp/vhp_head_grey.nii.gz  grey volume, ITK/LPS axis order (see below)
       data/raw/vhp/vhp_to_mni.tfm     SimpleITK composite transform (affine; + B-spline with --bspline),
                                        MNI -> VHP (fixed -> moving: what Resample needs to pull VHP masks into MNI)
       data/raw/vhp/vhp_head_grey_mni.nii.gz  the grey volume resampled into MNI space (visual check)
Why grey->T1: the cryosection luminance separates grey matter (darker), white matter (bright) and CSF much
like an inverted T1, so Mattes mutual information handles it.

Axes. SimpleITK physical coordinates are LPS (ITK convention; NIfTI RAS headers are converted on read), so
the stacked array must be ordered (z: inferior->superior, y: anterior->posterior, x: right->left) for an
identity direction matrix. The cryosections are photographed from the feet: image top = posterior, image
left = subject's right, slice numbers grow head -> feet, so  vol = grey[::-1, ::-1, :].  Any RAS point from
content/structures.json has to be negated in x and y before it is given to the transform (vhp_seed_from_mni.py).
An earlier version stacked the array as RAS, which ITK read as a 180-degree rotation about z; MI then
settled on a mirrored brain, convincing inside the brain and tens of millimetres off outside it.

Initialisation. The specimen's head is pitched (chin up) by ~25-35 degrees relative to the AC-PC frame, far
outside the basin of a gradient optimiser started from 0. The two eyeballs are segmented (vhp_segment.py,
data/derived/vhp/so-eyeball.{R,L}.npz) and are easy to find in the MNI T1, so they fix translation, scale,
roll and yaw; the pitch (rotation about the inter-eye axis) is then found by an exhaustive metric search
inside the MNI brain mask, and rigid/affine/B-spline refinement follows from there.
Visible Human Project, U.S. National Library of Medicine — no licence required (NLM).
"""
import sys
from pathlib import Path

import numpy as np
import SimpleITK as sitk
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "vhp" / "male-head"
OUT = ROOT / "data" / "raw" / "vhp"
DERIVED = ROOT / "data" / "derived" / "vhp"
MNI_DIR = ROOT / "data" / "raw" / "mni" / "mni_icbm152_nlin_asym_09c"
MNI = MNI_DIR / "mni_icbm152_t1_tal_nlin_asym_09c.nii"
MNI_MASK = MNI_DIR / "mni_icbm152_t1_tal_nlin_asym_09c_mask.nii"
MM = float(sys.argv[sys.argv.index("--mm") + 1]) if "--mm" in sys.argv else 1.0
PX = 0.33  # mm per pixel in the cryosections
FIRST, LAST = 1001, 1377


def load_stack():
    files = [SRC / f"a_vm{n}.png" for n in range(FIRST, LAST + 1)]
    files = [f for f in files if f.exists()]
    f = int(round(MM / PX))
    slabs = []
    for p in files:
        im = np.asarray(Image.open(p).convert("RGB"))
        h, w = (im.shape[0] // f) * f, (im.shape[1] // f) * f
        im = im[:h, :w].reshape(h // f, f, w // f, f, 3).mean(axis=(1, 3))  # box downsample to ~MM
        slabs.append(im.astype(np.uint8))
    rgb = np.stack(slabs)  # (z, y, x, 3) in photo order; z increases downwards (slice numbers run head -> feet)
    return rgb, len(files)


def grey_volume(rgb):
    """photo-order RGB stack -> grey LPS volume as a SimpleITK image (identity direction, centred origin)"""
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).astype(np.float32)
    blue_bg = (rgb[..., 2].astype(int) - rgb[..., 0].astype(int) > 40) & (rgb[..., 2] > 60)  # the blue gel
    grey = lum.copy()
    grey[blue_bg] = 0
    vol = grey[::-1, ::-1, :]  # LPS: z inferior->superior, y anterior->posterior, x right->left (= photo x)
    img = sitk.GetImageFromArray(vol)  # array (z, y, x) -> sitk (x, y, z)
    img.SetSpacing((MM, MM, MM))
    img.SetOrigin((-vol.shape[2] * MM / 2, -vol.shape[1] * MM / 2, -vol.shape[0] * MM / 2))
    return img


def photo_to_lps(grey, slice_no, x_px, y_px):
    """full-resolution photo pixel on a slice -> LPS physical point in the grey volume"""
    nx, ny, nz = grey.GetSize()
    f = MM / PX
    idx = (x_px / f - 0.5, (ny - 1) - (y_px / f - 0.5), (nz - 1) - (slice_no - FIRST))
    return np.array(grey.TransformContinuousIndexToPhysicalPoint(tuple(float(v) for v in idx)))


def lps_to_photo(grey, p):
    """inverse of photo_to_lps -> (slice number, x px, y px)"""
    nx, ny, nz = grey.GetSize()
    f = MM / PX
    ix, iy, iz = grey.TransformPhysicalPointToContinuousIndex(tuple(float(v) for v in p))
    return int(round(FIRST + (nz - 1) - iz)), int(round((ix + 0.5) * f)), int(round(((ny - 1) - iy + 0.5) * f))


def vhp_eye_centroids(grey):
    """LPS centroids of the segmented eyeballs, from the SAM masks (photo pixels)"""
    out = {}
    for side in ("R", "L"):
        d = np.load(DERIVED / f"so-eyeball.{side}.npz")
        pts = []
        for n, m in zip(d["slices"], d["masks"]):
            ys, xs = np.nonzero(m)
            if xs.size:
                pts.append(photo_to_lps(grey, int(n), xs.mean(), ys.mean()))
        out[side] = np.mean(pts, axis=0)
    return out


def mni_eye_centroids(mni):
    """LPS centroids of the eyeballs in the MNI T1: the vitreous is a dark sphere inside each orbit"""
    arr = sitk.GetArrayFromImage(mni)
    out = {}
    for side, xr in (("R", (-45.0, -15.0)), ("L", (15.0, 45.0))):  # LPS x: negative = right
        # orbit box in LPS (RAS y +40..+72, z -55..-15); the vitreous sits at 25-35 on the 2009c T1 scale
        # where the skin/air rim is < 20, so a fixed band beats a percentile (a percentile band grabbed the
        # dim rim and put the "eye" 20 mm too far forward)
        lo = mni.TransformPhysicalPointToIndex((xr[0], -72.0, -55.0))
        hi = mni.TransformPhysicalPointToIndex((xr[1], -40.0, -15.0))
        sl = [slice(min(a, b), max(a, b)) for a, b in zip(lo, hi)]
        sub = arr[sl[2], sl[1], sl[0]]
        m = (sub > 20) & (sub < 45)
        # keep the largest connected blob
        cc = sitk.ConnectedComponent(sitk.GetImageFromArray(m.astype(np.uint8)))
        st = sitk.LabelShapeStatisticsImageFilter(); st.Execute(cc)
        big = max(st.GetLabels(), key=st.GetPhysicalSize)
        mm = sitk.GetArrayFromImage(cc) == big
        zz, yy, xx = np.nonzero(mm)
        idx = (xx.mean() + sl[0].start, yy.mean() + sl[1].start, zz.mean() + sl[2].start)
        out[side] = np.array(mni.TransformContinuousIndexToPhysicalPoint(tuple(float(v) for v in idx)))
        print(f"MNI eye {side}: LPS {out[side].round(1)} (RAS {(out[side] * [-1, -1, 1]).round(1)}), {mm.sum()} voxels", flush=True)
    return out


def rotation_between(a, b):
    """rotation matrix taking unit vector a onto unit vector b (Rodrigues)"""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = float(a @ b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k * (1 / (1 + c))


def eye_init(f_eyes, m_eyes, pitch):
    """fixed(MNI) -> moving(VHP) similarity: eye midpoints coincide, inter-eye axes align, scale from the
    inter-eye distance, then a rotation `pitch` about the (MNI) inter-eye axis through the midpoint"""
    fc = (f_eyes["R"] + f_eyes["L"]) / 2
    mc = (m_eyes["R"] + m_eyes["L"]) / 2
    fa = f_eyes["L"] - f_eyes["R"]
    ma = m_eyes["L"] - m_eyes["R"]
    s = np.linalg.norm(ma) / np.linalg.norm(fa)
    r_align = rotation_between(fa, ma)
    ax = fa / np.linalg.norm(fa)
    k = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    r_pitch = np.eye(3) + np.sin(pitch) * k + (1 - np.cos(pitch)) * k @ k
    r = r_align @ r_pitch
    t = sitk.AffineTransform(3)
    t.SetCenter(tuple(map(float, fc)))
    t.SetMatrix(tuple(map(float, (s * r).ravel())))
    t.SetTranslation(tuple(map(float, mc - fc)))
    return t


def main():
    if "--skip-stack" in sys.argv and (OUT / "vhp_head_rgb.npz").exists():
        rgb = np.load(OUT / "vhp_head_rgb.npz")["rgb"]
        print("stack loaded", rgb.shape, flush=True)
    else:
        rgb, n = load_stack()
        print("stack", rgb.shape, "from", n, "slices", flush=True)
        np.savez_compressed(OUT / "vhp_head_rgb.npz", rgb=rgb, mm=MM, first=FIRST)
    img = grey_volume(rgb)
    sitk.WriteImage(img, str(OUT / "vhp_head_grey.nii.gz"))

    mni = sitk.ReadImage(str(MNI), sitk.sitkFloat32)
    mask = sitk.Cast(sitk.ReadImage(str(MNI_MASK)) > 0, sitk.sitkUInt8)
    mask = sitk.BinaryDilate(mask, [6, 6, 6])  # a little skull/CSF around the brain helps the surface
    mov = sitk.Cast(img, sitk.sitkFloat32)

    f_eyes = mni_eye_centroids(mni)
    m_eyes = vhp_eye_centroids(img)
    # the metric also sees the orbits (a 16 mm ball around each eye): with the brain alone, the affine is
    # free to shear the face and two runs that differed only in their start put the eyes 3 mm vs 16 mm off
    for s in ("R", "L"):
        c = mni.TransformPhysicalPointToIndex(tuple(map(float, f_eyes[s])))
        ball = sitk.Image(mni.GetSize(), sitk.sitkUInt8); ball.CopyInformation(mni)
        ball[c] = 1
        mask = sitk.Or(mask, sitk.BinaryDilate(ball, [16, 16, 16]))
    for s in ("R", "L"):
        print(f"VHP eye {s}: LPS {m_eyes[s].round(1)} -> photo {lps_to_photo(img, m_eyes[s])}", flush=True)
    print("inter-eye mm: MNI", np.linalg.norm(f_eyes['L'] - f_eyes['R']).round(1), "VHP", np.linalg.norm(m_eyes['L'] - m_eyes['R']).round(1), flush=True)

    # 0. pitch search about the inter-eye axis, metric inside the (dilated) brain mask
    small_f = sitk.Shrink(sitk.SmoothingRecursiveGaussian(mni, 2.0), [4, 4, 4])
    small_m = sitk.Shrink(sitk.SmoothingRecursiveGaussian(mov, 2.0), [4, 4, 4])
    small_mask = sitk.Shrink(mask, [4, 4, 4])
    probe = sitk.ImageRegistrationMethod()
    probe.SetMetricAsMattesMutualInformation(32)
    probe.SetMetricSamplingStrategy(probe.NONE)
    probe.SetMetricFixedMask(small_mask)
    probe.SetInterpolator(sitk.sitkLinear)
    best = None
    for deg in np.arange(-60, 61, 2.5):
        t = eye_init(f_eyes, m_eyes, np.radians(deg))
        probe.SetInitialTransform(t, inPlace=False)
        try:
            v = probe.MetricEvaluate(small_f, small_m)
        except RuntimeError:
            continue
        print(f"  pitch {deg:+6.1f} deg: metric {v:.4f}", flush=True)
        if best is None or v < best[0]:
            best = (v, float(deg))
    print(f"pitch search: best {best[1]:+.1f} deg (metric {best[0]:.4f})", flush=True)
    init = eye_init(f_eyes, m_eyes, np.radians(best[1]))

    # 1. affine refinement (the init is already a similarity, so go straight to affine)
    reg = sitk.ImageRegistrationMethod()
    reg.SetMetricAsMattesMutualInformation(50)
    reg.SetMetricSamplingStrategy(reg.RANDOM); reg.SetMetricSamplingPercentage(0.25, seed=1234)
    reg.SetMetricFixedMask(mask)
    reg.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=300, estimateLearningRate=reg.EachIteration)
    reg.SetOptimizerScalesFromPhysicalShift()
    reg.SetInitialTransform(init, inPlace=True)
    reg.SetShrinkFactorsPerLevel([8, 4, 2]); reg.SetSmoothingSigmasPerLevel([4, 2, 1])
    reg.SetInterpolator(sitk.sitkLinear)
    affine = reg.Execute(mni, mov)
    print("affine done, metric", reg.GetMetricValue(), flush=True)
    check(affine, img, mni, m_eyes, f_eyes, "affine (MI only)")
    affine = eye_corrected_affine(affine, mask, f_eyes, m_eyes)
    sitk.WriteTransform(affine, str(OUT / "vhp_to_mni_affine.tfm"))
    check(affine, img, mni, m_eyes, f_eyes, "affine")

    if "--bspline" not in sys.argv:
        # Default: the affine is the result. Every B-spline tried here over-fitted the mutual information
        # (12x14x12 grid / 60 iterations: 10 mm mean, 24 mm max displacement, Jacobian 0.1 at the sella, a
        # 0.9 mL pituitary blown up to 5.8 mL; 6x7x6 / 30 iterations: still 9 mm mean, Jacobian 0.36-2.9)
        # and nothing segmented from the cryosections so far lies deep enough in the brain to need one.
        final = sitk.CompositeTransform([affine])
        sitk.WriteTransform(final, str(OUT / "vhp_to_mni.tfm"))
        warped = sitk.Resample(mov, mni, final, sitk.sitkLinear, 0.0)
        sitk.WriteImage(sitk.Cast(warped, sitk.sitkFloat32), str(OUT / "vhp_head_grey_mni.nii.gz"))
        print("wrote", OUT / "vhp_to_mni.tfm", "(affine only) and the MNI-space grey volume")
        return
    # 2. optional B-spline refinement inside the brain mask (outside it the affine is extrapolated);
    #    bspline_stats prints what it did so the over-fitting above is visible before anything uses it
    bs = sitk.BSplineTransformInitializer(mni, [6, 7, 6])
    comp = sitk.CompositeTransform([affine, bs])
    reg2 = sitk.ImageRegistrationMethod()
    reg2.SetMetricAsMattesMutualInformation(50)
    reg2.SetMetricSamplingStrategy(reg2.RANDOM); reg2.SetMetricSamplingPercentage(0.1, seed=1234)
    reg2.SetMetricFixedMask(mask)
    reg2.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5, numberOfIterations=30)
    reg2.SetInitialTransform(comp, inPlace=True)
    reg2.SetShrinkFactorsPerLevel([4, 2]); reg2.SetSmoothingSigmasPerLevel([2, 1])
    reg2.SetInterpolator(sitk.sitkLinear)
    final = reg2.Execute(mni, mov)
    print("bspline done, metric", reg2.GetMetricValue(), flush=True)
    bspline_stats(final, mask)
    sitk.WriteTransform(final, str(OUT / "vhp_to_mni.tfm"))
    warped = sitk.Resample(mov, mni, final, sitk.sitkLinear, 0.0)
    sitk.WriteImage(sitk.Cast(warped, sitk.sitkFloat32), str(OUT / "vhp_head_grey_mni.nii.gz"))
    check(final, img, mni, m_eyes, f_eyes, "final")
    print("wrote", OUT / "vhp_to_mni.tfm", "and the MNI-space grey volume")


def eye_corrected_affine(affine, mask, f_eyes, m_eyes, n_brain=400, eye_weight=300.0):
    """Mutual information inside the brain fixes the affine well there but leaves its extrapolation to the
    face free: runs that differed only in their start put the eyes 3 mm or 15 mm off. Refit the affine by
    weighted least squares to (a) brain points mapped by the MI affine, so the brain alignment is kept, and
    (b) the two measured eye correspondences, weighted heavily. The B-spline step then refines the brain."""
    rng = np.random.default_rng(0)
    arr = sitk.GetArrayFromImage(mask)
    zz, yy, xx = np.nonzero(arr)
    pick = rng.choice(len(zz), size=n_brain, replace=False)
    src = [np.array(mask.TransformIndexToPhysicalPoint((int(xx[i]), int(yy[i]), int(zz[i])))) for i in pick]
    dst = [np.array(affine.TransformPoint(tuple(map(float, p)))) for p in src]
    w = [1.0] * n_brain
    for s in ("R", "L"):
        src.append(f_eyes[s]); dst.append(m_eyes[s]); w.append(eye_weight)
    S = np.array(src); D = np.array(dst); W = np.sqrt(np.array(w))[:, None]
    X = np.hstack([S, np.ones((len(S), 1))]) * W
    sol, *_ = np.linalg.lstsq(X, D * W, rcond=None)  # (4, 3): rows = x, y, z, 1
    A = sol[:3].T; b = sol[3]
    out = sitk.AffineTransform(3)
    out.SetMatrix(tuple(map(float, A.ravel())))
    out.SetTranslation(tuple(map(float, b)))
    resid = np.linalg.norm((S[:n_brain] @ A.T + b) - D[:n_brain], axis=1)
    print(f"eye-corrected affine: brain points moved {resid.mean():.1f} mm mean / {resid.max():.1f} mm max", flush=True)
    return out


def bspline_stats(final, mask, n=300):
    """displacement of the B-spline part and the Jacobian determinant of the whole map at brain points"""
    comp = sitk.CompositeTransform(final)
    bs = comp.GetNthTransform(1)
    arr = sitk.GetArrayFromImage(mask)
    zz, yy, xx = np.nonzero(arr)
    rng = np.random.default_rng(1)
    disp, dets = [], []
    for i in rng.choice(len(zz), size=n, replace=False):
        p = np.array(mask.TransformIndexToPhysicalPoint((int(xx[i]), int(yy[i]), int(zz[i]))))
        disp.append(np.linalg.norm(np.array(bs.TransformPoint(tuple(p))) - p))
        J = np.zeros((3, 3))
        for k in range(3):
            e = np.zeros(3); e[k] = 0.5
            J[:, k] = (np.array(final.TransformPoint(tuple(p + e))) - np.array(final.TransformPoint(tuple(p - e))))
        dets.append(np.linalg.det(J))
    print(f"bspline displacement in brain: mean {np.mean(disp):.1f} mm, max {np.max(disp):.1f} mm; "
          f"Jacobian det {np.min(dets):.2f}..{np.max(dets):.2f} (median {np.median(dets):.2f})", flush=True)


def check(tfm, grey, mni, m_eyes, f_eyes, label):
    """how far the VHP eye centroids land from the MNI eye centroids (the eyes are outside the brain mask,
    so this is an independent check of the extrapolation); the transform maps MNI -> VHP"""
    for s in ("R", "L"):
        q = np.array(tfm.TransformPoint(tuple(map(float, f_eyes[s]))))
        print(f"[{label}] MNI eye {s} -> VHP {q.round(1)} vs segmented {m_eyes[s].round(1)}: {np.linalg.norm(q - m_eyes[s]):.1f} mm off", flush=True)


if __name__ == "__main__":
    main()
