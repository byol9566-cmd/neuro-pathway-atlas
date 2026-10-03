# 대조 지시 (성연 데이터셋 ↔ 우리 근거)

목적: 성연이 보낸 데이터셋(강의 정리본 기반, 근거 등급 C)과 우리 근거(A급 인용, `merged/<id>.json`)가 **서로 다른 곳**을 찾는다. 같은 내용은 보고하지 않는다. 판단은 하지 않는다 — 어느 쪽이 맞는지 쓰지 말고, 두 쪽의 주장과 우리 쪽 근거의 출처·등급만 나란히 적는다.

## 규칙
1. **하위 에이전트 생성 금지(Agent 도구 사용 금지). WebSearch·WebFetch 금지.** 읽는 파일: `reconcile/theirs/<ours-id>.json`(성연 쪽 경로들), `merged/<ours-id>.json`(우리 근거), 필요하면 `draft-*.json`(우리 한국어 초안).
2. 비교 항목(각 성연 경로의 각 단계에 대해): 참여 구조(이름), 좌우(ipsi/contra — 둘 다 origin 기준이지만 **origin 정의가 다를 수 있으니 먼저 origin을 비교**), 교차 여부·위치, 시냅스 핵, 신경전달물질, 뉴런 차수, 병변-증상-쪽. 
3. 차이의 종류를 표시: `contradiction`(양립 불가), `granularity`(한쪽이 더 세분/합침 — 모순 아님), `addition`(한쪽에만 있음), `terminology`(같은 것의 다른 이름), `origin-definition`(기준쪽 정의 차이로 생긴 겉보기 차이).
4. 우리 쪽 근거를 적을 때는 `merged` 파일의 evidence에서 **출처 label·등급·인용 앞 20단어**를 그대로 가져온다. 우리 근거에 해당 내용이 없으면 `ours_evidence: null`.
5. 성연 데이터의 `evidenceStatus`와 `sourceRefs.pdfPages`를 그대로 기록(우리는 그 PDF가 없으므로 확인 불가라고 표시).
6. 성연 데이터에서 **우리 근거에 없는 새 내용**(단계·경로)은 `additions`에 id만 나열(요약 한 줄).
7. 우리 경로 하나 끝날 때마다 출력 파일을 다시 써라.

## 출력 (JSON 하나)
```json
{ "pathways": [ { "ours": "<id>", "theirs": ["<id>", ...],
    "origin_note": "<두 쪽의 origin 정의가 같은지>",
    "differences": [ { "kind": "contradiction|granularity|addition|terminology|origin-definition",
        "their_pathway": "<id>", "their_step": "<step id>", "their_claim_ko": "<성연 쪽 주장 한 줄>",
        "their_evidence": "<evidenceStatus; om-1 p.x / om-2 p.y>",
        "our_claim_ko": "<우리 쪽 주장 한 줄>", "ours_evidence": [ {"source": "", "grade": "A", "quote_head": ""} ],
        "severity": "high|medium|low", "note": "" } ],
    "additions": [ {"their_pathway": "<id>", "summary_ko": ""} ] } ] }
```
severity: high = 학습 도구에서 틀린 걸 가르치게 되는 차이(교차 방향, 핵 이름, 증상 쪽), medium = 표현·범위, low = 세분화·용어.
마지막 보고: 경로별 차이 수(종류별), high 항목 요약.
