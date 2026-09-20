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

- NextBrain (Casamitjana et al., Nature 2025) — CC0 — https://doi.org/10.5522/04/24243835
- Harvard Ascending Arousal Network Atlas v2.0 (Edlow et al.) — CC0 — https://zenodo.org/records/8161638

NextBrain은 왼쪽 반구 아틀라스라서 오른쪽 구조는 좌우 반전으로 만든다.
