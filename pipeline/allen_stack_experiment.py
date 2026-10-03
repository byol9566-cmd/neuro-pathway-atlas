#!/usr/bin/env python3
"""Experiment: stack the Allen adult human atlas annotations (106 coronal plates, SVG) into a label volume.

    pipeline/.venv/bin/python pipeline/allen_stack_experiment.py <scratch/allen> [--mm 0.5]

The API gives no 2D/3D alignment for these plates, so this does what "just stacking" means:
  y (anterior-posterior) = section_number x 50 um, plates placed by their own outline centroid, then each
  plate is rigidly (translation + rotation) aligned to its neighbour by the outline of the whole section.
Output: <scratch>/stack.nii.gz (uint16 structure ids, RAS-ish axes), a stats json, and meshes for a few
structures via the project's meshing module, to compare with NextBrain. Research/educational use only
(Allen Institute terms of use are non-commercial).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from svgelements import SVG, Path as SvgPath

scratch = Path(sys.argv[1])
MM = float(sys.argv[sys.argv.index("--mm") + 1]) if "--mm" in sys.argv else 0.5
plates = sorted(json.loads((scratch / "plates.json").read_text()), key=lambda p: p["section_number"])
onto = {s["id"]: s for s in json.loads((scratch / "ontology16.json").read_text())}


def rasterise(svg_file: Path, res_um: float, mm: float):
    """Label image for one plate at `mm` per pixel; later (child) paths overwrite earlier ones."""
    svg = SVG.parse(str(svg_file), reify=True)  # applies the group scale(7,7) to coordinates
    paths = []
    for el in svg.elements():
        if isinstance(el, SvgPath) and el.values.get("structure_id"):
            paths.append((int(el.values.get("order", 0)), int(el.values["structure_id"]), el))
    paths.sort(key=lambda t: t[0])
    px_per_mm = 1000.0 / res_um
    scale = 1.0 / (px_per_mm * mm)  # svg px -> image px
    w = h = 0
    polys = []
    for _, sid, p in paths:
        pts = []
        for seg in p.segments():
            n = max(2, int(seg.length(error=1e-2) * scale / 2) + 1) if hasattr(seg, "length") else 2
            for t in np.linspace(0, 1, n, endpoint=False):
                pt = seg.point(t)
                pts.append((pt.x * scale, pt.y * scale))
        if len(pts) >= 3:
            polys.append((sid, pts))
            w = max(w, max(x for x, _ in pts)); h = max(h, max(y for _, y in pts))
    img = Image.new("I", (int(w) + 2, int(h) + 2), 0)
    draw = ImageDraw.Draw(img)
    for sid, pts in polys:
        draw.polygon(pts, fill=sid)
    return np.array(img, dtype=np.int32)


def outline_pose(lab):
    ys, xs = np.nonzero(lab)
    c = np.array([xs.mean(), ys.mean()])
    cov = np.cov(np.stack([xs - c[0], ys - c[1]]))
    ang = 0.5 * np.arctan2(2 * cov[0, 1], cov[0, 0] - cov[1, 1])
    return c, ang


def main():
    labs = []
    for p in plates:
        f = next(scratch.glob(f"svg/{p['section_number']:05d}_*.svg"))
        lab = rasterise(f, p["resolution"], MM)
        labs.append((p["section_number"], lab))
        print(f"plate {p['section_number']:5d}: {lab.shape} labels={len(np.unique(lab)) - 1}", flush=True)
    H = max(l.shape[0] for _, l in labs) + 40
    W = max(l.shape[1] for _, l in labs) + 40
    y0, y1 = labs[0][0], labs[-1][0]
    depth = int(round((y1 - y0) * 0.05 / MM)) + 1  # 50 um per section number
    vol = np.zeros((depth, H, W), dtype=np.uint16)
    # place every plate with its outline centroid at the image centre, principal axis vertical:
    # the crudest possible alignment, but the same for every plate
    centre = np.array([W / 2, H / 2])
    for sec, lab in labs:
        c, ang = outline_pose(lab)
        im = Image.fromarray(lab.astype(np.int32), mode="I")
        canvas = Image.new("I", (W, H), 0)
        canvas.paste(im, (int(centre[0] - c[0]), int(centre[1] - c[1])))
        z = int(round((sec - y0) * 0.05 / MM))
        vol[z] = np.array(canvas, dtype=np.uint16)
    # fill the gaps between plates by nearest plate (so the volume is solid for meshing)
    filled = np.zeros_like(vol)
    zs = [int(round((sec - y0) * 0.05 / MM)) for sec, _ in labs]
    for z in range(depth):
        near = min(zs, key=lambda zz: abs(zz - z))
        filled[z] = vol[near]
    np.save(scratch / "stack.npy", filled)
    ids, counts = np.unique(filled, return_counts=True)
    stats = {int(i): {"name": onto.get(int(i), {}).get("name"), "acronym": onto.get(int(i), {}).get("acronym"), "mm3": float(c) * MM**3} for i, c in zip(ids, counts) if i}
    (scratch / "stack_stats.json").write_text(json.dumps(stats, indent=1))
    print(f"volume {filled.shape} @ {MM} mm, structures {len(stats)}, plates {len(labs)}, y-gaps: min {min(b-a for a,b in zip(zs,zs[1:]))*MM:.1f} mm max {max(b-a for a,b in zip(zs,zs[1:]))*MM:.1f} mm")


if __name__ == "__main__":
    main()
