"""Convert TRK bundles to representative centerlines in RAS+ millimetres.

Run from the repository root: python -m pipeline.tracts.bundle_centerlines --help
TRK spatial headers must describe MNI space; this module does not register images.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path
from typing import Iterable

import nibabel as nib
import numpy as np


SOURCE = {
    "atlas": "HCP1065",
    "license": "CC BY-SA 4.0",
    "url": "https://brain.labsolver.org/hcp_trk_atlas.html",
    "space": "ICBM 2009a nonlinear asym",
}

# Atlas filenames, rather than the inconsistent full-name cells in the XLSX,
# are authoritative. Aliases are only for selection and stable output IDs.
BASE_ALIASES = {
    "Cortico_Spinal_Tract": "CST",
    "Corticospinal_Tract": "CST",
    "Corticobulbar_Tract": "CBT",
    "Medial_Lemniscus": "ML",
    "Spinothalamic_Tract": "STT",
    "Superior_Cerebellar_Peduncle": "SCP",
    "Middle_Cerebellar_Peduncle": "MCP",
    "Inferior_Cerebellar_Peduncle": "ICP",
    "Medial_Longitudinal_Fasciculus": "MLF",
    "Optic_Radiation": "OR",
    "Fornix": "F",
    "Arcuate_Fasciculus": "AF",
    "Uncinate_Fasciculus": "UF",
    "Cingulum_Frontal_Parahippocampal": "C_FPH",
    "Cingulum_Frontal_Parietal": "C_FP",
    "Cingulum_Parahippocampal_Parietal": "C_PHP",
    "Cingulum_Parahippocampal": "C_PH",
    "Cingulum_Parolfactory": "C_PO",
    "Corticopontine_Tract_Frontal": "CPT_F",
    "Corticopontine_Tract_Parietal": "CPT_P",
    "Corticopontine_Tract_Occipital": "CPT_O",
}


def name_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def atlas_name(path: Path) -> str:
    name = path.name
    if name.lower().endswith(".gz"):
        name = name[:-3]
    return name[:-4]  # .trk or .tt handled separately by discovery


def tract_alias(name: str) -> str:
    side = name[-2:] if name[-2:].upper() in ("_L", "_R") else ""
    base = name[:-2] if side else name
    aliases = {name_key(k): v for k, v in BASE_ALIASES.items()}
    return aliases.get(name_key(base), base) + side.upper()


def clean_curve(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 2:
        raise ValueError("A streamline must contain at least two XYZ points")
    if not np.isfinite(points).all():
        raise ValueError("Non-finite streamline coordinates")
    keep = np.r_[True, np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-10]
    points = points[keep]
    if len(points) < 2:
        raise ValueError("Zero-length streamline")
    distance = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    return points, distance


def interpolate(points: np.ndarray, distance: np.ndarray, positions: np.ndarray) -> np.ndarray:
    return np.column_stack([np.interp(positions, distance, points[:, axis]) for axis in range(3)])


def resample_curve(points: np.ndarray, count: int = 100) -> np.ndarray:
    """Sample equal fractions of each streamline's own arc length."""
    if count < 2:
        raise ValueError("count must be at least 2")
    points, distance = clean_curve(points)
    return interpolate(points, distance, np.linspace(0, distance[-1], count))


def align_directions(curves: np.ndarray) -> np.ndarray:
    """Align ends to two endpoint means, seeded independently of input reversal.

    The principal endpoint-displacement axis prevents a 50/50 reversed bundle
    from starting with identical endpoint means. Iterative mean assignment uses
    the sum of squared endpoint distances, never mirrors coordinates.
    """
    aligned = np.asarray(curves, dtype=np.float64).copy()
    displacement = aligned[:, -1] - aligned[:, 0]
    _, _, axes = np.linalg.svd(displacement, full_matrices=False)
    axis = axes[0]
    if axis[np.argmax(np.abs(axis))] < 0:
        axis = -axis
    reverse = displacement @ axis < 0
    aligned[reverse] = aligned[reverse, ::-1]
    for _ in range(100):
        start, end = aligned[:, 0].mean(axis=0), aligned[:, -1].mean(axis=0)
        direct = np.sum((aligned[:, 0] - start) ** 2 + (aligned[:, -1] - end) ** 2, axis=1)
        flipped = np.sum((aligned[:, -1] - start) ** 2 + (aligned[:, 0] - end) ** 2, axis=1)
        reverse = flipped + 1e-9 < direct
        if not reverse.any():
            return aligned
        aligned[reverse] = aligned[reverse, ::-1]
    raise ValueError("Endpoint direction alignment did not converge")


def first_crossing_z(points: np.ndarray) -> float | None:
    """Z of first sampled point on the opposite side of x=0.

    Zeros alone are not a crossing. This is a geometric flag, not evidence of an
    anatomical decussation. The value is sampled, not an interpolated plane hit.
    """
    previous = 0.0
    for x, _, z in points:
        if abs(x) <= 1e-8:
            continue
        if previous and np.sign(x) != np.sign(previous):
            return float(z)
        previous = x
    return None


def summarize_bundle(streamlines: Iterable[np.ndarray], name: str, step_mm: float = 2.0) -> dict:
    if not np.isfinite(step_mm) or step_mm <= 0:
        raise ValueError("step-mm must be finite and positive")
    samples = []
    rejected = 0
    for line in streamlines:
        try:
            samples.append(resample_curve(line))
        except ValueError:
            rejected += 1
    if not samples:
        raise ValueError(f"{name}: no valid nonzero streamlines ({rejected} rejected)")
    aligned = align_directions(np.stack(samples))
    center = np.median(aligned, axis=0)
    radii = np.median(np.linalg.norm(aligned - center[None, :, :], axis=2), axis=0)

    # Give descending CST/CBT/CPT a cortical start; ML an inferior start.
    # All other bundles use z, then y, then x descending for reproducibility;
    # this convention does not infer neural conduction direction.
    alias = tract_alias(name)
    start_key = tuple(center[0, [2, 1, 0]])
    end_key = tuple(center[-1, [2, 1, 0]])
    ascending = alias.upper() in ("ML", "ML_L", "ML_R")
    reverse_center = start_key > end_key if ascending else start_key < end_key
    if reverse_center:
        center, radii = center[::-1], radii[::-1]
    keep = np.r_[True, np.linalg.norm(np.diff(center, axis=0), axis=1) > 1e-10]
    radii = radii[keep]
    center, distance = clean_curve(center)
    positions = np.r_[np.arange(0.0, distance[-1], step_mm), distance[-1]]
    points = interpolate(center, distance, positions)
    radii = np.interp(positions, distance, radii)
    result = {
        "id": re.sub(r"[^a-z0-9]+", "-", alias.lower()).strip("-"),
        "atlasName": name,
        "points": points.tolist(),
        "radiiMm": radii.tolist(),
        "lengthMm": float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum()),
        "streamlines": len(samples),
        "decussationZmm": first_crossing_z(points),
    }
    if rejected:
        result["rejectedStreamlines"] = rejected
        print(f"Warning: {name}: skipped {rejected} invalid streamlines", file=sys.stderr)
    return result


def read_trk(path: Path) -> Iterable[np.ndarray]:
    """nibabel applies TRK voxmm, voxel-centre and voxel_to_rasmm transforms."""
    opener = gzip.open if path.name.lower().endswith(".gz") else open
    with opener(path, "rb") as handle:
        trk = nib.streamlines.load(handle, lazy_load=True)
        if not isinstance(trk, nib.streamlines.TrkFile):
            raise ValueError(f"Not a TRK file: {path}")
        affine = trk.header["voxel_to_rasmm"]
        if not np.isfinite(affine).all() or abs(np.linalg.det(affine[:3, :3])) < 1e-12:
            raise ValueError(f"Invalid TRK spatial affine: {path}")
        world = trk.tractogram.to_world(lazy=True)
        for line in world.streamlines:
            yield np.asarray(line, dtype=np.float64)


def select_files(folder: Path, requested: list[str] | None) -> list[Path]:
    if not folder.is_dir():
        raise ValueError(f"Input directory does not exist: {folder}")
    files = sorted(p for p in folder.rglob("*") if p.is_file() and p.name.lower().endswith((".trk", ".trk.gz")))
    if not files:
        raise ValueError("No TRK files found. Extract the ZIP first. TT/.tt.gz is unsupported.")
    if requested:
        selected = set()
        for token in requested:
            matches = [p for p in files if name_key(token) in (name_key(atlas_name(p)), name_key(tract_alias(atlas_name(p))))]
            if len(matches) != 1:
                raise ValueError(f"Tract {token!r}: expected one file, found {len(matches)}")
            selected.add(matches[0])
        files = sorted(selected)
    ids = [name_key(tract_alias(atlas_name(p))) for p in files]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate tract IDs: remove duplicate TRK files or select unique names")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input_dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tracts", nargs="+", help="Exact atlas names or aliases, e.g. CST_L CST_R")
    parser.add_argument("--step-mm", type=float, default=2.0)
    args = parser.parse_args(argv)
    try:
        if not np.isfinite(args.step_mm) or args.step_mm <= 0:
            raise ValueError("step-mm must be finite and positive")
        files = select_files(args.input_dir, args.tracts)
        tracts = []
        for path in files:
            result = summarize_bundle(read_trk(path), atlas_name(path), args.step_mm)
            tracts.append(result)
            print(f"{result['id']}: {result['streamlines']} streamlines, {len(result['points'])} points, {result['lengthMm']:.2f} mm", file=sys.stderr)
        payload = json.dumps({"source": SOURCE, "tracts": tracts}, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # Never leave a partially written result after a conversion failure.
        temporary = args.out.with_name(args.out.name + ".tmp")
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(args.out)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
