"""Build viewer/public/data/{atlas.glb, manifest.json} from content/structures.json.

    python -m atlas_pipeline.build [--only ID ...] [--no-compress]

NextBrain is a left-hemisphere volume in MNI-aligned RAS mm; right-side meshes are mirrored across x = 0.
Every built mesh is also kept in data/derived/meshes (<meshId>.ply + its manifest record): a full build
rewrites that cache, `--only` rebuilds the given structures into it and assembles the outputs from the
whole cache, so they stay complete.
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

from . import CONTENT_DIR, DATA_DIR, OUT_DIR, REPO_ROOT, bp3d, meshing, models, sections

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
# nuclei whose argmax label is smaller than this are rebuilt from the probability maps (p >= threshold)
PROB_BELOW_MM3 = 40.0
PROB_THRESHOLD = 0.2
PROB_DIR = DATA_DIR / "nextbrain" / "prob"

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
    {
        "atlas": "vhp",
        "title": "Visible Human Project (male cryosections), U.S. National Library of Medicine",
        "citation": "Segmented here with Segment Anything and registered to MNI152 2009c (pipeline/vhp_*.py).",
        "license": "Public: NLM states a license is no longer required",
        "url": "https://www.nlm.nih.gov/research/visible/visible_human.html",
    },
    {
        "atlas": "model",
        "title": "기하 모형 (이 프로젝트에서 교과서 치수로 작성)",
        "citation": "Parametric shapes at literature MNI coordinates: cochlea, semicircular canals, ganglia, carotid sinus, spinal cord columns (pipeline/atlas_pipeline/models.py).",
        "license": "프로젝트 자체 제작",
        "url": "",
    },
    {
        "atlas": "bp3d",
        "title": "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International",
        "citation": "Mitsuhashi N, et al. BodyParts3D: 3D structure database for anatomical concepts. Nucleic Acids Res (2009). Polygon-reduced (99 %) meshes, fitted to MNI on brain and eye landmarks (pipeline/atlas_pipeline/bp3d.py).",
        "license": "CC BY 4.0",
        "url": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html",
    },
    {
        "atlas": "hcp1065",
        "title": "HCP1065 population-averaged tractography atlas (Yeh, DSI Studio)",
        "citation": "Yeh FC. Population-based tract-to-region connectome of the human brain and its hierarchical topology. Nat Commun (2022). Data: Human Connectome Project (WU-Minn consortium).",
        "license": "CC BY-SA 4.0 — the tract paths derived here carry the same licence",
        "url": "https://brain.labsolver.org/hcp_trk_atlas.html",
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

    def prob_mask(self, labels: list[int], threshold: float):
        """Boolean mask from the atlas's per-label probability maps (data/raw/nextbrain/prob/<label>.npz,
        scipy COO over the flattened argmax grid; fetch.fetch_nextbrain_probabilities). The argmax volume
        drops a small nucleus wherever a bigger neighbour is more probable, so the abducens nucleus keeps
        5 mm3 of its ~15; summing the labels' probabilities and thresholding keeps the whole nucleus.
        -> (mask, spacing, origin) like label_mask, or None if any map is missing."""
        import scipy.sparse

        total = None
        for lab in labels:
            p = PROB_DIR / f"{lab}.npz"
            if not p.exists():
                return None
            m = scipy.sparse.load_npz(p).tocoo()
            idx = np.unravel_index(m.row, self.data.shape)
            if total is None:
                total = {}
            for i, j, k, v in zip(*idx, m.data):
                total[(i, j, k)] = total.get((i, j, k), 0.0) + float(v)
        # the maps of the smallest nuclei never get confident (oculomotor peaks at 0.44), so the cut
        # follows the peak: 30% of it, between 0.08 and `threshold`
        pmax = max(total.values())
        vals = np.array(list(total.values()))
        voxel = self.spacing**3
        cut = None
        for cand in (min(threshold, max(0.08, 0.3 * pmax)), 0.15, 0.1, 0.08, 0.05, 0.03):
            if (vals >= cand).sum() * voxel >= PLACEHOLDER_BELOW_MM3:  # loosen until the nucleus has a body
                cut = cand
                break
        if cut is None:
            return None
        pts = np.array([key for key, v in total.items() if v >= cut])
        lo = pts.min(axis=0); hi = pts.max(axis=0) + 1
        mask = np.zeros(hi - lo, dtype=bool)
        mask[tuple((pts - lo).T)] = True
        return mask, self.spacing, self.origin + lo * self.spacing, cut

    def brainstem_axis(self) -> dict:
        """z (mm, RAS) -> (x, y, equivalent radius) of the brainstem cross-section, from the shell mask
        (stride SHELL_STRIDE); feeds the textbook tract models in models.py"""
        m = self.shell_masks()["brainstem"]
        sp = self.spacing * SHELL_STRIDE
        out = {}
        for k in range(m.shape[2]):
            sl = m[:, :, k]
            n = int(sl.sum())
            if n < 40:
                continue
            ii, jj = np.nonzero(sl)
            # the atlas is one hemisphere (the right is mirrored at build time): the brainstem sits on the
            # midline and the full cross-section is twice the half mask
            y = self.origin[1] + jj.mean() * sp
            z = self.origin[2] + k * sp
            out[round(float(z))] = (0.0, float(y), float(np.sqrt(2 * n / np.pi) * sp))
        return out

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


def build_vhp_side(structure, side, file):
    sid = structure["id"]
    img = nib.as_closest_canonical(nib.load(REPO_ROOT / file))
    affine = img.affine
    mask = np.asanyarray(img.dataobj) > 0
    if not mask.any():
        raise ValueError(f"{sid}: empty mask {file}")
    box = ndimage.find_objects(mask.astype(np.uint8))[0]
    start = np.array([b.start for b in box])
    spacing = float(affine[0, 0])
    factor = 2  # up-sample so the 1 mm voxel steps smooth out, like the AAN masks
    fine = np.kron(mask[box], np.ones((factor,) * 3, dtype=bool))
    origin = affine[:3, 3] + start * spacing + (0.5 / factor - 0.5) * spacing
    cleaned, stats, mesh = build_from_mask(fine, spacing / factor, origin, sigma_mm=1.0, faces_per_mm2=2.0, max_faces=20000, closing_iters=1)
    vol = cleaned.sum() * (spacing / factor) ** 3
    rec = mesh_record(f"{sid}.{side}", structure, side, mesh, volume_mm3=vol, approx=False, stats=stats)
    derived = VHP_DERIVED.get(sid) or {}
    if derived.get("organ"):
        rec["derived"] = derived["organ"]  # cut from this segmented organ by vhp_derive.py, not segmented itself
    if derived.get("note"):
        rec["note"] = derived["note"]  # e.g. the cord re-posed to a vertical axis
    return [(f"{sid}.{side}", mesh, rec)]


def _load_vhp_derived():
    p = REPO_ROOT / "data" / "derived" / "vhp" / "derived.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


VHP_DERIVED = _load_vhp_derived()


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

    if src["atlas"] == "vhp":
        # binary masks in the MNI152 grid, segmented from the Visible Human cryosections (data/derived/vhp);
        # one file per side
        for side, file in (src.get("sides") or {src.get("side", "M"): src["file"]}).items():
            out += build_vhp_side(structure, side, file)
        return out

    if src["atlas"] == "hcp1065":
        # fibre bundle from the HCP1065 tractography atlas, prepared by pipeline/tracts/prepare_tracts.py:
        # a tube along the bundle's centerline; the centerline itself is what the pathway animation follows
        for side, tid in src["tracts"].items():
            t = HCP_TRACTS[tid]
            pts = np.asarray(t["points"], dtype=float)
            mesh = meshing.tube(pts, t["radiiMm"])
            rec = mesh_record(f"{sid}.{side}", structure, side, mesh, volume_mm3=float(mesh.volume), approx=False, line=pts)
            rec["note"] = t["note"]
            out.append((f"{sid}.{side}", mesh, rec))
        return out

    if src["atlas"] == "bp3d":
        # BodyParts3D whole-body parts (real left and right, no mirroring), unioned per side
        for side, names in src["parts"].items():
            mesh = bp3d.mesh_for(names, max_faces=int(src.get("maxFaces", 6000)))
            rec = mesh_record(f"{sid}.{side}", structure, side, mesh, volume_mm3=float(abs(mesh.volume)), approx=False)
            rec["note"] = structure.get("note", "")
            out.append((f"{sid}.{side}", mesh, rec))
        return out

    if src["atlas"] == "model":
        # parametric textbook shape at literature coordinates (atlas_pipeline/models.py); right side given
        mesh, line = models.build(src)
        note = src.get("modelNote") or "기하 모형: 모양은 교과서 치수의 매개변수 모형, 위치·크기는 문헌 좌표. 분할 데이터가 아니다."
        vol = float(abs(mesh.volume))
        if src.get("bilateral", True):
            rec_r = mesh_record(f"{sid}.R", structure, "R", mesh, volume_mm3=vol, approx=True, line=line); rec_r["note"] = note
            out.append((f"{sid}.R", mesh, rec_r))
            if models.builds_left(src):  # the cord-level shapes and nerves to midline organs draw their own left
                mesh_l, line_l = models.build(src, "L")
            else:
                mesh_l = meshing.mirror_x(mesh)
                line_l = None if line is None else np.asarray(line) * np.array([-1.0, 1.0, 1.0])
            rec_l = mesh_record(f"{sid}.L", structure, "L", mesh_l, volume_mm3=vol, approx=True, line=line_l); rec_l["note"] = note
            out.append((f"{sid}.L", mesh_l, rec_l))
        else:
            rec = mesh_record(f"{sid}.M", structure, "M", mesh, volume_mm3=vol, approx=True, line=line); rec["note"] = note
            out.append((f"{sid}.M", mesh, rec))
        return out

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
    cleaned, stats = meshing.clean_mask(mask)
    vol = cleaned.sum() * spacing**3
    placeholder = src.get("placeholder")
    prob_note = None
    only_prob = False  # nothing of the label survives in the argmax: the probability map only places it
    if vol < PROB_BELOW_MM3 and not src.get("stride"):
        # small nucleus: the probability maps give its real extent where the argmax only kept a core
        got = nb.prob_mask(labels, PROB_THRESHOLD)
        if got is not None:
            pmask, pspacing, porigin, cut = got
            pcleaned, pstats = meshing.clean_mask(pmask)
            pvol = pcleaned.sum() * pspacing**3
            if vol == 0 and pcleaned.any():
                # (MNTB: 2 argmax voxels, gone after cleaning; its map peaks at 0.37) a low cut gives a
                # position, not a shape: an ellipsoid at the map's centroid
                only_prob = True
                prob_note = (f"NextBrain 확률 지도에서 p ≥ {cut:.2f}인 복셀({pvol:.1f} mm³)의 중심에 둔 타원체. "
                             "argmax 라벨에는 남은 복셀이 없다.")
                mask, spacing, origin, cleaned, stats, vol = pcleaned, pspacing, porigin, pcleaned, pstats, pvol
            elif pvol >= PLACEHOLDER_BELOW_MM3 and pvol > vol:
                prob_note = (f"NextBrain 확률 지도에서 p ≥ {cut:.2f}인 복셀로 만든 형태. " +
                             (f"argmax 라벨은 {vol:.1f} mm³만 남아 모양이 없었다." if vol < PLACEHOLDER_BELOW_MM3
                              else f"argmax 라벨({vol:.0f} mm³)은 이웃 구조에 밀려 일부만 남아 있었다."))
                mask, spacing, origin, cleaned, stats, vol = pmask, pspacing, porigin, pcleaned, pstats, pvol
    if vol == 0:
        raise ValueError(f"{sid}: labels {labels} have no voxels in the atlas or its probability maps")
    if only_prob or (vol < PLACEHOLDER_BELOW_MM3 and (placeholder or mask.any())):
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
        if prob_note:
            for _, _, rec in out:
                rec["note"] = prob_note
        return out

    sigma = 0.5 if src.get("stride", 1) > 1 else (0.2 if vol < 30 else 0.3)
    mesh = meshing.mask_to_mesh(cleaned, spacing, origin, smooth_sigma_mm=sigma)
    mesh = meshing.simplify(mesh, meshing.target_face_count(mesh, 6.0))
    wants_line = structure.get("tract") or structure.get("centerline")
    line = meshing.centerline(cleaned, spacing, origin) if wants_line else None
    add_pair(mesh, volume_mm3=vol, approx=False, stats=stats, line=line)
    if prob_note:
        for _, _, rec in out:
            rec["note"] = prob_note
    # a tractography centerline can replace the label's own (the NextBrain label is often only the
    # brainstem segment, the HCP1065 bundle runs the whole course)
    for side, tid in (src.get("centerlineFrom") or {}).items():
        for i, (mesh_id, m, rec) in enumerate(out):
            if mesh_id == f"{sid}.{side}":
                rec["centerline"] = np.round(np.asarray(HCP_TRACTS[tid]["points"], dtype=float), 2).tolist()
                rec["centerlineSource"] = "hcp1065"
    return out


LIMB_SEGMENTS = {"bone-humerus", "bone-forearm", "bone-hand", "bone-femur", "bone-leg", "bone-foot"}
TORSO_BONES = {"bone-skull", "bone-vertebral-column", "bone-rib-cage", "bone-pelvis", "bone-shoulder"}
# muscles that ride with a bone segment when its joint moves (their origin end detaches: schematic)
SEGMENT_MUSCLES = {
    "bone-humerus": ["mu-biceps-brachii", "mu-brachialis", "mu-triceps-brachii", "mu-deltoid"],
    "bone-femur": ["mu-quadriceps", "mu-hamstrings"],
    "bone-leg": ["mu-tibialis-anterior", "mu-triceps-surae"],
}
SKIN_PIECE_NAMES = {"bone-humerus": "위팔", "bone-forearm": "아래팔", "bone-hand": "손", "bone-femur": "넙다리", "bone-leg": "종아리", "bone-foot": "발"}
# joint -> (the proximal bone whose distal end is the pivot, or None for the segment's own top end),
#          the segment the joint moves, flexion sign about +x (RAS), Korean name
JOINTS = [
    ("shoulder", None, "bone-humerus", 1.0, "어깨"),
    ("elbow", "bone-humerus", "bone-forearm", 1.0, "팔꿈치"),
    ("wrist", "bone-forearm", "bone-hand", 1.0, "손목"),
    ("hip", None, "bone-femur", 1.0, "엉덩관절"),
    ("knee", "bone-femur", "bone-leg", -1.0, "무릎"),
    ("ankle", "bone-leg", "bone-foot", -1.0, "발목"),
]


def limb_joints(segment_meshes: dict) -> list:
    """Pivots for the schematic limb movement: the end of a bone is the mean of its vertices within 25 mm
    of its top or bottom. Each joint moves one segment; the viewer chains them (shoulder > elbow > wrist)."""
    out = []
    for name, proximal, segment, sign, ko in JOINTS:
        for side in ("R", "L"):
            seg = segment_meshes.get(f"{segment}.{side}")
            if seg is None:
                continue
            ref = segment_meshes.get(f"{proximal}.{side}") if proximal else seg
            if ref is None:
                continue
            v = ref.vertices
            if proximal:
                end = v[v[:, 2] < v[:, 2].min() + 25]  # distal end of the proximal bone
            else:
                end = v[v[:, 2] > v[:, 2].max() - 25]  # top of the segment itself
            pivot = end.mean(axis=0)
            moved = [f"{segment}.{side}", f"{segment}-skin.{side}"] + [f"{m}.{side}" for m in SEGMENT_MUSCLES.get(segment, [])]
            out.append({"id": f"{name}.{side}", "joint": name, "side": side, "name": {"ko": ko}, "pivot": np.round(pivot, 1).tolist(),
                        "axis": [1.0, 0.0, 0.0], "flexSign": sign, "segment": f"{segment}.{side}", "segments": moved,
                        "parent": next((f"{j[0]}.{side}" for j in JOINTS if j[2] == proximal), None) if proximal else None})
    return out


def split_body_skin(meshes, structure_records, segment_meshes, torso_meshes, skin_structure):
    """Replace the single skin mesh by a torso piece plus one piece per limb bone segment (as structures
    '<bone>-skin'), so the limbs' skin follows the joints. meshes: mesh id -> (trimesh, record);
    structure_records: structure id -> record."""
    skin = meshes.get("body-skin.M", (None,))[0]
    if skin is None or not segment_meshes or not torso_meshes:
        return
    pieces = bp3d.split_skin(skin, segment_meshes, torso_meshes)
    torso = pieces.pop("torso")
    r = mesh_record("body-skin.M", skin_structure, "M", torso, volume_mm3=float(abs(torso.volume)), approx=False); r["note"] = skin_structure.get("note", "")
    meshes["body-skin.M"] = (torso, r)
    by_struct = {}
    for seg_id, piece in pieces.items():
        bone, side = seg_id.rsplit(".", 1)
        sid = f"{bone}-skin"
        fake = {"id": sid, "name": {"ko": f"피부 — {SKIN_PIECE_NAMES[bone]}", "en": f"Skin, {bone.replace('bone-', '')}"}, "group": "body-shell"}
        r = mesh_record(f"{sid}.{side}", fake, side, piece, volume_mm3=float(abs(piece.volume)), approx=False); r["note"] = skin_structure.get("note", "")
        meshes[f"{sid}.{side}"] = (piece, r)
        by_struct.setdefault(sid, (fake, []))[1].append(f"{sid}.{side}")
    for sid, (fake, ids) in by_struct.items():
        structure_records[sid] = {"id": sid, "group": "body-shell", "name": fake["name"], "tract": False, "approx": False, "atlas": "bp3d", "labels": [], "meshIds": sorted(ids)}


SKIN_PIECES = {f"{b}-skin" for b in LIMB_SEGMENTS}  # structures split_body_skin makes from body-skin
MESH_CACHE = REPO_ROOT / "data" / "derived" / "meshes"  # <meshId>.ply + .json, structures/<id>.json


def load_cache():
    """-> (meshes: id -> (trimesh, record), structure records: id -> record) from MESH_CACHE"""
    meshes, srecs = {}, {}
    for j in sorted(MESH_CACHE.glob("*.json")):
        ply = j.with_suffix(".ply")
        if ply.exists():
            meshes[j.stem] = (trimesh.load(ply, process=False), json.loads(j.read_text(encoding="utf-8")))
    for j in sorted((MESH_CACHE / "structures").glob("*.json")):
        srecs[j.stem] = json.loads(j.read_text(encoding="utf-8"))
    return meshes, srecs


def write_cache(meshes: dict, srecs: dict, drop_meshes=(), drop_structures=()):
    (MESH_CACHE / "structures").mkdir(parents=True, exist_ok=True)
    for mid in drop_meshes:
        for ext in (".ply", ".json"):
            (MESH_CACHE / f"{mid}{ext}").unlink(missing_ok=True)
    for sid in drop_structures:
        (MESH_CACHE / "structures" / f"{sid}.json").unlink(missing_ok=True)
    for mid, (mesh, rec) in meshes.items():
        (MESH_CACHE / f"{mid}.ply").write_bytes(mesh.export(file_type="ply"))
        (MESH_CACHE / f"{mid}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    for sid, rec in srecs.items():
        (MESH_CACHE / "structures" / f"{sid}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")


def _load_hcp_tracts():
    p = REPO_ROOT / "data" / "derived" / "tracts" / "tracts-prepared.json"
    return json.loads(p.read_text(encoding="utf-8"))["tracts"] if p.exists() else {}


HCP_TRACTS = _load_hcp_tracts()
models.CORD_FILE = REPO_ROOT / "data" / "derived" / "vhp" / "sp-cord.M.mni.nii.gz"


def compress(raw_glb, out_glb) -> bool:
    cli = REPO_ROOT / "viewer" / "node_modules" / ".bin" / "gltf-transform"
    if not cli.exists():
        return False
    subprocess.run([str(cli), "meshopt", str(raw_glb), str(out_glb), "--level", "medium"], check=True, capture_output=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="rebuild only these structure ids into the mesh cache (data/derived/meshes), "
                    "then write atlas.glb + manifest.json from the whole cache (needs one full build first); "
                    "skips the 2D section export")
    ap.add_argument("--no-compress", action="store_true")
    ap.add_argument("--no-sections", action="store_true", help="skip exporting the 2D section slices")
    args = ap.parse_args(argv)

    config = json.loads((CONTENT_DIR / "structures.json").read_text())
    content_ids = {s["id"] for s in config["structures"]}
    if args.only:
        if not any(MESH_CACHE.glob("*.json")):
            sys.exit(f"--only needs the mesh cache, and {MESH_CACHE} is empty: run a full build first "
                     "(PYTHONPATH=pipeline pipeline/.venv/bin/python -m atlas_pipeline.build)")
        unknown = [i for i in args.only if i not in content_ids]
        if unknown:
            print(f"not in content/structures.json: {', '.join(unknown)}", file=sys.stderr)
    structures = [s for s in config["structures"] if not args.only or s["id"] in args.only]
    rebuilt = {s["id"] for s in structures}

    t0 = time.time()
    nb = NextBrain()
    models.BRAINSTEM_AXIS = nb.brainstem_axis()
    print(f"nextbrain loaded: {nb.data.shape} @ {nb.spacing} mm, {len(nb.present)} labels ({time.time() - t0:.1f}s)")

    new_meshes, new_srecs, skipped = {}, {}, []
    for s in structures:
        t = time.time()
        try:
            built = build_structure(s, nb)
        except ValueError as err:
            print(f"  !! skipped {s['id']}: {err}")
            skipped.append(s["id"])
            continue
        for mesh_id, mesh, rec in built:
            new_meshes[mesh_id] = (mesh, rec)
        first = built[0][2]
        new_srecs[s["id"]] = {
            "id": s["id"],
            "group": s["group"],
            "name": s["name"],
            "tract": bool(s.get("tract")),
            "approx": first["approx"],
            # atlas label ids behind this structure: lets the 2D section panel map a pixel to it
            "labels": nb.expand_labels(s["source"]) if s["source"]["atlas"] == "nextbrain" and "shell" not in s["source"] else [],
            "meshIds": [m[0] for m in built],
            **({"color": s["color"]} if s.get("color") else {}),
        }
        flag = " [placeholder]" if first["approx"] else ""
        kept = first.get("cleanup", {}).get("keptFraction")
        print(f"  {s['id']:24s} {first['volumeMm3']:9.1f} mm3  {first['faces']:6d} faces  kept={kept}  {time.time() - t:4.1f}s{flag}")

    if skipped:
        print(f"skipped {len(skipped)} structures with no usable voxels: {', '.join(skipped)}")

    # the rebuilt structures replace their cached meshes (the skin pieces go with body-skin); everything
    # else comes from the cache
    replaced = lambda sid: sid in rebuilt or (sid in SKIN_PIECES and "body-skin" in rebuilt)
    meshes, srecs = load_cache() if args.only else ({}, {})
    stale_meshes = [mid for mid, (_, rec) in meshes.items() if replaced(rec["structureId"])]
    stale_srecs = [sid for sid in srecs if replaced(sid)]
    for mid in stale_meshes:
        del meshes[mid]
    for sid in stale_srecs:
        del srecs[sid]
    meshes.update(new_meshes)
    srecs.update(new_srecs)
    by_structure = lambda ids: [m for m, rec in meshes.values() if rec["structureId"] in ids]
    segment_meshes = {mid: m for mid, (m, rec) in meshes.items() if rec["structureId"] in LIMB_SEGMENTS}  # for the joint pivots
    skin_structure = next((s for s in structures if s["id"] == "body-skin"), None)
    if skin_structure:
        split_body_skin(meshes, srecs, segment_meshes, by_structure(TORSO_BONES), skin_structure)
    if args.only:
        write_cache({mid: v for mid, v in meshes.items() if replaced(v[1]["structureId"])},
                    {sid: v for sid, v in srecs.items() if replaced(sid)}, drop_meshes=stale_meshes, drop_structures=stale_srecs)
    else:
        shutil.rmtree(MESH_CACHE, ignore_errors=True)
        write_cache(meshes, srecs)

    # structures since removed from content/structures.json do not linger in the cache's outputs
    keep = lambda sid: sid in content_ids or (sid in SKIN_PIECES and "body-skin" in content_ids)
    order = [s["id"] for s in config["structures"]] + sorted(SKIN_PIECES)
    structure_records = [srecs[sid] for sid in order if sid in srecs and keep(sid)]
    gone = sorted(sid for sid in srecs if not keep(sid))
    if gone:
        print(f"cache entries no longer in content, left out: {', '.join(gone)}")
    if args.only:
        missing = sorted(content_ids - set(srecs) - set(skipped))
        if missing:
            print(f"not in the cache (run a full build to add them): {', '.join(missing)}", file=sys.stderr)
    scene = trimesh.Scene()
    mesh_records = []
    for srec in structure_records:
        for mid in srec["meshIds"]:
            mesh, rec = meshes[mid]
            mesh.vertex_normals  # noqa: B018 -- compute so the GLB carries smooth normals
            scene.add_geometry(mesh, node_name=mid, geom_name=mid)
            mesh_records.append(rec)

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
        "joints": limb_joints(segment_meshes),
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
