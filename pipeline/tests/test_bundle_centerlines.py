"""Geometric accuracy, direction invariance, real TRK coordinates and CLI contract."""

import gzip
import json
import struct

import nibabel as nib
import numpy as np
import pytest

from pipeline.tracts.bundle_centerlines import (
    first_crossing_z,
    main,
    read_trk,
    resample_curve,
    select_files,
    summarize_bundle,
)


def synthetic(kind):
    t = np.linspace(0, 1, 250)
    x = 15 * np.sin(2 * np.pi * t) if kind == "s" else np.full_like(t, 12)
    return np.column_stack((x, -10 + 8 * t, 70 - 120 * t))


@pytest.mark.parametrize("kind", ["straight", "s"])
def test_noisy_100_streamline_center_is_within_one_mm(kind):
    rng = np.random.default_rng(20261004)
    truth = synthetic(kind)
    lines = [truth + rng.normal(0, 0.35, truth.shape) for _ in range(100)]
    result = summarize_bundle(lines, "CST_L")
    # Compare full curves at equal arc fractions, not only their endpoints.
    actual = resample_curve(result["points"], 500)
    expected = resample_curve(truth, 500)
    error = np.linalg.norm(actual - expected, axis=1)
    assert error.mean() < 1.0
    assert error.max() < 1.0
    assert result["streamlines"] == 100
    assert np.isfinite(result["radiiMm"]).all()
    assert len(result["radiiMm"]) == len(result["points"])
    assert max(np.linalg.norm(np.diff(result["points"], axis=0), axis=1)) <= 2.000001


def test_half_reversed_streamlines_align_and_are_order_invariant():
    rng = np.random.default_rng(12)
    truth = synthetic("s")
    lines = [truth + rng.normal(0, 0.2, truth.shape) for _ in range(100)]
    baseline = summarize_bundle(lines, "CST_L")
    mixed = [line[::-1] if i % 2 else line for i, line in enumerate(lines)]
    rng.shuffle(mixed)
    result = summarize_bundle(mixed, "CST_L")
    np.testing.assert_allclose(result["points"], baseline["points"], atol=1e-8)
    np.testing.assert_allclose(result["radiiMm"], baseline["radiiMm"], atol=1e-8)


def test_known_radius_length_step_and_short_last_segment():
    # Eight symmetrically spaced streamlines lie exactly 3 mm from the axis.
    z = np.linspace(10, -1, 30)
    lines = [np.column_stack((np.full_like(z, 3 * np.cos(a)), np.full_like(z, 3 * np.sin(a)), z)) for a in np.arange(8) * np.pi / 4]
    result = summarize_bundle(lines, "CST_L", 2)
    np.testing.assert_allclose(np.asarray(result["points"])[:, :2], 0, atol=1e-12)
    np.testing.assert_allclose(result["radiiMm"], 3)
    np.testing.assert_allclose(np.linalg.norm(np.diff(result["points"], axis=0), axis=1), [2, 2, 2, 2, 2, 1])
    assert result["lengthMm"] == pytest.approx(11)


def raw_trk(path, affine):
    """Write voxel-mm payload manually; expected RAS never uses nibabel's reader.

    TrackVis coordinates are measured from voxel corners. Sample voxel indices
    below refer to centres, hence the +0.5 before multiplying by voxel sizes.
    """
    voxel = np.array([[2, 3, 4], [8, 9, 12], [15, 13, 20]], dtype=float)
    sizes = np.linalg.norm(affine[:3, :3], axis=0)
    header = nib.streamlines.TrkFile.create_empty_header()
    header["voxel_to_rasmm"] = affine
    header["voxel_sizes"] = sizes
    header["dimensions"] = [50, 50, 50]
    header["voxel_order"] = "".join(nib.aff2axcodes(affine)).encode()
    nib.streamlines.TrkFile(nib.streamlines.Tractogram([], affine_to_rasmm=np.eye(4)), header).save(str(path))
    with path.open("r+b") as handle:
        handle.seek(988)  # TrackVis header: n_count
        handle.write(struct.pack("<i", 1))
        handle.seek(1000)
        handle.write(struct.pack("<i", len(voxel)))
        handle.write(np.asarray((voxel + 0.5) * sizes, dtype="<f4").tobytes())
    return voxel @ affine[:3, :3].T + affine[:3, 3]


@pytest.mark.parametrize("affine", [
    np.array([[2, 0, 0, -90], [0, 3, 0, -120], [0, 0, 4, -70], [0, 0, 0, 1.0]]),
    np.array([[-2, 0, 0, 90], [0, -3, 0, 100], [0, 0, 4, -70], [0, 0, 0, 1.0]]),
    np.array([[0, -3, 0, 90], [2, 0, 0, -100], [0, 0, 4, -70], [0, 0, 0, 1.0]]),
])
def test_trk_header_affine_and_corner_offset_produce_ras_mm(tmp_path, affine):
    path = tmp_path / "CST_L.trk"
    expected = raw_trk(path, affine)
    actual = list(read_trk(path))
    assert len(actual) == 1
    np.testing.assert_allclose(actual[0], expected, atol=1e-5)
    compressed = tmp_path / "CST_R.trk.gz"
    compressed.write_bytes(gzip.compress(path.read_bytes()))
    np.testing.assert_allclose(list(read_trk(compressed))[0], expected, atol=1e-5)


def test_crossing_preserved_without_mirroring_and_ml_direction():
    z = np.linspace(60, -60, 101)
    line = np.column_stack((z / 10, np.full_like(z, -20), z))
    cst = summarize_bundle([line, line[::-1]], "CST_L", 2)
    points = np.asarray(cst["points"])
    assert points[0, 0] > 0 and points[-1, 0] < 0
    assert cst["decussationZmm"] == first_crossing_z(points)
    assert -2.1 < cst["decussationZmm"] < 0
    ml = summarize_bundle([line], "ML_L")
    assert ml["points"][0][2] < ml["points"][-1][2]


@pytest.mark.parametrize("xs, expected", [
    ([1, 0, -1], 2), ([1, 0, 1], None), ([0, 0, -1], None),
    ([-1, 1, -1], 1), ([1, 1, 1], None),
])
def test_crossing_ignores_touches_and_reports_first_opposite_sample(xs, expected):
    assert first_crossing_z(np.column_stack((xs, np.zeros(len(xs)), np.arange(len(xs))))) == expected


@pytest.mark.parametrize("step", [0, -1, float("nan"), float("inf")])
def test_invalid_steps_rejected(step):
    with pytest.raises(ValueError, match="step-mm"):
        summarize_bundle([synthetic("s")], "CST_L", step)


def test_bad_streamlines_accounted_for_and_duplicates_allowed():
    valid = synthetic("straight")
    result = summarize_bundle([np.repeat(valid, 2, axis=0), np.zeros((4, 3)), np.array([[0, 0, 0], [np.nan, 0, 0]])], "CST_L")
    assert result["streamlines"] == 1
    assert result["rejectedStreamlines"] == 2
    with pytest.raises(ValueError, match="no valid"):
        summarize_bundle([np.zeros((2, 3))], "CST_L")


def test_cli_alias_schema_and_missing_tract_preserves_output(tmp_path):
    incoming = tmp_path / "input"
    incoming.mkdir()
    raw_trk(incoming / "Cortico_Spinal_Tract_L.trk", np.diag([2., 3., 4., 1.]))
    output = tmp_path / "output" / "centerlines.json"
    argv = ["--in", str(incoming), "--out", str(output), "--tracts", "CST_L"]
    assert main(argv) == 0
    original = output.read_bytes()
    doc = json.loads(original)
    assert doc["source"]["space"] == "ICBM 2009a nonlinear asym"
    tract = doc["tracts"][0]
    assert tract["id"] == "cst-l"
    assert tract["atlasName"] == "Cortico_Spinal_Tract_L"
    assert tract["streamlines"] == 1
    assert len(tract["points"]) == len(tract["radiiMm"])
    with pytest.raises(SystemExit) as exc:
        main(argv[:-1] + ["MISSING"])
    assert exc.value.code == 2
    assert output.read_bytes() == original


def test_tt_only_and_duplicate_files_fail_clearly(tmp_path):
    (tmp_path / "CST_L.tt.gz").touch()
    with pytest.raises(ValueError, match="TT"):
        select_files(tmp_path, None)
    (tmp_path / "CST_L.trk").touch()
    (tmp_path / "CST_L.trk.gz").touch()
    with pytest.raises(ValueError, match="Duplicate"):
        select_files(tmp_path, None)
