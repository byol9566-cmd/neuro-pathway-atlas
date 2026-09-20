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
(세션 종료 시 갱신)
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
