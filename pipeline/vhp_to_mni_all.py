#!/usr/bin/env python3
"""Re-project every Visible Human mask (data/derived/vhp/<id>.<side>.npz) into MNI space with the current
transform, then cut the derived parts. Run after vhp_stack_register.py changes the transform.

    pipeline/.venv/bin/python pipeline/vhp_to_mni_all.py
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import SimpleITK as sitk

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vhp_segment as vs  # noqa: E402

DER = Path(__file__).resolve().parent.parent / "data" / "derived" / "vhp"

for npz in sorted(DER.glob("*.npz")):
    d = np.load(npz)
    out = vs.to_mni(d["masks"], d["slices"], d["masks"].shape[1:])
    target = npz.with_name(npz.name.replace(".npz", ".mni.nii.gz"))
    sitk.WriteImage(out, str(target))
    a = sitk.GetArrayFromImage(out) > 0
    zz, yy, xx = np.nonzero(a)
    c = out.TransformContinuousIndexToPhysicalPoint((float(xx.mean()), float(yy.mean()), float(zz.mean())))
    print(f"{target.name}: {a.sum() * np.prod(out.GetSpacing()) / 1000:.2f} mL (VHP {d['masks'].sum() * vs.PX**2 / 1000:.2f} mL), centroid RAS {np.round([-c[0], -c[1], c[2]], 1)}")
subprocess.run([sys.executable, str(Path(__file__).with_name("vhp_derive.py"))], check=True)
