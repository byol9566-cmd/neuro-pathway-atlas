"""Binary mask -> clean, smooth, decimated surface mesh in world (RAS mm) coordinates."""

from dataclasses import dataclass

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure


@dataclass
class MaskStats:
    voxels_raw: int
    voxels_kept: int
    components_raw: int
    components_kept: int

    @property
    def kept_fraction(self) -> float:
        return self.voxels_kept / self.voxels_raw if self.voxels_raw else 0.0


def clean_mask(mask: np.ndarray, closing_iters: int = 1, min_component_frac: float = 0.1):
    """Drop argmax speckle: bridge 1-voxel gaps, then keep components >= `min_component_frac` of the largest.

    The NextBrain argmax volume scatters tens to hundreds of tiny fragments per label around the main
    body; tracts legitimately come in a few large pieces, hence a relative rather than a top-1 rule.
    """
    raw_labels, n_raw = ndimage.label(mask)
    if n_raw == 0:
        return mask.copy(), MaskStats(0, 0, 0, 0)
    work = ndimage.binary_closing(mask, iterations=closing_iters) if closing_iters else mask
    labels, n = ndimage.label(work)
    sizes = np.bincount(labels.ravel())[1:]
    keep = np.flatnonzero(sizes >= min_component_frac * sizes.max()) + 1
    cleaned = np.isin(labels, keep)
    return cleaned, MaskStats(int(mask.sum()), int(cleaned.sum()), int(n_raw), int(len(keep)))


def mask_to_mesh(mask: np.ndarray, spacing_mm: float, origin_mm, smooth_sigma_mm: float = 0.3) -> trimesh.Trimesh:
    """Marching cubes on a Gaussian-blurred mask. `origin_mm` is the world position of voxel (0,0,0)."""
    pad = int(np.ceil(3 * smooth_sigma_mm / spacing_mm)) + 2
    field = np.pad(mask.astype(np.float32), pad)
    field = ndimage.gaussian_filter(field, smooth_sigma_mm / spacing_mm)
    # Blurring pulls the 0.5 iso-surface inwards on anything small or thin (a 5 mm3 nucleus loses ~40%).
    # Pick the level that encloses as many voxels as the mask had, i.e. preserve volume by construction.
    k = field.size - int(mask.sum())
    below, at = np.partition(field, [k - 1, k], axis=None)[[k - 1, k]]
    # a level that coincides with a voxel value makes marching cubes emit zero-area triangles (holes
    # once they are dropped), so sit strictly between two sample values
    level = float(below + at) / 2 if at > below else float(at) - 1e-4
    level = float(np.clip(level, 0.12, 0.5))
    verts, faces, _, _ = measure.marching_cubes(field, level=level, spacing=(spacing_mm,) * 3)
    verts += np.asarray(origin_mm, dtype=np.float64) - pad * spacing_mm
    mesh = trimesh.Trimesh(verts, faces, process=True)
    # marching_cubes orients faces by the gradient of `field`, i.e. inwards for a bright blob
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def simplify(mesh: trimesh.Trimesh, target_faces: int, taubin_iters: int = 8) -> trimesh.Trimesh:
    if len(mesh.faces) > target_faces:
        mesh = mesh.simplify_quadric_decimation(face_count=target_faces)
        # quadric collapse occasionally leaves degenerate or duplicated triangles behind
        mesh.update_faces(mesh.nondegenerate_faces() & mesh.unique_faces())
        mesh.remove_unreferenced_vertices()
        trimesh.repair.fill_holes(mesh)  # dropping those can open a triangle-sized gap
    if taubin_iters:
        trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=0.53, iterations=taubin_iters)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def target_face_count(mesh: trimesh.Trimesh, faces_per_mm2: float, lo: int = 400, hi: int = 12000) -> int:
    return int(np.clip(mesh.area * faces_per_mm2, lo, hi))


def mirror_x(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Reflect across the mid-sagittal plane (x = 0 in MNI-aligned RAS), keeping outward normals."""
    verts = mesh.vertices.copy()
    verts[:, 0] *= -1
    return trimesh.Trimesh(verts, mesh.faces[:, ::-1].copy(), process=False)


def ellipsoid(center_mm, radii_mm, subdivisions: int = 3) -> trimesh.Trimesh:
    """Stand-in shape for nuclei whose label is too small in the argmax volume to mesh."""
    mesh = trimesh.creation.icosphere(subdivisions=subdivisions)
    mesh.vertices = mesh.vertices * np.asarray(radii_mm, dtype=np.float64) + np.asarray(center_mm, dtype=np.float64)
    return mesh


def _component_centerline(m: np.ndarray, n_points: int) -> np.ndarray:
    """Centerline of one connected mask, in voxel index coordinates of `m`."""
    from skimage.graph import MCP_Geometric

    costs = np.where(m, 1.0, -1.0)  # negative = impassable
    inside = np.argwhere(m)

    def geodesic(seed):
        dist, _ = MCP_Geometric(costs, fully_connected=True).find_costs([tuple(seed)])
        return np.where(m & np.isfinite(dist), dist, -1.0)

    tip = np.unravel_index(np.argmax(geodesic(inside[0])), m.shape)
    d = geodesic(tip)[m]
    edges = np.linspace(0, d.max() + 1e-6, n_points + 1)
    which = np.digitize(d, edges) - 1
    return np.asarray([inside[which == i].mean(axis=0) for i in range(n_points) if np.any(which == i)])


def _chain(lines: list[np.ndarray]) -> np.ndarray:
    """Join polylines end to end, greedily picking the nearest remaining piece (flipped if needed)."""
    center = np.concatenate(lines).mean(axis=0)
    ends = [(i, flip) for i in range(len(lines)) for flip in (False, True)]
    first, flip = max(ends, key=lambda e: np.linalg.norm(lines[e[0]][-1 if e[1] else 0] - center))
    chain = lines[first][::-1] if flip else lines[first]
    rest = [ln for i, ln in enumerate(lines) if i != first]
    while rest:
        tail = chain[-1]
        i, flip = min(
            ((i, f) for i in range(len(rest)) for f in (False, True)),
            key=lambda e: np.linalg.norm(rest[e[0]][-1 if e[1] else 0] - tail),
        )
        nxt = rest.pop(i)
        chain = np.concatenate([chain, nxt[::-1] if flip else nxt])
    return chain


def centerline(mask: np.ndarray, spacing_mm: float, origin_mm, n_points: int = 14, min_component_frac: float = 0.1) -> np.ndarray:
    """Ordered points along an elongated, possibly curved and possibly fragmented mask (world mm).

    Voxels are binned by geodesic distance from one tip, so arched tracts come out as one curve instead
    of folding onto their principal axis. Tracts the atlas labels in several pieces (NextBrain's fornix
    lacks its body) get one centerline per piece, chained end to end.
    """
    # geodesic search cost grows with voxel count: thin tracts at 0.4 mm, bulky structures at 1 mm
    target_mm = 0.4 if mask.sum() * spacing_mm**3 < 1500 else 1.0
    step = max(1, int(round(target_mm / spacing_mm)))
    if step > 1:  # any-pooling keeps thin tracts connected
        pad = [(0, -n % step) for n in mask.shape]
        m = np.pad(mask, pad)
        m = m.reshape(m.shape[0] // step, step, m.shape[1] // step, step, m.shape[2] // step, step).any(axis=(1, 3, 5))
    else:
        m = mask
    labels, n = ndimage.label(m, structure=np.ones((3, 3, 3)))
    if n == 0:
        raise ValueError("empty mask")
    sizes = np.bincount(labels.ravel())[1:]
    keep = np.flatnonzero(sizes >= min_component_frac * sizes.max()) + 1
    lines = []
    for lab in keep:
        share = sizes[lab - 1] / sizes[keep - 1].sum()
        lines.append(_component_centerline(labels == lab, max(3, int(round(n_points * share)))))
    line = _chain(lines)
    return (line * step + (step - 1) / 2) * spacing_mm + np.asarray(origin_mm, dtype=np.float64)
