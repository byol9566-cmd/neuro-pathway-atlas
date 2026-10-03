#!/usr/bin/env python3
"""Turn reconcile/compare-*.json into REPORT.md, worst differences first.

    python3 docs/data/pathway-evidence/reconcile/make_report.py
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
rows, additions, origin_notes = [], [], []
for f in sorted(HERE.glob("compare-*.json")):
    for p in json.loads(f.read_text(encoding="utf-8"))["pathways"]:
        origin_notes.append((p["ours"], p.get("origin_note", "")))
        for d in p.get("differences", []):
            rows.append({**d, "ours": p["ours"]})
        for a in p.get("additions", []):
            additions.append({**a, "ours": p["ours"]})

sev = {"high": 0, "medium": 1, "low": 2}
rows.sort(key=lambda r: (sev.get(r.get("severity"), 9), r["ours"]))
by_kind = Counter(r.get("kind") for r in rows)
by_sev = Counter(r.get("severity") for r in rows)

out = ["# 성연 데이터셋(2026-10-02) ↔ 우리 근거 대조 보고", "",
       f"대응표 `mapping.json`(우리 32 ↔ 성연 131). 차이 {len(rows)}건 — 심각도 {dict(by_sev)}, 종류 {dict(by_kind)}. 성연 쪽 근거는 강의 정리본(우리에게 PDF 없음, 확인 불가)이고, 우리 쪽은 `merged/`의 A급 인용. **누가 맞는지는 여기서 정하지 않는다** — 성연에게 되묻거나 판정 시트(검수시트2/6_판정)로 넘길 항목.", ""]

def fmt_ev(evs):
    if not evs:
        return "(우리 근거 없음)"
    return "; ".join(f"{e.get('source','')} ({e.get('grade','?')}): “{(e.get('quote_head') or '')[:90]}”" for e in evs[:3])

for level, title in [("high", "## 1. high — 그대로 두면 틀린 내용을 가르치게 되는 차이"), ("medium", "## 2. medium — 표현·범위·강조의 차이"), ("low", "## 3. low — 세분화·용어 차이 (참고)")]:
    xs = [r for r in rows if r.get("severity") == level]
    out += [title, "", f"{len(xs)}건", ""]
    if level == "low":
        out += ["| 우리 경로 | 성연 경로·단계 | 종류 | 성연 쪽 | 우리 쪽 |", "|---|---|---|---|---|"]
        for r in xs:
            out.append(f"| {r['ours']} | {r.get('their_pathway','')} {r.get('their_step','')} | {r.get('kind','')} | {(r.get('their_claim_ko') or '').replace('|','/')[:110]} | {(r.get('our_claim_ko') or '').replace('|','/')[:110]} |")
        out.append("")
        continue
    for r in xs:
        out += [f"### {r['ours']} ← {r.get('their_pathway','')} / {r.get('their_step','')}  `{r.get('kind','')}`", "",
                f"- **성연**: {r.get('their_claim_ko','')}  ⟨{r.get('their_evidence','')}⟩",
                f"- **우리**: {r.get('our_claim_ko','') or '(해당 내용 없음)'}",
                f"- 근거: {fmt_ev(r.get('ours_evidence'))}"]
        if r.get("note"):
            out.append(f"- 메모: {r['note']}")
        out.append("")

out += ["## 4. 성연 데이터에만 있는 내용 (우리 근거 범위 밖)", ""]
for a in additions:
    out.append(f"- {a.get('their_pathway','')} ({a['ours']} 관련): {a.get('summary_ko','')}")
out += ["", "## 5. 기준쪽(origin) 정의 비교", ""]
for o, n in origin_notes:
    out.append(f"- {o}: {n}")
(HERE / "REPORT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"differences {len(rows)} {dict(by_sev)} | additions {len(additions)}")
