# 신경경로 3D 아틀라스 — 시제품

신경경로를 고르면 참여하는 뇌 구조만 남고 나머지는 투명해지는 웹 3D 학습 도구의 시제품(PoC).
배경 조사와 데이터 출처·라이선스는 [`docs/research-sources.md`](docs/research-sources.md) 참고.

> 경로 설명과 한국어 용어는 **검수 전 초안**입니다. 학습 자료로 쓰지 마세요.

## 구성

```
content/     구조 정의(structures.json)와 경로 정의(pathways.json) — 도메인 담당자가 편집하는 곳
pipeline/    Python: 아틀라스 라벨 볼륨 → 구조별 메시(GLB) + manifest.json
viewer/      Vite + TypeScript + three.js 뷰어
docs/        조사 문서, NextBrain 실측 라벨 목록
data/        내려받은 아틀라스 원본 (git 제외)
```

## 실행

```bash
# 1) 메시 만들기 (최초 1회, 약 35 MB 다운로드 + 15초 빌드)
cd pipeline
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m atlas_pipeline.fetch     # NextBrain 라벨 볼륨(zip에서 필요한 파일만) + Harvard AAN
(cd ../viewer && npm install)                # gltf-transform(meshopt 압축)이 여기서 설치됨
.venv/bin/python -m atlas_pipeline.build     # -> viewer/public/data/{atlas.glb, manifest.json, sections/axial/*.png}

# 2) 뷰어
cd ../viewer
npm run dev
```

## 테스트

```bash
cd pipeline && .venv/bin/python -m pytest          # 메시 처리 단위 테스트
cd viewer   && npm test                            # 경로 로직 + content 무결성
cd viewer   && npx playwright install chromium && npm run e2e   # 브라우저 시나리오
```

## 데이터 규모 (2026-10-27)

- 구조 313개(`content/structures.json`): NextBrain 라벨 145, Harvard AAN 핵 2, HCP1065 신경로 27, BodyParts3D 55(몸 윤곽·뼈·근육·내장),
  Visible Human 9(눈·뇌하수체·척수), 기하 모형 71(속귀·신경절·말초신경·척수 분절 등), MNI 좌표 타원체 자리표시 4(그물체 핵 — 화면에 "근사" 표시).
  만든 방법은 `docs/data/structures-3d/README.md`.
- 경로·기전 247개(`content/pathways.json`, `pipeline/integrate_pathways.py`로 성연 데이터셋에서 변환): 197개는 3D 구조가 켜지고 50개는 설명만.
  전부 `reviewStatus: draft` — 설명 문장은 공개 문헌 근거(`docs/data/pathway-evidence/`)로 다시 쓰는 중.
  `pipeline/content_lint.py`가 단계의 `missing` 문구와 `has3d`를 구조 목록·manifest에 맞춰 정리한다(`pipeline/tests/test_content.py`).

## 화면 구성

3D가 화면 전체를 차지하고 유리 패널이 그 위에 떠 있다(디자인 방향과 근거: `docs/design-direction.md`).
배경은 three.js 안에서 그리는 흑백 은빛 안개 바다(GPU 파동 시뮬레이션, 입자는 뇌 아래에만). 첫 방문 때는
오프닝 영상(`viewer/public/media/intro.mp4`, 10초)에 이어 입자가 모여 뇌가 되는 등장 연출이 재생되며 클릭이나
키 입력으로 건너뛸 수 있고, `prefers-reduced-motion`이면 영상·연출·배경 움직임 없이 바로 표시된다.
단면 창은 헤더를 끌어 옮길 수 있고(더블클릭하면 제자리), 열린 패널을 피해 뇌가 빈 공간으로 옮겨진다.
단축키: `/` 검색 · `← →` 경로 단계 · `Space` 재생 · `Esc` 나가기 · 툴바의 `?`에 전체 목록.

## 가로 단면 패널

툴바의 **단면** 버튼. NextBrain 라벨 볼륨의 가로 단면(평면 해상도 0.2 mm, 높이 0.4 mm 간격, 393장)을
라벨 id가 담긴 PNG로 뽑아 두고 필요한 장만 불러온다(전체 7.5 MB). 휠: 높이 이동(Shift: 5장씩),
Ctrl+휠 또는 +/−: 확대, 드래그: 이동, 클릭: 구조 선택. 구조나 경로를 고르면 그 높이로 따라간다.
"3D 자르기"를 켜면 3D에서도 그 높이 위쪽이 잘려 나간다. 메시로 만들지 않은 라벨(333개 전부)도
단면에서는 보이고, 마우스를 올리면 Allen 구조명이 나온다. 방사선학 관례(앞이 위, 환자의 왼쪽이 화면 오른쪽).

## 검수 템플릿

`python -m atlas_pipeline.review_template` → `docs/handover-seongyeon/검수시트/` (CSV 5개 + `0_안내.txt`).
현재 content를 미리 채운 구조/경로/단계/병변 시트 + NextBrain 라벨 333개 참고 시트. 계정 없이 Numbers·구글 시트 등
어디서나 열린다. `--xlsx`를 붙이면 색·드롭다운이 있는 엑셀 파일 하나로 뽑는다.

## content 편집

- **구조 추가**: `content/structures.json`에 항목을 넣고 빌드를 다시 돌린다. `source.labels`는 NextBrain 라벨 id
  (`docs/data/nextbrain-argmax-labels.tsv`에서 이름·부피 확인). 여러 라벨을 적으면 하나의 메시로 합쳐진다.
  - `"tract": true` / `"centerline": true` — 경로선이 무게중심 대신 구조의 중심선을 따라간다.
  - `"placeholder": { "radiiMm": [x, y, z] }` — 라벨이 6 mm³ 미만이면 라벨 위치에 타원체를 대신 놓는다(뷰어에 "근사"로 표시).
- **경로 추가**: `content/pathways.json`. 각 단계의 `structures[].side`는 기시쪽 기준 `ipsi`/`contra`이고,
  뷰어에서 기시쪽(좌/우)을 바꾸면 실제 좌우가 뒤집힌다. 메시가 없는 단계는 `structures: []` + `missing` 설명.

## 데이터와 라이선스

`pipeline/atlas_pipeline/build.py`의 `ATTRIBUTION` 목록(빌드 때 `manifest.json`의 `attribution`으로 그대로 나감)과 같은 순서다.

| atlas | 출처 | 이 프로젝트에서 쓰는 곳 | 라이선스 | 우리가 지킬 것 |
|---|---|---|---|---|
| `nextbrain` | NextBrain (Casamitjana et al., Nature 2025) — https://doi.org/10.5522/04/24243835 | 대뇌겉질·시상·바닥핵·둘레계통·뇌줄기 핵·소뇌·시상하부, 일부 신경로와 뇌 윤곽 (145개) | CC0 1.0 | 의무 없음(출처 표기는 관행으로 유지) |
| `aan` | Harvard Ascending Arousal Network Atlas v2.0 (Edlow et al.) — https://zenodo.org/records/8161638 | 등쪽솔기핵, 다리뇌 콜린성핵군(PPT/LDT) (2개) | CC0 1.0 | 의무 없음(출처 표기는 관행으로 유지) |
| `vhp` | Visible Human Project, U.S. NLM — https://www.nlm.nih.gov/research/visible/visible_human.html | 안구·수정체·망막·각막, 뇌하수체, 척수 (9개; SAM으로 분할 후 MNI 정합) | NLM: 라이선스 불필요 | 의무 없음(NLM 출처 표기 권장) |
| `model` | 기하 모형 (이 프로젝트에서 교과서 치수로 작성) | 속귀·신경절·말초신경·척수 분절·경동맥굴 등 (71개) | 프로젝트 자체 제작 | 없음 |
| `bp3d` | BodyParts3D, © DBCLS — https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html | 몸 윤곽·뼈·근육·내장 (55개, 폴리곤 축소 후 MNI에 맞춤) | CC BY 4.0 | 저작자 표시(© The Database Center for Life Science, CC BY 4.0)와 변경 사실 표기 |
| `hcp1065` | HCP1065 tractography atlas (Yeh, DSI Studio) — https://brain.labsolver.org/hcp_trk_atlas.html | 신경로 중심선·튜브 메시 (27개) | CC BY-SA 4.0 | 저작자 표시 + 동일조건변경허락: 이 데이터로 만든 신경로 메시도 CC BY-SA 4.0으로 배포 |
| `mni` | MNI152 좌표 기반 타원체 자리표시 | RVLM·CVLM·거대세포그물핵·피개그물핵 (4개, 공개된 좌표 세트가 생길 때까지 임시) | 프로젝트 자체 제작 (좌표: 공개 문헌) | 없음(좌표 출처 문헌 표기) |

HCP1065에서 만든 신경로 메시는 CC BY-SA 4.0이고 지금은 나머지 메시와 같은 `atlas.glb` 한 파일에 묶여 있으므로, 그 합본 파일은 BY-SA 조건으로 배포되는 셈이다 — 신경로를 별도 GLB로 분리할지는 아직 결정 전이다.

NextBrain은 왼쪽 반구 아틀라스라서 오른쪽 구조는 좌우 반전으로 만든다.
