import numpy as np
import pytest

from atlas_pipeline import meshing


def ball(shape, center, radius):
    grid = np.indices(shape).transpose(1, 2, 3, 0)
    return np.linalg.norm(grid - np.asarray(center), axis=-1) <= radius


def test_clean_mask_drops_speckle_keeps_large_pieces():
    mask = ball((60, 60, 60), (20, 30, 30), 10)
    mask |= ball((60, 60, 60), (45, 30, 30), 6)  # second real piece (~20% of the first)
    mask[2, 2, 2] = mask[57, 5, 5] = mask[5, 57, 30] = True  # speckle
    cleaned, stats = meshing.clean_mask(mask)
    assert stats.components_raw == 5
    assert stats.components_kept == 2
    assert not cleaned[2, 2, 2]
    assert cleaned[45, 30, 30]


def test_clean_mask_empty():
    cleaned, stats = meshing.clean_mask(np.zeros((5, 5, 5), bool))
    assert stats.voxels_raw == 0 and not cleaned.any()


def test_mask_to_mesh_is_closed_outward_and_in_world_coordinates():
    spacing, origin, r_vox = 0.2, np.array([-81.0, -132.0, -88.0]), 15
    mask = ball((50, 50, 50), (25, 25, 25), r_vox)
    mesh = meshing.mask_to_mesh(mask, spacing, origin)
    r_mm = r_vox * spacing
    assert mesh.is_watertight
    assert mesh.volume == pytest.approx(4 / 3 * np.pi * r_mm**3, rel=0.08)
    assert np.allclose(mesh.centroid, origin + 25 * spacing, atol=0.05)


def test_thin_structure_survives_smoothing():
    mask = np.zeros((20, 20, 80), bool)
    mask[9:11, 9:11, 10:70] = True  # 0.4 mm wide rod
    mesh = meshing.mask_to_mesh(mask, 0.2, (0, 0, 0))
    assert mesh.extents[2] > 11


def test_simplify_reaches_target_and_stays_closed():
    mesh = meshing.mask_to_mesh(ball((60, 60, 60), (30, 30, 30), 22), 0.2, (0, 0, 0))
    out = meshing.simplify(mesh, 1000)
    assert len(out.faces) <= 1000
    assert out.is_watertight and out.volume > 0


def test_mirror_keeps_outward_normals():
    mesh = meshing.ellipsoid((-5.0, 2.0, 3.0), (1.0, 2.0, 1.5))
    mirrored = meshing.mirror_x(mesh)
    assert mirrored.volume == pytest.approx(mesh.volume)
    assert mirrored.volume > 0
    assert mirrored.centroid[0] == pytest.approx(5.0, abs=1e-6)


def test_centerline_is_ordered_along_a_straight_rod():
    mask = np.zeros((10, 10, 100), bool)
    mask[4:6, 4:6, 5:95] = True
    line = meshing.centerline(mask, 0.2, (0, 0, 0), n_points=8)
    z = line[:, 2]
    assert len(line) == 8
    assert np.all(np.diff(z) > 0) or np.all(np.diff(z) < 0)
    assert abs(z.max() - z.min()) > 0.8 * 90 * 0.2


def test_centerline_follows_an_arch_instead_of_its_principal_axis():
    # half ring in the y-z plane, radius 30 voxels: a PCA/slab centerline would collapse both limbs together
    yy, zz = np.mgrid[0:80, 0:80]
    r = np.hypot(yy - 40, zz - 5)
    ring = (np.abs(r - 30) <= 1.5) & (zz >= 5)
    mask = np.zeros((8, 80, 80), bool)
    mask[3:5] = ring
    spacing = 0.2
    line = meshing.centerline(mask, spacing, (0, 0, 0), n_points=12)
    radii = np.hypot(line[:, 1] / spacing - 40, line[:, 2] / spacing - 5)
    assert np.all(np.abs(radii - 30) < 3)  # every point stays on the ring
    length = np.linalg.norm(np.diff(line, axis=0), axis=1).sum()
    assert length > 0.8 * np.pi * 30 * spacing


def test_centerline_chains_fragments_in_spatial_order():
    mask = np.zeros((10, 10, 200), bool)
    mask[4:6, 4:6, 5:60] = True
    mask[4:6, 4:6, 140:195] = True  # same tract, middle third unlabeled
    line = meshing.centerline(mask, 0.2, (0, 0, 0), n_points=10)
    z = line[:, 2]
    assert np.all(np.diff(z) > 0) or np.all(np.diff(z) < 0)
    assert z.min() < 60 * 0.2 and z.max() > 140 * 0.2


def test_small_blob_keeps_its_volume():
    mask = ball((30, 30, 30), (15, 15, 15), 5)  # ~1 mm radius at 0.2 mm, the size of a small brainstem nucleus
    mesh = meshing.mask_to_mesh(mask, 0.2, (0, 0, 0), smooth_sigma_mm=0.3)
    assert mesh.volume == pytest.approx(mask.sum() * 0.2**3, rel=0.12)
