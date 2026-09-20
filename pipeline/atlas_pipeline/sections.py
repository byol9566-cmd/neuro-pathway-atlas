"""Export axial slices of the NextBrain label volume for the viewer's 2D section panel.

    python -m atlas_pipeline.sections

Each slice is a PNG whose pixels carry the label id (R = low byte, G = high byte), so the viewer can
colour, highlight and hit-test all 333 labels without shipping the volume. In-plane resolution stays at
the atlas's native 0.2 mm; slices are taken every `Z_STEP` voxels. Only the left hemisphere is stored
(up to the midline); the viewer mirrors it, exactly as the 3D meshes are mirrored.

Image layout: column 0 = most lateral (x = xMin), last column = midline (x = 0);
row 0 = most anterior (y = yMax). Output: viewer/public/data/sections/axial/{meta.json, 0000.png, ...}
"""

import json
import re

import imageio.v3 as iio
import nibabel as nib
import numpy as np

from . import DATA_DIR, OUT_DIR

Z_STEP = 2  # 0.4 mm between slices


def read_lut() -> dict[int, tuple[str, list[int]]]:
    lut = {}
    for line in (DATA_DIR / "nextbrain" / "lut.freeview.txt").read_text().splitlines():
        m = re.match(r"^\s*(\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
        if m:
            lut[int(m.group(1))] = (m.group(2), [int(m.group(i)) for i in (3, 4, 5)])
    return lut


def slice_to_png_array(slab: np.ndarray) -> np.ndarray:
    """(x, y) uint16 labels -> (rows = y flipped, cols = x, 3) uint8 with the id packed into R and G."""
    rgb = np.zeros(slab.shape + (3,), np.uint8)
    rgb[..., 0] = slab & 0xFF
    rgb[..., 1] = slab >> 8
    return np.flipud(rgb.transpose(1, 0, 2))


def decode_png_array(rgb: np.ndarray) -> np.ndarray:
    """Inverse of `slice_to_png_array`."""
    ids = rgb[..., 0].astype(np.uint16) | (rgb[..., 1].astype(np.uint16) << 8)
    return np.flipud(ids).T


def export_axial():
    img = nib.load(DATA_DIR / "nextbrain" / "atlas.labels.argmax.nii.gz")
    spacing = float(img.affine[0, 0])
    origin = img.affine[:3, 3]
    data = np.asanyarray(img.dataobj)[..., 0].astype(np.uint16)

    midline = int(round((0.0 - origin[0]) / spacing))  # column of x = 0
    occupied = np.argwhere(data[: midline + 1].any(axis=2))
    (x0, y0), (x1, y1) = occupied.min(axis=0), occupied.max(axis=0)
    x1 = midline
    z_used = np.flatnonzero(data.any(axis=(0, 1)))
    z_indices = list(range(int(z_used.min()), int(z_used.max()) + 1, Z_STEP))

    out = OUT_DIR / "sections" / "axial"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    total = 0
    for n, k in enumerate(z_indices):
        png = iio.imwrite("<bytes>", slice_to_png_array(data[x0 : x1 + 1, y0 : y1 + 1, k]), extension=".png")
        (out / f"{n:04d}.png").write_bytes(png)
        total += len(png)

    lut = read_lut()
    present = np.unique(data)
    meta = {
        "axis": "axial",
        "pixelMm": spacing,
        "width": int(x1 - x0 + 1),
        "height": int(y1 - y0 + 1),
        "xMin": round(float(origin[0] + x0 * spacing), 3),  # RAS mm of column 0 (lateral edge, left hemisphere)
        "xMax": round(float(origin[0] + x1 * spacing), 3),  # ~0: the midline
        "yMin": round(float(origin[1] + y0 * spacing), 3),  # last row
        "yMax": round(float(origin[1] + y1 * spacing), 3),  # row 0
        "zStart": round(float(origin[2] + z_indices[0] * spacing), 3),
        "zStep": round(spacing * Z_STEP, 3),
        "count": len(z_indices),
        "labels": {str(int(i)): {"name": lut[int(i)][0], "color": lut[int(i)][1]} for i in present if i != 0},
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False))
    print(f"sections: {len(z_indices)} axial slices {meta['width']}x{meta['height']} px, {total / 1e6:.1f} MB -> {out}")
    return meta


if __name__ == "__main__":
    export_axial()
