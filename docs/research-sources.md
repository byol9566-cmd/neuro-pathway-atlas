# 3D 신경과학 학습 도구 — 자료 조사 결과 (2026-09-20, 2차 갱신)

조사 방식: 검색 전용 서브에이전트(1차 6개, 2차 10개 — Sonnet/Haiku) → 핵심 주장(라이선스·다운로드 위치·라벨 목록·논문)을 메인 세션이 1차 출처에서 재확인.

신뢰도 표기
- ✅ **직접 검증**: 1차 출처(Zenodo/Figshare/OSF/GitHub API, 논문 본문, 공식 페이지, 배포 파일 원문)를 메인 세션이 직접 열어 확인
- ⚠️ **에이전트 보고**: 서브에이전트가 1차 출처를 인용했으나 재확인하지 않음. 사용 전 확인 필요
- ❓ **충돌/미확정**: 출처 간 정보가 어긋나거나 라이선스가 명시되지 않음. 제작자에게 문의 필요

---

## 1. 결론 요약

1. **구현 가능**. 거의 동일한 컨셉의 오픈소스(nervous-system-atlas, 2026-09-09 생성, 1인 개발)가 이미 작동 중 → 기술적 실현성은 증명됨.
2. **3D 모델은 "생성"이 아니라 "변환"**: 공개 아틀라스의 라벨 볼륨(NIfTI) → 메시 추출. 생성형 3D(힉스필드·Meshy·Hunyuan3D 등)는 해부학 메시에 부적합.
3. **핵심 데이터 백본은 NextBrain(CC0)**. 2차 조사에서 원본 라벨 볼륨을 직접 열어 확인 ✅: 0.2mm 이산 라벨 볼륨(좌반구, MNI에 정렬된 좌표), **333 라벨**. VPL·VPM·VPI·VA·VL·MD·풀비나·CM/Pf·편도 핵은 물론 **뇌신경핵(안면·외전·삼차 3종·전정 4종·달팽이 2종·설하·미주등쪽·고립로·의문·동안·활차), 박·쐐기핵, 청반, MLF·내측섬유띠·중심피개로·척수섬유띠·피질척수로까지 라벨이 존재**. 단, 뇌간 소핵 상당수는 argmax 볼륨에서 부피가 극소(<5mm³)라 그대로는 메시가 안 됨 → 확률지도에서 라벨별로 재추출하거나 수작업 보정 필요. FreeSurfer 배포판(265 라벨)·MNI 1mm 재패키징(248 라벨)에서는 이 뇌간 세부가 빠져 있음.
4. **공개 데이터가 없는 영역**(직접 모델링 필요): 렌즈핵고리·시상밑다발·등쪽세로다발 등 일부 소전도로, 동공반사 회로(시개앞핵), 척수 Rexed 층. 뇌신경핵은 NextBrain 원본에서 출발해 보정하는 경로가 생김(§2-5).
5. **진짜 병목은 "구조 ↔ 신경과정" DB**: 중추신경 경로에 대한 공개 기계가독 DB는 없음(SCKAN은 자율·말초 한정 ✅) → 수작업 큐레이션이 프로젝트의 핵심 가치.
6. **라이선스가 수익화 가능 범위를 결정**: 상업 가능 소스(CC0/CC BY)만으로 전뇌·간뇌·기저핵·중뇌 핵·시상하부·소뇌핵·주요 백질은 커버됨. 뇌간은 NextBrain 원본으로 상당 부분 커버되나 보정 작업이 필요하고, 더 완성도 높은 뇌간 자료(Duke CIVM, Brainstem Navigator, Tang 2018)와 척수 내부(PAM50)·기저핵 소전도로(Petersen 2019)는 비상업 또는 라이선스 미기재.
7. **렌더링 리스크 완화 소식**: three.js r183에서 `BatchedMesh` 인스턴스별 불투명도, r186에서 WebGPU용 공식 OIT(`OITPassNode`)가 들어옴 ✅ (§4).

---

## 2. 데이터 소스 (선별)

### 2-1. 상업 이용 가능 — 백본으로 채택 권장

| 소스 | 내용 | 라이선스 | 신뢰도 | 위치 |
|---|---|---|---|---|
| **NextBrain** (Casamitjana/Iglesias, Nature 2025) | 조직학 기반 확률 아틀라스. 상세는 아래 "NextBrain 상세" 참조 | **CC0** | ✅ Figshare API license=CC0, readme·zip 내부 readme·LUT 원문 직접 확인 | https://doi.org/10.5522/04/24243835 (`3dAtlas.zip` 397MB) |
| **Harvard AAN Atlas v2.0** (Edlow) | 뇌간 각성계 핵: LC, VTA, PAG, DR, MnR, PTg, LDTg, PBC, mRt, PnO. MNI152 1mm NIfTI | **CC0** | ✅ (Zenodo) | https://zenodo.org/records/8161638 |
| **Neudorfer 시상하부 아틀라스** (Sci Data 2020) | 시상하부 13 + 주변 12 구조, 0.25/0.5mm, MNI152 2009b. 전도로는 유두시상로·뇌궁만 포함 ⚠️(라벨 CSV, 에이전트 확인) | **CC BY 4.0** | ✅ (Zenodo) | https://zenodo.org/records/3942115 |
| **MASSP 2.0 / AHEAD** (Imaging Neuroscience 2025) | 35구조: STN, RN, SN, GPi/GPe, VTA, PAG, PPN, 상·하구, 솔기핵, LGN/MGN, 해마 세부, 교련, 뇌궁 등. **시상·편도는 통짜 라벨**. 7T | **CC BY 4.0** (데이터 레코드 자체). 코드 nighres Apache-2.0 | ✅ Figshare API 27291714(Parcellation Priors, v2, 2025-09-25) 직접 확인. 단 설명문에 "priors는 아틀라스로 쓰는 확률지도가 아님" 명시 → 아틀라스 용도는 **Lifespan Probabilistic Atlas(27291579, CC BY 4.0 ⚠️)** 사용. 구버전 MASSP 2021(19646334, 17구조, MNI2009b)도 CC BY 4.0 ✅ | uvaauas.figshare.com (DOI 10.21942/uva.27291714). MNI2009cAsym 재표본판이 TemplateFlow에 `atlas-MASSP20_dseg`로 있음 ✅(NOTICE의 다운로드 URL) |
| **CIT168** (Pauli 2018) | 기저핵·중뇌 핵(SNc/SNr, RN, VTA, STN, 유두체, 고삐핵 등) 확률 아틀라스 | **CC BY 4.0** | ✅ OSF API `nodes/r2hvk` license="CC-By Attribution 4.0 International" | https://osf.io/r2hvk/ (TemplateFlow에는 tpl-CIT168 없음 ⚠️) |
| **LC metamask** (Dahl 2022) | 청반 마스크, MNI | CC BY 4.0 | ⚠️ (에이전트가 OSF API `nodes/sf2ky`에서 확인) | https://osf.io/sf2ky/ |
| **Allen Human Reference Atlas 3D (2020)** | 141구조, ICBM 2009b Nonlinear Symmetric, `annotation.nii.gz`·`annotation_full.nii.gz` (NIfTI만 있음) | **CC BY 4.0** (2022-09-01부) | ✅ README.pdf 원문 "These materials are now provided under the Attribution International 4.0 (CC BY 4.0) license as of Sept. 1, 2022" + 공식 포럼 공지. Allen 일반 이용약관(비상업)과 달리 이 자료는 개별 허용. 뇌신경핵 포함 여부는 미확인 ⚠️ | download.alleninstitute.org/informatics-archive/allen_human_reference_atlas_3d_2020/version_1/ |
| **TractSeg** | 72개 백질 다발 분할(가중치 포함). CST, 뇌궁, 시각로부챗살, 시상방사 등 | **Apache-2.0** | ✅ (GitHub API) | github.com/MIC-DKFZ/TractSeg |
| **ORG 섬유 클러스터 아틀라스** (O'Donnell) | 심부 백질 58 tract + 표층 클러스터 | **CC BY 4.0** | ✅ (Zenodo) | https://zenodo.org/records/2648292 |
| **Pandora 백질 아틀라스** | 216 다발(6개 방법), 2,443명 | **CC BY 4.0** ("even commercially") | ✅ (NITRC) | https://www.nitrc.org/projects/pandora_atlas/ |
| **BodyParts3D** | 전신 메시(뇌는 큰 구조 단위, 뇌신경·척수신경 포함). 핵 단위는 없음 | **CC BY 4.0** | ✅ DBCLS 공식 라이선스 페이지(2025-02-27 갱신): "BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International". CC BY-SA 2.1 JP는 구버전 표기로 보이며 현행 1차 출처에서는 확인되지 않음 | dbarchive.biosciencedbc.jp/en/bodyparts3d/ |
| **spine-generic** (multi/single-subject) | 척수 MRI 원자료(아틀라스 아님) | **CC BY 4.0** | ✅ (GitHub API 두 repo 모두 CC-BY-4.0) | github.com/spine-generic |
| **요천수 MRI 데이터셋(Fudan, Sci Data 2024)** | 14명 요천추 MRI + 신경근 3D 재구성 모델. 척수 내부 구조 아님 | CC BY 4.0 | ⚠️ (에이전트가 Figshare API 26403262에서 확인) | figshare collection 10.6084/m9.figshare.c.7372564 |
| **Edlow 2019 100µm 7T ex vivo 뇌** | 수작업 분할용 원본 영상(전뇌, 뇌간 포함) | **CC0** | ✅ OpenNeuro `dataset_description.json` "License": "CC0" | openneuro.org/datasets/ds002179 |
| **Open Anatomy SPL/NAC 뇌 아틀라스** | 300+ 구조 메시(1인 MRI 기반), Slicer 라이선스(상업 허용) | ⚠️ (GitHub repo는 2017년 이후 정지, 라이선스 NOASSERTION) | | openanatomy.org |

#### NextBrain 상세 (2차 조사에서 직접 확인 ✅)

- **`3dAtlas.zip` 내용**(HTTP range 요청으로 목차·텍스트만 읽음): `readme.txt`, `atlas.labels.argmax.nii.gz`(14.5MB, **이산 라벨 볼륨** — "hard segmentation in which each voxel is assigned the label with the highest probability"), `atlas.labels.rgb.nii.gz`(391MB, 확률 가중 RGB 시각화), `lut.freeview.txt`, `lut.itksnap.txt`.
- **argmax 볼륨 실측**(zip에서 해당 파일만 13MB 추출해 nibabel로 확인 ✅): shape 460×1145×910, **0.2mm 등방**, RAS, affine 원점 (-81, -132, -88), float32. 비영 영역 x -80~+1.6mm → **좌반구만**. readme에 공간 명시는 없으나 적핵 중심 (-5.4, -18.4, -11.6)·치아핵 (-16.2, -59.3, -37.5)·안면신경핵 (-6.6, -38.7, -46.3)이 MNI 좌표와 1~2mm 내로 일치 → **사실상 MNI 정렬**(정확히 어느 MNI 변형인지는 ❓, PoC에서 MNI T1에 겹쳐 확인). 우반구는 좌우 반전으로 생성.
- **실제 존재 라벨: 333개**(0 제외; 그중 34개는 FreeSurfer aparc 피질 라벨 `ctx-rh-*`, 나머지 299개가 조직학 라벨). 전체 목록·부피는 `docs/data/nextbrain-argmax-labels.tsv`에 저장. 부피 분포(299개): ≥20mm³ 196개, 5~20mm³ 50개, 1~5mm³ 34개, <1mm³ 19개.
- **뇌간 — 원본 볼륨에는 있음** ✅ (괄호는 argmax 부피 mm³, 한쪽):
  - 메시화 가능한 규모: spinal_trigeminal_nucleus(60.6), medial_vestibular(29.4), facial_nucleus(25.1), cuneate(21.4), nucleus_coeruleus(9.6), inferior/lateral_vestibular(7.8/7.5), abducens(5.7), gracile(5.6), motor_trigeminal(5.3), ventral_cochlear(5.3), hypoglossal(4.9), pontine_nucleus(3411), inferior_olive_principal(117), PAG(199), superior_colliculus(166), pontine/medullary reticular formation(761/340)
  - 라벨은 있으나 argmax에서 극소(실제 해부학적 크기보다 훨씬 작게 남음): dorsal_cochlear(3.2), solitary_nucleus(3.2), principal_sensory_trigeminal(3.1), dorsal_motor_vagus(2.7), mesencephalic_trigeminal(0.9), oculomotor(0.4), trochlear(0.4), superior_vestibular(0.4), Edinger-Westphal(0.1), ambiguus(0.1). → 확률 아틀라스(`SegmentationCode.zip` 2.5GB 또는 FreeSurfer `atlas_simplified.zip`의 전체판)에서 라벨별 확률지도를 임계값 처리해 재추출하거나, 위치만 취하고 형상은 수작업 보정 ⚠️(확률지도 구조는 미확인)
  - 전도로: **medial_lemniscus(400), central_tegmental_tract(246), spinal_trigeminal_tract(125), lateral_lemniscus(127), spinal_lemniscus(84), medial_longitudinal_fasciculus(74), corticospinal_tract(64, 일부 구간), frontopontine/parietotemporopontine, 상·하소뇌다리**
  - 없음: internal capsule(별도 라벨 없음), ansa lenticularis, 시개앞핵 세분(pretectal_region 통짜만)
- **라벨 목록은 세 가지가 있음 — 혼동 주의**:
  1. zip 안의 `lut.freeview.txt`: **918행**(Allen 온톨로지 기반 전체 표). 이 중 333개만 볼륨에 실재 ✅.
  2. FreeSurfer 배포판 `mri_histo_util/ERC_bayesian_segmentation/data_simplified/AllenAtlasLUT`: **265 라벨**(실제 분할 도구가 쓰는 목록). 뇌간은 `midbrain`, `pons`, `medulla_oblongata`, `red_nucleus`, SNr/SNc, `dorsal_raphe_nucleus`, `inferior_olive_principal`, `central_nucleus_of_inferior_colliculus`, `facial_nucleus`, `solitary_tract` 정도. **그 외 뇌신경핵 없음.**
  3. 커뮤니티 MNI 1mm 재패키징(compneurobilbao): **248 라벨/반구**. 1mm 재표본화에서 17개 소실(`facial_nucleus`, `solitary_tract`, `suprachiasmatic_nucleus`, `medial_habenular_nucleus`, `interstitial_nucleus_of_cajal`, `optic_nerve` 등).
- **1차 조사의 "VPL/VPM/VA/VL/MD가 안 보인다"는 틀렸음**: 라벨명이 약어·세분 표기라 놓친 것. 2·3번 목록 모두에 존재: VA(parvo/magnocellular), VL(`rostral_division_of_vl`, VLc dorsal/ventral/medial), MD 5분할, **VPL rostral/caudal, VPM(+parvocellular), VPI**, 풀비나 6종, CM(medial/lateral)·Pf, CL 4분할, LGN/MGN, LD, LP, 망상핵 등.
- **편도**: `lateral_nucleus`, `basolateral_nucleus_(basal)`, `ventral_division_of_basomedial`(≈부기저핵), `central_nucleus` medial/lateral, `rostral_subdivision_of_medial_nucleus`, `ventral_subdivision_of_coa`(피질핵), 이행 영역 4종. 교과서 6핵 구도와 1:1은 아니지만 병합하면 대응 가능.
- **포함된 소전도로**: `mammillothalamic_tract`, `lenticular_fasciculus`, `nucleus_of_the_field_of_forel`, `stria_terminalis`, `stria_medullaris_of_thalamus`, `fasciculus_retroflexus`, `fornix`, `fimbria`, `optic_tract/chiasm`, 상·하소뇌다리. **없는 것**: ansa lenticularis, internal capsule, medial lemniscus, MLF.
- **시상밑핵(STN)은 있음** ✅: `medial/laterodorsal/lateroventral_portion_of_sth`(315·316·321, 합 331mm³) 3분할로 세 목록 모두에 존재 — 이름이 약어(sth)라 "subthalamic" 검색에 안 걸려 한때 "없음"으로 잘못 적었던 항목. 청반(LC)은 원본에만 있고(9.6mm³) 2·3번 목록에는 없음 → AAN과 비교해 선택.
- 피질 라벨명이 `ctx-rh-*`인데 좌표는 x<0(RAS 기준 좌측) — 좌우 표기는 PoC에서 MNI T1에 겹쳐 확인 ❓
- **MNI 재패키징의 라이선스 상태** ❓: repo 라이선스 없음(`license: null` ✅). FreeSurfer 8.1 도구 + FreeSurfer FTP의 `atlas_simplified.zip`으로 생성됨. 원 데이터는 Figshare에서 CC0이지만 FreeSurfer 경유 배포물에는 FreeSurfer Software License가 걸림(상업화는 "at the sole risk", 재배포 시 라이선스 전문 동반 ⚠️). **Figshare CC0 원본(argmax 0.2mm)에서 직접 메시를 뽑는 것을 권장** — 라이선스가 깨끗하고, 해상도가 5배 높으며, 뇌간 세부 라벨이 살아 있음. MNI 재패키징은 빠른 확인용으로만.

### 2-2. 조건부 — ShareAlike(파생물도 동일 라이선스)

| 소스 | 내용 | 라이선스 | 신뢰도 |
|---|---|---|---|
| **MIAL 시상핵 아틀라스** (Najdenovska 2018) | 시상 14핵 확률지도 + MaxProb, MNI. TemplateFlow에 `atlas-MIAL67ThalamicNuclei_dseg`(2009cAsym) 있음 | **CC BY-SA 4.0** — 1차 문서의 "CC BY 4.0"은 틀렸음(타 프로젝트 NOTICE를 옮겨 적은 오류). 논문이 인용하는 정식 레코드 Zenodo 1405484 기준 | ✅ Zenodo API. NextBrain이 시상핵을 더 세밀하게 CC0로 제공하므로 **불필요** |
| **HCP-1065 tract atlas** (Yeh 2022) | 집단 평균 트랙토그램 | 배포 페이지: **CC BY-SA 4.0** ✅ + HCP 약관에 따른 acknowledgment 요구. 한편 WU-Minn HCP 약관은 "파생 데이터는 같은 Data Use Terms로 재배포" ⚠️ → 두 조건이 겹쳐 어느 쪽이 우선인지 ❓. 뇌간 소전도로(MLF 등) 포함 여부도 페이지에서 확인 안 됨 | ❓ |
| **Z-Anatomy** | BodyParts3D 기반 전신 모델 | CC BY-SA 4.0 (README) | ⚠️ |
| **nervous-system-atlas 생성 메시** | 585~592 메시, 릴리스 아카이브 `atlas-data-v1.0.2.tar.gz`(45MB) | CC BY-SA 4.0 (NOTICE) | ✅ 릴리스 존재 확인 / 라이선스 문구는 ⚠️ |

### 2-3. 비상업 전용 — 무료 교육용이면 사용 가능, 유료화 시 제외

| 소스 | 내용 | 신뢰도 |
|---|---|---|
| **Tang 2018 뇌간 전도로 아틀라스** | 내측섬유띠·척수시상로·외측섬유띠·CST·소뇌다리 23 다발, MNI. NITRC `brainstem_atlas`에서 `Brainstem23BundleAtlas.zip` | ✅ "Permission is granted to use this atlas without charge for non-commercial research purposes only." / "YOU MAY NOT DISTRIBUTE COPIES of this atlas, or copies of files derived from this atlas, to others outside your organization." → **비상업이어도 파생 메시 재배포 불가 = 웹 공개 불가** |
| **Petersen 2019 기저핵 경로 아틀라스** (Neuron) | **ansa lenticularis, lenticular fasciculus**, 시상다발, 소뇌시상로, 담창구-시상밑 경로, hyperdirect 등 VTK 스트림라인, CIT168 공간. osf.io/mhd4z | ✅ 논문 본문: "The pathway atlas is the property of CWRU and may not be used for commercial purposes without the written consent of CWRU." (OSF 노드 라이선스는 "No license") — 렌즈핵고리의 유일한 3D 소스. 무료 교육판에는 쓸 수 있을 가능성, 유료화 시 CWRU 서면 동의 필요 |
| **BigBrain** | 20µm 조직학 볼륨(수작업 분할용 원본으로 가치) | ✅ `License.txt`: CC BY-NC-SA 4.0 |
| **Julich-Brain** | 세포구축 아틀라스, v3.1부터 시상 아핵 포함 | ⚠️ 에이전트가 EBRAINS KG API에서 v2.9~v3.1 전부 CC BY-NC-SA 4.0 확인. CC BY 버전 없음 |
| **Brainstem Navigator** (Bianciardi, 7T) v1.0 (2024-10-08) | 뇌간 핵 58 라벨(망상체, 솔기핵군, 전정·달팽이핵, 상·하구, 하올리브 등) | ⚠️ NITRC 프로젝트 페이지에는 라이선스 문구가 보이지 않음(직접 확인). 비상업·조직 외 재배포 금지 문구는 에이전트·타 프로젝트 NOTICE 보고 — 다운로드 패키지 내 라이선스 파일 확인 필요 |
| **Duke CIVM 뇌간 아틀라스** (Adil 2021) | 50µm ex vivo, 90구조(**뇌신경핵 포함**) + 섬유다발 11 | ⚠️ 논문은 CC BY-NC-ND, 뷰어는 등록제, 원자료는 "reasonable request". 상업 라이선스는 요청 시 가능하다는 보고 |
| **Rushmore 2020** (Front Neuroanat, 50µm 뇌간 123구조) | 뇌신경핵을 전부 명명한 가장 완전한 분할이지만 **라벨 볼륨이 아니라 축상 도판 291장(보충자료)**으로 제공되고, 원본 MRI가 Duke CIVM | ✅ 논문 본문 Data Availability 확인. → 3D 소스로는 못 쓰고 수작업 분할 시 참고 도판으로만 가치 |
| **FreeSurfer 세부 분할** | 시상핵 26, 해마 아구역 ~13, 편도핵 ~9 | ⚠️ FreeSurfer Software License: 상업화는 "at the sole risk of the party", 임상 비권장, 재배포 시 라이선스 전문 동반. 1차 문서의 "비상업 라이선스"는 부정확 — 명시적 비상업 조항은 아님. Iglesias/Edlow의 FreeSurfer판 AAN 분할 논문은 CC BY-NC-ND ⚠️ (Zenodo의 AAN v2.0 CC0와는 별개 산출물) |
| **XTRACT / JHU (FSL)** | FSL 비상업 라이선스 | ⚠️ |
| **Morel/Krauth 시상 42핵** | ETH 라이선스 요청 필요 | ⚠️ |
| **Visible Korean 뇌 분할** (Chung & Park, JKMS 2019) | 머리 297 구조, CC BY-NC 4.0 / Zenodo 3956014는 CC BY 4.0 | ⚠️ |
| **Digital Brain Bank** (Oxford, Tendler 2022) | 사후 뇌 확산 MRI + 조직학 | ⚠️ MTA 필요(연구·교육 목적) |

### 2-4. 라이선스 충돌·미기재 — 제작자 문의 필요

- **PAM50 / SCT 척수 아틀라스** (백질 15 tract×2, 회백질 3구역×2, 척수 분절, `histology` 폴더): repo에 LICENSE 없음 ✅(`gh api` license=null, 루트 목록에 LICENSE 파일 없음). SCT 소프트웨어는 LGPL-3.0 ✅이나 데이터 repo에 미치는지 불명. 포럼/이슈에서 유지관리자의 라이선스 답변은 찾지 못함 ⚠️. nervous-system-atlas NOTICE도 "no licence file is shipped with the data" ✅. **문의처: Julien Cohen-Adad (NeuroPoly, Polytechnique Montréal) — forum.spinalcordmri.org 또는 PAM50 repo issue.** 척수 내부 구조의 유일한 실용 소스라 문의 가치 큼.
- **SUIT 소뇌 아틀라스**(소엽 28 + 심부핵 6): **같은 연구실의 두 1차 출처가 서로 다름** ✅ — GitHub README "distributed under a Creative Commons CC BY (Attribution) license" vs 연구실 웹페이지(atlasPackage.htm) "Creative Commons license CC BY-ND (Attribution - No derivatives)". repo에 LICENSE 파일 없음, `atlas_description.json`은 "See LICENSE file"(없는 파일) ⚠️. ND라면 메시 변환 자체가 파생물이라 사용 불가 → Diedrichsen lab 문의 필요. 대안: 소뇌 심부핵은 NextBrain(CC0)에 4종 있음 ✅.
- **Saranathan 2021 시상 13핵**: Zenodo 4586928(v3.0)·5499504(v4.3) **둘 다 license 필드 없음, access=restricted** ✅. 1차 문서의 "두 레코드 표기 불일치"는 부정확 — 둘 다 미기재. NextBrain으로 대체되므로 **추적 중단**.
- **DISTAL 아틀라스(Lead-DBS)**: 데이터 라이선스 문구 없음 ⚠️.

### 2-5. 공개 데이터 없음 → 직접 제작

- **뇌신경핵 개별 메시**(동안·EW·활차·삼차 4종·외전·안면·전정·달팽이·고립로·의문·미주등쪽·설하): **NextBrain 원본 argmax(CC0)가 유일한 상업 가능 출발점** ✅ — 안면·외전·삼차(척수/운동)·전정(내측/외측/하)·배쪽달팽이·설하·박/쐐기핵은 바로 메시화를 시도할 만한 부피, 동안·활차·EW·의문·고립로·미주등쪽·상전정은 극소라 확률지도 재추출 또는 수작업 보정 필요(위 "NextBrain 상세"). "완성된 뇌신경핵 메시 세트"를 주는 상업 가능 소스는 여전히 없음. 그 밖의 후보:
  - Allen 3D 2020(CC BY 4.0): 141구조 수준이라 가능성 낮음, 온톨로지 미확인 ⚠️
  - Duke CIVM / Brainstem Navigator / Rushmore 2020: 비상업 또는 도판만 제공
  - WIKIBrainStem(Lechanoine 2021, 11.7T 115 클래스): 웹 위키 형태, 다운로드·라이선스 확인 실패 ⚠️
  - 좌표·치수 논문: Rushmore 2020 Table 2는 Paxinos 대비 상하 범위 **비율**만 제공 ⚠️. "Three-dimensional interactive and stereotactic atlas of the cranial nerves and their nuclei"(J Neurosci Methods로 추정, S0165027012000829)는 유료벽으로 미확인 ⚠️
  - **현실적 경로**: NextBrain 라벨 위치를 씨앗으로 삼아 3D Slicer에서 보정(배경 영상은 Edlow 100µm CC0, 참고 자료는 Rushmore 도판·Paxinos — 도판 자체를 복제하지 않음). 극소 핵은 1단계로 타원체/캡슐 근사 → 도메인 담당자 검수.
- **전도로**:
  - 유두시상로·렌즈핵다발(H2)·Forel 영역·분계섬유줄·시상수질줄·고삐핵다리사이로·뇌궁, 그리고 뇌간의 **MLF·내측섬유띠·중심피개로·척수섬유띠·외측섬유띠·삼차신경척수로** → **NextBrain 원본에 있음(CC0)** ✅ — 1차 문서의 "공개 데이터 없음" 목록에서 제외. 단 부피로 보아(예: corticospinal_tract 64mm³) 기시~종지 전체가 아니라 일부 구간만 라벨된 것으로 추정 ⚠️ → 메시를 뽑아 보고 스플라인으로 이어 붙일지 판단
  - 렌즈핵고리(ansa lenticularis)·시상다발 → Petersen 2019만 존재(CWRU 비상업)
  - 등쪽세로다발, 시상밑다발, 내측전뇌다발, 동공반사 회로(시개앞핵-EW) → 확인된 공개 3D 소스 없음 → 스플라인 수작업
  - ex vivo 고해상도 트랙토그래피·PLI: 공개된 전뇌 소전도로 자료는 확인되지 않음(EBRAINS PLI는 해마 블록 위주라는 보고) ⚠️
- **척수 Rexed 층(I–X)·회백질 뿔 세분**: 공개 3D 자료 없음. Sengul & Watson 아틀라스는 도서 구매자용, Allen Spinal Cord는 생쥐, Duval 2019(osf.io/8k7jr)는 백질 축삭 형태계측 ⚠️. → 분절별 2D 도식을 직접 그려 압출하는 방식.

---

## 3. 생성형 AI / 힉스필드 판단

- **힉스필드**: 2026-09-04 "3D Jutsu" = 프롬프트→편집 가능한 3D 장면→**영상**. 메시(GLB/OBJ) 내보내기 없음 ✅(공식 changelog). 2026-08-21 Blender 플러그인에 "3D Model" 도구 언급만 있음. → 해부학 메시 제작 용도로는 부적합. 홍보 영상용.
- **생성형 3D 일반**(Hunyuan3D, TRELLIS, Rodin, Meshy, Tripo): 단일 물체의 겉표면 생성용. 보이지 않는 면을 지어내고(Janus problem), 내부 구조·공통 좌표계·부품 간 정합성이 없음 ⚠️. 해부학 정확도를 평가한 논문은 발견되지 않음. 참고: Hunyuan3D 커뮤니티 라이선스는 **한국·EU·영국에서 적용 제외** ⚠️.
- **실제로 유용한 AI**:
  - 슬라이스 스택 분할·전파: SAM 2 (Apache-2.0), MedSAM2 (Apache-2.0), nnInteractive(코드 Apache-2.0, 가중치 CC BY-NC-SA) ⚠️
  - 드문드문 그린 윤곽 → 볼륨 보간: Biomedisa, 3D Slicer "Fill between slices" ⚠️
  - 거친 전체 분할: SynthSeg, FastSurfer(HypVINN, CerebNet) — Apache-2.0 ⚠️
  - 앱 코드 작성: AI 코딩 에이전트 (실행으로 검증 가능)
  - 설명 텍스트·DB 초안: LLM 가능하나 **전문가 검수 필수** — 신경과 보드 문제 정답률 ChatGPT-5 84.1% vs 전공의 64.9%이지만 확신도-정확도 보정이 약함 ✅(Almomani 2026, PMC12813092). LLM이 생성한 인용의 오류율 25~75% 보고 ⚠️

---

## 4. 구현 기술 스택

### 메시 파이프라인
1. 라벨 볼륨 정리: 3D Slicer (Segment Editor, Joint smoothing). Slicer는 2023-09-06 커밋부터 `vtkSurfaceNets3D` 기반 변환을 내장 ⚠️
2. 다중 라벨 → 메시: **`vtkSurfaceNets3D`** — 인접 구조 경계를 공유(틈·겹침 없음), discrete marching cubes 대비 10~100배 빠름 ✅(Kitware 2023-06-13). **VTK ≥ 9.3** 필요, 출력의 2-성분 셀 배열 `BoundaryLabels`로 라벨별 분리, VTK 9.7에서 일부 옵션이 `vtkSurfaceNetsAtlas`로 이관 예정 ⚠️(에이전트가 헤더 확인). 공식 Python 예제 페이지는 찾지 못함 ⚠️
   - 간이 대안: `nii2mesh -a 1`(라벨별 자동 메시, enhanced marching cubes + quadric 감량) ⚠️
   - 참고 구현(nervous-system-atlas `pipeline/atlas_pipeline/meshing.py` ✅): 마스크 → 부호거리장(EDT) → `skimage.marching_cubes` → Taubin 평활 → `trimesh` quadric 감량 → **`weld_group`(KD-tree 0.35mm)로 이웃 메시의 공유 경계 용접**. 의존성은 numpy/scipy/nibabel/scikit-image/trimesh뿐(VTK 없음)
3. 경계 보존 감량: 다중 라벨 메시 전체를 **분리 전에** 감량하거나, gltf-transform `simplify`의 `lockBorder`(meshoptimizer `SimplifyLockBorder`) 사용 ⚠️. 순서는 `weld → simplify → meshopt` ⚠️
4. 수작업 구조: SlicerOpenAnatomy의 **OpenAnatomy Export** → glTF(이름·계층·색·투명도 보존) ✅
5. 압축: gltf-transform CLI + meshopt(`EXT_meshopt_compression`, Draco보다 디코드가 빠름 ⚠️). 영역별 GLB 몇 개로 묶어 지연 로딩. DB id는 glTF `node.extras`에 기록 ⚠️
6. **템플릿 공간 정합**:
   - TemplateFlow가 제공하는 변환은 **MNI152NLin2009cAsym ↔ MNI152NLin6Asym뿐**(`..._from-..._mode-image_xfm.h5`). 2009bAsym·Colin27에는 xfm 없음, CIT168·AHEAD는 TemplateFlow에 없음 → 직접 정합 ⚠️
   - 2009b와 2009c는 같은 Fonov 템플릿 계열(2009b=0.5mm 단일 해상도, 2009c=1~4mm) ⚠️ → 실무상 동일 공간 취급 가능성 높으나 PoC에서 겹쳐 보고 확인
   - MIAL·MASSP는 이미 2009cAsym으로 재표본된 `dseg`가 TemplateFlow S3에 있음 ✅(NOTICE의 URL) → **작업 공간을 MNI152NLin2009cAsym으로 통일**하는 것이 가장 수월
   - 직접 정합: `antsRegistrationSyN.sh -d 3 -f B -m A -o out_` → `antsApplyTransforms -n GenericLabel -t out_1Warp.nii.gz -t out_0GenericAffine.mat` (ANTsPy: `ants.registration(type_of_transform="SyN")` + `apply_transforms(interpolator="genericLabel")`) ⚠️
   - nervous-system-atlas는 대부분 아핀/유사 변환만 쓰고(AAN은 1~2mm 오차 감수), ANTs SyN은 선택적 extra로 CerebrA에만 사용 ✅

### 뷰어
- **three.js r186 (2026-09-08)** ✅. WebGPU는 WebGL2 폴백 전제 ⚠️
- **반투명 다중 메시 — 선택지 현황**:
  - **A. 고스트 셰이더 방식(권장 1순위)**: 선택 구조는 불투명, 나머지는 `transparent:true, depthWrite:false`, 극저 불투명도 + fresnel 림. nervous-system-atlas가 실제로 이렇게 함 ✅(`src/scene/materials.ts`: dimmed = `opacity ≤ 0.03, depthWrite:false, renderOrder 5`, `MeshPhysicalMaterial`에 `onBeforeCompile`로 fresnel 림 주입, 불투명도 구간별 `renderOrder` 0/1/5/6/10). 정렬 아티팩트가 눈에 띄지 않는 영역으로 불투명도를 낮추는 실용적 회피책
  - **B. `alphaHash`**(r154~ ⚠️): 디더 방식이라 정렬 문제 자체가 없음. 노이즈는 TAA로 완화하나 카메라가 움직이면 다시 보임 ⚠️
  - **C. 공식 OIT**: **`OITPassNode`(가중 혼합 OIT, McGuire/Bavoil)가 r186에 포함** ✅(PR #34253, 2026-08-15 병합, milestone r186, r186 태그에 `examples/jsm/tsl/display/OITPassNode.js`·`examples/webgpu_oit.html` 존재). **WebGPURenderer 전용.** 1차 문서의 "three.js는 OIT 미지원"은 r186부터 WebGPU 한정으로 틀림. WebGLRenderer용 공식 OIT는 여전히 없음
  - D. 서드파티: `stevinz/three-wboit`(MIT, r152+), `gkjohnson/three-depthpeeling-demo`(MIT) — 최신 three 호환·유지 상태 미확인 ⚠️
- **BatchedMesh**: r159에 core 편입, `setVisibleAt`/`setColorAt`, raycast가 `batchId` 반환, 객체별 절두체 컬링·정렬 ⚠️. **r183에서 인스턴스별 불투명도 지원** ✅(PR #32725 "Enable per-instance opacity", 2026-01-19 병합 — 4성분 색의 알파를 셰이더에서 사용). three-mesh-bvh에 `computeBatchedBoundsTree` 있음 ⚠️. → 수백 메시를 draw call 1~2개로 줄이면서 하이라이트/고스트 전환 가능. nervous-system-atlas는 BatchedMesh 없이 개별 메시 + three-mesh-bvh(`firstHitOnly`, 프레임당 1회 raycast)로 592 메시를 처리 ⚠️
- 성능 수치: 300~1000 메시·2~10M 삼각형 규모의 1차 출처 벤치마크는 찾지 못함 ⚠️. iOS Safari WebGL 메모리 한계(300~500MB 추정)는 공식 수치 없음 ⚠️ → PoC에서 실측
- 단면: clipping plane + stencil cap(공식 예제 `webgl_clipping_stencil`), 2D 슬라이스 패널은 NiiVue(BSD-2) ⚠️
- 경로: QuickBundles(DIPY)로 대표 곡선 추출 → `TubeGeometry` + UV 스크롤 셰이더 ⚠️. (nervous-system-atlas는 튜브 렌더러 없이 waypoint 메시 하이라이트 위주 ⚠️)
- 호스팅: Cloudflare R2(egress 무료) + Pages ⚠️

### nervous-system-atlas — 포크 vs 참고 판단 근거
- ✅ 확인: Vite 8 + TypeScript 7 + **바닐라 three.js 0.185.1**(React 없음) + three-mesh-bvh + fuse.js. 파이프라인은 Python(`pipeline/atlas_pipeline`, uv). 코드 Apache-2.0, 콘텐츠·생성 메시 CC BY-SA 4.0. 95 커밋, 별 48, 마지막 push 2026-09-16. `public/data/`는 gitignore지만 **릴리스에 `atlas-data-v1.0.2.tar.gz`(45MB)로 메시 배포** → `npm run data`로 받아 바로 실행 가능
- ⚠️ 에이전트 보고: zod 스키마(`content/schema/pathway.ts`): `neuronChain[{order, cellBody, synapse}]`, `decussation{level, structureId?, note}`, `waypoints[{order, structureId, meshId?, mni?, sideRelativeToOrigin}]`, `lesionEffectsByLevel[{level, effects, side}]`, `clinical{pearls, syndromes}`, `citations`, i18n(`names.tr`). 매니페스트는 `mesh.id` + `structureId` + 원본 라벨값 배열. vitest + Playwright 테스트 있음. AI 에이전트로 작성된 흔적(`CLAUDE.md`, `AGENTS.md`, `tools/author/batch01~33`)
- **판단: 참고만(포크하지 않음) 권장.** 이유: (1) 생성 메시가 CC BY-SA라 포크하면 수익화 여지가 좁아짐, (2) 원본 아틀라스 원자료는 repo에 없어 파이프라인 재실행 필요, (3) 콘텐츠 2,300여 파일이 영어/터키어 중심이라 한국 의대 커리큘럼용으로는 거의 새로 써야 함, (4) 우리 백본(NextBrain)은 저쪽이 쓰지 않는 소스. **가져올 것**: 경로 스키마 구조, 매니페스트 설계, 고스트 머티리얼 상태 기계, weld 방식 메시 파이프라인(Apache-2.0 코드는 저작자 표시 후 재사용 가능). 로컬에서 한 번 실행해 렌더링 품질을 직접 보는 것은 가치 있음.

### 지식 레이어 (구조 ↔ 과정 DB)
- 중추신경 경로의 공개 기계가독 DB 없음: NeuroNames·BAMS 접속 불가 ⚠️, **SCKAN은 자율·말초신경 한정(CC BY 4.0 ⚠️ Zenodo 18840513)** → 수작업 큐레이션
- **스키마 참고**: SCKAN/ApiNATOMY의 핵심 모델 = "뉴런 집단 N은 A(세포체 위치)에서 C(축삭 경유 구조, 신경 포함)를 거쳐 B(축삭 종말)로 투사" + 감각 종말, 표현형, forward connection(1차→2차 뉴런 시냅스) ⚠️(Imam 2025, Front Neuroinform). nervous-system-atlas의 `neuronChain`/`waypoints`/`decussation`/`lesionEffectsByLevel`과 결합하면 교육용으로 충분
- 권장 스키마: `Structure`(id, 이름 ko/en/la, 상위, mesh id, UBERON/TA2 참조) / `Pathway`(분류, 기능, 임상) / `PathwayStep`(순서, 뉴런 차수, 세포체 구조, 경유 tract, 시냅스 구조, 좌우/교차 수준, 신경전달물질, 근거 인용) / `Lesion → Deficit`(수준, 쪽, 증상)
- **용어 체계**:
  - UBERON: **CC BY 3.0** ⚠️(OBO Foundry 페이지). 핵 단위까지 포함(nucleus ambiguus UBERON:0001719, VPL UBERON:0002942, EW는 UBERON:0002141의 동의어) ⚠️ → **기본 식별자로 권장**
  - TNA(FIPAT 2017): "CC BY-ND 4.0 … The individual terms in this terminology are within the public domain" ⚠️(에이전트가 Front Matter PDF 확인). 개별 용어 사용은 자유, 편집물 재구성은 FIPAT 허가 대상. 기계가독 공식판 없음(Wikidata P1323 TA98 ID / P7173 TA2 ID) ⚠️
  - FMA: OBO Foundry에 "inactive", 라이선스 custom 표기 ⚠️. CC BY 3.0이라는 말은 스니펫뿐 ❓ → 쓰지 않음
  - Allen HBA 온톨로지: Allen 일반 약관은 비상업 ⚠️(3D 2020 아틀라스만 CC BY 4.0)
  - **한국어 용어**: 대한의사협회 의학용어집(term.kma.org)은 "사전 승인 없이 무단전재 및 재배포" 금지 ⚠️, 대한해부학회 사이트는 "ALL RIGHTS RESERVED"·검색 DB/공개 데이터 없음 ⚠️. Wikidata에 일부 한국어 라벨 존재(의문핵 등) ⚠️. → 개별 용어 자체는 저작물성이 낮지만 **용어집을 통째로 옮기지 말고**, 도메인 담당자가 해부학용어 6판을 참고해 필요한 수백 개만 직접 입력하는 방식이 안전. 대량 사용 시 학회 문의
- **표준 경로 목록의 근거 자료** — 이번 조사에서 **원문 목차를 여는 데 실패** ❓: Haines 아틀라스 8장("Tracts, Pathways, and Systems…"), Blumenfeld 3e, Purves 6e 장 제목은 검색 스니펫 수준 ⚠️. 의사 국가시험 필기 평가목표집(kuksiwon.or.kr notice seq=1790, PDF 첨부)과 KAMC 「기본의학교육 학습성과: 과학적 개념과 원리 중심」은 문서 존재만 확인하고 내용 추출 실패 ⚠️. → **도메인 담당자(성연)가 교과서·학습성과집 실물로 목록을 확정**하는 것이 가장 빠름. 분류 틀(안): 체성감각 / 운동(피질척수·피질연수·추체외로) / 뇌신경 반사(동공·각막·구역·턱반사·전정안구) / 시각·안구운동 / 청각·전정 / 자율신경·시상하부 / 소뇌 회로 / 기저핵 직접·간접·hyperdirect / 변연계·Papez / 각성·수면 / 통증 조절 / 언어·주의 네트워크 / 척수 반사
- 초기엔 스프레드시트 → JSON. 백엔드 불필요

---

## 5. 경쟁 환경·교육 근거

- **nervous-system-atlas** ✅: 2026-09-09 생성, 592 메시, 경로 웨이포인트·병변 모드·퀴즈, 영어/터키어, 코드 Apache-2.0·콘텐츠 CC BY-SA 4.0, 기여자 1명. 차별화: 한국어·의대 커리큘럼 정렬, 생리학(반사·기능) 통합, 시상·편도 세분(NextBrain), 뇌신경핵, 시험 대비.
- 상용(Complete Anatomy, Visible Body, BioDigital, IMAIOS, Kenhub, MEDICALIP MDBOX): "경로 클릭 → 참여 구조 하이라이트" 기능 확인되지 않음 ⚠️. Complete Anatomy 학생 페이지에서 확인된 것은 근육 신경지배 시각화·구조 isolate/fade뿐 ✅(CNS 경로 언급 없음). 에이전트가 보고한 "Innervation Pathway tool" 인용은 해당 페이지에서 재확인되지 않음 ⚠️
- **atlas-neuro.com**: 직접 열면 "NeuroAtlas — Interactive 3D Brain Atlas" 제목의 JS 앱(내용 렌더링 안 됨) ✅. 에이전트는 신경 탐침 제조사(ATLAS Neuroengineering)로 보고 → 도메인 혼동으로 판단, 기능·제작자·가격은 여전히 미확인 ❓(브라우저로 직접 열어볼 것)
- **Sylvius 4 Online**(OUP): 표면·단면·시각 용어집 중심 ✅. 에이전트가 보고한 "Pathways" 기능은 OUP 페이지에서 확인되지 않음 ⚠️
- Visible Body 생리학 애니메이션↔3D 연동, TeachMeAnatomy 3D 경로 페이지 동작: 공개 페이지에서 확인 불가 ⚠️
- 한국: MDBOX(메디컬아이피)가 서울대·제주대·충북대 의대에서 사용된다는 보고 ⚠️. 의학도서관의 Complete Anatomy/Visible Body 구독 공지는 찾지 못함 ⚠️ → 성연을 통해 실제 학생 사용 도구를 묻는 편이 정확
- 가격대 ⚠️: Complete Anatomy 학생 $74.99/년, Visible Body 학생 $34.99/년, Kenhub $39/월, 기관 라이선스는 전부 견적제
- 교육 효과:
  - Ekstrand 2018 RCT(N=64) ✅: 지식 점수는 VR ≈ 종이, 그러나 "신경해부가 덜 두려워졌다" 81% vs 12%
  - Han 2024 메타분석 ✅: neurophobia 유병률 46% (24개 연구, N=10,395), **아시아 54%**
  - 메타분석들 ⚠️: 3D/VR 지식 효과 SMD 0.3~0.6(이질성 큼), AR 단독은 무효(Salimi 2024)
  - → 소구점은 "성적 향상"보다 **neurophobia 완화·동기 부여·해부-생리 통합**

---

## 6. 권장 진행 순서

1. **PoC — 완료(§6-1)**. 당시 계획:
   - 데이터: **NextBrain 원본 `atlas.labels.argmax.nii.gz`(CC0, 0.2mm, 13MB — `3dAtlas.zip`에서 이 파일만 range 요청으로 추출 가능)** + AAN v2.0(CC0, MNI 1mm). 메모리 주의: 460×1145×910 float32 ≈ 1.9GB → 라벨별 bounding box로 잘라 처리하거나 uint16으로 변환
   - 메시: 시상핵(VPL·VPM·VL·VA·MD·LGN·MGN), 기저핵, 적핵·SN, 해마, 뇌궁·유두시상로, 소뇌핵, 박·쐐기핵, 내측섬유띠, 안면·외전·삼차·전정핵, MLF, 뇌간 외형 + AAN 핵 등 20~30개. 우반구는 좌우 반전
   - 경로: **후섬유단-내측섬유띠(박/쐐기핵→내측섬유띠→VPL), Papez 회로(해마→뇌궁→유두체→유두시상로→AV→대상회), 수평 주시/전정안구반사(전정핵→MLF→외전·동안핵)** 가 현 데이터로 표현 가능. 무릎반사는 척수 데이터(PAM50 라이선스 미해결)가 없어 placeholder 필요, 동공반사는 시개앞핵·EW가 극소/통짜라 보정 필요
   - 검증 항목: 고스트 셰이더(A안) 품질, BatchedMesh(r183+) 인스턴스별 불투명도, 0.2mm argmax에서 뽑은 소핵 메시의 품질(극소 핵을 확률지도에서 재추출해야 하는지), NextBrain↔AAN 좌표 일치도, 모바일 메모리
2. NextBrain 확률 아틀라스 원본(라벨별 확률지도) 구조 확인 — 극소 뇌간 핵을 임계값 처리로 복원할 수 있는지
3. 구조·경로 스프레드시트 템플릿 확정 → 도메인 담당자가 표준 경로 목록과 기본 경로 채움
4. 뇌간 뇌신경핵·누락 전도로 수작업 모델링 방식 결정(Edlow 100µm 위 Slicer 분할 vs 단순 형상)
5. 라이선스 문의: PAM50(NeuroPoly), SUIT(Diedrichsen lab), 필요 시 Petersen 2019(CWRU), Brainstem Navigator
6. nervous-system-atlas를 로컬 실행해 렌더링·UX 참고(포크하지 않음)

## 6-1. PoC 결과 (2026-09-20, `poc` 브랜치)

구현: `pipeline/`(Python 메시 파이프라인) · `content/`(구조 50개, 경로 3개 JSON) · `viewer/`(Vite + TS + three.js r186). 실행법은 루트 `README.md`.

**검증된 것** ✅ (직접 실행·측정)
- **데이터 → 메시가 자동으로 된다**: Figshare zip에서 13MB만 받아 105 메시(50구조×좌우, 58만 면)를 14초에 생성, meshopt 압축 후 **GLB 3.9MB**. 뷰어 JS는 gzip 200KB.
- **고스트 렌더링(A안)이 통한다**: 선택 구조는 불투명, 나머지는 fresnel 림 위주의 극저 알파 + `depthWrite:false`. 100여 개가 겹쳐도 정렬 아티팩트가 눈에 띄지 않음. OIT·alphaHash는 필요 없었음.
  - 실제로 부딪힌 문제는 정렬이 아니라 **"안개"**: 작은 구조로 확대하면 카메라가 윤곽 메시 안으로 들어가 앞쪽 층들이 스침각으로 겹쳐 뿌옇게 됨 → (1) 카메라~초점 사이 조각을 거리 기반으로 페이드, (2) 윤곽 메시의 내부 공동(뇌실)을 메워 안쪽 면 제거로 해결.
- **성능 여유 큼**: Apple M5 Pro(ANGLE Metal)에서 프레임 제한을 풀고 약 800fps, draw call 105, JS heap 39MB. 개별 메시 방식으로 충분 → **BatchedMesh는 수백 메시 규모가 될 때까지 불필요**(이번에 시험하지 않음). 모바일 실기기는 미측정.
- **아틀라스 간 좌표 일치**: NextBrain 청반과 Harvard AAN 청반의 중심 거리 **1.36mm** → 추가 정합 없이 섞어 쓸 수 있는 수준.
- **경로 기능**: 기시쪽(좌/우) 전환 시 ipsi/contra가 뒤집히는 구조, 단계별 재생, 교차 표시, 구조 클릭 → 해당 단계 이동, 검색, 그룹 표시 전환. 단위 테스트(pytest 10, vitest 8) + 브라우저 e2e 5개 통과.

**데이터에서 새로 알게 된 것** ✅
- argmax 볼륨은 라벨마다 파편이 수십~수백 개(예: 내측섬유띠 263조각) → "1복셀 닫기 + 최대 덩어리의 10% 미만 제거"가 필수. 제거 후에도 주 덩어리가 94~99%.
- 가우시안 평활 후 0.5 등치면을 쓰면 5~30mm³급 핵의 부피가 20~47% 줄어듦 → **마스크 복셀 수와 같은 부피를 감싸는 등치 수준을 고르는 방식**으로 해결(대부분 ±10% 이내).
- **NextBrain의 뇌활은 두 조각뿐**(앞쪽 기둥·몸통 일부 + 해마술). 몸통~다리 구간 라벨이 없음 → 경로선은 조각별 중심선을 이어 빈 구간을 곡선으로 보간. 제품에서는 수작업 보완 대상.
- 띠이랑·해마처럼 휜 구조는 무게중심이 구조 밖에 놓임 → 경로선은 측지거리 기반 중심선을 따라가게 함.
- 동안신경핵(0.4mm³)·혀밑신경핵(4.9mm³, 파편화)은 타원체로 대체(뷰어에 "근사" 표시). 외전핵(5.2mm³)은 메시가 되지만 실제 크기보다 작을 가능성.

**추가 (같은 날)**: 가로 단면 패널 — 라벨 볼륨을 라벨 id 인코딩 PNG 393장(7.5MB, 지연 로딩)으로 내보내 3D와 연동(높이 표시면, 3D 자르기, 선택 따라가기, 333개 라벨 전부 표시). 성연의 요청과 JKMS 2023 뇌줄기 단면 논문(You & Park, CC BY-NC, 데이터 비공개 → 저자 문의 필요)의 3평면+3D 구성을 참고.

**알려진 한계**
- **정중선 틈**: NextBrain 반구의 안쪽 절단면이 평면이 아님(높이에 따라 안쪽 가장자리가 x = −1.0 ~ +1.2mm, 뇌줄기 일부 높이에서는 중앙값 −4mm). x=0 기준 좌우 반전이라 뇌줄기 좌우 반쪽 사이에 최대 2~4mm 틈이 생기거나 겹침. 3D 메시와 2D 단면 모두 해당. 해결하려면 높이별 정중선 보정 또는 양반구 아틀라스 필요.
- 경로 설명·한국어 용어는 전부 초안(도메인 검수 전). 해부학적 위치·형상의 타당성도 수치(부피·중심)로만 점검.
- 감량(quadric) 후 일부 메시에 비다양체 모서리 1~5개(렌더링 영향 없음). 인접 구조 간 공유 경계는 보장하지 않음(구조별 독립 메싱) → 제품 단계에서 `vtkSurfaceNets3D` 검토.
- 윤곽(대뇌반구)은 0.8mm 재표본 + 평활이라 고랑이 메워진 형태. 척수·속섬유막·말초 구조 없음.
- 오른쪽 반구는 좌우 반전본.

## 7. 조사 한계

- 2차 조사도 세션 웹 검색 한도(200회) 안에서 에이전트당 10~15회로 제한해 진행. 유료벽·JS 렌더링·403으로 열지 못한 1차 출처가 다수(교과서 목차, KAMC·국시원 PDF, FMA, WIKIBrainStem, Brainstem Navigator 라이선스 파일).
- NextBrain은 argmax 볼륨의 헤더·라벨값·부피만 확인. 메시 품질, 정확한 MNI 변형, 확률지도 원본(2.5GB `SegmentationCode.zip`)은 열지 않음.
- 상용 제품의 기능 부재는 공개 페이지 기준이며 직접 사용해 본 것은 아님.
- ⚠️ 항목은 에이전트가 1차 출처를 열었다고 보고했으나 메인 세션이 재확인하지 않은 것. 사용 결정 전에 재확인 필요.
