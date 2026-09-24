# 검수 시트 초안 작성 지시 (drafting agents)

목적: 의대생 검수자(성연)가 화면 없이 CSV만 보고 경로를 검수할 수 있도록, `merged/<pathway>.json`(영어 구조 필드 + 인용)을 **한국어 검수 시트 초안**으로 바꾼다. 너는 번역·정리만 한다. **새 사실을 보태지 말 것** — 근거 파일에 있는 내용만 쓴다. 모르면 빈칸.

## 규칙
1. **하위 에이전트 생성 금지. WebSearch·WebFetch 금지.** 읽는 파일은 `merged/*.json`, `merged/_structure-ids.tsv`, 그리고 문체 참고용 `content/pathways.json`뿐.
2. **용어**: 대한의사협회 새 용어(현재 `content/pathways.json`과 `_structure-ids.tsv`가 쓰는 식). 예: 널판핵, 쐐기핵, 안쪽섬유띠, 시상 배쪽뒤가쪽핵(VPL), 중심뒤이랑, 갓돌림신경핵, 안쪽세로다발(MLF), 유두체, 시상앞핵, 띠이랑, 해마곁이랑, 치아이랑, 편도체, 분계선조, 청색반점, 솔기핵, 수도관주위회색질(PAG), 고립로핵(NTS), 의문핵, 시상밑핵(STN), 창백핵 속·바깥분절(GPi/GPe), 흑색질, 치아핵, 위·중간·아래소뇌다리. 옛 용어(후주, 내측모대, 시상하부핵…)는 쓰지 말고, 영문 약어는 괄호로 병기.
3. **구조 id 매핑**: 단계의 `cellBodies`·`terminatesIn`·`courseVia`에 나오는 구조 중 `_structure-ids.tsv`에 있는 것은 그 id로. 없는 것은 `구조_이름(참고)`에 한국어 이름만 적고 `메시_없는_구조`에도 적는다. 억지로 비슷한 id에 붙이지 말 것(예: "시상 VPM"이 목록에 있으면 그것만, "시상 속판내핵"은 없음).
4. **좌우(`side`)**: 원본의 `laterality`를 기준쪽(origin) 대비 `같은쪽`/`반대쪽`/`양쪽`/`정중`으로. origin은 경로마다 네가 정해 적는다(예: "자극을 받는 몸 쪽", "빛을 비춘 눈", "머리가 도는 쪽", "표시할 반구").
5. **설명**: 단계당 2~3문장, 근거 파일의 cellBodies → courseVia → terminatesIn 순으로. 교차하면 어디서 교차하는지 명시. 근거 파일의 `conflicts`에 걸린 내용은 단정하지 말고 "(출처에 따라 …/… — 판정 시트 참고)"로 쓴다.
6. **출처 열**: 그 단계 evidence의 출처 label을 등급 순(A 먼저)으로 최대 3개, `;`로 구분. 예: `Nieuwenhuys 2008 Springer (A); Willis 1997 J Clin Neurophysiol (A); StatPearls (B)`.
7. **병변**: `lesions` 항목을 그대로 한국어로. 근거 없는 병변(evidence 비어 있음)은 `출처`를 `(근거 없음 — 검수 필요)`로.
8. **판정(conflicts)**: 각 conflict를 한국어 쟁점 한 줄 + 입장별(출처 label·등급·인용 앞 25단어를 한국어로 요약)로. 입장은 최대 4개. 어느 쪽이 맞는지 **네 의견을 쓰지 말 것**.
9. 경로 하나 끝날 때마다 출력 파일을 다시 써라.

## 출력 (JSON 하나, 지정된 경로에)
```json
{
  "pathways": [
    {
      "id": "dcml-pathway", "name_ko": "", "name_en": "", "category_ko": "체성감각", "summary_ko": "", "origin_ko": "자극을 받는 몸 쪽",
      "steps": [
        { "order": 1, "title_ko": "", "neuronOrder": 1, "structure_ids": ["bs-gracile"], "structure_names_ko": "널판핵, 쐐기핵",
          "side": "같은쪽", "decussation": false, "decussation_where_ko": "", "neurotransmitter_ko": "",
          "description_ko": "", "missing_ko": "척수신경절·뒤기둥은 3D에 없음", "sources": "Nieuwenhuys 2008 Springer (A); StatPearls (B)" }
      ],
      "lesions": [ { "site_ko": "", "deficit_ko": "", "side_ko": "", "sources": "" } ],
      "conflicts": [ { "issue_ko": "", "positions": [ { "source": "Nieuwenhuys 2008 Springer", "grade": "A", "summary_ko": "" } ] } ]
    }
  ]
}
```
마지막 보고: 경로 수, 단계 수, 매핑된 구조 id 수 / 매핑 못 한 구조 수, 판정 항목 수.
