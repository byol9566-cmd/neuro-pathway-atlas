# Codex 과제: 섬유로 다발 → 경로용 중심선 변환기 (2026-10-04)

이 파일 전체를 Codex에 넣으면 된다. 저장소: `/Users/lim/orca/projects/project-5` (브랜치 `poc`). **`pipeline/tracts/` 아래 새 파일과 `pipeline/tests/`의 새 테스트만 만들 것. `content/`, `viewer/`, 기존 `pipeline/atlas_pipeline/`은 수정 금지** (다른 작업자가 동시에 편집 중).

---

## 배경
웹 3D 신경해부학 학습 도구. 경로(예: 겉질척수로)를 재생할 때 지금은 구조의 중심점을 직선으로 잇고, 신경로 메시가 있는 구간만 그 메시의 중심선을 따른다(`viewer/public/data/manifest.json`의 `meshes[].centerline`: RAS mm 좌표의 점 배열). 실제 섬유 주행(속섬유막 → 대뇌다리 → 다리뇌 → 피라미드 → 교차 → 가쪽 척수)을 따라가게 하려면, 확산 MRI 트랙토그래피 아틀라스의 다발을 **중심선 + 반지름**으로 바꾼 데이터가 필요하다.

## 데이터
- **HCP1065 population-averaged tractography atlas** (Yeh, DSI Studio). 라이선스 CC BY-SA 4.0 (https://brain.labsolver.org/hcp_trk_atlas.html 에 명시). 공간: ICBM 2009a Nonlinear Asymmetric(= MNI152 2009 계열, 우리 좌표계와 호환).
- 받을 것: "Population-averaged tractography atlas"의 **TRK 또는 TT 형식 다발**(tract 이름별 파일). 다운로드 전 페이지의 정확한 파일 목록·크기를 `pipeline/tracts/SOURCES.md`에 기록하고 받아라. 저장 위치 `data/raw/hcp1065/` (gitignore됨). 수 GB면 필요한 다발만.
- 우선 다발(이름은 아틀라스 표기를 그대로 적어 둘 것): Corticospinal tract(좌/우), Corticobulbar(있으면), Medial lemniscus, Spinothalamic tract, Superior/Middle/Inferior cerebellar peduncle, Medial longitudinal fasciculus, Optic radiation, Fornix, Cingulum, Arcuate fasciculus, Uncinate fasciculus, Corticopontine tracts.

## 만들 것
`pipeline/tracts/bundle_centerlines.py` — CLI:
```
pipeline/.venv/bin/python -m pipeline.tracts.bundle_centerlines --in data/raw/hcp1065 --out data/derived/tracts/centerlines.json [--tracts CST_L CST_R ...] [--step-mm 2]
```
1. TRK/TT 파일을 읽는다. TRK는 `nibabel.streamlines`(venv에 nibabel 있음) 사용; TT(DSI Studio 전용)는 읽을 수 없으면 TRK만 지원하고 README에 적는다. 좌표를 **RAS mm(MNI)** 로 통일(TRK는 voxmm→RAS 변환에 헤더의 affine 필요; nibabel이 처리하지만 결과가 RAS인지 테스트로 확인).
2. 다발마다 **대표 중심선**을 구한다: 스트림라인을 길이로 정규화해 N=100점으로 리샘플 → 방향을 맞춤(양 끝 평균점 기준으로 뒤집기) → 점별 중앙값(median)으로 중심선 → `--step-mm` 간격으로 다시 샘플. 각 점에서 다발 단면 반지름 = 그 점의 스트림라인 점들의 거리 중앙값(mm).
3. **교차 처리**: 겉질척수로처럼 정중선을 건너는 다발은 중심선이 그대로 건너야 한다(좌·우 다발을 따로 두되, 교차점의 z(mm)을 메타에 기록: 중심선에서 x의 부호가 바뀌는 첫 점).
4. 출력 JSON:
```json
{ "source": {"atlas": "HCP1065", "license": "CC BY-SA 4.0", "url": "https://brain.labsolver.org/hcp_trk_atlas.html", "space": "ICBM 2009a nonlinear asym"},
  "tracts": [ { "id": "cst-l", "atlasName": "Corticospinal_Tract_L", "points": [[x,y,z],...], "radiiMm": [..], "lengthMm": 0, "streamlines": 0, "decussationZmm": null } ] }
```
5. `pipeline/tracts/README.md`: 사용법, 변환 방법, 검증 결과(아래), 라이선스 표기 문구(CC BY-SA, HCP 데이터 이용약관 링크).

## 검증 (반드시)
- `pipeline/tests/test_bundle_centerlines.py`: (a) 합성 스트림라인(직선·S자 곡선 100개, 노이즈)에서 중심선이 진짜 곡선과 평균 1mm 이내인지; (b) 뒤집힌 스트림라인이 섞여도 방향 정렬이 되는지; (c) 좌표 변환이 RAS를 유지하는지(헤더 affine을 바꾼 TRK를 만들어 확인). `pipeline/.venv/bin/python -m pytest pipeline/tests -q` 통과.
- 실제 데이터로: 겉질척수로 중심선이 (i) 중심앞이랑 근처(z>+50)에서 시작해 (ii) 속섬유막 뒤다리(x≈±20, y≈−10, z≈+5 근처)를 지나 (iii) 피라미드(z≈−50 근처, x≈±4)에 이르는지 좌표를 README에 표로 적어라. 안쪽섬유띠는 숨뇌에서 교차한 뒤 시상 VPL(x≈±15, y≈−20, z≈+5)에 끝나야 한다. **맞지 않으면 그 사실을 그대로 적는다**(고치려 하지 말고).
- 결과 파일 크기, 다발 수, 각 다발의 길이·점 수를 README 표로.

## 금지
- `content/`·`viewer/`·`pipeline/atlas_pipeline/` 수정, 기존 테스트 변경, 커밋·푸시(커밋은 사람이 한다), `data/raw/` 외 위치에 대용량 저장, 라이선스가 CC BY-SA가 아닌 다른 트랙토그래피 아틀라스 사용(XTRACT·JHU는 비상업이라 금지).

## 끝나면
`pipeline/tracts/README.md` 맨 위에 "완료 상태" 절: 되는 것·안 되는 것·검증 표·열어 본 URL. 그 뒤 `git status`만 출력하고 멈춘다.
