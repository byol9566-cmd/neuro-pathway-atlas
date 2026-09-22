# 후보 문헌 조사 지시 (wanted list)

목적: 우리 경로 근거 데이터(`docs/data/pathway-evidence/*.json`)는 StatPearls(B등급)에 지나치게 기대고 있다. 각 경로마다 **A등급 문헌**(동료심사 리뷰, 고전 해부학 원저, 표준 교과서 장)을 후보로 찾아라. 사용자가 대학 도서관 계정으로 직접 내려받을 것이므로 **유료 문헌도 좋다.** 다만 오픈액세스로 이미 구할 수 있는지는 표시해야 한다.

## 규칙 (어기면 결과를 버린다)

1. **DOI는 반드시 Crossref로 실재 확인**: `https://api.crossref.org/works/<DOI>` 를 WebFetch/curl로 열어 제목·저널·연도가 네가 적은 것과 일치하는지 본다. 응답의 제목을 `crossrefTitle`에 그대로 복사. 확인 안 된 DOI는 넣지 말 것. 기억에 의존해 DOI를 쓰지 말 것.
2. **오픈액세스 여부는 Europe PMC로**: `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<DOI>&format=json&resultType=lite` → `isOpenAccess`("Y"/"N"), `pmcid`가 있으면 기록. 결과가 없으면 `"oa": "unknown"`.
3. WebSearch는 에이전트당 **3회 이하**. 문헌 탐색은 Europe PMC 검색 API(`query=... AND PUB_TYPE:review`, `SRC:MED`)와 Crossref 검색(`https://api.crossref.org/works?query=...&rows=5`)으로 한다.
4. 교과서는 DOI 대신 ISBN과 장 제목을 적고 `"kind": "book"`. 출판사(Springer/Elsevier/Wolters Kluwer/Oxford)를 적어 도서관 전자책 검색이 되게 한다.
5. 경로당 후보 **2~4개**. 우선순위: (a) 그 주제의 고전·표준 리뷰(피인용 많은 것), (b) 최근 10년 이내 종합 리뷰, (c) 표준 교과서 장. 증례 보고, 가설 모델 논문, 질병 논문의 배경 설명, MDPI/Frontiers의 피인용 0 논문은 제외.
6. 각 후보에 `"why"`: 우리 근거의 어떤 주장(뉴런 차수·교차 위치·시냅스 핵·종착)을 받쳐 줄 것으로 기대하는지 한 문장. 실제로 그 논문을 열어 확인했으면 `"checked": true`, 제목·초록으로만 판단했으면 `false`.
7. **경로 하나 끝날 때마다 출력 파일을 다시 써라** (중간에 죽어도 남게).
8. 하위 에이전트 생성 금지. 다른 파일 수정 금지.

## 출력 JSON 스키마

```json
{
  "batch": "<배치 id>",
  "pathways": [
    {
      "id": "<pathways-evidence json의 경로 id>",
      "weakness": "<현재 근거의 약점 한 줄: 예) StatPearls 한 장 의존>",
      "candidates": [
        {
          "kind": "article" | "book",
          "citation": "<저자. 제목. 저널 연도;권:쪽>",
          "doi": "<DOI 또는 null>",
          "crossrefTitle": "<Crossref 응답 제목>",
          "isbn": "<책일 때>",
          "publisher": "<책일 때>",
          "chapter": "<책일 때 장 제목>",
          "oa": "Y" | "N" | "unknown",
          "pmcid": "<있으면>",
          "why": "<한 문장>",
          "checked": true | false
        }
      ]
    }
  ],
  "notes": "<막힌 것, 못 찾은 것>"
}
```
