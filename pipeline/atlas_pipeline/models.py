"""Parametric anatomical models for structures no open atlas segments at a usable size (the membranous
labyrinth, peripheral ganglia, the carotid sinus): textbook dimensions turned into meshes and placed at
literature MNI coordinates. They are still approximations (the viewer says so), but a spiral cochlea or a
crescent ganglion teaches the shape an ellipsoid cannot.

content/structures.json:  "source": {"atlas": "model", "shape": "cochlea", "centreMni": [36, -30, -27],
                                      "axis": [0.7, 0.5, -0.3], "up": [0, 0, 1], "params": {...}, "bilateral": true}
`axis` is where the model's local +z points in MNI (RAS), `up` fixes the roll (local +x). The right side is
given; the left is the mirror image. Every builder returns a trimesh in its local frame, centred.
"""
from __future__ import annotations

import numpy as np
import trimesh

from . import meshing


# ---------------------------------------------------------------- frames
def frame(axis, up=None) -> np.ndarray:
    """rotation matrix whose columns are local x, y, z expressed in MNI"""
    z = np.asarray(axis, dtype=float); z /= np.linalg.norm(z)
    # default roll: local x along MNI x, so axis [0,0,1] with no `up` is the identity (an earlier default
    # of [0,0,1] fell back to y and silently rotated such models 90 degrees about z)
    u = np.asarray(up if up is not None else [1.0, 0.0, 0.0], dtype=float)
    if abs(u @ z) > 0.95:
        u = np.array([0.0, 0.0, 1.0]) if abs(z[2]) < 0.95 else np.array([0.0, 1.0, 0.0])
    x = u - z * (u @ z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=1)


def place(mesh: trimesh.Trimesh, centre, axis, up=None) -> trimesh.Trimesh:
    R = frame(axis, up)
    verts = mesh.vertices @ R.T + np.asarray(centre, dtype=float)
    return trimesh.Trimesh(verts, mesh.faces.copy(), process=False)


# ---------------------------------------------------------------- curves
def spiral(turns: float, r0: float, r1: float, height: float, n: int = 120, phase: float = 0.0):
    """conical spiral from radius r0 at the base (z=0) to r1 at the apex (z=height); the cochlea"""
    t = np.linspace(0, 1, n)
    th = phase + 2 * np.pi * turns * t
    r = r0 + (r1 - r0) * t
    return np.stack([r * np.cos(th), r * np.sin(th), height * t], axis=1), t


def arc(radius: float, degrees: float, n: int = 48):
    """circular arc in the local xy plane, centred on the origin, symmetric about +x"""
    a = np.radians(degrees)
    th = np.linspace(-a / 2, a / 2, n)
    return np.stack([radius * np.cos(th), radius * np.sin(th), np.zeros(n)], axis=1)


def ribbon(points: np.ndarray, width: np.ndarray, thickness: float, normal_hint=(0.0, 0.0, 1.0)) -> trimesh.Trimesh:
    """flat strip along a polyline: width in the plane perpendicular to normal_hint, given thickness"""
    P = np.asarray(points, float); W = np.broadcast_to(np.asarray(width, float), (len(P),))
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
    N = np.asarray(normal_hint, float)
    side = np.cross(T, N); side /= np.linalg.norm(side, axis=1)[:, None] + 1e-9
    nrm = np.cross(side, T)
    corners = []
    for sgn_w in (-1, 1):
        for sgn_t in (-1, 1):
            corners.append(P + side * (sgn_w * W / 2)[:, None] + nrm * (sgn_t * thickness / 2))
    V = np.concatenate(corners)  # 4 rails of len(P)
    n = len(P)
    rails = [(0, 1), (1, 3), (3, 2), (2, 0)]  # around the rectangle: (-w,-t) (-w,+t) (+w,+t) (+w,-t)
    faces = []
    for a, b in rails:
        for i in range(n - 1):
            faces.append([a * n + i, b * n + i, b * n + i + 1])
            faces.append([a * n + i, b * n + i + 1, a * n + i + 1])
    faces += [[0, 2 * n, 3 * n], [0, 3 * n, n], [n - 1, 2 * n - 1, 4 * n - 1], [n - 1, 4 * n - 1, 3 * n - 1]]
    return meshing.outward(trimesh.Trimesh(V, np.asarray(faces), process=False))


# ---------------------------------------------------------------- shapes
def cochlea(turns=2.5, base_radius=4.2, apex_radius=1.2, height=4.5, canal_radius=(1.0, 0.5), **_):
    """the bony cochlear canal: 2.5 turns, ~9 mm across at the base, ~5 mm tall, canal tapering apexward"""
    P, t = spiral(turns, base_radius, apex_radius, height)
    r = canal_radius[0] + (canal_radius[1] - canal_radius[0]) * t
    m = meshing.tube(P, r, segments=14)
    return m.apply_translation(-P.mean(axis=0))


def cochlear_strip(kind: str, turns=2.5, base_radius=4.2, apex_radius=1.2, height=4.5, **_):
    """structures of the cochlear duct drawn along the same spiral as cochlea():
    basilar membrane (floor of the duct, widening toward the apex), organ of Corti (ridge on it),
    tectorial membrane (strip above the organ), stria vascularis (band on the outer wall),
    spiral ganglion (in the modiolus, inside the spiral at ~55 % of its radius)"""
    P, t = spiral(turns, base_radius, apex_radius, height)
    centre = P.mean(axis=0)
    radial = P.copy(); radial[:, 2] = 0
    radial /= np.linalg.norm(radial, axis=1)[:, None] + 1e-9
    if kind == "basilar-membrane":
        m = ribbon(P - radial * 0.1, 0.25 + 0.3 * t, 0.12)
    elif kind == "organ-corti":
        m = meshing.tube(P - radial * 0.15 + [0, 0, 0.12], np.full(len(P), 0.2), segments=8)
    elif kind == "tectorial-membrane":
        m = ribbon(P - radial * 0.2 + [0, 0, 0.32], 0.2 + 0.25 * t, 0.08)
    elif kind == "stria-vascularis":
        r = 1.0 + (0.5 - 1.0) * t
        m = ribbon(P + radial * (r * 0.85)[:, None], 0.35 + 0.1 * t, 0.1, normal_hint=(1.0, 0.0, 0.0))
    elif kind == "spiral-ganglion":
        Q, _ = spiral(turns, base_radius * 0.55, apex_radius * 0.6, height * 0.95)
        m = meshing.tube(Q, 0.35 - 0.12 * t, segments=8)
    else:
        raise ValueError(kind)
    return m.apply_translation(-centre)


def semicircular_canal(radius=3.2, degrees=240.0, canal_radius=0.45, ampulla_radius=1.0, **_):
    """one semicircular canal as an arc of the bony canal with its ampulla at one end (the +y end)"""
    P = arc(radius, degrees)
    n = len(P)
    r = np.full(n, canal_radius)
    bulge = np.exp(-((np.arange(n) - (n - 6)) / 4.0) ** 2)
    r = r + (ampulla_radius - canal_radius) * bulge
    m = meshing.tube(P, r, segments=10)
    return m.apply_translation(-P.mean(axis=0))


def spindle(length=10.0, radius=3.0, sharpness=0.7, n=24, **_):
    """fusiform body along local z (ganglia, the carotid sinus)"""
    t = np.linspace(0, 1, n)
    P = np.stack([np.zeros(n), np.zeros(n), (t - 0.5) * length], axis=1)
    r = radius * np.sin(np.pi * t) ** sharpness
    r = np.maximum(r, 0.15)
    return meshing.tube(P, r, segments=16)


def crescent(radius=7.0, degrees=150.0, thickness=(2.5, 1.5), flatten=0.6, **_):
    """semilunar body in the local xy plane (the trigeminal ganglion), thicker at the convex middle"""
    P = arc(radius, degrees)
    n = len(P)
    r = thickness[1] + (thickness[0] - thickness[1]) * np.sin(np.pi * np.linspace(0, 1, n))
    m = meshing.tube(P, r, segments=14)
    m.vertices[:, 2] *= flatten
    return m.apply_translation(-P.mean(axis=0))


def ellipsoid(radii=(2.0, 2.0, 1.5), **_):
    return meshing.ellipsoid([0, 0, 0], radii)


def disc(radius=2.0, thickness=0.8, **_):
    """flattened ovoid (the ciliary, otic, pterygopalatine ganglia)"""
    return meshing.ellipsoid([0, 0, 0], [radius, radius, thickness / 2])


# ---------------------------------------------------------------- spinal cord columns
_CORD_AXIS = None
CORD_FILE = None  # set by build.py: data/derived/vhp/sp-cord.M.mni.nii.gz
Z_T1, Z_L1, Z_CONUS = -230.0, -470.0, -495.0


def cord_axis():
    """z (mm, RAS) -> (x, y, radius) along the cord: the Visible Human cord down to about T1, then a
    textbook continuation — the thoracic cord bows ~25 mm posteriorly with the kyphosis, narrows to
    ~4.5 mm radius, swells again at the lumbosacral enlargement and tapers into the conus near L1."""
    global _CORD_AXIS
    if _CORD_AXIS is not None:
        return _CORD_AXIS
    import nibabel as nib

    pts = {}
    if CORD_FILE is not None and CORD_FILE.exists():
        img = nib.as_closest_canonical(nib.load(CORD_FILE))
        a = np.asanyarray(img.dataobj) > 0
        A = img.affine
        for k in range(a.shape[2]):
            sl = a[:, :, k]
            if sl.sum() < 20:
                continue
            ii, jj = np.nonzero(sl)
            c = A @ np.array([ii.mean(), jj.mean(), k, 1.0])
            pts[round(float(c[2]))] = np.array([c[0], c[1], np.sqrt(sl.sum() / np.pi) * abs(A[0, 0])])
    if pts:
        zs = sorted(pts)
        arr = np.array([pts[z] for z in zs])
        k = np.ones(15) / 15
        sm = np.stack([np.convolve(np.pad(arr[:, i], 7, mode="edge"), k, mode="valid") for i in range(3)], axis=1)
        pts = {z: sm[i] for i, z in enumerate(zs)}
        z_end = min(zs)
        x_end, y_end, _ = pts[z_end]
    else:  # no segmentation available: straight cord under the medulla
        z_end, x_end, y_end = -56.0, 0.0, -38.0
        for z in range(int(z_end), int(Z_T1) - 1, -1):
            pts[z] = np.array([0.0, -38.0 + 12.0 * (z_end - z) / (z_end - Z_T1), 6.0])
        z_end, x_end, y_end = Z_T1, 0.0, -26.0
    for z in range(int(z_end) - 1, int(Z_CONUS) - 1, -1):
        u = (z_end - z) / (z_end - Z_L1)  # 0 at the end of the data, 1 at L1
        y = y_end - 25.0 * np.sin(np.pi * min(u, 1.0))
        x = x_end * max(0.0, 1 - u)
        if z > Z_L1 + 40:
            r = 5.5 + (4.5 - 5.5) * min(u / 0.5, 1.0)  # taper into the thoracic cord
        elif z > Z_L1:
            r = 4.5 + 1.0 * np.sin(np.pi * (z - Z_L1) / 40.0)  # lumbosacral enlargement
        else:
            r = max(1.0, 5.0 * (z - Z_CONUS) / (Z_L1 - Z_CONUS))  # conus
        pts[z] = np.array([x, y, r])
    _CORD_AXIS = pts
    return pts


def cord_extension(**_):
    """the cord below the Visible Human data as a tapered tube, so the thoracolumbar columns have a body"""
    ax = cord_axis()
    zs = [z for z in sorted(ax, reverse=True) if z <= Z_T1 + 4]
    P = np.array([[ax[z][0], ax[z][1], float(z)] for z in zs[::4]])
    R = np.array([ax[z][2] for z in zs[::4]])
    m = meshing.tube(P, R, segments=16)
    return m  # already in MNI; place() receives centre [0,0,0]


def cord_column(z_top: float, z_bottom: float, offset=(2.5, -0.5), radius=0.8, lateral_sign=1.0, **_):
    """a cell column inside the cord: offset (lateral, anterior) from the axis, in mm at a 4.5 mm cord,
    scaled with the local radius; right side (lateral_sign=+1)"""
    ax = cord_axis()
    zs = [z for z in sorted(ax, reverse=True) if z_bottom <= z <= z_top]
    P, R = [], []
    for z in zs[::3]:
        x, y, r = ax[z]
        s = r / 4.5
        P.append([x + lateral_sign * offset[0] * s, y + offset[1] * s, float(z)])
        R.append(radius)
    return meshing.tube(np.array(P), np.array(R), segments=10)


BUILDERS = {
    "cord-extension": cord_extension,
    "cord-column": cord_column,
    "cochlea": cochlea,
    "basilar-membrane": lambda **p: cochlear_strip("basilar-membrane", **p),
    "organ-corti": lambda **p: cochlear_strip("organ-corti", **p),
    "tectorial-membrane": lambda **p: cochlear_strip("tectorial-membrane", **p),
    "stria-vascularis": lambda **p: cochlear_strip("stria-vascularis", **p),
    "spiral-ganglion": lambda **p: cochlear_strip("spiral-ganglion", **p),
    "semicircular-canal": semicircular_canal,
    "spindle": spindle,
    "crescent": crescent,
    "ellipsoid": ellipsoid,
    "disc": disc,
}


def path_tube(points, radius=1.0, **_):
    """a nerve drawn as a tube through MNI waypoints (resampled every 2 mm so the bends are smooth)"""
    P = np.asarray(points, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.arange(0, s[-1], 2.0)
    Q = np.stack([np.interp(t, s, P[:, i]) for i in range(3)], axis=1)
    k = np.ones(3) / 3
    Q = np.stack([np.convolve(np.pad(Q[:, i], 1, mode="edge"), k, mode="valid") for i in range(3)], axis=1)
    return meshing.tube(Q, np.full(len(Q), float(radius)), segments=10)


BUILDERS["path-tube"] = path_tube
WORLD_SHAPES = {"cord-extension", "cord-column", "path-tube"}  # built in MNI already: no placement


def build(source: dict) -> trimesh.Trimesh:
    """mesh for one side (the right) in MNI from a `model` source"""
    mesh = BUILDERS[source["shape"]](**source.get("params", {}))
    if source["shape"] in WORLD_SHAPES:
        return mesh
    return place(mesh, source["centreMni"], source.get("axis", [0, 0, 1]), source.get("up"))
