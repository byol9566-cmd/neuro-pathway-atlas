# 구조 3D 확장 (2026-10-03)

성연 데이터셋(2026-10-02)의 새 구조 349개 중 **위치와 크기를 정할 수 있는 것은 모두 3D로 만든다**는 사용자 기준에 따라 `content/structures.json`을 53개 → 188개(빌드 결과 187개)로 늘렸다.

## 출처별

| 방식 | 개수 | 내용 |
|---|---|---|
| NextBrain 라벨 (CC0) | 95 | `label-mapping.json`의 high·medium 전부 + low 중 겉질 근사(FEF·LIP·PIVC·V4·perirhinal). 겉질 기능영역은 Desikan–Killiany 이랑 라벨로 **근사**(`approxArea: true`). |
| Harvard AAN v2 (CC0) | 1 (+기존 2) | `bs-ppt-ldt` = LDTg+PTg 좌/우. 통합 볼륨 `data/raw/aan/AAN_Brainstem_MNI152_1mm_v2p0.nii`(핵 10개)로 전환 — 좌우 분리 핵은 73xx/74xx 라벨만 채워져 있음. |
| MNI 좌표 타원체 | 39 | `placeholders.json`. 눈·속귀·뇌하수체·솔방울샘·신경절·척수 분절·RVLM 등. **전부 추정 좌표**(문헌 좌표 아님). 에이전트 초안 중 28개를 메인 세션이 보정(눈·속귀·삼차신경절이 10~15mm 어긋나 있었음). 뷰어에 "근사"로 표시. |

- 극소 라벨(에딩거-베스트팔핵 0.1mm³ 등)은 빌드가 자동으로 작은 구 자리표시로 대체(`build.py`, `PLACEHOLDER_BELOW_MM3`).
- 제외: 세포 수준 66개(공간 구조 아님), 근육·샘 32개, 말초신경 경로 24개, 분포형 수용기 등. `bs-mntb`(사다리체핵)는 라벨 복셀이 2개뿐이라 빌드에서 제외.
- 별칭(`aliases.json`): 라벨 집합이 기존 구조와 같은 6개(S1의 BA3b·1·2 → 중심뒤이랑, 고립로핵 앞·뒤부분 → 고립로핵, perirhinal → 해마곁이랑). 경로 데이터 반영 때 이 id들을 기존 id로 치환해야 함.
- 라벨 집합이 기존 구조의 부분집합인 것은 `subpartOf`로 표시하고 따로 그림(SNc/SNr ⊂ 흑색질 등).

## 뷰어 쪽 처리
- 겉질 영역 26개는 같은 이랑 위에 겹치므로 **선택 전에는 외곽선(고스트)**으로만 그림(`isOutline`).
- 척수(43cm)는 안개 바다 아래로 내려가므로 바다 높이 아래는 페이드(`sceneFloor`, 고스트 셰이더).
- 사이드바는 멤버 14개 초과 그룹을 접힌 상태로 시작, 선택·검색 시 자동 펼침.

## 재현
```
pipeline/.venv/bin/python pipeline/integrate_structures.py --write   # content/structures.json 재생성 (기존 53개 파일에서 시작해야 함: git checkout content/structures.json)
pipeline/.venv/bin/python -m atlas_pipeline.build                      # 메시·manifest·단면
```
