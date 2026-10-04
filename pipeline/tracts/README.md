# 완료 상태

2026-10-04: **변환기 구현 및 실제 데이터 변환 완료. 해부학적 요구는 일부 불충족.**

## 되는 것

- HCP1065 공식 TRK 아카이브의 우선 다발 **34개**, **129,649개 스트림라인**을 중심선·반지름으로 변환했다.
- 결과: `data/derived/tracts/centerlines.json`, **138,882 bytes**, **1,770개 점**, 간격 옵션 2 mm.
- `.trk`와 `.trk.gz`를 읽으며 헤더에 따른 RAS+ mm 변환, N=100 호길이 리샘플, 방향 정렬, 점별 중앙값, 반지름 및 교차 메타를 구현했다.
- CST/CBT, ML, ICP, MCP, SCP, OR, Fornix, Cingulum의 5개 하위 묶음, AF, UF, Corticopontine의 3개 하위 묶음을 처리했다.
- 파일 선택·실패 처리 및 실제 결과 통계/좌표 검증 도구를 포함한다. 데이터는 기존 `.gitignore`의 `/data/` 규칙에 따라 버전 관리에서 제외된다.

## 안 되는 것 / 실제 데이터의 불일치

- **TT/TT.GZ는 지원하지 않는다.** 공식 TRK 배포본을 사용한다.
- **STT(척수시상로), MLF(안쪽세로다발)는 받은 ZIP 목록에 없다.** 다른 아틀라스로 대체하지 않았다. `MdLF`(middle longitudinal fasciculus)는 MLF와 다른 다발이며 대체재로 선택하지 않았다.
- **CST 좌우 중심선은 정중선을 건너지 않는다.** 둘 다 z≈−51 mm에서 끝나므로, 피라미드 교차 및 반대쪽 가쪽 척수까지 이어지는 경로는 이 결과로 제공하지 못한다.
- **ML 좌우 중심선도 정중선 교차가 없고 VPL에서 끝나지 않는다.** VPL 기준점 가까이를 지나지만 끝점은 z≈+74 mm이며, 기준점과 약 70 mm 떨어져 있다. 과제 지시에 따라 잘라내기·좌우 반전·가상 교차 추가 없이 그대로 보존했다.
- MCP와 SCP는 배포본에서 각각 단일 파일이다. 임의의 좌우 분리나 미제공 구간 생성을 하지 않았다. SCP 결과에서도 x 부호 변경은 검출되지 않았다.
- 좌표 근접성을 확인했으며, 별도 피질/핵 분할과의 중첩·정합 검증은 하지 않았다. RAS 축 일치 및 동일 MNI 계열이라는 사실만으로 다른 템플릿과의 정밀 정합을 보장하지 않는다.
- 대표 중심선은 분기·부채꼴 다발을 하나로 요약한다. 실제 단일 축삭이나 모든 분기를 대표하는 신경 회로로 해석하면 안 된다.

## 검증 요약

| 검증 | 결과 |
|---|---|
| 합성 직선 100개, 좌표 노이즈 표준편차 0.35 mm | 평균 오차 **0.0587 mm**, 최대 **0.1189 mm** |
| 합성 S자 100개, 동일 노이즈 | 평균 오차 **0.0897 mm**, 최대 **0.1694 mm** |
| 50% 역방향 + 입력 순서 섞기 | 동일 중심선/반지름, 허용 오차 1e−8 mm |
| 알려진 반지름 3 mm의 직선 다발 | 반지름 3 mm, 길이 11 mm, 간격 2 mm 및 마지막 1 mm 확인 |
| TRK 헤더 변환 | 서로 다른 스케일·이동, LPS 반전, 축 순열 3개 affine에서 RAS 좌표 확인; gzip도 확인 |
| TRK voxel corner→center | 수동으로 작성한 voxmm payload의 반 voxel 오프셋을 독립적인 affine 계산과 비교 |
| 교차 | 합성 교차 보존, 첫 반대 부호 점의 z, x=0에 닿기만 하는 경우 제외 |
| 오류 입력 | 잘못된 간격, 퇴화/비유한 스트림라인, 누락 다발, 중복 파일, TT 단독 입력 처리 확인 |
| CLI 출력 | ID/atlasName/JSON 필드 확인, 실패 시 기존 결과 보존 |
| 전체 테스트 | **32 passed**: 기존 12개 + 새 20개 |
| 실제 JSON | 유한 좌표·반지름, 길이, 점 수, ID 중복, 교차 메타 확인 통과 |
| 실제 해부학 | CST 경유 기준에 근접. **CST 교차/척수 및 ML 교차/VPL 종점 요구 불충족** |

합성 오차는 참 곡선과 출력 곡선을 각각 호길이 비율 500점으로 재표본화해 계산했다. 난수 시드는 20261004이며 테스트에 고정되어 있다.

### 열어 본 URL

- [HCP1065 공식 출처·배포·라이선스](https://brain.labsolver.org/hcp_trk_atlas.html)
- [GitHub 릴리스 메타데이터 API](https://api.github.com/repos/data-others/atlas/releases/tags/hcp1065)
- [TRK ZIP](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_avg_tracts_trk.zip)
- [공식 약어 표](https://github.com/data-others/atlas/releases/download/hcp1065/abbreviation.xlsx)
- [공식 약어 표 2](https://github.com/data-others/atlas/releases/download/hcp1065/abbreviation2.xlsx)
- [TT ZIP 링크](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_avg_tracts_tt.zip): 웹 도구에서 링크 확인을 시도했으나 리디렉션 오류. TT 데이터는 다운로드하지 않음.
- [HCP 데이터 이용약관 및 감사 표기](https://www.humanconnectome.org/study/hcp-young-adult/document/wu-minn-hcp-consortium-open-access-data-use-terms)
- [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- [nibabel streamlines API](https://nipy.org/nibabel/reference/nibabel.streamlines.html)

전체 다운로드 목록·바이트 크기, ZIP 내부 목록, SHA-256, 원문 긴 이름은 [SOURCES.md](SOURCES.md)에 기록했다. 공개 파일 목록과 크기는 ZIP 다운로드 전에 기록했다.

## 실제 결과 검증 표

<!-- BEGIN GENERATED VALIDATION -->

결과: `data/derived/tracts/centerlines.json` — **138,882 bytes**, **34개 다발**, 총 **1,770개 점**, 입력 **129,649개 유효 스트림라인**.

좌표·반지름 유한성, 점/반지름 수, 길이, ID 중복, 교차 메타 검증 통과.

### CST 경유 좌표

좌표 단위는 RAS mm. 속섬유막은 과제의 기준점까지 가장 가까운 **출력 점**을 선택했다. 피라미드는 과제에 y 기준이 없으므로 z=−50에 가장 가까운 출력 점을 표시한다. 좌표 근접성만 확인했으며 중심앞이랑/핵의 실제 분할 영역과 중첩 검증은 수행하지 않았다.

| 다발 | 시작점 (z>50) | 속섬유막 기준 (±20, −10, +5) 최근접점 | 기준과 거리 mm | z=−50 최근접점 | 끝점 | 첫 x 부호 변경 z |
|---|---|---|---:|---|---|---|
| cst-l | (-21.38, -18.62, +71.16) (충족) | (-21.56, -11.82, +4.10) | 2.56 | (-3.49, -32.07, -50.81) | (-3.47, -32.12, -50.97) | null |
| cst-r | (+28.75, -17.16, +66.81) (충족) | (+23.14, -11.70, +3.76) | 3.78 | (+3.59, -31.93, -50.59) | (+3.53, -32.06, -50.94) | null |

### ML 종점과 교차

VPL 비교 기준은 과제에 주어진 (±15, −20, +5)이다. 최근접점과 **실제 종점**을 별도로 보고한다.

| 다발 | 시작점 | VPL 기준 최근접점 | 최근접 거리 mm | 실제 끝점 | 끝점↔VPL 거리 mm | 첫 x 부호 변경 z |
|---|---|---|---:|---|---:|---|
| ml-l | (-7.31, -38.91, -50.72) | (-18.92, -20.64, +1.97) | 5.00 | (-12.53, -34.56, +74.06) | 70.62 | null |
| ml-r | (+8.22, -38.75, -50.62) | (+19.07, -17.97, +1.18) | 5.94 | (+13.88, -30.16, +74.53) | 70.28 | null |

### 다발별 출력 통계

atlasName은 ZIP의 파일 약어를 그대로 사용한다. 긴 이름 대응은 SOURCES.md에 있다. `null`은 출력 중심선에서 x 부호 변경을 찾지 못했다는 뜻이다.

| id | atlasName | 스트림라인 수 | 길이 mm | 점 수 | decussationZmm |
|---|---|---:|---:|---:|---:|
| af-l | AF_L | 34,156 | 127.76 | 65 | null |
| af-r | AF_R | 3,356 | 127.41 | 65 | null |
| c-fph-l | C_FPH_L | 679 | 109.83 | 56 | null |
| c-fph-r | C_FPH_R | 142 | 111.91 | 58 | null |
| c-fp-l | C_FP_L | 10,806 | 76.14 | 40 | null |
| c-fp-r | C_FP_R | 9,146 | 77.85 | 40 | null |
| c-php-l | C_PHP_L | 74 | 105.77 | 54 | null |
| c-php-r | C_PHP_R | 386 | 104.17 | 54 | null |
| c-ph-l | C_PH_L | 1,022 | 38.72 | 21 | null |
| c-ph-r | C_PH_R | 1,245 | 35.24 | 19 | null |
| c-po-l | C_PO_L | 1,356 | 74.34 | 39 | null |
| c-po-r | C_PO_R | 958 | 103.79 | 53 | null |
| uf-l | UF_L | 5,672 | 78.83 | 41 | null |
| uf-r | UF_R | 9,425 | 87.40 | 45 | null |
| icp-l | ICP_L | 3,003 | 70.56 | 37 | null |
| icp-r | ICP_R | 2,315 | 72.14 | 38 | null |
| mcp | MCP | 2,780 | 83.87 | 44 | -41.64 |
| scp | SCP | 2,847 | 50.79 | 27 | null |
| cbt-l | CBT_L | 165 | 124.78 | 64 | null |
| cbt-r | CBT_R | 631 | 124.86 | 64 | null |
| cpt-f-l | CPT_F_L | 1,038 | 114.13 | 59 | null |
| cpt-f-r | CPT_F_R | 4,576 | 113.96 | 58 | null |
| cpt-o-l | CPT_O_L | 324 | 117.38 | 60 | null |
| cpt-o-r | CPT_O_R | 242 | 106.51 | 55 | null |
| cpt-p-l | CPT_P_L | 3,064 | 123.20 | 63 | null |
| cpt-p-r | CPT_P_R | 3,393 | 122.16 | 63 | null |
| cst-l | CST_L | 5,577 | 132.14 | 68 | null |
| cst-r | CST_R | 2,397 | 128.31 | 66 | null |
| f-l | F_L | 600 | 107.62 | 56 | null |
| f-r | F_R | 2,633 | 101.56 | 52 | null |
| ml-l | ML_L | 6,621 | 137.22 | 70 | null |
| ml-r | ML_R | 5,817 | 138.22 | 71 | null |
| or-l | OR_L | 1,968 | 104.45 | 54 | null |
| or-r | OR_R | 1,235 | 99.28 | 51 | null |

<!-- END GENERATED VALIDATION -->

## 사용법

저장소 루트(`/Users/lim/orca/projects/project-5`)에서 실행한다. 기존 `pipeline/.venv`의 numpy와 nibabel을 사용하며 추가 설치는 하지 않았다. 확인 환경: Python 3.11, numpy 2.4.6, nibabel 5.4.2, pytest 9.1.1.

```bash
# data/raw/hcp1065 아래에 추출한 34개 TRK.GZ 모두 변환
pipeline/.venv/bin/python -m pipeline.tracts.bundle_centerlines \
  --in data/raw/hcp1065 \
  --out data/derived/tracts/centerlines.json \
  --step-mm 2

# 특정 다발만 선택: 위의 전체 결과를 덮어쓰지 않도록 별도 출력
pipeline/.venv/bin/python -m pipeline.tracts.bundle_centerlines \
  --in data/raw/hcp1065 \
  --out data/derived/tracts/cst-centerlines.json \
  --tracts CST_L CST_R

# 실제 출력의 통계와 과제 기준 좌표를 Markdown으로 출력
pipeline/.venv/bin/python -m pipeline.tracts.validate_centerlines \
  data/derived/tracts/centerlines.json

# 기존 테스트는 atlas_pipeline을 최상위 패키지로 import한다.
# 루트에서 import 경로를 지정하고 과제의 전체 테스트 명령 실행.
export PYTHONPATH="$PWD/pipeline${PYTHONPATH:+:$PYTHONPATH}"
pipeline/.venv/bin/python -m pytest pipeline/tests -q
```

기존 테스트를 루트에서 환경 설정 없이 실행하면 `ModuleNotFoundError: atlas_pipeline`으로 수집 단계에서 실패한다. 위 환경 설정으로 기존 코드를 수정하지 않고 전체 32개 테스트가 통과한다.

`--tracts`는 실제 파일 약어, 지원되는 긴 이름 파일의 약어, 또는 출력 ID 형태(`cst-l`)를 받는다. 지정한 항목이 없거나 중복되면 오류로 종료한다. 생략하면 입력 디렉터리의 모든 TRK/TRK.GZ를 재귀 탐색한다. ZIP 자체를 입력으로 읽지는 않는다. 이름이 알려지지 않은 TRK도 파일명을 ID로 변환해 처리하므로 입력 디렉터리는 HCP1065 데이터 전용으로 사용한다.

### 다시 다운로드·추출하기

아카이브 587,869,457 bytes(약 561 MiB)는 `data/raw/hcp1065/`에 보관했다. 아래 추출 예시는 실제 처리한 34개 파일만 선택한다. SOURCE 목록의 다운로드 크기와 해시로 확인할 수 있다.

```bash
mkdir -p data/raw/hcp1065
curl -fL --retry 3 \
  https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_avg_tracts_trk.zip \
  -o data/raw/hcp1065/hcp1065_avg_tracts_trk.zip

pipeline/.venv/bin/python - <<'PY'
from pathlib import Path
from zipfile import ZipFile

root = Path('data/raw/hcp1065')
families = {
    'CST', 'CBT', 'ML', 'ICP', 'MCP', 'SCP', 'OR', 'F', 'AF', 'UF',
    'C_FPH', 'C_FP', 'C_PHP', 'C_PH', 'C_PO', 'CPT_F', 'CPT_O', 'CPT_P',
}
with ZipFile(root / 'hcp1065_avg_tracts_trk.zip') as archive:
    for member in archive.infolist():
        if not member.filename.endswith('.trk.gz'):
            continue
        name = Path(member.filename).name.removesuffix('.trk.gz')
        family = name[:-2] if name.endswith(('_L', '_R')) else name
        if family in families:
            archive.extract(member, root)
PY
```

## 변환 방법

1. **좌표**: `nibabel.streamlines.load(..., lazy_load=True)` 및 `to_world(lazy=True)`로 RAS+ mm를 얻는다. TRK 헤더의 voxel sizes, voxel order, voxel-to-RAS affine, voxel corner/center 차이를 nibabel이 반영한다. 수동 LPS→RAS 반전을 추가하지 않는다.
2. **전처리**: 연속 중복점을 제거한다. 두 점 미만, 길이 0, NaN/Inf 스트림라인은 제외하고 stderr 및 `rejectedStreamlines`에 개수를 기록한다. 이번 실제 데이터에서 제외된 스트림라인은 없다. 유효 다발이 없으면 실패한다.
3. **리샘플**: 각 스트림라인의 누적 호길이를 0~1로 정규화해 N=100점을 선형 보간한다. 각 섬유의 길이·원래 점 수가 달라도 대응점 수는 같다.
4. **방향 정렬**: 끝점 변위의 주성분으로 초기 방향을 잡는다. 이후 양 끝 평균점에 대한 거리 제곱 합이 작은 방향으로 스트림라인 순서만 뒤집고 반복 갱신한다. 50%가 거꾸로 저장된 경우에도 초기 양 끝 평균이 겹쳐 무너지는 것을 피한다. 좌표 자체를 반사하지 않는다.
5. **중심과 반지름**: 정렬된 N=100점에서 좌표별 중앙값을 중심으로 취한다. 각 대응점에서 중심까지의 3D 유클리드 거리 중앙값이 `radiiMm`이다. 이는 과제의 정의에 따른 대표 폭이며 중심선에 수직인 실제 단면의 최대 반지름이나 포락면은 아니다.
6. **출력 방향**: ML은 낮은 z→높은 z, 나머지는 높은 z→낮은 z로 출력한다. 끝점 z가 같으면 y, x 순으로 비교한다. 이 정렬은 재생을 위한 규약이며 생리적 전도 방향을 추론한 것이 아니다.
7. **최종 간격**: 중앙값 곡선의 누적 호길이에서 `0, step, 2*step, ...`와 마지막 끝점을 샘플링하고 같은 위치에서 반지름을 보간한다. 마지막 간격은 step보다 짧을 수 있다. 곡선의 코너를 가로지르는 출력 점 간 직선거리는 step보다 약간 짧을 수 있다. `lengthMm`는 최종 출력 점 사이 거리의 합이다.
8. **교차**: 최종 중심선에서 x가 반대 부호가 된 첫 출력 점의 z를 `decussationZmm`로 기록한다. x=0에 닿기만 하면 교차로 보지 않는다. 선분과 x=0 평면의 정확한 교차를 보간한 값은 아니며, 다중 교차도 첫 번째만 기록한다. 이 필드는 기하학적 플래그이며 해부학적 교차의 판정은 별도다.

실제 CST/ML TRK 헤더는 voxel order `LPS`, voxel sizes `[1, 1, 1]`, 다음 affine을 갖는다.

```text
[-1,  0,  0,  78]
[ 0, -1,  0,  76]
[ 0,  0,  1, -50]
[ 0,  0,  0,   1]
```

이 affine을 반영한 결과가 앞의 RAS 좌표 표다. 이 도구는 등록(registration)을 수행하지 않는다. 임의의 환자 공간 TRK를 넣어도 MNI로 정합해 주는 도구가 아니며, `source.space`는 HCP1065 입력을 전제로 한 메타데이터다.

## 출력 형식

```json
{
  "source": {
    "atlas": "HCP1065",
    "license": "CC BY-SA 4.0",
    "url": "https://brain.labsolver.org/hcp_trk_atlas.html",
    "space": "ICBM 2009a nonlinear asym"
  },
  "tracts": [
    {
      "id": "cst-l",
      "atlasName": "CST_L",
      "points": [[-21.375, -18.625, 71.15625], [-3.46875, -32.125, -50.96875]],
      "radiiMm": [0, 0],
      "lengthMm": 132.14,
      "streamlines": 5577,
      "decussationZmm": null
    }
  ]
}
```

위 예시는 **스키마 설명용 축약본**이다. 중간 점과 실제 반지름은 생략했으므로 예시의 길이를 두 점만으로 재계산하면 일치하지 않는다. 실제 JSON은 모든 점과 반지름을 포함한다. `atlasName`은 실제 배포 파일의 약어를 보존하고, 긴 이름은 SOURCES.md의 원문 대응표에 둔다. 원문 약어 표의 `C_FP_R` 긴 이름 셀에는 `_L`로 끝나는 불일치가 있어 파일명 R을 기준으로 처리했다.

## 라이선스 및 인용 표기

데이터 표기 예시:

> HCP1065 Population-Averaged Tractography Atlas, Fang-Cheng Yeh (2022)를 이용하여 생성한 대표 중심선 및 반지름 데이터입니다. 원본 섬유 다발에 방향 정렬, 호길이 재표본화, 중앙값 요약을 적용했습니다. 원본 및 이 파생 데이터의 라이선스는 CC BY-SA 4.0입니다. 원본 출처: https://brain.labsolver.org/hcp_trk_atlas.html . 라이선스: https://creativecommons.org/licenses/by-sa/4.0/ .

이 표기는 아틀라스 및 파생 데이터에 관한 것이며 저장소 코드 전체의 라이선스를 변경하지 않는다.

아틀라스 인용:

Yeh, F.-C. (2022). *Population-based tract-to-region connectome of the human brain and its hierarchical topology*. Nature Communications 13, 4933. https://doi.org/10.1038/s41467-022-32595-4

원본은 Human Connectome Project(WU-Minn Consortium) 영상 데이터에서 파생되었다. 공개 배포·발표 시 [HCP Open Access Data Use Terms](https://www.humanconnectome.org/study/hcp-young-adult/document/wu-minn-hcp-consortium-open-access-data-use-terms)의 재배포 조건 및 5항의 공식 감사 표기 문구를 함께 적용한다. 위의 한국어 아틀라스 표기는 HCP의 필수 감사 문구를 대체하지 않는다.

## 변경 범위

이번 작업은 `pipeline/tracts/`의 새 파일, `pipeline/tests/test_bundle_centerlines.py`, 지정된 `data/raw/hcp1065/` 및 `data/derived/tracts/` 출력에 한정했다. `content/`, `viewer/`, 기존 `pipeline/atlas_pipeline/`, 기존 테스트는 수정하지 않았다. 커밋·푸시는 하지 않았다.

# 아틀라스 반영 (메인 세션, 2026-10-04)

변환기 결과를 뷰어에 넣는 두 단계. 둘 다 결정은 코드 안의 표로 명시돼 있어 다시 돌리면 같은 결과가 나온다.

1. `prepare_tracts.py` → `data/derived/tracts/tracts-prepared.json`. 중심선 손질: 안쪽섬유띠는 **VPL에 가장 가까운 점에서 자름**(아틀라스 다발은 겉질까지 이어짐); 겉질척수로는 **겉질~위다리뇌 구간**(z ≥ −22)만 튜브로 쓰고(피라미드는 NextBrain 라벨), **교차 뒤 가쪽겉질척수로**는 반대쪽 다발의 숨뇌 끝에서 정중선을 건너 Visible Human 척수(자세 보정본)의 가쪽기둥을 따라 C7/T1까지, **앞겉질척수로**는 같은 쪽 앞기둥을 따라 T1까지 — 교차·기둥 위치는 교과서 기하이지 아틀라스 데이터가 아니며 각 조각의 `note`에 적혀 뷰어 상세 패널에 그대로 보인다. 반지름은 다발 퍼짐 중앙값을 1.5~6 mm로 제한.
2. `apply_to_content.py --write` → `content/structures.json`에 `source.atlas: "hcp1065"` 구조 8개(겉질척수로 3구간·겉질숨뇌로·시각부챗살·활꼴다발·갈고리다발·띠다발 C_FPH), NextBrain 신경로 3개(안쪽섬유띠·아래소뇌다리·뇌활)에 `centerlineFrom`(메시는 라벨 그대로, 경로 재생 중심선만 HCP). `content/pathways.json`의 단계 16개에 해당 신경로를 끼워 넣고(표 `STEP_TRACTS`; '활꼴'은 활꼴핵과 겹쳐 키워드 매칭 대신 명시 표) `missing` 문구에서 이제 3D가 있는 이름을 지운다.
3. 빌드(`atlas_pipeline/build.py`의 `hcp1065` 분기)는 `meshing.tube()`로 중심선을 따라 튜브를 만들고 그 중심선을 매니페스트 `centerline`으로 내보낸다. 출처는 매니페스트 `attribution`의 HCP1065 항목(CC BY-SA 4.0 — 파생 경로도 같은 라이선스).

쓰지 않은 다발: 겉질다리뇌 3구간(NextBrain 라벨이 뇌줄기 구간을 갖고 있음), MCP·SCP(배포본이 좌우 구분 없는 단일 파일), 띠다발 나머지 4구간, 뇌활·아래소뇌다리 튜브(라벨 메시 유지).
