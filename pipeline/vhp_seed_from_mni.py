#!/usr/bin/env python3
"""MNI coordinates -> Visible Human slice number and pixel position, through the fitted MNI->VHP transform.

    pipeline/.venv/bin/python pipeline/vhp_seed_from_mni.py            # all 'mni' placeholders in content/structures.json
    pipeline/.venv/bin/python pipeline/vhp_seed_from_mni.py 0 4 -32    # one RAS point
    ... --affine-only                                                   # skip the B-spline part (outside the brain mask)

Prints a targets.json fragment for vhp_segment.py: the slice where the structure's centre lands and the
full-resolution pixel seed, plus a slice range from the placeholder's z radius.
Coordinates: content/structures.json is RAS (MNI convention); SimpleITK works in LPS, so x and y are
negated before the transform. The transform maps MNI (fixed) -> VHP (moving), so a point goes forward.
"""
import json
import sys
from pathlib import Path

import numpy as np
import SimpleITK as sitk

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vhp_stack_register import lps_to_photo  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TFM = ROOT / "data" / "raw" / "vhp" / "vhp_to_mni.tfm"
GREY = ROOT / "data" / "raw" / "vhp" / "vhp_head_grey.nii.gz"


def ras_to_vhp(tfm, p_ras):
    lps = (float(-p_ras[0]), float(-p_ras[1]), float(p_ras[2]))
    return np.array(tfm.TransformPoint(lps))


def main():
    tfm = sitk.ReadTransform(str(TFM))
    if "--affine-only" in sys.argv:
        tfm = sitk.CompositeTransform(tfm).GetNthTransform(0)
        sys.argv.remove("--affine-only")
    grey = sitk.ReadImage(str(GREY))
    if len(sys.argv) == 4:
        p = [float(v) for v in sys.argv[1:4]]
        q = ras_to_vhp(tfm, p)
        print({"mni_ras": p, "vhp_lps_mm": np.round(q, 1).tolist(), "slice_px": lps_to_photo(grey, q)})
        return
    structures = json.loads((ROOT / "content" / "structures.json").read_text(encoding="utf-8"))["structures"]
    out = []
    for s in structures:
        src = s["source"]
        if src.get("atlas") != "mni":
            continue
        c = np.array(src["centreMni"], float)
        rz = src["radiiMm"][2]
        for side in (["R", "L"] if src.get("bilateral") else ["M"]):
            cc = c.copy()
            if side == "L":
                cc[0] = -abs(cc[0])
            elif side == "R":
                cc[0] = abs(cc[0])
            q = ras_to_vhp(tfm, cc)
            sl, x, y = lps_to_photo(grey, q)
            area = np.pi * src["radiiMm"][0] * src["radiiMm"][1]
            out.append({"id": s["id"], "side": side, "slices": [int(sl - rz - 2), int(sl + rz + 2)], "seedSlice": int(sl), "seed": [x, y],
                        "areaMm2": [round(area * 0.15), round(area * 3)], "note": s["name"]["ko"]})
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
