#!/usr/bin/env python3
"""Replace ellipsoid placeholders with parametric textbook models (atlas_pipeline/models.py) for the inner
ear, the peripheral ganglia and the carotid sinus/body.

    pipeline/.venv/bin/python pipeline/apply_models.py [--write]

Positions are the placeholders' literature coordinates (kept in `replaced`); the orientation of each model
is textbook anatomy, right side in MNI (x lateral, y anterior, z superior):
- labyrinth: lateral canal plane tilted ~30 deg anterior-up; anterior canal in a vertical plane across the
  petrous axis (anterolateral-posteromedial) with its ampulla anterolateral; posterior canal in a vertical
  plane along the petrous axis with its ampulla inferior; cochlea anteromedial-inferior to the vestibule,
  modiolar axis pointing anterolaterally and a little down.
- ganglia: trigeminal = crescent in Meckel's cave, convex anterolaterally; the autonomic head ganglia are
  flattened discs; nodose, petrosal, Scarpa and the superior cervical ganglion are spindles along their
  nerve. Carotid sinus = dilated spindle at the bifurcation; carotid body = flattened ovoid behind it.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "structures.json"

PETROUS = [-0.7, 0.7, 0.0]  # anteromedial direction of the right petrous axis (xy)
COCHLEA = {"centreMni": [35, -29, -26], "axis": [0.6, 0.75, -0.3], "up": [0, 0, 1]}
MODELS = {
    "so-cochlea": {"shape": "cochlea", **COCHLEA},
    "so-basilar-membrane": {"shape": "basilar-membrane", **COCHLEA},
    "so-organ-corti": {"shape": "organ-corti", **COCHLEA},
    "so-tectorial-membrane": {"shape": "tectorial-membrane", **COCHLEA},
    "so-stria-vascularis": {"shape": "stria-vascularis", **COCHLEA},
    "pn-spiral-ganglion": {"shape": "spiral-ganglion", **COCHLEA},
    "so-horizontal-canal": {"shape": "semicircular-canal", "centreMni": [41, -35, -20], "axis": [0, -0.5, 0.87], "up": [1, 0, 0]},
    "so-anterior-canal": {"shape": "semicircular-canal", "centreMni": [38, -31, -16], "axis": PETROUS, "up": [0, 0, 1]},
    "so-posterior-canal": {"shape": "semicircular-canal", "centreMni": [42, -38, -23], "axis": [0.7, 0.7, 0], "up": [0.7, -0.7, -0.2]},
    "so-utricle": {"shape": "ellipsoid", "params": {"radii": [3.0, 2.0, 1.5]}, "centreMni": [38, -33, -21], "axis": [0, -0.5, 0.87], "up": [1, 0, 0]},
    "so-saccule": {"shape": "ellipsoid", "params": {"radii": [1.5, 1.2, 1.8]}, "centreMni": [36, -31, -24], "axis": [0, 0, 1]},
    "pn-vestibular-ganglion": {"shape": "spindle", "params": {"length": 5, "radius": 1.8}, "centreMni": [31, -30, -26], "axis": [1, 0.2, 0]},
    "pn-geniculate-ganglion": {"shape": "disc", "params": {"radius": 1.5, "thickness": 1.0}, "centreMni": [35, -28, -22], "axis": [1, 0, 0]},
    "pn-trigeminal-ganglion": {"shape": "crescent", "params": {"radius": 6.0, "degrees": 150, "thickness": [2.5, 1.5], "flatten": 0.6},
                               "centreMni": [20, -10, -32], "axis": [0.2, 0.3, 0.93], "up": [0.7, 0.7, 0]},
    "pn-nodose-ganglion": {"shape": "spindle", "params": {"length": 16, "radius": 3.0}, "centreMni": [18, -26, -64], "axis": [0.1, -0.2, -1]},
    "pn-petrosal-ganglion": {"shape": "spindle", "params": {"length": 6, "radius": 2.0}, "centreMni": [15, -30, -52], "axis": [0, 0, -1]},
    "pn-superior-cervical": {"shape": "spindle", "params": {"length": 25, "radius": 4.0}, "centreMni": [22, -30, -88], "axis": [0, 0.15, -1]},
    "pn-ciliary-ganglion": {"shape": "disc", "params": {"radius": 1.5, "thickness": 0.8}, "centreMni": [29, 38, -28], "axis": [0, 1, 0]},
    "pn-pterygopalatine": {"shape": "disc", "params": {"radius": 3.0, "thickness": 1.5}, "centreMni": [24, 20, -44], "axis": [1, 0, 0]},
    "pn-submandibular": {"shape": "disc", "params": {"radius": 2.0, "thickness": 1.0}, "centreMni": [33, 12, -76], "axis": [0, 0, 1]},
    "pn-otic": {"shape": "disc", "params": {"radius": 2.5, "thickness": 1.0}, "centreMni": [24, -6, -50], "axis": [1, 0, 0]},
    "so-carotid-baroreceptor": {"shape": "spindle", "params": {"length": 14, "radius": 4.5, "sharpness": 0.5}, "centreMni": [28, -20, -102], "axis": [0.1, 0.1, 1],
                                "modelNote": "기하 모형: 목동맥팽대(온목동맥 갈림 부위의 확장부)를 방추형으로 표현. 압력수용기는 이 벽 안의 신경종말이다."},
    "so-carotid-body": {"shape": "ellipsoid", "params": {"radii": [2.5, 1.5, 3.0]}, "centreMni": [27, -22, -104], "axis": [0, 0, 1]},
}


def main(write):
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    n = 0
    for s in data["structures"]:
        m = MODELS.get(s["id"])
        if not m:
            continue
        old = s["source"]
        replaced = old.get("replaced", old) if old.get("atlas") == "model" else old
        s["source"] = {"atlas": "model", **m, "bilateral": True, "replaced": replaced}
        n += 1
    print(f"{n} structures -> model")
    missing = [k for k in MODELS if k not in {s["id"] for s in data["structures"]}]
    if missing:
        print("not in content:", missing)
    if write:
        CONTENT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written", CONTENT)


if __name__ == "__main__":
    main("--write" in sys.argv)
