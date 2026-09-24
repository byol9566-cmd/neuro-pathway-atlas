#!/usr/bin/env python3
"""Assemble the reviewer's sheets (검수시트2) from the drafting agents' JSON.

    pipeline/.venv/bin/python docs/data/pathway-evidence/make_review_sheets.py

Reads merged/draft-*.json and writes docs/handover-seongyeon/검수시트2/*.csv (utf-8-sig so Excel and
Numbers open them with Hangul intact). The columns mirror 검수시트/ so the reviewer sees one format.
Also validates every structure id against content/structures.json and reports the ones it dropped.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
OUT = ROOT / "docs" / "handover-seongyeon" / "검수시트2"
VALID = {s["id"] for s in json.loads((ROOT / "content" / "structures.json").read_text(encoding="utf-8"))["structures"]}


def write(name, header, rows):
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def main():
    OUT.mkdir(exist_ok=True)
    pathways = []
    for f in sorted(HERE.glob("merged/draft-*.json")):
        pathways += json.loads(f.read_text(encoding="utf-8"))["pathways"]
    bad_ids = {}
    rows_p, rows_s, rows_l, rows_c = [], [], [], []
    for p in pathways:
        rows_p.append([p["id"], p.get("name_ko", ""), p.get("name_en", ""), p.get("category_ko", ""), p.get("summary_ko", ""), p.get("origin_ko", ""), "", "", ""])
        for s in p.get("steps", []):
            ids = [i for i in s.get("structure_ids", []) if i]
            good = [i for i in ids if i in VALID]
            for i in ids:
                if i not in VALID:
                    bad_ids.setdefault(i, []).append(f"{p['id']}#{s.get('order')}")
            rows_s.append([p["id"], s.get("order"), s.get("title_ko", ""), s.get("neuronOrder") or "", ", ".join(good), s.get("structure_names_ko", ""),
                           s.get("side", ""), "예" if s.get("decussation") else "", s.get("decussation_where_ko", ""), s.get("neurotransmitter_ko", ""),
                           s.get("description_ko", ""), s.get("missing_ko", ""), s.get("sources", ""), "", ""])
        for l in p.get("lesions", []):
            rows_l.append([p["id"], l.get("site_ko", ""), l.get("deficit_ko", ""), l.get("side_ko", ""), "", l.get("sources", ""), "", ""])
        for n, c in enumerate(p.get("conflicts", []), 1):
            pos = c.get("positions", [])[:4]
            cells = []
            for i in range(4):
                if i < len(pos):
                    cells.append(f"[{pos[i].get('grade', '?')}] {pos[i].get('source', '')}: {pos[i].get('summary_ko', '')}")
                else:
                    cells.append("")
            rows_c.append([p["id"], f"{p['id']}-c{n}", c.get("issue_ko", ""), *cells, "", ""])
    write("2_경로.csv", ["경로_id", "한국어명", "영어명", "분류", "한줄요약", "기시쪽_설명", "중요도", "검수", "수정안·메모"], rows_p)
    write("3_단계.csv", ["경로_id", "순서", "단계_제목", "뉴런_차수", "강조할_구조(구조_id)", "구조_이름(참고)", "좌우", "여기서_교차", "교차_위치", "신경전달물질", "설명", "메시_없는_구조", "출처", "검수", "수정안"], rows_s)
    write("4_병변.csv", ["경로_id", "병변_위치", "증상", "증상_쪽", "관련_증후군", "출처", "검수", "수정안"], rows_l)
    write("6_판정.csv", ["경로_id", "쟁점_id", "쟁점", "입장1", "입장2", "입장3", "입장4", "선택(1/2/3/4/둘다/보류)", "메모"], rows_c)
    if bad_ids:
        print("dropped unknown structure ids:", json.dumps(bad_ids, ensure_ascii=False))


if __name__ == "__main__":
    main()
