# pipeline — 원본 데이터 → content → 메시

저장소 루트에서 실행한다. 파이썬은 `pipeline/.venv/bin/python`, `atlas_pipeline` 모듈은 `PYTHONPATH=pipeline`가 필요하다.
전체 순서는 `pipeline/run_all.sh`에 있다(`--dry-run`으로 명령만 출력, `--from/--to/--skip STAGE`, 첫 오류에서 멈춤).

## 단계

| # | stage (`run_all.sh`) | 스크립트 | 입력 | 출력 | 시간(측정/추정) | 다시 돌릴 때 |
|---|---|---|---|---|---|---|
| 0 | — (수동) | BodyParts3D 아카이브, MNI152 2009c, SAM 체크포인트, HCP1065 TRK 내려받기 | 웹 (`docs/data/body-model.md`, `pipeline/tracts/README.md`) | `data/raw/{bodyparts3d,mni,sam,hcp1065}` | — | 최초 1회. `bodyparts3d/to_mni.json`은 랜드마크로 손으로 맞춘 것(스크립트 없음) |
| 1 | `fetch` | `python -m atlas_pipeline.fetch` | Figshare(NextBrain), Zenodo(AAN) | `data/raw/nextbrain/{atlas.labels.argmax.nii.gz,prob/*.npz}`, `data/raw/aan/*.nii` | 수 분(네트워크) | 최초 1회. content에 NextBrain 라벨이 늘면 확률 지도만 추가로 받음 |
| 2 | `canal` | `bp3d_canal_axis.py` | `data/raw/bodyparts3d` | `data/derived/bp3d/canal_axis.json` | 측정 안 함 | BodyParts3D나 `to_mni.json`이 바뀔 때 |
| 3 | `vhp-register` | `vhp_stack_register.py [--skip-stack] [--bspline]` | `data/raw/vhp/male-head/a_vm1001..1377.png`(377장), MNI T1, `data/derived/vhp/so-eyeball.{R,L}.npz` | `data/raw/vhp/{vhp_head_rgb.npz, vhp_head_grey.nii.gz, vhp_to_mni.tfm, vhp_head_grey_mni.nii.gz}` | ~1 분 | 정합 코드·눈 분할이 바뀔 때. 그 뒤 4단계 필수 |
| — | — (수동) | `vhp_seed_from_mni.py` → `vhp_segment.py targets.json` | 정합, SAM | `data/derived/vhp/<id>.<side>.npz` (+ `.mni.nii.gz`) | 구조당 수 분 | 새 구조를 분할할 때만 |
| 4 | `vhp-project` | `vhp_to_mni_all.py` (끝에 `vhp_derive.py` 실행) | `data/derived/vhp/*.npz`, `vhp_to_mni.tfm`, `canal_axis.json` | `data/derived/vhp/*.mni.nii.gz`, 파생 부위, `sp-cord.M.mni-straight.nii.gz`, `derived.json` | ~15 초 | 3단계 뒤, 마스크가 바뀔 때 |
| 5 | `tracts` | `python -m pipeline.tracts.bundle_centerlines …` → `tracts/prepare_tracts.py` | `data/raw/hcp1065`, 곧은 척수 | `data/derived/tracts/{centerlines.json, tracts-prepared.json}` | 측정 안 함 | TRK·편집 규칙·척수가 바뀔 때 |
| 6 | `content` | `integrate_vhp`, `apply_models`, `tracts/apply_to_content`, `apply_axis_tracts`, `apply_body`, `apply_body_targets`, `apply_effects` (모두 `--write`) | 각 스크립트의 표, `data/derived/vhp`, BodyParts3D 색인 | `content/structures.json`, `content/pathways.json`, 검수표 `docs/data/structures-3d/*-review.md` | 수 초 | 표를 고칠 때. 모두 재실행해도 같은 결과(멱등) |
| 7 | `build` | `python -m atlas_pipeline.build` | content, 위의 모든 data | `data/derived/meshes/`(캐시), `viewer/public/data/{atlas.glb, manifest.json, sections/}` | 수 분(이번에 측정 안 함) | content나 data가 바뀔 때 |
| 8 | `nerves` | `apply_cranial_nerves.py --write`, `apply_autonomic.py --write` | content, **메시 캐시의 무게중심**, `canal_axis.json` | content(신경 경유점), `cranial-nerves-review.md` | 수 초 | 7단계 뒤 매번(핵·장기 위치가 바뀌었을 수 있음) |
| 9 | `nerves-build` | `build --only <8단계의 신경 id>` | 캐시 | 캐시·출력 갱신 | ~15 초 | 8단계 뒤 |

`integrate_structures.py`·`integrate_pathways.py`는 검수자 데이터(2026-10-02)를 처음 들여온 일회성 스크립트다. content를 통째로 다시 쓰므로 재실행하지 않는다. `make_handover.py`는 검수 묶음만 만든다.

## 명령

```bash
PY=pipeline/.venv/bin/python; export PYTHONPATH=pipeline
$PY -m atlas_pipeline.fetch
$PY pipeline/bp3d_canal_axis.py
$PY pipeline/vhp_stack_register.py
$PY pipeline/vhp_to_mni_all.py
$PY -m pipeline.tracts.bundle_centerlines --in data/raw/hcp1065 --out data/derived/tracts/centerlines.json --step-mm 2
$PY pipeline/tracts/prepare_tracts.py
for s in integrate_vhp apply_models tracts/apply_to_content apply_axis_tracts apply_body apply_body_targets apply_effects; do $PY pipeline/$s.py --write; done
$PY -m atlas_pipeline.build
$PY pipeline/apply_cranial_nerves.py --write && $PY pipeline/apply_autonomic.py --write
$PY -m atlas_pipeline.build --only pn-cn4 pn-cn5 …   # run_all.sh가 id 목록을 content에서 뽑아 준다
```

`--write` 없이 돌리면 apply/integrate 스크립트는 바꿀 내용만 출력한다.

## data/ 구성 (git 제외)

```
data/raw/nextbrain/      atlas.labels.argmax.nii.gz, lut, prob/<label>.npz (확률 지도)
data/raw/aan/            AAN v2.0: 핵별 파일 + AAN_Brainstem_MNI152_1mm_v2p0.nii (통합 라벨)
data/raw/bodyparts3d/    isa_BP3D_4.0_obj_99 (obj/), 부위 색인 txt, to_mni.json
data/raw/vhp/            male-head/*.png, 쌓은 볼륨, vhp_to_mni.tfm (MNI -> VHP)
data/raw/mni/, sam/, hcp1065/
data/derived/vhp/        <id>.<side>.npz (사진 픽셀 마스크), <id>.<side>.mni.nii.gz (MNI 투영),
                         sp-cord.M.mni-straight.nii.gz (척추관 축으로 옮긴 척수), derived.json
data/derived/bp3d/       canal_axis.json
data/derived/tracts/     centerlines.json, tracts-prepared.json
data/derived/meshes/     빌드 캐시: <meshId>.ply + <meshId>.json(manifest 레코드), structures/<id>.json
```

## 주의

- **apply → build 순서.** `apply_cranial_nerves.py`(핵 → 신경 첫 점)와 `apply_autonomic.py`(장기·신경절 위치)는 빌드가 남긴 메시 캐시(`data/derived/meshes/*.json`의 `centroid`)를 읽는다. 캐시가 없으면 빌드 명령을 알려 주고 멈춘다. 그래서 순서는 전체 빌드 → 이 두 스크립트 → `build --only <신경 id>`. 핵 메시가 바뀐 빌드 뒤에는 이 두 스크립트를 다시 돌려야 신경이 따라간다.
- **`--only`**: 주어진 구조만 다시 만들어 캐시에 넣고 출력(glb·manifest)은 캐시 전체에서 조립한다. 전체 빌드가 한 번은 있어야 하고, 단면 PNG는 내보내지 않는다. content에서 빠진 구조는 캐시에 남아도 출력에서 빠진다.
- **입력 점검**: 빌드는 시작 전에 필요한 입력(NextBrain argmax·확률 지도, AAN 파일, content가 가리키는 VHP 마스크, 곧은 척수, `canal_axis.json`, BodyParts3D, `tracts-prepared.json`)을 확인하고 빠진 목록과 만드는 명령을 출력한 뒤 멈춘다.
- **곧은 척수**: `vhp_derive.py`는 투영된 `sp-cord.M.mni.nii.gz`를 읽어 `sp-cord.M.mni-straight.nii.gz`에 쓴다(예전에는 같은 파일을 덮어써 돌릴 때마다 닫힘·스무딩이 겹쳤다). 빌드(`derived.json`의 `files`, `models.CORD_FILE`)와 `prepare_tracts.py`는 곧은 파일을 읽는다. 이름이 `*.mni.nii.gz`가 아니어서 `integrate_vhp.py`가 별도 구조로 집어 가지 않는다.
- **VHP 픽셀 축척**: 볼륨은 사진 3×3 픽셀 블록 = 0.99 mm(층 간격 1 mm). 상수 `F`, `PX`, `MM`은 `vhp_stack_register.py`에만 있고 `vhp_segment.to_mni`·`vhp_seed_from_mni.py`는 그것과 `lps_to_photo`를 쓴다. 회색 볼륨의 간격이 다르면 `to_mni`가 정합을 다시 하라고 멈춘다.
- **정중선**: NextBrain은 왼쪽 반구이고 오른쪽은 거울상이다. 라벨이 x = +1.6 mm까지 넘어가므로(띠이랑·vmPFC·SMA 등) 라벨·확률 마스크를 x ≤ 0에서 자른 뒤 메시를 만든다. 외곽(shell) 메시는 자르지 않는다.
- **BodyParts3D 이름**: `apply_body.py`는 색인에 없는 부위 이름이 있으면 실패한다(`--allow-missing`으로 무시). 빌드는 .obj가 없는 요소 id를 경고로 출력한다.
- `vhp_segment.py`는 torch·segment_anything을 분할할 때만 불러오므로 `vhp_to_mni_all.py`는 가볍게 `to_mni`만 가져온다.
