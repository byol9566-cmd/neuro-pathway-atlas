"""Emit reproducible Markdown checks for generated centerlines, without editing them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .bundle_centerlines import first_crossing_z


def xyz(point) -> str:
    return "(" + ", ".join(f"{value:+.2f}" for value in point) + ")"


def report(path: Path) -> str:
    doc = json.loads(path.read_text())
    tracts = doc["tracts"]
    ids = set()
    for tract in tracts:
        points = np.asarray(tract["points"])
        radii = np.asarray(tract["radiiMm"])
        if points.ndim != 2 or points.shape[1] != 3 or len(points) < 2:
            raise ValueError(f"Bad point shape: {tract['id']}")
        if radii.shape != (len(points),) or not np.isfinite(points).all() or not np.isfinite(radii).all() or (radii < 0).any():
            raise ValueError(f"Bad coordinates/radii: {tract['id']}")
        length = np.linalg.norm(np.diff(points, axis=0), axis=1).sum()
        if not np.isfinite(tract["lengthMm"]) or length <= 0 or not np.isclose(length, tract["lengthMm"]):
            raise ValueError(f"Bad length: {tract['id']}")
        if tract["streamlines"] <= 0 or tract["id"] in ids:
            raise ValueError(f"Bad count/duplicate: {tract['id']}")
        if first_crossing_z(points) != tract["decussationZmm"]:
            raise ValueError(f"Bad crossing metadata: {tract['id']}")
        ids.add(tract["id"])

    lines = [
        f"결과: `{path}` — **{path.stat().st_size:,} bytes**, **{len(tracts)}개 다발**, "
        f"총 **{sum(len(t['points']) for t in tracts):,}개 점**, "
        f"입력 **{sum(t['streamlines'] for t in tracts):,}개 유효 스트림라인**.",
        "", "좌표·반지름 유한성, 점/반지름 수, 길이, ID 중복, 교차 메타 검증 통과.", "",
        "### CST 경유 좌표", "",
        "좌표 단위는 RAS mm. 속섬유막은 과제의 기준점까지 가장 가까운 **출력 점**을 선택했다. "
        "피라미드는 과제에 y 기준이 없으므로 z=−50에 가장 가까운 출력 점을 표시한다. "
        "좌표 근접성만 확인했으며 중심앞이랑/핵의 실제 분할 영역과 중첩 검증은 수행하지 않았다.", "",
        "| 다발 | 시작점 (z>50) | 속섬유막 기준 (±20, −10, +5) 최근접점 | 기준과 거리 mm | z=−50 최근접점 | 끝점 | 첫 x 부호 변경 z |",
        "|---|---|---|---:|---|---|---|",
    ]
    by_id = {t["id"]: t for t in tracts}
    for key, sign in (("cst-l", -1), ("cst-r", 1)):
        if key not in by_id:
            lines.append(f"| {key} | 데이터 없음 | — | — | — | — | — |")
            continue
        tract = by_id[key]
        points = np.asarray(tract["points"])
        distances = np.linalg.norm(points - [20 * sign, -10, 5], axis=1)
        near = points[distances.argmin()]
        pyramid = points[np.abs(points[:, 2] + 50).argmin()]
        lines.append(f"| {key} | {xyz(points[0])} ({'충족' if points[0, 2] > 50 else '불충족'}) | {xyz(near)} | {distances.min():.2f} | {xyz(pyramid)} | {xyz(points[-1])} | {tract['decussationZmm']} |")
    lines += ["", "### ML 종점과 교차", "",
              "VPL 비교 기준은 과제에 주어진 (±15, −20, +5)이다. 최근접점과 **실제 종점**을 별도로 보고한다.", "",
              "| 다발 | 시작점 | VPL 기준 최근접점 | 최근접 거리 mm | 실제 끝점 | 끝점↔VPL 거리 mm | 첫 x 부호 변경 z |",
              "|---|---|---|---:|---|---:|---|"]
    for key, sign in (("ml-l", -1), ("ml-r", 1)):
        if key not in by_id:
            lines.append(f"| {key} | 데이터 없음 | — | — | — | — | — |")
            continue
        tract = by_id[key]
        points = np.asarray(tract["points"])
        distances = np.linalg.norm(points - [15 * sign, -20, 5], axis=1)
        lines.append(f"| {key} | {xyz(points[0])} | {xyz(points[distances.argmin()])} | {distances.min():.2f} | {xyz(points[-1])} | {distances[-1]:.2f} | {tract['decussationZmm']} |")
    lines += ["", "### 다발별 출력 통계", "",
              "atlasName은 ZIP의 파일 약어를 그대로 사용한다. 긴 이름 대응은 SOURCES.md에 있다. `null`은 출력 중심선에서 x 부호 변경을 찾지 못했다는 뜻이다.", "",
              "| id | atlasName | 스트림라인 수 | 길이 mm | 점 수 | decussationZmm |",
              "|---|---|---:|---:|---:|---:|"]
    for t in tracts:
        crossing = "null" if t["decussationZmm"] is None else f"{t['decussationZmm']:.2f}"
        lines.append(f"| {t['id']} | {t['atlasName']} | {t['streamlines']:,} | {t['lengthMm']:.2f} | {len(t['points'])} | {crossing} |")
    return "\n".join(lines).replace("| None |", "| null |") + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    print(report(args.input), end="")


if __name__ == "__main__":
    main()
