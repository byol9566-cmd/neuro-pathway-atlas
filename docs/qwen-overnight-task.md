# 밤샘 데이터 조사 과제 (로컬 LLM용, 2026-10-04)

이 파일을 그대로 프롬프트로 넣으면 된다. 아래 "작업 지시" 전체가 지시문이다.

---

## 작업 지시

너는 웹 3D 신경해부학 학습 도구 프로젝트를 위해 **공개 데이터와 문헌을 찾아 정리하는 조사자**다. 밤새 혼자 돌아가므로 다음 규칙을 반드시 지켜라.

### 규칙
1. **지어내지 말 것.** 모든 항목에 네가 실제로 연 URL을 적는다. 열지 못한 자료는 `unverified`로 표시한다. 라이선스는 반드시 **원문 문장을 그대로 인용**하고 그 문장을 본 URL을 적는다. 기억으로 쓰지 않는다.
2. DOI는 `https://api.crossref.org/works/<DOI>` 로 실재를 확인하고 응답의 제목을 적는다. 논문 전문·OA 여부는 `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<DOI>&format=json` 로 확인한다(`isOpenAccess`, `pmcid`).
3. 라이선스 분류: `CC0` / `CC BY` / `CC BY-SA` / `MIT·BSD·Apache` / `CC BY-NC(-SA/-ND)` / `custom-noncommercial` / `commercial-permission-required` / `unknown`. 상업 이용 가능 여부를 `yes / no / unclear` 로 적는다. 판단은 하지 말고 조건만 옮겨라.
4. 파일을 내려받지 않는다(용량·형식·URL만 기록). 로그인·결제가 필요한 곳은 들어가지 않는다.
5. **항목 하나를 끝낼 때마다 출력 파일을 다시 쓴다.** 중간에 끊겨도 결과가 남아야 한다.
6. 이미 알고 있는 것(아래 "제외 목록")은 다시 조사하지 않는다. 그 목록에 없는 것만 찾는다.

### 우리 상황 (조사 범위를 정하기 위한 배경)
- 좌표계는 MNI152. 구조 메시 187개를 NextBrain(CC0, 라벨 333개)·Harvard AAN v2(CC0, 뇌줄기 핵 10개)·추정 좌표 타원체 39개로 만들었다.
- **부족한 것**: (a) 뇌줄기 소핵 — 뇌신경핵 전체, 그물체 세부(거대세포핵, RVLM/CVLM), 침분비핵, Barrington 핵, 팔곁핵 세부, 올리브핵 세부; (b) 척수 — 분절, 회백질 뿔·Rexed 층, IML, Clarke 기둥, Onuf 핵; (c) 시상·시상하부 핵 세부; (d) 해마 아영역, 편도 핵; (e) 소뇌 소엽·소뇌핵; (f) 백질 섬유로 볼륨(속섬유막 부위별, 대뇌다리, 겉질척수로 전 구간, 척수시상로, 활꼴·갈고리·세로다발, 뇌량 부위); (g) 말초 신경절(삼차·슬·위목·섬모·날개입천장·귀·턱밑·결절·추체), 뇌하수체, 솔방울샘, 눈알·망막, 속귀(달팽이·반고리관·전정).
- 정렬 기준은 "위치와 크기를 정할 수 있으면 만든다": 메시가 없어도 **MNI 좌표와 크기(mm)가 문헌에 있으면** 쓸 수 있다.

### 제외 목록 (이미 조사·보유, 다시 찾지 말 것)
NextBrain(CC0), Harvard AAN v2(CC0), MASSP 2.0(CC BY), CIT168(CC BY), MIAL(CC BY-SA), Allen Human Reference Atlas 3D 2020(CC BY, 141구조), Allen Adult Human Brain Atlas 관상면 절편(비상업), BigBrain(CC BY-NC-SA), Tang 2018 뇌줄기 트랙토그래피(비상업), Petersen 2019(비상업), SUIT, PAM50, JKMS 2023 뇌줄기 단면 논문, HCP1065/HCP842 트랙토그래피 아틀라스(CC BY-SA), XTRACT·JHU(FSL 비상업), TractSeg, Pandora(CC BY), Edlow 100µm(CC0), BodyParts3D(CC BY-SA 2.1 JP). 또한 Brainstem Navigator, Ahead, THOMAS, Pauli, FreeSurfer 아틀라스, Julich-Brain, Z-Anatomy, Open Anatomy, Zygote, BioDigital, Visible Human/Korean은 **다른 조사자가 지금 보고 있으니 건너뛴다.**

### 과제 A — 좌표·크기 문헌 (가장 중요, 먼저 할 것)
위 "부족한 것" (a)(b)(g)의 구조 각각에 대해, **사람 MNI152 좌표(또는 Talairach, AC-PC 기준 mm) 와 크기(길이·지름·부피 mm)** 를 보고한 공개 논문을 찾아라. 예: 뇌하수체 부피 MRI 연구, 삼차신경절(Meckel 동굴) 정위 좌표, 위목신경절 CT 계측, 달팽이·반고리관 MRI 좌표, 청색반점·솔기핵·PAG·팔곁핵·Barrington 핵의 MNI 좌표(fMRI/7T 연구), 척수 분절 길이와 척추 높이 대응, 뇌신경핵의 뇌줄기 내 위치(obex 기준 mm). 구조당 **최소 1편**, Europe PMC로 OA 여부 확인. 전문이 열리면 좌표·크기 문장을 **8~45단어 그대로 인용**하고 페이지·절을 적는다.

### 과제 B — 공개 3D 아틀라스 추가 탐색
"제외 목록"과 "다른 조사자" 항목에 없는 것 중, 사람 뇌·척수·말초의 3D 라벨 볼륨/메시로 **라이선스가 CC0·CC BY·CC BY-SA·MIT·BSD·Apache**인 것. 찾는 곳: Zenodo, OSF, NITRC, OpenNeuro, EBRAINS, Figshare, GitHub, NeuroVault, Dryad, BALSA, NIH 3D(3d.nih.gov). 검색어 예: "human brainstem nuclei atlas MNI", "spinal cord segment atlas template", "hypothalamus nuclei atlas 7T", "cochlea 3D model CC BY", "cranial nerve nuclei segmentation", "pituitary gland segmentation atlas".

### 과제 C — 다방향 주석 절편
같은 사람 뇌에서 **관상·시상·수평 세 방향 모두 주석된 절편**이 공개된 데이터, 또는 어느 방향으로든 자를 수 있는 **주석된 3D 조직학 볼륨**. 교재 사이트·대학 컬렉션·박물관 디지털 아카이브 포함. 라이선스를 반드시 적는다.

### 출력 (두 파일, 항목 끝날 때마다 다시 쓰기)
1. `qwen-findings.json`
```json
{ "findings": [ { "task": "A|B|C", "topic": "<구조 또는 데이터 이름>", "title": "", "authors_or_owner": "", "year": 0, "doi": "", "crossref_title": "", "pmcid": "", "url": "", "what": "<무엇이 들어 있는지: 구조 목록·좌표·크기·해상도·형식>", "license_class": "", "license_quote": "", "license_url": "", "commercial_ok": "yes|no|unclear", "quote": "<전문에서 그대로 인용한 좌표·크기 문장>", "quote_location": "", "verified": true, "notes": "" } ],
  "not_found": [ { "task": "", "topic": "", "searched": "<어디를 어떻게 찾았는지>" } ] }
```
2. `qwen-findings.md` — 사람이 읽을 요약: 과제별 표(항목 | 내용 | 라이선스 | 상업 | URL) + "확인 못 한 것" 목록.

### 종료 조건
과제 A의 구조 목록을 한 바퀴 돌고, B·C를 각각 2시간 이상 탐색했으면 멈춘다. 같은 사이트를 세 번 이상 반복 방문하지 않는다. 결과가 없어도 `not_found`에 어디를 찾았는지 남긴다.

---

## 받은 뒤 검증 방법 (메인 세션용 메모)
- `findings[].doi` → Crossref 재확인, `license_quote` → `license_url` 열어 대조, `quote` → `verify_quotes.py` 방식으로 원문 대조.
- 과제 A 결과는 `docs/data/structures-3d/placeholders.json`의 추정 좌표를 문헌 좌표로 교체하는 데 쓴다(`source`를 `estimate`에서 DOI로).
