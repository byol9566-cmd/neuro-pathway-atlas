# 근거 데이터 검토 기록

수집: 서브에이전트(Sonnet) — 규칙은 `AGENT_BRIEF.md`. 검토: 메인 세션.
검토는 두 층으로 한다.

1. **기계 대조** (`verify_quotes.py`): 출처의 원문을 받아 ID 실재 여부·제목/연도 일치·인용문이 원문에 있는지 확인. 결과는 `verification/<batch>.report.json`.
2. **판단** (이 문서): 출처의 급, 주장이 인용문보다 더 나갔는지, 단일 출처 의존, 종(種), 출처 간 충돌.

출처 등급
- **A** 동료심사 리뷰·해부학 원저 (인지도 있는 학술지, PMC 전문 확인)
- **B** 교과서(Purves *Neuroscience*, NCBI Bookshelf) · StatPearls — 내용은 대체로 표준적이나 장(章)마다 질 편차가 있고 1차 근거가 아님
- **C** 그 외(소규모 학술지, 인용 거의 없음) — 단독 근거로 쓰지 않음
- **X** 약탈적·정체불명 → 삭제

라이선스 주의: StatPearls는 CC BY-NC-ND 4.0. **사실(fact)은 저작권 대상이 아니므로 근거로 인용하는 것은 문제없지만, 문장을 제품 텍스트로 옮겨 쓰면 안 된다.** 이 폴더의 인용문은 검증용 발췌이며 뷰어에 그대로 싣지 않는다.

---

## somatosensory (2026-09-20)

**기계 대조**: 인용 85개 — exact 82, fuzzy 3(점수 0.98~0.99, Wallenberg 장의 표 서식 차이), NOT_FOUND 0. 출처 15개 모두 원문 확보, NBK/PMCID 실재, 제목 일치.

**출처 구성**: StatPearls 13 (B), 리뷰 1 — Kang & Im, *Korean J Neurotrauma* 2023, PMC10567534, CC BY-NC (대한신경손상학회지, PMC 등재, 피인용 4 → **B+**; A로 보기엔 학술지 영향력·피인용이 낮음). A급 출처 없음.

**판단**
- DCML 단계별 주장과 인용문을 대조 — 주장이 인용문 범위 안에 있음(뉴런 차수, 속활꼴섬유 교차 위치 "caudal medulla", VPL, 속섬유막 뒤다리 뒤 1/3). 핵심 사슬이 독립 출처 2개(S1/S2 StatPearls + S7 리뷰)로 받쳐짐 ✅
- **단일 출처 의존**: 삼차신경 체성감각 경로는 인용 10개가 전부 StatPearls 한 장(S5)에서 나옴 ⚠️ → 보강 필요. 하행 통증조절도 StatPearls 3개 장뿐 ⚠️ (이 주제는 Basbaum/Fields, Ossipov 등 A급 리뷰가 많으므로 교체 가능)
- **널판/쐐기다발 경계 분절**: S7은 "T7 and below / C2–T7". 시제품 `content/pathways.json`에는 T6로 적어 둠. 교과서마다 T6/T7로 갈리는 항목 → 성연 확인 필요 ❓
- **수집자가 기록한 충돌 2건**
  1. 척수시상로 섬유가 교차 전 몇 분절을 오르는가: "two segments"(S3) vs "1 to 3 levels"(S4). 참고: 수집자의 쟁점 서술은 "2차 뉴런 섬유가 Lissauer로를 오른다"로 돼 있는데, 표준 서술은 **1차 구심섬유**가 Lissauer로에서 1~2분절 오르내리고 2차 뉴런 축삭은 앞백색맞교차에서 비스듬히 교차하는 것 → 서술 자체를 전문가가 바로잡아야 함 ⚠️
  2. 배쪽척수소뇌로의 정보 성격: 운동(원심성 사본) 정보(S6) vs 무의식 고유감각(S7, S13). 실제 문헌에서도 갈리는 항목 — 양쪽 다 표기
- **출처 없음으로 남긴 것**(수집자가 정직하게 분리함): DCML·척수시상로 시냅스의 글루탐산/물질 P, 척수그물시상 성분의 CL핵 종착, 아교질의 GABA/글라이신 억제. 모두 표준 교과서 내용이므로 Purves(Bookshelf)로 보강 가능

**결론**: 인용의 진실성은 확인됨. 근거의 급은 B 위주 → 뼈대로는 쓸 수 있으나, 삼차신경·통증조절은 A급 리뷰로 보강한 뒤 확정.

---

## morphometry (2026-09-20)

**기계 대조**: 인용 38개 — exact 37, fuzzy 1, NOT_FOUND 0. 출처 6개 모두 PMCID 실재, 제목·연도 일치(Europe PMC 등록 정보 기준).

**출처별 등급과 쓸모**

| 출처 | 등급 | 판단 |
|---|---|---|
| S1 Pauli 2018, *Sci Data* (CIT168, n=168, 피인용 477, CC BY) | **A** | STN·SNc·SNr·적색핵·유두체·고삐핵 부피. 표준으로 널리 쓰이는 아틀라스 논문 |
| S5 García-Gomar 2019, *Front Neurosci* (7T, n=12, 피인용 62, CC BY) | **A−** | 위·아래둔덕, LGN, MGN, 위올리브핵 부피. 표본이 작고 in vivo MRI로 보이는 범위만 측정 |
| S4 da Silva 2024, *Surg Radiol Anat* (CC BY) | **B** | 유두체의 AC-PC 좌표. 수술 해부학용, 우리 좌표계(MNI)로 직접 쓰기는 어려움 |
| S3 Erginoglu 2026, *Irish J Med Sci* (사체 n=40, 피인용 0) | **C+** | 넷째뇌실 바닥 표면 지표 거리. **혀밑신경삼각·미주신경삼각은 핵 자체가 아니라 표면 융기**이므로 핵 크기의 대용으로 쓰면 안 됨. 안면둔덕↔빗장 14.5mm는 뇌줄기 비율 점검용으로만 |
| S2 Dunlop 2026, *Alzheimers Dement* | A(학술지) / **용도 부적합** | 값은 단면당 뉴런 밀도(중앙값 60~83)인데 수집자가 `neuron_count`로 분류함 → 청색반점의 크기·총 뉴런 수 근거로 쓸 수 없음. 분류 오류 ⚠️ |
| S6 Fenske 2020, *NeuroImage Clin* | A(학술지) / **C(해당 값)** | PAG 길이 10~14mm·지름 4~5mm는 서론의 서술(2차 인용), MNI (4,−26,−14)는 fMRI ROI 중심으로 고른 좌표 — 둘 다 해부학적 측정값이 아님 ⚠️ |

**수집 실패(정직하게 `notFound` 29개로 기록됨)**: 정작 필요했던 눈돌림·도르래·갓돌림신경핵, 삼차신경핵 4종, 얼굴신경핵, 안뜰핵 4종, 달팽이핵, 고립로핵, 의문핵, 미주등쪽핵·혀밑신경핵 본체, 널판·쐐기핵, 아래올리브, 신경로 굵기 전부. → 공개 전문(OA)에서는 찾기 어려움. 다음 시도: Büttner-Ennever/Horn의 안구운동핵 조직학 논문, Paxinos 아틀라스 계측, Olszewski & Baxter — 대부분 유료/단행본이라 성연의 도서관 접근이 더 빠를 수 있음.

**우리 메시와의 대조 (한쪽, mm³)** — 이 배치의 가장 쓸모 있는 결과

| 구조 | 문헌 (A급) | NextBrain 메시 | 비 |
|---|---|---|---|
| 유두체 | 62–64 (S1) | 61.9 | 1.0 |
| 적색핵 | 298–301 (S1) | 353.0 | 1.2 |
| 흑색질 (SNc+SNr) | 393–405 (S1) | 572.9 | 1.4 |
| 시상밑핵 | 128–135 (S1) | 334.9 | **2.5** |
| 안쪽무릎핵 | 57–66 (S5) | 102.2 | 1.7 |
| 위둔덕 | 71–75 (S5) | 172.3 | **2.4** |
| 아래둔덕 | 55–60 (S5) | 157.6 (중심핵 라벨만) | **2.7** |
| 가쪽무릎핵 | 93–101 (S5) | 352.2 | **3.5** |

해석(미확정 ❓): 유두체·적색핵은 잘 맞으므로 복셀 크기·좌표 스케일 오류는 아님. 1.2~1.4배는 MNI 공간이 실제 뇌보다 큰 것과 방법 차이로 설명 가능. **2.4~3.5배인 STN·둔덕·LGN은 별도 확인 필요** — 가능한 원인: (a) in vivo MRI는 대비로 보이는 부분만 그려 과소 추정(예: 지름 6~7mm 구형인 아래둔덕은 기하학적으로 110~180mm³가 자연스러움), (b) NextBrain 조직학 경계가 더 넓음(위둔덕 깊은 층, LGN 주변 포함), (c) 5증례 확률 아틀라스의 argmax가 경계를 부풀림. → 성연에게 "LGN·STN이 눈으로 봐서 너무 크지 않은지" 물어볼 것. 문헌의 조직학 기반 값(예: LGN 조직학 부피)을 추가 수집해 교차 확인.

**결론**: 인용은 전부 진짜. 쓸 수 있는 것은 S1·S5의 부피(메시 검증용)뿐이고, 원래 목적(타원체 대체 핵의 크기)은 달성하지 못함.

---

## motor (2026-09-20)

**기계 대조**: 인용 119개 — exact 106, fuzzy 13, NOT_FOUND 0. 출처 17개 모두 실재, 저널 논문 4편은 제목·연도가 Europe PMC 등록 정보와 일치.

**출처 구성**: StatPearls 13 (B) + 저널 4편. 저널 4편은 인용문은 진짜지만 **해부학의 권위 있는 근거로는 약함**:
- S14 *Eur J Pain* 2025 체계적 고찰(도피반사 신경생리 평가 권고) — A−. 단 주제가 측정법이라 회로 해부의 근거로는 간접적
- S15 *Tremor Other Hyperkinet Mov* 2026 리뷰(파킨슨 떨림의 진동 네트워크 모델, 피인용 0) — B. hyperdirect 경로 근거로 썼지만 **가설 모델 논문**이라 해부학적 사실의 1차 근거로 부적합 ⚠️ → Nambu 2002 (hyperdirect 개념 원저) 같은 표준 문헌으로 교체 권장
- S16 *Int J Mol Sci* 2025 (FMR1 전돌연변이와 소뇌다리, 피인용 0, MDPI) — C+. 소뇌다리·위소뇌다리교차 서술을 **질병 논문의 배경 설명**에서 가져옴 ⚠️
- S17 *J Neurosurg Case Lessons* 2026 **증례 보고** — C. Guillain–Mollaret 삼각의 근거가 증례 1건의 서론 ⚠️ → 비대올리브변성 리뷰로 교체 권장

**판단**
- 수집자 보고대로 핵심 사슬(피질척수로, 피질핵로, 바닥핵, 소뇌 출력, 반사궁)은 출처 2개로 받쳐지나, 두 번째 출처가 대부분 또 다른 StatPearls 장 → "독립 출처 2개"라기보다 같은 계열 2개. A급 교차 확인은 없음
- **충돌 1건(수집자 기록)**: 피라미드교차에서 교차하는 비율 — ">90%"(S1) vs "70~80%"(S13). 교과서도 75~90%로 갈림 → 뷰어에는 범위로 표기하고 성연 확인 ❓
- **출처 없음으로 분리된 것**: 소뇌 반구 병변이 같은쪽 증상인 이유를 "이중 교차"로 설명하는 문장(두 교차 각각은 출처 있음, 종합 서술은 없음), 조롱박세포 출력의 GABA, 적색핵→아래올리브의 중심뒤판로 명칭, 교차폄반사. 전부 표준 교과서 내용 — Purves/Kandel로 보강 가능. 수의학(개·고양이) 리뷰를 사람 해부 근거에서 **제외한 판단은 적절**
- fuzzy 13개는 모두 0.9 이상이나 exact가 아니므로 표본 확인 필요(아래 점수 참조). StatPearls HTML의 특수문자·위첨자 차이로 추정

**결론**: 인용 진실성 확인. 등급은 B 위주 + 부적합 저널 3편. hyperdirect·Guillain–Mollaret·소뇌다리는 출처 교체 후 확정.

---

## brainstem-reflexes (2026-09-20)

**기계 대조**: 인용 80개 — exact 80, NOT_FOUND 0. 출처 17개 모두 실재, 저널 3편 제목·연도 일치. (수집자 보고는 "StatPearls 15 + 리뷰 2"였으나 실제 파일은 StatPearls 14 + 저널 3 — 보고와 산출물의 사소한 불일치.)

**출처 구성**: StatPearls 14 (B) + 저널 3편
- S10 Lee & Chau 2025, *Front Surg* — 수술 중 눈깜박반사 감시에 관한 **원저(research-article)**, 피인용 1. 각막반사 구심로가 "주감각핵"에서 시냅스한다는 주장의 유일한 근거인데, 수술 감시 논문의 배경 서술임 → **C+**, 단독 근거로 부적합 ⚠️
- S13 Brown 2026, *Physiol Rep* 리뷰(만성 기침 기전, 피인용 0) — B. 기침반사 구심로에 한해 적절
- S17 Colombari 2026, *Curr Hypertens Rep* 리뷰(피인용 0) — B+. 압력수용기반사의 NTS→CVLM→RVLM 사슬에 적절(이 분야 연구자의 리뷰)

**판단**
- **원문 자체의 오류 발견** ⚠️: S6(StatPearls "Vestibular Pathways") 인용문 — "Using first-order sensory neurons of **cranial nerve V**, most of the semicircular canal inputs synapse at the superior and medial nuclei". 인용은 원문과 일치하지만 **원문이 틀림**(안뜰 구심은 VIII). 기계 대조는 "그 문장이 거기 있다"만 보장하고 "그 문장이 맞다"는 보장하지 않는다는 실례 → 이 인용은 근거에서 제외하고, StatPearls 단독 근거 항목은 전부 교차 확인 대상으로 둔다
- **시제품 VOR 경로와의 일치** ✅: S5(StatPearls "Vestibulo-ocular Reflex")의 "left semicircular canal → left vestibular nuclei → right abducens nucleus … interneurons ascend in the MLF to stimulate the left oculomotor nucleus"는 `content/pathways.json`의 hvor 사슬(같은쪽 안뜰핵 → 반대쪽 갓돌림신경핵 → 같은쪽 MLF → 같은쪽 눈돌림신경핵)과 좌우까지 일치. 다만 근거가 B급 1개뿐
- **충돌 2건(수집자 기록)**
  1. 수평 VOR을 매개하는 안뜰핵: "위·안쪽안뜰핵"(S5, S6) vs 특정 핵을 지목하지 않고 Deiters 오름로 등 여러 경로를 나열(S7). 실질적 모순이라기보다 서술 수준의 차이 — 시제품은 안쪽안뜰핵만 강조하고 있으므로 위안뜰핵을 함께 표시할지 성연 확인 ❓
  2. 각막반사 구심로의 1차 시냅스: 삼차신경척수핵(S9) vs 주감각핵(S10). 눈깜박반사의 R1(초기, 다리뇌 주감각핵 경유)·R2(후기, 척수핵 경유) 성분으로 설명되는 항목인데 수집자가 이 설명을 **출처 없는 가설로 분리해 둔 것은 적절**. A급 근거(Cruccu, Kimura, Aramideh & Ongerboer de Visser의 눈깜박반사 생리 리뷰)로 보강 필요
- **출처 없음**: ipRGC/멜라놉신, Cajal 사이질핵의 적분기 역할, 턱반사 항진의 임상 의미, Wallenberg–Horner 연결(1차 교감신경로의 뇌줄기 주행) 등. 마지막 항목은 임상적으로 중요하므로 우선 보강

**결론**: 인용 진실성 100%. 그러나 이 배치는 "인용이 진짜여도 원문이 틀릴 수 있다"는 사례(S6)를 포함 — B급 단독 근거는 확정으로 승격하지 않는다.

---

## special-senses (2026-09-20)

**기계 대조**: 인용 66개 — exact 66, NOT_FOUND 0. 출처 14개 모두 실재, 저널 5편 제목·연도 일치.

**출처 구성** — 지금까지 배치 중 **가장 좋음**: StatPearls 8 (B) + 저널 5편 + Purves 1
- S13 *Annual Review of Psychology* 2024 (사람 후각계, 피인용 32) — **A**
- S9 *Cerebral Cortex* 2023 (사람 안뜰겉질 OP2의 기능해부, 원저, 피인용 29) — **A**
- S6 *Front Neurol* 2018 (올리브달팽이 원심계: 동물과 사람, 피인용 108) — **A−**
- S4 *Front Neurosci* 2023 (등쪽 LGN과 시상베개, 피인용 14) — **A−**
- S8 *Brain Sciences* 2024 (전기자극에 의한 안뜰겉질 위치, 체계적 고찰, MDPI, 피인용 5) — **B**
- S14 Purves *Neuroscience* 2판 (NBK11071) — B. 단, 수집자 기록대로 Bookshelf의 **검색 미리보기 발췌만** 열 수 있었음(출판사 제한) → 장 전체 문맥은 확인 못 한 인용

**판단**
- **종(種) 표시가 제대로 됨** ✅: 시각 경로의 S4 인용 3개와 청각 경로의 S6 인용 3개에 `species: animal` 표시. 올리브달팽이 원심계(MOC/LOC의 교차/비교차)는 동물 해부가 근거이므로 뷰어에 옮길 때 "사람에서는 추정" 단서를 달 것
- **충돌 2건(수집자 기록)** — 둘 다 실제 학계의 미해결 쟁점이라 기록이 적절
  1. 안뜰겉질: 단일 핵심 영역 OP2(S9) vs 경계가 불분명한 넓은 네트워크(S8)
  2. 미각 3차 투사: 같은쪽만(S10) vs 교차·비교차 둘 다(S11)
- **출처 없음**: 청각부챗살의 렌즈밑 속섬유막 주행, "일측 중추 병변은 난청을 거의 일으키지 않는다"(근거가 되는 양측성 표상은 출처 있음), 미각의 중심뒤판로 주행과 영장류-설치류 차이(팔곁핵 중계), 앞맞교차의 후각 교련 연결. 중심뒤판로 항목은 시제품에 쓸 가능성이 높으므로 우선 보강(Pritchard, Small 등의 영장류 미각 리뷰)
- 시각 경로의 시야결손 대응(한눈 실명, 양귀쪽반맹, 같은쪽반맹, 위사분맹 "pie in the sky", 황반회피)은 전부 인용 있음 — 출처는 StatPearls 위주(B)이나 교과서적으로 이견이 없는 내용

**결론**: 인용 진실성 100%, A급 출처 4편 포함. 시각·후각·안뜰겉질은 뼈대로 채택 가능. 청각 원심계는 동물 근거 단서 필요.

---

## limbic-arousal-autonomic (2026-09-20)

**기계 대조**: 인용 70개 — exact 69, fuzzy 1, NOT_FOUND 0. 출처 20개 모두 실재. **서지 오류 1건**: S5의 연도를 2024로 적었으나 Europe PMC 등록은 2025 → 수정 필요(내용에는 영향 없음).

**출처 구성**: StatPearls 9 (B) + 저널 10편 + 단행본 장 1
- **A**: S1 *Brain Topography* 2023 (피질-변연-시상 회로 개정, 피인용 86) · S12 *Critical Care* 2020 (중환자의 뇌줄기 기능장애, 피인용 109) · S3/S5 *Hippocampus* 리뷰 2편(해마이행부 회로; H.M. 사례 재검토)
- **A−/B+**: S4 *Anat Sci Int* 2025(해마 구조) · S7 *iScience* 2026 원저(사람의 청각 "low road", 피인용 0 — 최신 단일 연구라 편도 저위로의 **사람 근거로는 아직 약함**) · S10 *Front Neurosci* 2026(VLPO) · S15 *Front Syst Neurosci* 2026 · S20 *NPP—Digital Psychiatry and Neuroscience* 2026(일주기 입문)
- **C**: S6 *Bioinformation* 2024 (편도 해부 리뷰) — 수집자가 스스로 저급 학술지로 표시함. 학술지 평판이 낮고 편집·심사 품질 논란이 있는 곳 → **단독 근거 불가**. 편도 핵 구분·출력로는 Sah 2003 (*Physiol Rev*), Janak & Tye 2015 (*Nature*) 등으로 교체
- S9 Springer 단행본 장(NBK595465, 감정 회로의 분자영상) — B

**판단**
- **StatPearls끼리의 모순 발견** ⚠️ (수집자 기록): ACTH 자극으로 코르티솔을 만드는 부신겉질 층 — "다발층(zona fasciculata)"(S14 *Physiology, Cortisol*) vs "그물층(zona reticularis)"(S13 *Neuroanatomy, Hypothalamus*). 표준 생리학은 다발층 → **S13이 틀림**. brainstem-reflexes 배치의 "CN V" 오류에 이어 두 번째 StatPearls 원문 오류 → StatPearls 단독 근거는 확정 금지 원칙 유지
- 해마이행부의 역할(삼시냅스 회로의 "네 번째 다리" vs 통합·재분배 허브): 한 리뷰(S3) 안의 전통적 견해와 최근 견해 — 학습용으로는 전통적 서술 + 각주
- **종 표시 적절** ✅: VLPO/수면 스위치 인용 일부에 `rat`, "설치류·사람 종합" 표시. 수면-각성 flip-flop 모델은 본래 설치류 연구 기반이므로 뷰어에 단서 필요
- **출처 없음**: 편도 중심핵→PAG 투사, 흑색질선조체 변성→파킨슨증, PVN→엉치 부교감핵 직접 투사, 멜라토닌 합성 효소, 해마 삼시냅스의 글루탐산. 앞의 둘은 교과서 기본 사항이라 Purves로 즉시 보강 가능
- 시제품의 파페츠 회로 사슬(해마이행부 → 뇌활 → 유두체 → 유두시상로 → 시상앞핵 → 띠이랑 → 띠다발 → 해마곁이랑/속후각겉질 → 관통로 → 해마)은 S1(A급)의 서술과 일치 ✅

**결론**: 인용 진실성 확인, A급 출처 4편. 파페츠·해마 회로·각성계는 뼈대로 채택 가능. 편도 회로는 S6 교체 후 확정.

---

## 전체 요약 (2026-09-20, 6개 배치)

| 배치 | 인용 | exact | fuzzy | NOT_FOUND | 출처 | StatPearls | A급 |
|---|---|---|---|---|---|---|---|
| somatosensory | 85 | 82 | 3 | 0 | 15 | 13 | 0 |
| motor | 119 | 106 | 13 | 0 | 17 | 13 | 0 (A− 1) |
| brainstem-reflexes | 80 | 80 | 0 | 0 | 17 | 14 | 0 |
| special-senses | 66 | 66 | 0 | 0 | 14 | 8 | 4 |
| limbic-arousal-autonomic | 70 | 69 | 1 | 0 | 20 | 9 | 4 |
| morphometry | 38 | 37 | 1 | 0 | 6 | 0 | 2 |
| **합계** | **458** | 440 | 18 | **0** | 89 | 57 | 10 |

- **날조된 인용·존재하지 않는 논문: 0건.** "실제로 연 원문에서만, 직접 인용과 함께" 규칙 + 기계 대조가 제대로 작동함.
- **그러나 인용이 진짜인 것과 내용이 맞는 것은 별개**: StatPearls 원문 오류 2건(안뜰 구심을 "CN V"로 표기, 코르티솔 생성층을 그물층으로 표기), 수집자의 분류 오류 1건(밀도를 뉴런 수로), 서지 연도 오류 1건, 부적합 근거(가설 모델·증례·질병 논문의 배경 서술·저급 학술지) 5편.
- **가장 큰 약점은 출처의 급**: 89개 중 57개가 StatPearls. 다음 수집은 새 주제 확장보다 **B급 단독 근거 항목을 A급 리뷰로 교체**하는 데 우선순위를 둘 것.
- **성연에게 물어볼 것**: 널판/쐐기다발 경계(T6 vs T7), 피라미드교차 비율(70~80% vs >90%), 수평 VOR에서 위안뜰핵 표시 여부, 각막반사 구심 시냅스(척수핵 vs 주감각핵), 배쪽척수소뇌로의 정보 성격, LGN·STN 메시가 너무 커 보이는지.

---

## upgrade-* (2026-09-22~23, A급 출처 교체 1차: PMC 무료 전문 19편)

배경: 6개 배치의 출처 89개 중 57개가 StatPearls(B급)였음. 사용자가 대학 도서관으로 유료 문헌을 받아 주기로 했고(목록 `wanted/WANTED.md`), 그 전에 **PMC에 무료 전문이 있는 A급 후보 19편**을 서브에이전트 3개가 열어 기존 주장에 대한 인용을 추출함(`upgrade-limbic.json`, `upgrade-motor-somatosensory.json`, `upgrade-brainstem-senses.json`). 기존 배치 파일은 건드리지 않았고, 통합은 성연 검수와 함께 나중에.

| 파일 | 출처 | 인용 | exact | fuzzy | NOT_FOUND | 비고 |
|---|---|---|---|---|---|---|
| upgrade-brainstem-senses | 7 | 29 | 27 | 2 | 0 | fuzzy 2는 구두점·연결 부호 차이(0.99, 0.94) |
| upgrade-motor-somatosensory | 5 | 27 | 27 | 0 | 0 | 빈 position 1개는 StatPearls 반대 입장 자리표시(의도된 것) |
| upgrade-limbic | 7 | 48 | 48 | 0 | 0 | S7 Fowler 2008의 5개는 PMC 봇 차단으로 한 번 실패했다가 차단이 풀린 뒤 재검증에서 전부 exact |

출처 등급: 19편 전부 A(Physiol Rev, Nature, Neuron, Brain, JNNP, Nat Rev Neurosci, Compr Physiol, Trends Neurosci, Front Neurol, Cerebellum, NeuroImage, Neurosci Biobehav Rev, Eye Brain, Neuropsychopharmacology). 다만 **리뷰 다수가 설치류·원숭이 연구의 종합**이라 수집자가 `species`를 정직하게 표시함 — 사람 해부학 서술의 근거로 쓸 때는 교과서(도서관 목록의 ★ 4권)로 한 번 더 받쳐야 함.

### 이번에 해결된 것
- **StatPearls끼리의 모순(코르티솔 생성층)**: Herman 2016 *Compr Physiol* — "ACTH acts on melanocortin 2 receptors (MC2R) in the zona fasciculata" → **다발층**으로 확정. StatPearls *Hypothalamus* 장의 "그물층"은 오류.
- **Guillain–Mollaret 삼각**: 증례 보고 1건 → Tilikete & Desestret 2017 리뷰. 반대쪽 치아핵 → 위소뇌다리(교차) → 같은쪽 적색핵 → 중심뒤판로 → 아래올리브핵까지 한 문장으로 서술되고, 병변 측성도 받쳐짐. motor 배치의 `unsourced`였던 "중심뒤판로" 이름도 해결.
- **얼굴 겉질숨뇌로의 고리 주행**(숨뇌 아래까지 내려갔다 교차 후 되올라감): Kanbayashi & Sonoo 2021(사람, Wallenberg 환자) — 기존 StatPearls 서술보다 정밀.
- **편도 중심핵 → PAG 투사**: Janak & Tye 2015로 `unsourced` 해소. 편도 회로의 C급 출처(S6 Bioinformation)는 이제 제외해도 됨.
- **Horner 1차 뉴런의 뇌줄기 주행과 Wallenberg**: Kanagalingam & Miller 2015(사람, "91%에서 Horner").
- **미각의 영장류 경로**: Carleton 2010 — 설치류는 NTS → 팔곁핵 중계, 영장류는 NTS → VPMpc 직접. 기존 서술의 "중심뒤판로" 이름과 "같은쪽" 표현은 이 논문에 없음(계속 `unsourced`).

### 새로 드러난 충돌 (성연에게 물어볼 것) ❓
1. **하행 통증조절의 신경전달물질**: StatPearls는 PAG→RVM→후각 경로를 "세로토닌성"이라 함. Heinricher 2009는 "at least some NEUTRAL-cells, but apparently no ON-cells or OFF-cells are serotonergic". 즉 RVM에 세로토닌 뉴런은 있지만 통증 조절의 핵심인 ON/OFF 세포는 세로토닌성이 아님 → 학습 도구에서 "세로토닌성 하행로"라고 단순화할지, 구분해서 쓸지 결정 필요.
2. **시각앞구역 올리브핵 → EW핵 투사**: 기존 "같은쪽과 반대쪽에 균등"(StatPearls) vs McDougal & Gamlin 2015의 원숭이 추적 "predominantly contralaterally". 양측 투사(뒤맞교차 경유)라는 큰 틀은 같고 비율의 문제.
3. **REM-off 뉴런의 표적**: 기존 단계는 vlPAG/LPT GABA 뉴런이 LDT/PPT에 종착한다고 했으나, Saper 2010은 SLD(sublaterodorsal nucleus)로의 투사를 서술 → 단계의 `terminatesIn` 수정 검토.
4. **해마이행부(subiculum)의 위치**: Aggleton 2022는 직렬 파페츠 회로 자체를 재고하자는 논문 — 회로를 "고리"로 그리는 우리 표현은 유지하되, 설명에 "고전적 서술"임을 명시하는 게 안전.

### 이번 출처로 못 받친 것 (도서관 문헌·교과서 필요)
삼차신경 체성감각 경로 전체, 척수시상로 교차 분절 수, 겉질척수로 교차 비율, hyperdirect 경로, 각막반사 R1/R2 회로 세부(Kimura 1972·Ongerboer de Visser 1976은 1970년대 스캔본이라 초록만 열림), VOR의 MLF·갓돌림핵 이름, 파페츠 회로의 해마 내부 3시냅스, 도파민 중뇌겉질·결절깔때기 경로, 시상하부 거대세포계, 배뇨의 척수 분절, 소뇌다리 3개의 해부, 뇌줄기 핵 크기 대부분(형태계측). → `wanted/WANTED.md` "0. 최소 세트"(책 4권 + 논문 7편)가 이 공백을 겨냥함.

### 방법 메모
- PMC 저자원고(Europe PMC에 XML 없음)는 `pmc.ncbi.nlm.nih.gov/articles/<PMCID>/` HTML로 대조하도록 `verify_quotes.py` 확장. 연속 요청 시 PMC가 **reCAPTCHA 페이지를 200으로** 돌려주므로(캐시에 그대로 저장됨) 캡차 페이지를 걸러내는 처리가 필요 — 이번엔 수동으로 지우고 재실행함.
- 수집자들이 WebFetch 요약 대신 curl로 원문을 받아 자체 대조한 것이 인용 정확도(**exact 102/104, NOT_FOUND 0**)에 기여함.
