#!/usr/bin/env python3
"""Attach the body structures (apply_body.py) to the pathway steps that start or end on them: muscles for
motor outputs, organs and glands for autonomic outputs, skin for the sensory origins.

    pipeline/.venv/bin/python pipeline/apply_body_targets.py [--write]
Sides follow the step's existing side convention ('ipsi' = the side the pathway's origin switch names);
midline organs are 'ipsi' and resolve to their single M mesh.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATHWAYS = ROOT / "content" / "pathways.json"

STEP_TARGETS = {
    # cranial motor outputs -> muscles
    "cranial-iii-motor-2": [("mu-medial-rectus", "ipsi"), ("mu-superior-rectus", "ipsi"), ("mu-inferior-rectus", "ipsi"), ("mu-inferior-oblique", "ipsi"), ("mu-levator-palpebrae", "ipsi")],
    "cranial-iv-motor-2": [("mu-superior-oblique", "ipsi")],
    "cranial-vi-motor-2": [("mu-lateral-rectus", "ipsi")],
    "cranial-xi-motor-2": [("mu-sternocleidomastoid", "ipsi"), ("mu-trapezius", "ipsi")],
    "cranial-xii-motor-2": [("mu-genioglossus", "ipsi")],
    "hvor-inhibition-2": [("mu-lateral-rectus", "ipsi")],
    "hvor-4": [("mu-medial-rectus", "ipsi")],
    "hvor-2": [("mu-lateral-rectus", "contra")],
    "accommodation-3": [("mu-medial-rectus", "ipsi")],
    # spinal motor outputs: a flexor and an extensor of the arm and the leg stand in for 'muscle'
    "corticospinal-lateral-4": [("mu-biceps-brachii", "contra"), ("mu-quadriceps", "contra")],
    "corticospinal-anterior-4": [("mu-trapezius", "ipsi"), ("mu-iliopsoas", "ipsi")],
    "withdrawal-reflex-3": [("mu-hamstrings", "ipsi"), ("mu-quadriceps", "ipsi")],
    "stretch-reflex-1": [("mu-quadriceps", "ipsi")],
    "stretch-reflex-3": [("mu-quadriceps", "ipsi")],
    "vestibulospinal-lateral-3": [("mu-quadriceps", "ipsi"), ("mu-triceps-surae", "ipsi")],
    "reticulospinal-pontine-3": [("mu-quadriceps", "ipsi")],
    "reticulospinal-medullary-3": [("mu-biceps-brachii", "ipsi")],
    "rubrospinal-3": [("mu-biceps-brachii", "contra")],
    "tectospinal-3": [("mu-sternocleidomastoid", "contra")],
    # sensory origins: the skin
    "dcml-1": [("body-skin", "ipsi")],
    "spinothalamic-lateral-1": [("body-skin", "ipsi")],
    "spinothalamic-anterior-1": [("body-skin", "ipsi")],
    "withdrawal-reflex-1": [("body-skin", "ipsi")],
    # autonomic effectors
    "vagal-parasympathetic-3": [("vs-heart", "ipsi"), ("vs-lung", "ipsi"), ("vs-stomach", "ipsi"), ("vs-small-intestine", "ipsi")],
    "baroreflex-vagal-3": [("vs-heart", "ipsi")],
    "facial-lacrimation-3": [("vs-lacrimal-gland", "ipsi")],
    "facial-salivation-3": [("vs-submandibular-gland", "ipsi"), ("vs-sublingual-gland", "ipsi")],
    "sympathetic-thoracic-2": [("vs-heart", "ipsi"), ("vs-lung", "ipsi")],
    "sympathetic-abdominopelvic-3": [("vs-stomach", "ipsi"), ("vs-small-intestine", "ipsi"), ("vs-large-intestine", "ipsi"), ("vs-kidney", "ipsi"), ("vs-bladder", "ipsi")],
    "sympathetic-adrenal-1": [("vs-adrenal", "ipsi")],
    "sympathetic-somatic-3": [("body-skin", "ipsi")],
    "sympathetic-sweat-2": [("body-skin", "ipsi")],
    "autonomic-micturition-1": [("vs-bladder", "ipsi")],
    "autonomic-micturition-2": [("vs-bladder", "ipsi")],
    "parasympathetic-sacral-3": [("vs-bladder", "ipsi"), ("vs-large-intestine", "ipsi")],
    "autonomic-sexual-1": [("vs-prostate", "ipsi")],
    "hypothalamic-temperature-3": [("body-skin", "ipsi")],
    "brainstem-respiratory-regulation-1": [("vs-diaphragm", "ipsi")],
    "cough-reflex-3": [("vs-diaphragm", "ipsi"), ("vs-trachea", "ipsi")],
    "swallowing-reflex-3": [("vs-tongue", "ipsi"), ("vs-esophagus", "ipsi")],
    "gag-reflex-3": [("vs-tongue", "ipsi")],
    "gut-satiety-nucleus-solitary-1": [("vs-stomach", "ipsi"), ("vs-small-intestine", "ipsi")],
    "visceral-afferent-1": [("vs-carotid", "ipsi")],
    "baroreflex-sympathetic-1": [("vs-carotid", "ipsi")],
    "cranial-xii-motor-1": [],
    "language-spoken-4": [("vs-tongue", "ipsi")],
    "language-written-4": [("vs-tongue", "ipsi")],
}


def main(write):
    p = json.loads(PATHWAYS.read_text(encoding="utf-8"))
    changed = []
    for pw in p["pathways"]:
        for st in pw["steps"]:
            for sid, side in STEP_TARGETS.get(st["id"], []):
                if any(r["id"] == sid for r in st["structures"]):
                    continue
                st["structures"].append({"id": sid, "side": side})
                changed.append((st["id"], sid, side))
    print(f"{len(changed)} step targets added")
    if write:
        PATHWAYS.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
