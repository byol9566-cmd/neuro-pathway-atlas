# 다음 세션 전달용 지시문 — 경로 근거 데이터 수집 이어가기

아래 내용을 새 세션에 그대로 붙여넣으면 됩니다. (이전 조사용 지시문은 `docs/handoff-prompt.md` — 그 작업은 끝났음.)

---

## 배경

의대생 지인(성연)과 만드는 웹 3D 신경과학 학습 도구. 시제품은 `poc` 브랜치에 구현돼 있고 https://neuro-pathway-atlas.vercel.app 에 배포됨(README.md, `docs/research-sources.md` §6-1 참고). 지금 하는 일은 **경로(구조 ↔ 신경과정) DB의 근거 자료를 논문에서 모으는 것**이다. 성연이 경로 내용을 검수·확장할 때 출처가 붙은 자료를 보고 판단할 수 있게 하려는 목적.

## 역할 분담 (반드시 지킬 것)

- **수집은 서브에이전트가 한다.** 메인 세션은 **출처와 신빙성 검토만** 한다. 메인 세션이 직접 문헌을 뒤지거나 내용을 채우지 말 것.
- 사용자가 요청하지 않은 코드 수정·배포·커밋을 하지 말 것. 질문을 받으면 답부터 하고, 실행은 요청받은 범위만.

## 수집 방식

- 수집 규칙과 JSON 스키마: `docs/data/pathway-evidence/AGENT_BRIEF.md`. 에이전트 프롬프트는 "이 파일을 먼저 읽고 그대로 따르라 + 배치 id + 출력 파일 경로 + 다룰 경로 목록"으로 구성한다. 모델은 `sonnet`.
- 에이전트는 자기 배치 파일 하나(`docs/data/pathway-evidence/<batch>.json`)만 쓴다. 하위 에이전트 금지.
- **웹 검색 한도(세션당 200회)가 병목**이다. 에이전트당 WebSearch는 3회 이하로 제한하고, 문헌 검색은 API로 시킨다(WebFetch나 curl — 검색 횟수에 안 잡힘):
  - Europe PMC 검색: `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<q>&format=json` (`OPEN_ACCESS:y`, `PUB_TYPE:review` 필터)
  - Europe PMC 전문: `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`
  - NCBI Bookshelf(StatPearls, Purves Neuroscience 2판): `https://www.ncbi.nlm.nih.gov/books/NBK<id>/`
  - 새 세션을 시작할 때 `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`을 올려두면 더 여유롭다.
- 모든 주장에는 **실제로 연 원문에서 복사한 8~45단어 직접 인용**이 붙어야 한다. 기억에 의존한 인용 금지. 출처를 못 찾은 사실은 `unsourced`로, 출처끼리 어긋나면 `conflicts`로.

## 검토 방식 (메인 세션)

1. `python3 docs/data/pathway-evidence/verify_quotes.py [배치.json ...]` — 각 출처의 원문을 받아 (a) PMCID가 실재하는지, 제목·연도가 Europe PMC 등록 정보와 맞는지, (b) 인용문이 원문에 실제로 있는지(exact/fuzzy/NOT_FOUND) 대조. 결과는 `verification/<batch>.report.json`.
2. 사람 판단이 필요한 부분을 `docs/data/pathway-evidence/REVIEW.md`에 기록:
   - 출처 등급: A 동료심사 리뷰·해부학 원저(인지도 있는 학술지) / B 교과서(Purves)·StatPearls / C 그 외 / X 약탈적·불명 학술지 → 제외
   - 인용문은 맞지만 **주장이 인용문보다 더 나간 경우**(예: 인용문에는 "시상"인데 주장은 "VPL") 표시
   - 동물 연구를 사람 해부학 근거로 쓴 경우 표시
   - 핵심 사슬(뉴런 차수·교차 위치·종착)이 독립된 출처 2개 이상으로 받쳐지는지
   - NOT_FOUND 인용은 해당 에이전트에게 SendMessage로 재확인시키거나 삭제
3. 검토를 통과한 것만 나중에 `content/pathways.json`으로 옮긴다(그 작업은 성연 검수와 함께, 사용자가 요청할 때).

## 진행 상황

<!-- STATUS:BEGIN -->
2026-09-20 세션 종료 시점:

- **수집·검토 완료 6개 배치** (`docs/data/pathway-evidence/*.json`, 검토는 `REVIEW.md`): somatosensory, motor, brainstem-reflexes, special-senses, limbic-arousal-autonomic, morphometry. 인용 458개 중 원문에 없는 것 0개.
- **약점**: 출처 89개 중 57개가 StatPearls(B급). StatPearls 원문 오류가 2건 확인됨 → B급 단독 근거는 확정 금지.
- **다음 세션의 1순위는 새 주제가 아니라 "출처 교체"**: REVIEW.md에서 ⚠️로 표시한 항목을 A급 리뷰로 보강한다.
  - 삼차신경 체성감각 경로(StatPearls 1개 장에 전부 의존), 하행 통증조절(Basbaum/Fields, Ossipov 등)
  - hyperdirect 경로(Nambu 2002), Guillain–Mollaret 삼각(비대올리브변성 리뷰), 소뇌다리
  - 각막·눈깜박반사의 R1/R2 성분(Cruccu, Kimura, Aramideh & Ongerboer de Visser)
  - 편도 회로(Sah 2003 Physiol Rev, Janak & Tye 2015 Nature) — 현재 근거 S6(Bioinformation)는 제외 대상
  - 미각의 중심뒤판로 주행, Wallenberg–Horner 연결(1차 교감신경로의 뇌줄기 주행)
  - 각 배치 `unsourced` 항목은 Purves *Neuroscience*(NCBI Bookshelf)로 보강. 주의: Bookshelf의 Purves는 검색 미리보기 발췌만 열리는 장이 있음
- **형태계측은 목적 미달**: 뇌신경핵 크기는 공개 전문에서 못 찾음(`notFound` 29개). 유료 문헌·단행본 영역 → 성연의 도서관 접근 또는 JKMS 2023 뇌줄기 단면 논문 저자 문의(`docs/handover-seongyeon/` 참고)가 더 현실적.
- 에이전트가 600초 무응답으로 죽는 일이 2번 있었음 → 프롬프트에 "경로 하나 끝날 때마다 파일을 다시 써라"를 넣을 것. 죽으면 SendMessage로 같은 에이전트를 재개하면 읽은 내용을 유지한 채 이어감.
- 검증 스크립트는 Python 3.10+ 필요: `pipeline/.venv/bin/python docs/data/pathway-evidence/verify_quotes.py <파일>`

2026-09-22 추가:
- 사용자가 대학 도서관 계정으로 유료 문헌을 직접 받아 주기로 함. **받을 문헌 목록은 `docs/data/pathway-evidence/wanted/WANTED.md`** (책 11권·논문 75편, 그중 받을 논문 56편, 1순위 구분 있음). 후보 조사는 서브에이전트(`wanted/*.json`), DOI·ISBN 실재 확인은 `wanted/verify_wanted.py`(`*.report.json`). 전문 내용은 아직 아무것도 확인하지 않음(`checked: false`).
- 받은 PDF는 `~/Downloads/atlas-refs/`에 들어옴 → 다음 할 일: 각 PDF에서 우리 주장에 대한 8~45단어 인용을 뽑아(에이전트가 PDF를 읽고 추출, 메인이 `verify_quotes.py`류로 원문 대조 — PDF는 로컬 파일이므로 대조 스크립트를 로컬 텍스트 기준으로 확장해야 함) StatPearls 근거를 교체하고 REVIEW.md 갱신.
- 2026-09-23: 무료 전문 19편에서 인용 104개 추출·검증 완료(`upgrade-*.json`, REVIEW.md "upgrade-*" 절). NOT_FOUND 0. 해결: 코르티솔 생성층 모순(다발층 확정), Guillain–Mollaret 삼각, 얼굴 겉질숨뇌로 고리 주행, 편도→PAG. 새 충돌 4건은 REVIEW.md ❓ 목록. **기존 배치 파일에는 아직 통합하지 않음** — 성연 검수와 함께 `content/pathways.json` 반영 시 같이 할 것. 사용자 몫은 `wanted/WANTED.md` "0. 최소 세트"(책 4권 + 논문 7편)로 축소.
- 2026-09-24: 사용자가 받아 준 도서관 PDF 2건 처리 — Sah 2003(편도, 인용 18), **Nieuwenhuys 2008 교과서(경로 32개 전부, 인용 409)**. 전부 exact, NOT_FOUND 0. 파일 `upgrade-lib-*.json`, 검토는 REVIEW.md "upgrade-lib-*" 절(교과서 vs StatPearls 충돌 22건 ❓ 목록 — 성연 검수 필수, 특히 적색척수로·뒤섬유기둥·VMpo). PDF 처리 도구 `pdf_text.py`(+ `verify_quotes.py`의 `file` 필드). 받은 PDF와 추출 텍스트는 `~/Downloads/atlas-refs/`와 `verification/cache/local/`(둘 다 저장소 밖/gitignore). 남은 최소 세트: Haines·Brodal·Kandel + 논문 6편 — 임상 항목(증후군·병변)은 Haines/Brodal이 필요.
- 2026-09-24 저녁: 유료 목록의 무료 대체본 처리 — Inoue 2012(사용자 제공, CC BY), Willis & Westlund 1997(PMC), Lemon 2019 + Haber 2016(OA). 인용 85개, NOT_FOUND 0. hyperdirect 용어·노르아드레날린 기원(A5/A6/A7) 해결; 교차율·VMpo·적색척수로·세로토닌성은 입장 병기 후 성연 판단(REVIEW.md "upgrade-lib 2차"). 남은 건 임상 교과서 1권(Haines/Brodal → 성연 도서관)과 Cruccu 2005뿐.
<!-- STATUS:END -->

## 아직 수집하지 않은 주제 (우선순위 순)

1. 고위 피질 기능 네트워크: 언어(브로카–활꼴다발–베르니케, 등쪽/배쪽 흐름), 주의·무시(우측 두정엽), 전두엽–피질하 회로 5개(Alexander), 기본모드 네트워크, 시각 등쪽/배쪽 흐름
2. 뇌신경별 핵–기능 성분 표(GSE/SVE/GVE/GSA/SVA/GVA), 핵상/핵하 병변 구분, 뇌간 혈관 증후군(Wallenberg, Weber, Benedikt, Millard-Gubler, Foville, 내측 연수 증후군)과 침범 구조
3. 척수: Rexed 층별 기능, 척수 증후군(전척수동맥, 중심척수, Brown-Séquard 상세), 분절별 피부분절·근육분절, 자율신경 유출
4. 혈관 영역과 구조 대응(전·중·후대뇌동맥, 렌즈핵선조체동맥, 시상 혈관 영역) — 경로 병변 시뮬레이션용
5. 시상핵별 입출력 표(구심/원심 연결), 시상하부핵별 기능
6. 신경전달물질 계통 상세(콜린성 기저전뇌 Ch1–Ch6, 세로토닌 B1–B9, 히스타민)
7. 한국어 용어 대조표: 새 용어/옛 용어/영어/TA2 — 공개 출처가 거의 없으므로(조사 문서 §4 지식 레이어 참고) 성연에게 맡기는 편이 나음
8. 형태계측 보강: `morphometry.json`의 `notFound`에 남은 구조

## 산출물

- 배치별 JSON(`docs/data/pathway-evidence/*.json`), 검증 리포트(`verification/`), `REVIEW.md`
- 마지막 보고: 배치별 인용 검증률, 제외한 출처와 이유, 출처 간 충돌 목록, 성연에게 물어봐야 할 것
