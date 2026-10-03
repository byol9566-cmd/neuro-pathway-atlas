"""Build viewer/public/data/{atlas.glb, manifest.json} from content/structures.json.

    python -m atlas_pipeline.build [--only ID ...] [--no-compress]

NextBrain is a left-hemisphere volume in MNI-aligned RAS mm; right-side meshes are mirrored across x = 0.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time

import nibabel as nib
import numpy as np
import trimesh
from scipy import ndimage

from . import CONTENT_DIR, DATA_DIR, OUT_DIR, REPO_ROOT, meshing, sections

# Labels that make up the brainstem / cerebellum outlines. `white_matter_of_hindbrain` (611) spans
# both and is split by proximity in `shell_masks`.
HINDBRAIN_WM = 611
CEREBELLUM_IDS = [595, 597, 715, 721, 751, 752]
BRAINSTEM_IDS = [
    310, 352, 384, 385, 386, 401, 414, 415, 431, 435, 436, 465, 471, 499, 507, 515, 520, 521, 525, 526, 527,
    528, 531, 535, 541, 542, 543, 546, 580, 581, 586, 589, 591, 592, 598, 599, 600, 610, 617, 624, 630, 645,
    647, 649, 654, 655, 659, 660, 662, 666, 669, 671, 677, 682, 683, 685, 687, 689, 690, 693, 694, 695, 697,
    703, 717, 724, 725, 726, 731, 755, 756, 765, 771, 779, 827, 828, 829, 842, 844,
]  # fmt: skip

SHELL_STRIDE = 4
PLACEHOLDER_BELOW_MM3 = 6.0

ATTRIBUTION = [
    {
        "atlas": "nextbrain",
        "title": "NextBrain: registered histology, MRI and manual annotations of 5 human hemispheres",
        "citation": "Casamitjana A, et al. A probabilistic histological atlas of the human brain for MRI segmentation. Nature (2025).",
        "license": "CC0 1.0",
        "url": "https://doi.org/10.5522/04/24243835",
    },
    {
        "atlas": "aan",
        "title": "Harvard Ascending Arousal Network Atlas v2.0",
        "citation": "Edlow BL, et al. Sustaining wakefulness: brainstem connectivity in human consciousness.",
        "license": "CC0 1.0",
        "url": "https://zenodo.org/records/8161638",
    },
]


class NextBrain:
    def __init__(self):
        img = nib.load(DATA_DIR / "nextbrain" / "atlas.labels.argmax.nii.gz")
        affine = img.affine
        assert np.allclose(affine[:3, :3], np.diag(np.diag(affine[:3, :3]))) and np.all(np.diag(affine) > 0), affine
        self.spacing = float(affine[0, 0])
        self.origin = affine[:3, 3].copy()
        self.data = np.asanyarray(img.dataobj)[..., 0].astype(np.uint16)
        self.objects = ndimage.find_objects(self.data)
        self.present = {i + 1 for i, sl in enumerate(self.objects) if sl is not None}
        self._shells = None

    def expand_labels(self, source: dict) -> list[int]:
        labels = list(source.get("labels", []))
        for lo, hi in source.get("labelRanges", []):
            labels += [i for i in range(lo, hi + 1) if i in self.present]
        missing = [i for i in labels if i not in self.present]
        if missing:
            raise ValueError(f"labels not present in the volume: {missing}")
        return labels

    def label_mask(self, labels: list[int], stride: int = 1):
        """Boolean mask of `labels` cropped to their joint bounding box -> (mask, spacing, origin)."""
        boxes = [self.objects[i - 1] for i in labels]
        box = tuple(slice(min(b[a].start for b in boxes), max(b[a].stop for b in boxes)) for a in range(3))
        mask = np.isin(self.data[box], labels)
        start = np.array([s.start for s in box])
        if stride > 1:
            mask = mask[::stride, ::stride, ::stride]
        return mask, self.spacing * stride, self.origin + start * self.spacing

    def shell_masks(self) -> dict[str, np.ndarray]:
        if self._shells is None:
            ds = self.data[::SHELL_STRIDE, ::SHELL_STRIDE, ::SHELL_STRIDE]
            brainstem = np.isin(ds, BRAINSTEM_IDS)
            cerebellum = np.isin(ds, CEREBELLUM_IDS)
            wm = ds == HINDBRAIN_WM
            nearer_cerebellum = ndimage.distance_transform_edt(~cerebellum) < ndimage.distance_transform_edt(~brainstem)
            cerebellum = cerebellum | (wm & nearer_cerebellum)
            brainstem = brainstem | (wm & ~nearer_cerebellum)
            cerebrum = (ds > 0) & ~brainstem & ~cerebellum
            # outlines only: closing off the ventricles removes inner surfaces that would stack up as ghost layers
            cerebrum, brainstem, cerebellum = (ndimage.binary_fill_holes(m) for m in (cerebrum, brainstem, cerebellum))
            self._shells = {"cerebrum": cerebrum, "brainstem": brainstem, "cerebellum": cerebellum}
        return self._shells


def load_aan_mask(filename: str):
    """AAN nuclei are 1 mm MNI152 masks; upsample x4 (nearest) so smoothing can round off the voxel blocks."""
    img = nib.as_closest_canonical(nib.load(DATA_DIR / "aan" / filename))
    affine = img.affine
    assert np.allclose(affine[:3, :3], np.diag(np.diag(affine[:3, :3]))), affine
    data = np.asanyarray(img.dataobj)
    mask = data > 0.5 * data.max()
    box = ndimage.find_objects(mask.astype(np.uint8))[0]
    start = np.array([s.start for s in box])
    spacing, factor = float(affine[0, 0]), 4
    fine = np.kron(mask[box], np.ones((factor,) * 3, dtype=bool))
    # centre of fine voxel j sits at old index (j + 0.5) / factor - 0.5
    origin = affine[:3, 3] + start * spacing + (0.5 / factor - 0.5) * spacing
    return fine, spacing / factor, origin


AAN_COMBINED = "AAN_Brainstem_MNI152_1mm_v2p0.nii"
_aan_combined = None


def load_aan_labels(labels: list[int]):
    """Same as load_aan_mask, but from the combined v2.0 volume (one label id per nucleus, see its LUT)."""
    global _aan_combined
    if _aan_combined is None:
        img = nib.as_closest_canonical(nib.load(DATA_DIR / "aan" / AAN_COMBINED))
        _aan_combined = (img.affine, np.asanyarray(img.dataobj).astype(np.int32))
    affine, data = _aan_combined
    assert np.allclose(affine[:3, :3], np.diag(np.diag(affine[:3, :3]))), affine
    mask = np.isin(data, labels)
    if not mask.any():
        raise ValueError(f"AAN labels {labels} are empty")
    box = ndimage.find_objects(mask.astype(np.uint8))[0]
    start = np.array([s.start for s in box])
    spacing, factor = float(affine[0, 0]), 4
    fine = np.kron(mask[box], np.ones((factor,) * 3, dtype=bool))
    origin = affine[:3, 3] + start * spacing + (0.5 / factor - 0.5) * spacing
    return fine, spacing / factor, origin


def open_edge_count(mesh) -> int:
    """Edges used by a single face, i.e. actual holes. (Decimation may also pinch an edge between four
    faces, which breaks `is_watertight` but is invisible when rendered.)"""
    _, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    return int((counts == 1).sum())


def mesh_record(mesh_id, structure, side, mesh, *, volume_mm3, approx, stats=None, line=None):
    rec = {
        "id": mesh_id,
        "structureId": structure["id"],
        "side": side,
        "centroid": np.round(mesh.centroid, 2).tolist(),
        "bboxMin": np.round(mesh.bounds[0], 2).tolist(),
        "bboxMax": np.round(mesh.bounds[1], 2).tolist(),
        "volumeMm3": round(float(volume_mm3), 1),
        "meshVolumeMm3": round(float(mesh.volume), 1),
        "faces": int(len(mesh.faces)),
        "openEdges": open_edge_count(mesh),
        "approx": approx,
    }
    if stats is not None:
        rec["cleanup"] = {
            "componentsRaw": stats.components_raw,
            "componentsKept": stats.components_kept,
            "keptFraction": round(stats.kept_fraction, 3),
        }
    if line is not None:
        rec["centerline"] = np.round(line, 2).tolist()
    return rec


def build_from_mask(mask, spacing, origin, *, sigma_mm, faces_per_mm2, max_faces, closing_iters=1):
    cleaned, stats = meshing.clean_mask(mask, closing_iters=closing_iters)
    mesh = meshing.mask_to_mesh(cleaned, spacing, origin, smooth_sigma_mm=sigma_mm)
    mesh = meshing.simplify(mesh, meshing.target_face_count(mesh, faces_per_mm2, hi=max_faces))
    return cleaned, stats, mesh


def build_structure(structure: dict, nb: NextBrain):
    """-> list of (mesh_id, trimesh, manifest record)."""
    src = structure["source"]
    sid = structure["id"]
    out = []

    def add_pair(mesh_l, **kw):
        line = kw.pop("line", None)
        out.append((f"{sid}.L", mesh_l, mesh_record(f"{sid}.L", structure, "L", mesh_l, line=line, **kw)))
        mesh_r = meshing.mirror_x(mesh_l)
        line_r = None if line is None else line * np.array([-1.0, 1.0, 1.0])
        out.append((f"{sid}.R", mesh_r, mesh_record(f"{sid}.R", structure, "R", mesh_r, line=line_r, **kw)))

    if src["atlas"] == "mni":
        # no atlas gives the shape, but the position and size are known: an ellipsoid at MNI coordinates,
        # given for the right side when bilateral (the left is its mirror image)
        center = np.array(src["centreMni"], dtype=float)
        mesh = meshing.ellipsoid(center, src["radiiMm"])
        vol = float(mesh.volume)
        if src.get("bilateral"):
            out.append((f"{sid}.R", mesh, mesh_record(f"{sid}.R", structure, "R", mesh, volume_mm3=vol, approx=True)))
            mesh_l = meshing.mirror_x(mesh)
            out.append((f"{sid}.L", mesh_l, mesh_record(f"{sid}.L", structure, "L", mesh_l, volume_mm3=vol, approx=True)))
        else:
            out.append((f"{sid}.M", mesh, mesh_record(f"{sid}.M", structure, "M", mesh, volume_mm3=vol, approx=True)))
        return out

    if src["atlas"] == "aan":
        # either one file per side (v2.0 per-nucleus files) or label ids in the combined volume
        sources = src.get("files") or {side: labels for side, labels in src["labels"].items()}
        for side, what in sources.items():
            mask, spacing, origin = load_aan_mask(what) if isinstance(what, str) else load_aan_labels(what)
            cleaned, stats, mesh = build_from_mask(
                mask, spacing, origin, sigma_mm=0.6, faces_per_mm2=6, max_faces=4000, closing_iters=0
            )
            vol = cleaned.sum() * spacing**3
            out.append((f"{sid}.{side}", mesh, mesh_record(f"{sid}.{side}", structure, side, mesh, volume_mm3=vol, approx=False, stats=stats)))
        return out

    if "shell" in src:
        mask = nb.shell_masks()[src["shell"]]
        spacing = nb.spacing * SHELL_STRIDE
        cleaned, stats, mesh = build_from_mask(
            mask, spacing, nb.origin, sigma_mm=1.0, faces_per_mm2=0.8, max_faces=50000, closing_iters=0
        )
        add_pair(mesh, volume_mm3=cleaned.sum() * spacing**3, approx=False, stats=stats)
        return out

    labels = nb.expand_labels(src)
    mask, spacing, origin = nb.label_mask(labels, stride=src.get("stride", 1))
    if not mask.any():
        raise ValueError(f"{sid}: labels {labels} have no voxels in the atlas")
    cleaned, stats = meshing.clean_mask(mask)
    vol = cleaned.sum() * spacing**3
    placeholder = src.get("placeholder")
    if vol < PLACEHOLDER_BELOW_MM3 and (placeholder or mask.any()):
        # too few voxels for a surface: an ellipsoid at the label's centroid. Explicit radii if the
        # content gives them, otherwise a sphere a little larger than the label's own volume so the
        # nucleus is at least visible (small nuclei of the reviewer's list land here)
        center = np.argwhere(mask).mean(axis=0) * spacing + origin
        if placeholder:
            radii = placeholder["radiiMm"]
        else:
            r = max(1.0, (3.0 * max(vol, 0.5) / (4.0 * np.pi)) ** (1.0 / 3.0) * 1.5)
            radii = [r, r, r]
        mesh = meshing.ellipsoid(center, radii)
        add_pair(mesh, volume_mm3=mask.sum() * spacing**3, approx=True, stats=stats)
        return out
    if not mask.any():
        raise ValueError(f"{sid}: labels {labels} have no voxels")

    sigma = 0.5 if src.get("stride", 1) > 1 else (0.2 if vol < 30 else 0.3)
    mesh = meshing.mask_to_mesh(cleaned, spacing, origin, smooth_sigma_mm=sigma)
    mesh = meshing.simplify(mesh, meshing.target_face_count(mesh, 6.0))
    wants_line = structure.get("tract") or structure.get("centerline")
    line = meshing.centerline(cleaned, spacing, origin) if wants_line else None
    add_pair(mesh, volume_mm3=vol, approx=False, stats=stats, line=line)
    return out


def compress(raw_glb, out_glb) -> bool:
    cli = REPO_ROOT / "viewer" / "node_modules" / ".bin" / "gltf-transform"
    if not cli.exists():
        return False
    subprocess.run([str(cli), "meshopt", str(raw_glb), str(out_glb), "--level", "medium"], check=True, capture_output=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="build only these structure ids (manifest is still complete for them)")
    ap.add_argument("--no-compress", action="store_true")
    ap.add_argument("--no-sections", action="store_true", help="skip exporting the 2D section slices")
    args = ap.parse_args(argv)

    config = json.loads((CONTENT_DIR / "structures.json").read_text())
    structures = [s for s in config["structures"] if not args.only or s["id"] in args.only]

    t0 = time.time()
    nb = NextBrain()
    print(f"nextbrain loaded: {nb.data.shape} @ {nb.spacing} mm, {len(nb.present)} labels ({time.time() - t0:.1f}s)")

    scene = trimesh.Scene()
    mesh_records, structure_records, skipped = [], [], []
    for s in structures:
        t = time.time()
        try:
            built = build_structure(s, nb)
        except ValueError as err:
            print(f"  !! skipped {s['id']}: {err}")
            skipped.append(s["id"])
            continue
        for mesh_id, mesh, rec in built:
            mesh.vertex_normals  # noqa: B018 -- compute so the GLB carries smooth normals
            scene.add_geometry(mesh, node_name=mesh_id, geom_name=mesh_id)
            mesh_records.append(rec)
        first = built[0][2]
        structure_records.append(
            {
                "id": s["id"],
                "group": s["group"],
                "name": s["name"],
                "tract": bool(s.get("tract")),
                "approx": first["approx"],
                "atlas": s["source"]["atlas"],
                # atlas label ids behind this structure: lets the 2D section panel map a pixel to it
                "labels": nb.expand_labels(s["source"]) if s["source"]["atlas"] == "nextbrain" and "shell" not in s["source"] else [],
                "meshIds": [m[0] for m in built],
            }
        )
        flag = " [placeholder]" if first["approx"] else ""
        kept = first.get("cleanup", {}).get("keptFraction")
        print(f"  {s['id']:24s} {first['volumeMm3']:9.1f} mm3  {first['faces']:6d} faces  kept={kept}  {time.time() - t:4.1f}s{flag}")

    if skipped:
        print(f"skipped {len(skipped)} structures with no usable voxels: {', '.join(skipped)}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = OUT_DIR / "atlas.raw.glb"
    final = OUT_DIR / "atlas.glb"
    raw.write_bytes(scene.export(file_type="glb", include_normals=True))
    compressed = False if args.no_compress else compress(raw, final)
    if compressed:
        raw.unlink()
    else:
        shutil.move(raw, final)

    manifest = {
        "space": "MNI-aligned RAS, millimetres (x: left- / right+, y: posterior- / anterior+, z: inferior- / superior+)",
        "compressed": compressed,
        "attribution": ATTRIBUTION,
        "groups": config["groups"],
        "structures": structure_records,
        "meshes": mesh_records,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    total_faces = sum(m["faces"] for m in mesh_records)
    print(f"{len(mesh_records)} meshes, {total_faces} faces, atlas.glb {final.stat().st_size / 1e6:.1f} MB"
          f"{'' if compressed else ' (uncompressed)'}, {time.time() - t0:.0f}s")
    if not args.no_sections and not args.only:
        sections.export_axial()
    leaky = [m["id"] for m in mesh_records if m["openEdges"]]
    if leaky:
        print("meshes with holes:", ", ".join(leaky), file=sys.stderr)


if __name__ == "__main__":
    main()
