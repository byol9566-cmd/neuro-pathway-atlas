# Codex 작업 검토: 섬유로 다발 → 중심선 변환기 (`pipeline/tracts/`)

검토일: 2026-10-04 (독립 리뷰, 읽기 전용)

## 결론: **채택 가능** (경미한 보완 권장)

과제 지시(`docs/codex-task.md`)와 실제 산출물을 대조한 결과, 구현·테스트·데이터·문서·금지사항 준수 모두 과제 요구를 충족한다. 해부학적 요구(CST 교차, ML의 VPL 종점)는 실제 데이터에서 **충족되지 않았지만**, Codex가 이를 숨기거나 임의로 고치지 않고 README에 정직하게 기록했다 — 이것이 과제가 명시적으로 요구한 태도(§검증: "맞지 않으면 그 사실을 그대로 적는다")이므로 결함이 아니라 준수 사항이다.

---

## findings (근거 포함)

### 1. README "완료 상태" 절
`pipeline/tracts/README.md:1-54`에 "완료 상태" 절이 맨 위에 있고, "되는 것"/"안 되는 것" 목록이 명확하다. 특히:
- CST 좌우 중심선이 **정중선을 건너지 않는다**(둘 다 z≈−51 mm에서 끝남)고 명시 (README.md:17).
- ML 좌우 중심선이 VPL에서 끝나지 않고 끝점이 z≈+74 mm, 기준점과 약 70 mm 떨어져 있다고 명시 (README.md:18).
- STT·MLF는 배포본에 없어 다른 아틀라스로 대체하지 않았다고 명시 (README.md:16).
- TT 미지원 명시 (README.md:15).

내용이 "완료 상태" 절 요구 형식(되는 것·안 되는 것·검증 표·열어 본 URL)을 모두 갖췄다.

### 2. 테스트 실행
과제가 지정한 그대로 저장소 루트에서 실행:
```
cd /Users/lim/orca/projects/project-5 && pipeline/.venv/bin/python -m pytest pipeline/tests -q
```
결과: **collection 단계에서 에러 2건으로 실패**(`ModuleNotFoundError: No module named 'atlas_pipeline'`, `test_meshing.py`·`test_sections.py`에서).

원인 확인: 이 두 테스트 파일은 Codex가 만든 것이 아니라 **기존에 커밋된 파일**(`git show HEAD:pipeline/tests/test_meshing.py` 확인됨, 커밋 `4587066`)이며, Codex의 새 테스트를 빼고 기존 파일만 실행해도 동일하게 `ModuleNotFoundError`가 난다 — 즉 **PYTHONPATH 미설정 시 루트에서 실행하면 실패하는 것은 Codex 이전부터 있던 저장소 구조 문제**이다. README는 이를 알고 있고 다음 해결책을 명시했다(README.md:146-152):
```
export PYTHONPATH="$PWD/pipeline${PYTHONPATH:+:$PYTHONPATH}"
pipeline/.venv/bin/python -m pytest pipeline/tests -q
```
이 환경변수를 설정하고 재실행하면:
```
32 passed in 0.65s
```
새 테스트 20개(`test_bundle_centerlines.py`) + 기존 12개(`test_meshing.py` + `test_sections.py`) = 32개, README의 "32 passed: 기존 12개 + 새 20개" 주장과 정확히 일치.

**중요**: 과제가 지정한 명령 그대로는(`PYTHONPATH` 없이) 실패한다. Codex는 이를 숨기지 않고 README에 적었지만, 과제 문구("`pipeline/.venv/bin/python -m pytest pipeline/tests -q` 통과")를 문자 그대로 만족시키지는 못한다. 다만 이 실패는 Codex가 만든 결함이 아니라 기존 저장소의 import 구조(패키지가 `pipeline/` 안에 있는데 루트에서 실행) 때문이며, Codex 자신의 새 테스트만 따로 돌리면 문제없이 20개 전부 통과한다.

### 3. `bundle_centerlines.py` 구현 검토 (전체 읽음, `/Users/lim/orca/projects/project-5/pipeline/tracts/bundle_centerlines.py`)
- **(a) TRK 읽기/RAS 변환**: `read_trk()` (L188-200)가 `nib.streamlines.load(..., lazy_load=True)`로 읽고, 헤더의 `voxel_to_rasmm` affine 유한성·특이성(determinant)을 검사한 뒤 `trk.tractogram.to_world(lazy=True)`로 RAS mm을 얻는다. 수동 LPS→RAS 반전을 추가하지 않고 nibabel의 공식 변환에 위임 — 과제가 요구한 방식과 일치. 테스트(`test_trk_header_affine_and_corner_offset_produce_ras_mm`, `test_bundle_centerlines.py:91-104`)가 3가지 affine(스케일+이동, LPS 반전, 축 순열)과 voxel corner→center 반오프셋까지 독립적으로 계산한 기대값과 비교해 통과함을 확인했다. 스텁이 아니다.
- **(b) 리샘플/방향 정렬/중앙값 중심선/반지름**: `resample_curve()`(L91-96, 호길이 비율로 N=100 선형보간), `align_directions()`(L99-122, 끝점 변위 SVD로 초기축 설정 후 반복적 평균-거리 기반 뒤집기), `summarize_bundle()`의 `center = np.median(aligned, axis=0)`·`radii = np.median(거리, axis=0)`(L154-155) — 모두 과제 기술과 일치하게 실제 구현되어 있으며 스텁이 아니다. 합성 데이터 테스트로 평균 오차 <1mm, 반전 50%에도 결과 불변임을 확인(테스트 통과).
- **(c) 교차 검출**: `first_crossing_z()`(L125-138)가 x=0 접촉은 무시하고 최초로 반대 부호가 된 점의 z를 반환. 다중 교차 중 첫 번째만 기록한다는 한계를 주석·README에 명시. 테스트로 엣지케이스(터치만 하는 경우, 교차 없는 경우) 확인됨.
- **(d) 출력 JSON 스키마**: `summarize_bundle()`(L173-181)의 결과 딕셔너리가 과제가 제시한 스키마(`id`, `atlasName`, `points`, `radiiMm`, `lengthMm`, `streamlines`, `decussationZmm`)와 정확히 일치하고, `main()`(L239)이 `source` 메타(`atlas`/`license`/`url`/`space`)를 포함해 과제 예시와 동일한 top-level 구조로 출력한다.
- **(e) 조용한 실패(silent fallback) 없음**: 입력 디렉터리 없음·TRK 없음·TT만 있음·중복 파일·유효 스트림라인 0개·step-mm 비정상 등 모든 비정상 경로가 `ValueError`를 던지며(L142, 152, 205, 208, 214, 219, 231-232), `main()`에서 이를 잡아 `parser.exit(2, ...)`로 종료한다(L245-246). 빈 결과를 조용히 반환하는 경로는 없음을 코드 전체에서 확인했다.

### 4. 실제 데이터 검증 (독립 재계산, Codex의 README/validate_centerlines.py 결과와 별도로 JSON을 직접 로드해 계산)
- `data/raw/hcp1065/`에 `hcp1065_avg_tracts_trk.zip`(587,869,457 bytes)이 실제로 존재하며, SHA-256을 재계산한 결과 `344aad4394f18b8926ed5e1bda911ad56e328c6cf75faa45e1302512ad779c67`로 SOURCES.md 기록과 **정확히 일치**. 하위 `association/`, `cerebellum/`, `projection/`에 `*.trk.gz` **34개**가 실제로 추출되어 있음(개수 확인: `find ... | wc -l` → 34).
- `data/derived/tracts/centerlines.json` (138,882 bytes) 로드 결과: **34개 다발, 총 1,770개 점, 유효 스트림라인 129,649개** — README claim과 일치.
- 주요 다발 좌표(직접 계산, README 표와 비교):
  - `cst-l`: 시작점 (-21.38, -18.62, +71.16) [z>50 충족], PLIC 기준(-20,-10,+5) 최근접점 (-21.56, -11.82, +4.10) 거리 **2.56mm**, z=-50 최근접점 (-3.49, -32.07, -50.81), 끝점 (-3.47, -32.12, -50.97), decussationZmm=null.
  - `cst-r`: 시작점 (+28.75, -17.16, +66.81) [충족], PLIC 최근접 거리 **3.78mm**, 끝점 (+3.53, -32.06, -50.94), decussationZmm=null.
  - `ml-l`: VPL 기준(-15,-20,+5) 최근접점 (-18.92, -20.64, +1.97) 거리 **5.00mm**, 실제 끝점 (-12.53, -34.56, **+74.06**) — VPL과 70.62mm 떨어짐.
  - `ml-r`: VPL 최근접 거리 **5.94mm**, 끝점 (+13.88, -30.16, **+74.53**) — VPL과 70.28mm.
  - 모두 **README 표(`README.md:70-80`)의 수치와 정확히 일치**. 불일치 없음.
  - CST는 시작(중심앞이랑, z>50)과 속섬유막 뒤다리 통과는 충족하지만, **피라미드 교차(정중선 넘기)는 발생하지 않음**(decussationZmm=null, 좌우 모두 z≈−51에서 끝남) — README가 이를 그대로 밝혔다.
  - ML은 VPL 근접점은 5~6mm 이내로 지나가지만 **실제 종점이 VPL이 아니라 반대쪽(z≈+74, 즉 상행 경로의 다른 쪽 끝)이며 교차도 검출되지 않음** — README가 이를 그대로 밝혔다.
- `rejectedStreamlines` 필드가 어떤 다발에도 없음 → README의 "제외된 스트림라인 없음" 주장과 일치.
- `validate_centerlines.py`가 README의 표를 그대로 생성하는 스크립트임을 확인했다(수동 수치 입력이 아니라 프로그램 생성 — 오기 위험이 낮음).

### 5. 라이선스 (SOURCES.md)
`pipeline/tracts/SOURCES.md:8`에 "라이선스: CC BY-SA 4.0 (원문 Population-Averaged 섹션)"과 출처 URL `https://brain.labsolver.org/hcp_trk_atlas.html`이 명시되어 있다. README에도 라이선스 표기 예시 문구와 HCP Data Use Terms 링크, CC BY-SA 4.0 링크가 포함되어 있다(README.md:234-246). 요구사항 충족.

### 6. 금지 항목 준수 확인
```
git status --short
 M pipeline/atlas_pipeline/build.py
 M pipeline/atlas_pipeline/fetch.py
?? pipeline/tests/test_bundle_centerlines.py
?? pipeline/tracts/
(기타 docs/*, pipeline/vhp_*.py, pipeline/integrate_vhp.py 등 — 이번 과제와 무관한 기존 미추적 파일)

git diff --stat
 pipeline/atlas_pipeline/build.py | 25 ++++++++++++++++++++
 pipeline/atlas_pipeline/fetch.py | 50 ++++++++++++++++++++++++++++++++++++++--
 2 files changed, 73 insertions(+), 2 deletions(-)
```
`pipeline/atlas_pipeline/build.py`와 `fetch.py`의 변경은 지시대로 **메인 세션이 오늘 만든 미커밋 변경**으로 Codex 소관이 아니다(과제 지시사항에 명시된 바와 일치하며, 이 리뷰는 그 변경을 Codex 책임으로 돌리지 않음). `content/`, `viewer/`, 기존 테스트 파일에는 어떤 변경도 없다. `git log`에 Codex가 만든 새 커밋은 없다(최근 커밋 전부 기존 작업). 금지 항목을 준수했다.

---

## 꼭 고쳐야 할 것

- 과제가 지정한 정확한 pytest 명령(`cd .../project-5 && pipeline/.venv/bin/python -m pytest pipeline/tests -q`, PYTHONPATH 없이)이 **collection 단계에서 실패**한다. 이는 Codex 이전부터 있던 기존 테스트의 import 구조 문제이지만, 과제 문구를 문자 그대로는 만족하지 못한 채 README의 "환경변수 설정 후 실행" 안내로 대체했다. 사람이 이 저장소의 pytest 실행 규칙(conftest.py 또는 pytest.ini로 `pipeline`을 rootdir에 추가하는 것 등)을 전역적으로 정리할지 결정하고, 최소한 과제 발행자 쪽에서 "이 저장소는 PYTHONPATH 설정이 필요하다"는 점을 인지해야 한다. (Codex의 새 코드 자체 문제는 아님.)

## 있으면 좋은 것

- CST·ML이 해부학적 목표(교차·VPL 종점)를 만족하지 못하는 원인(예: HCP1065 다발이 뇌줄기 이하까지 완전히 포함하지 않을 가능성, 중심선 대표화 과정에서 분기 다발이 뭉개지는 효과 등)에 대한 한 줄짜리 가설이라도 README에 추가하면 다음 작업자가 원인 조사 시간을 아낄 수 있음 (현재는 "그대로 보존했다"는 사실만 기록).
- `decussationZmm`가 거의 모든 다발에서 `null`인데(MCP만 예외), 이 필드가 실제로 유용하게 작동하는 사례가 적다는 점을 README 통계표 근처에 한 줄 요약해주면 좋음(현재도 추론 가능하지만 명시적 요약은 없음).
- SOURCES.md의 "ZIP 내용과 실제 선택" 표에 있는 `C_FP_R` 긴 이름 불일치(XLSX 원문이 `_L`로 끝남) 처리 방식은 잘 기록되어 있으나, 이런 원본 메타데이터 오류가 또 있을 가능성을 체크리스트화해두면 재현성에 도움.

---

## 최종 메시지

**검증 결론: 채택 가능.** 가장 중요한 세 가지: (1) `bundle_centerlines.py`는 TRK→RAS 변환, 리샘플, 방향정렬, 중앙값 중심선·반지름, 교차 검출을 모두 실제로 구현했고 스텁·조용한 실패가 없다 — 테스트(32개, 신규 20개)도 통과한다. (2) 과제가 지정한 정확한 pytest 명령은 PYTHONPATH 없이는 collection 에러로 실패하지만, 이는 Codex 이전부터 있던 기존 저장소 구조 문제이며 Codex가 README에 해결법을 투명하게 적어두었다. (3) 실제 데이터(34개 다발, 1,770점)를 독립적으로 재계산한 결과 README 표의 모든 좌표·거리·decussationZmm 수치가 정확히 일치했고, CST 교차 미발생·ML의 VPL 비종점이라는 해부학적 불일치를 Codex가 고치려 하지 않고 과제 지시대로 그대로 기록했다 — 이는 결함이 아니라 과제 요구사항 준수다.
