#!/usr/bin/env python3
"""Lint the pathway steps against the structure list and fix what is mechanical.

    pipeline/.venv/bin/python pipeline/content_lint.py [--write]

(a) a step's `missing` text ("… 3D 정의 없음: A · B · 3D 없음: A, B") still names structures that the step now
    links — those items are dropped (an empty section loses its prefix; an empty text drops `missing`);
(b) an item that names an existing structure the step does not link yet is linked (appended to `structures`)
    and dropped from `missing` — side 'contra' when the text around the item says 반대쪽/대측, else the step's
    majority side (default 'ipsi'); body-skin, bone-* and shell-* are never linked this way;
(c) `has3d` is recomputed: a step structure with a mesh in viewer/public/data/manifest.json (without a
    manifest: any step structure);
(d) items that name no structure are only counted (the next modelling list);
(e) what remains is written as one section, "3D 없음: A · B", each name once.
Without --write it only prints the report. Matching: ko name with its parenthetical stripped, or the en name.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATHWAYS = ROOT / "content" / "pathways.json"
STRUCTURES = ROOT / "content" / "structures.json"
MANIFEST = ROOT / "viewer" / "public" / "data" / "manifest.json"

# section prefixes of the missing text and the separator between their items
PREFIXES = [("현재 제공 데이터에 독립 3D 정의 없음:", " · "), ("3D 없음:", ", ")]
NO_AUTOLINK = re.compile(r"^(body-skin$|bone-|shell-)")
CONTRA = ("반대쪽", "대측")
MISSING_PREFIX = "3D 없음:"  # the one prefix written back (the old texts listed every name twice, see (e))
EDGE = " ·,"  # stray separators around an item ("A ·  · B", "3D 없음: , B") are dropped


def strip_paren(name: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def split_top(text: str, sep: str) -> list[str]:
    """Split on sep, but not inside parentheses (an item like "척수 (C1, C2)" stays whole)."""
    out, depth, cur, i = [], 0, "", 0
    while i < len(text):
        if depth == 0 and text.startswith(sep, i):
            out.append(cur)
            cur, i = "", i + len(sep)
            continue
        depth += {"(": 1, ")": -1}.get(text[i], 0)
        cur += text[i]
        i += 1
    out.append(cur)
    return out


def parse_missing(text: str) -> list[tuple[str, list[str]]]:
    """'P1: a · b · P2: a, b' -> [(P1, [a, b]), (P2, [a, b])]."""
    sections = []
    for token in split_top(text, " · "):
        for prefix, sep in PREFIXES:
            if token.startswith(prefix):
                items = [i.strip(EDGE) for i in split_top(token[len(prefix):], sep)]
                sections.append((prefix, [i for i in items if i]))
                break
        else:
            if not sections:
                raise ValueError(f"missing text without a known prefix: {text!r}")
            if token.strip(EDGE):
                sections[-1][1].append(token.strip(EDGE))  # a further item of the first section
    return sections


def format_missing(sections) -> str:
    """One section, "3D 없음: A · B", each name once (first-seen form, parenthetical kept)."""
    seen, names = set(), []
    for _, items in sections:
        for item in items:
            if strip_paren(item) not in seen:
                seen.add(strip_paren(item))
                names.append(item)
    return f"{MISSING_PREFIX} {' · '.join(names)}" if names else ""


def name_keys(structure: dict) -> set[str]:
    name = structure["name"]
    keys = {strip_paren(name["ko"]), name["ko"].strip()}
    if name.get("en"):
        keys |= {strip_paren(name["en"]), name["en"].strip()}
    return keys


def item_keys(item: str) -> set[str]:
    return {item.strip(), strip_paren(item)}


def side_for(step: dict, item: str) -> tuple[str, str]:
    """Side for a newly linked structure and the reason (shown in the report for review)."""
    texts = [step.get("title", {}).get("ko", ""), step.get("description", {}).get("ko", "")]
    name = strip_paren(item)
    for text in texts:
        for clause in re.split(r"[.,·→]|\s-\s", text):
            if name in clause and any(w in clause for w in CONTRA):
                return "contra", "text near item"
    if not any(name in t for t in texts) and any(w in t for t in texts for w in CONTRA):
        return "contra", "step text"
    sides = Counter(s["side"] for s in step["structures"])
    if sides:
        side = max(sorted(sides), key=lambda k: sides[k])
        return side, f"majority {dict(sides)}"
    return "ipsi", "default"


def main():
    write = "--write" in sys.argv
    pathways = json.loads(PATHWAYS.read_text(encoding="utf-8"))
    structures = json.loads(STRUCTURES.read_text(encoding="utf-8"))["structures"]
    by_id = {s["id"]: s for s in structures}
    by_key: dict[str, list[str]] = {}
    for s in structures:
        for k in name_keys(s):
            by_key.setdefault(k, []).append(s["id"])
    if MANIFEST.exists():
        meshed = {m["structureId"] for m in json.loads(MANIFEST.read_text(encoding="utf-8"))["meshes"]}
    else:
        meshed = None
        print("no manifest — has3d falls back to 'has at least one structure'")

    stale, stale_names, rewritten = 0, 0, 0
    linked, ambiguous, unmatched, skipped = [], [], Counter(), Counter()
    for pw in pathways["pathways"]:
        for step in pw["steps"]:
            if "missing" not in step:
                continue
            keys = set()
            for s in step["structures"]:
                keys |= name_keys(by_id[s["id"]]) if s["id"] in by_id else set()
            sections = parse_missing(step["missing"]["ko"])
            step_stale, step_unmatched = set(), set()
            for _, items in sections:
                kept = []
                for item in items:
                    if item_keys(item) & keys:  # (a) already linked
                        stale += 1
                        step_stale.add(strip_paren(item))
                        continue
                    ids = sorted({i for k in item_keys(item) for i in by_key.get(k, [])})
                    ids = [i for i in ids if not NO_AUTOLINK.match(i)]
                    if not ids:
                        if any(by_key.get(k) for k in item_keys(item)):
                            skipped[strip_paren(item)] += 1  # names only body-skin / bone-* / shell-*
                        else:
                            step_unmatched.add(strip_paren(item))
                        kept.append(item)
                        continue
                    if meshed is not None and len(ids) > 1:
                        ids = [i for i in ids if i in meshed] or ids
                    if len(ids) > 1:
                        ambiguous.append((pw["id"], step["id"], item, ids))
                        kept.append(item)
                        continue
                    sid = ids[0]  # (b) exists but not linked: link it once, drop every mention
                    side, why = side_for(step, item)
                    step["structures"].append({"id": sid, "side": side})
                    keys |= name_keys(by_id[sid])
                    linked.append((pw["id"], step["id"], item, sid, side, why))
                items[:] = kept
            stale_names += len(step_stale)
            unmatched.update(step_unmatched)
            text = format_missing(sections)
            if text and text != step["missing"]["ko"]:
                rewritten += 1
            if text:
                step["missing"]["ko"] = text
            else:
                del step["missing"]

    flips = []
    for pw in pathways["pathways"]:  # (c)
        has3d = any(
            (s["id"] in meshed) if meshed is not None else True
            for step in pw["steps"] for s in step["structures"]
        )
        if pw.get("has3d") != has3d:
            flips.append((pw["id"], pw.get("has3d"), has3d))
        pw["has3d"] = has3d

    print(f"(a) stale missing items removed (already linked in the step): {stale} mentions, {stale_names} distinct per step")
    print(f"(b) linked from missing: {len(linked)}")
    for row in linked:
        print("    " + " | ".join(row))
    if ambiguous:
        print(f"    ambiguous, left in missing: {len(ambiguous)}")
        for pid, sid, item, ids in ambiguous:
            print(f"    {pid} | {sid} | {item} -> {', '.join(ids)}")
    if skipped:
        print(f"    not auto-linked (body-skin / bone-* / shell-* only): {dict(skipped)}")
    print(f"(c) has3d flips: {len(flips)}")
    for pid, old, new in flips:
        print(f"    {pid}: {old} -> {new}")
    print(f"(e) missing texts collapsed to one '{MISSING_PREFIX}' section: {rewritten}")
    print(f"(d) missing items naming no structure: {sum(unmatched.values())} (per step) / {len(unmatched)} distinct names; top 20:")
    for name, n in unmatched.most_common(20):
        print(f"    {n:4d}  {name}")

    if write:
        PATHWAYS.write_text(json.dumps(pathways, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", PATHWAYS.relative_to(ROOT))


if __name__ == "__main__":
    main()
