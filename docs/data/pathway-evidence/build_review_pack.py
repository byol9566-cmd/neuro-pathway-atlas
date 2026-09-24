#!/usr/bin/env python3
"""Merge the evidence batches and every upgrade file into one record per pathway.

    pipeline/.venv/bin/python docs/data/pathway-evidence/build_review_pack.py

Writes merged/<pathway-id>.json: the step skeleton (from the base batch), every source that supports
each step (with its grade), all conflicts from every file, the remaining unsourced items, and lesions.
This is the input for drafting the reviewer's sheets; nothing here is prose yet.
"""
import json
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "merged"
BASE = ["somatosensory", "motor", "brainstem-reflexes", "special-senses", "limbic-arousal-autonomic"]

# source grade by how it was obtained / what it is (REVIEW.md's A/B/C scale)
def grade(src):
    t = (src.get("type") or "").lower()
    j = (src.get("journal") or "").lower()
    if t == "statpearls" or "statpearls" in j or (src.get("nbk") and "purves" not in j):
        return "B"
    if t == "textbook":
        return "A" if "springer" in j or "nieuwenhuys" in (src.get("authors") or "").lower() else "B"
    if "bioinformation" in j:
        return "C"
    if t in ("review", "primary"):
        return "A"
    return "?"


def label(src):
    a = (src.get("authors") or "").split(",")[0].split(" ")[0]
    return f"{a} {src.get('year', '')} {src.get('journal', '')}".strip()


def main():
    OUT.mkdir(exist_ok=True)
    merged = OrderedDict()
    files = [HERE / f"{b}.json" for b in BASE] + sorted(HERE.glob("upgrade-*.json"))
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        srcs = {s["id"]: s for s in d.get("sources", [])}
        for p in d.get("pathways", []):
            pid = p.get("id") or p.get("pathwayId")
            if not pid:
                continue
            rec = merged.setdefault(pid, {"id": pid, "name": p.get("name"), "category": p.get("category"), "function": p.get("function"),
                                          "steps": [], "lesions": [], "conflicts": [], "unsourced": [], "sources": {}})
            if p.get("name") and not rec["name"]:
                rec.update(name=p.get("name"), category=p.get("category"), function=p.get("function"))
            for st in p.get("steps", []):
                order = st.get("order")
                have = next((s for s in rec["steps"] if s["order"] == order), None)
                if not have:
                    have = {k: st.get(k) for k in ("order", "neuronOrder", "cellBodies", "courseVia", "terminatesIn", "laterality", "decussation", "neurotransmitter")}
                    have["evidence"] = []
                    rec["steps"].append(have)
                for e in st.get("evidence", []):
                    s = srcs.get(e.get("source"))
                    if not s:
                        continue
                    key = s.get("pmcid") or s.get("doi") or s.get("isbn") or s.get("nbk") or s.get("title")
                    rec["sources"][key] = {"label": label(s), "grade": grade(s), "title": s.get("title"), "doi": s.get("doi"), "pmcid": s.get("pmcid"), "isbn": s.get("isbn"), "nbk": s.get("nbk")}
                    have["evidence"].append({"source": key, "grade": grade(s), "quote": e.get("quote"), "species": e.get("species"), "page": e.get("page"), "file": f.name})
            for l in p.get("lesions", []):
                ev = []
                for e in l.get("evidence", []):
                    s = srcs.get(e.get("source"))
                    if s:
                        ev.append({"source": label(s), "grade": grade(s), "quote": e.get("quote")})
                rec["lesions"].append({"site": l.get("site"), "deficit": l.get("deficit"), "side": l.get("side"), "evidence": ev, "file": f.name})
            for c in p.get("conflicts", []):
                positions = []
                for pos in c.get("positions", []):
                    s = srcs.get(pos.get("source"))
                    positions.append({"source": label(s) if s else (pos.get("source") or "?"), "grade": grade(s) if s else "?", "claim": pos.get("claim"), "quote": pos.get("quote")})
                rec["conflicts"].append({"issue": c.get("issue"), "positions": positions, "file": f.name})
            for u in p.get("unsourced", []):
                if isinstance(u, str) and not u.upper().startswith("RESOLVED"):
                    rec["unsourced"].append({"text": u, "file": f.name})
    for pid, rec in merged.items():
        rec["steps"].sort(key=lambda s: s["order"] or 0)
        (OUT / f"{pid}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    n_conf = sum(len(r["conflicts"]) for r in merged.values())
    n_steps = sum(len(r["steps"]) for r in merged.values())
    print(f"pathways {len(merged)}, steps {n_steps}, conflicts {n_conf}, lesions {sum(len(r['lesions']) for r in merged.values())}")
    for pid, rec in merged.items():
        grades = [e["grade"] for s in rec["steps"] for e in s["evidence"]]
        print(f"  {pid:46} steps={len(rec['steps'])} A={grades.count('A'):3} B={grades.count('B'):3} C={grades.count('C')} conflicts={len(rec['conflicts'])}")


if __name__ == "__main__":
    main()
