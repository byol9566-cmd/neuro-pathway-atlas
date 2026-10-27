import numpy as np
import pytest

from atlas_pipeline import meshing, models


def test_path_tube_reaches_both_waypoint_ends():
    pts = [[0, 0, 0], [5, 3, 20], [8, -2, 50], [10, 0, 80]]
    mesh, line = models.path_tube(pts, radius=1.0)
    assert np.linalg.norm(line[0] - pts[0]) < 0.1
    assert np.linalg.norm(line[-1] - pts[-1]) < 0.1
    assert mesh.bounds[1][2] > 80 - 0.1  # the end cap reaches the last waypoint (was 78.2)
    short, sline = models.path_tube([[0, 0, 0], [0, 0, 5]], radius=0.5)
    assert np.linalg.norm(sline[-1] - [0, 0, 5]) < 0.1  # (was 3.33)
    tiny, tline = models.path_tube([[0, 0, 0], [0, 0, 0.3]], radius=0.2)  # shorter than a step
    assert len(tline) == 2 and tiny.volume > 0


def test_path_tube_mesh_is_closed_with_positive_volume():
    mesh, _ = models.path_tube([[0, 0, 0], [5, 3, 20], [8, -2, 50], [10, 0, 80]], radius=1.0)
    assert mesh.is_watertight
    assert mesh.volume > 0


def test_tube_straight_line_closed():
    m = meshing.tube(np.array([[0, 0, 0], [0, 0, 5], [0, 0, 10.0]]), np.full(3, 1.0))
    assert m.is_watertight
    assert m.volume == pytest.approx(np.pi * 10, rel=0.1)  # 12-gon prism, slightly under pi r^2 h


def test_axis_tract_sides_symmetric_about_offset_neuraxis(monkeypatch):
    # a straight cord 4 mm left of the MNI midline, no brainstem part
    monkeypatch.setattr(models, "_CORD_AXIS", {z: np.array([-4.0, -40.0, 5.0]) for z in range(-60, -320, -1)})
    monkeypatch.setattr(models, "BRAINSTEM_AXIS", None)
    for cross in (None, [-200, -180]):
        src = {"shape": "axis-tract", "params": {"keys": [[-60, 0.6, 0.1], [-300, 0.5, -0.2]], "z_top": -70, "z_bottom": -290, "cross": cross}}
        mr, lr = models.build(src, "R")
        ml, ll = models.build(src, "L")
        assert (lr[:, 0].mean() + ll[:, 0].mean()) / 2 == pytest.approx(-4.0, abs=0.1)
        assert (mr.centroid[0] + ml.centroid[0]) / 2 == pytest.approx(-4.0, abs=0.1)
        # the R mesh is the right side above the decussation
        assert lr[0, 0] > -4.0 and ll[0, 0] < -4.0


def test_path_tube_mirror_fixed_tail_meets_the_organ():
    organ = [-19.0, -15.0, -312.0]
    src = {"shape": "path-tube", "params": {"points": [[30, -20, -200], [10, -10, -260], organ], "radius": 0.8, "mirrorFixedTail": 1}}
    assert models.builds_left(src)
    _, lr = models.build(src, "R")
    _, ll = models.build(src, "L")
    assert np.linalg.norm(lr[-1] - organ) < 0.1 and np.linalg.norm(ll[-1] - organ) < 0.1
    assert ll[0, 0] == pytest.approx(-30.0)
