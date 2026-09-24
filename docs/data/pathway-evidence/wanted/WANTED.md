# 도서관에서 받아 주실 문헌 — 남은 것 (2026-09-24 정리)

후보 전체 표(책 12권·논문 75편)는 지웠습니다. 필요하면 `make_wanted_md.py`로 다시 만들 수 있고, 후보 자체는 `*.json`·`*.report.json`에 그대로 있습니다. 아래는 **지금까지 받은 것으로 해결된 부분을 빼고 남은 것**만입니다.

## 받은 것 (처리 완료)

| | 결과 |
|---|---|
| ✅ Nieuwenhuys *The Human Central Nervous System* 4판 | 경로 32개 전부에 사람 교과서 인용 409개 |
| ✅ Sah 2003 *Physiol Rev* (편도) | 인용 18개, C급 출처 대체 |
| ✅ 무료 전문 19편 (제가 직접) | 인용 104개 |

이제 StatPearls 단독 근거인 경로는 없습니다. 남은 문제는 세 가지입니다: ① **임상 서술**(증후군·병변)은 Nieuwenhuys에 거의 없음, ② 교과서와 기존 서술이 다른 **충돌 22건**(REVIEW.md) 중 일부는 판정할 제3의 출처가 필요, ③ 데이터(핵 크기)용 아틀라스.

## 1순위 — 이것만 받으면 근거 작업은 마무리됩니다 (책 1권 + 논문 3편)

| 받기 | 문헌 | 찾는 법 | 해결되는 것 |
|---|---|---|---|
| ✅ | Haines (ed). *Fundamental Neuroscience for Basic and Clinical Applications*. 5th ed. Elsevier 2018 (또는 Brodal *The Central Nervous System* 5th ed. Oxford 2016 — 둘 중 하나면 됨) | ClinicalKey / Oxford Medicine 전자책, ISBN 9780323396325 / 9780190228958 | 병변·증후군 전부(Brown-Séquard, Wallenberg, 뒤섬유기둥 증후군, 제뇌 자세, UMN/LMN 징후, Wernicke–Korsakoff…). 임상 항목은 현재 StatPearls만 남음 |
| ✅ | Lemon RN. Descending pathways in motor control. *Annu Rev Neurosci* 2008;31:195 | [10.1146/annurev.neuro.31.060407.125547](https://doi.org/10.1146/annurev.neuro.31.060407.125547) | 피라미드 교차율(70–80% vs >90%, 교과서도 사람 수치 없음), 적색척수로가 사람에 있는지, 겉질외 하행로 정리 |
| ✅ | Nambu, Tokuno & Takada. 'Hyperdirect' pathway. *Neurosci Res* 2002;43:111 | [10.1016/S0168-0102(02)00027-5](https://doi.org/10.1016/S0168-0102(02)00027-5) | "hyperdirect"라는 용어 자체가 교과서에 없음. 지금 근거는 가설 모델 논문뿐 |
| ✅ | Cruccu et al. Brainstem reflex circuits revisited. *Brain* 2005;128:386 | [10.1093/brain/awh366](https://doi.org/10.1093/brain/awh366) | 각막반사 R1/R2 회로(출처 셋이 서로 다름), 턱반사 이시냅스 경로 |

## 2순위 — 있으면 좋은 것 (논문 2편)

| 받기 | 문헌 | 찾는 법 | 해결되는 것 |
|---|---|---|---|
| ○ | Willis & Westlund. Neuroanatomy of the pain system. *J Clin Neurophysiol* 1997;14:2 | [10.1097/00004691-199701000-00002](https://doi.org/10.1097/00004691-199701000-00002) | 척수시상로 교차 전 분절 수, VPL vs VMpo 판정 |
| ○ | Basbaum & Fields. Endogenous pain control systems. *Annu Rev Neurosci* 1984;7:309 | [10.1146/annurev.ne.07.030184.001521](https://doi.org/10.1146/annurev.ne.07.030184.001521) | 하행 통증조절의 "세로토닌성" 여부 충돌 |

빠진 것: Kandel(★였음)은 Nieuwenhuys가 그 역할을 다 해서 제외. Sessle 2000(삼차신경)은 교과서 인용 9개로 대체돼 제외. 나머지 2순위 후보 60여 편은 해당 경로가 이미 독립 A급 출처 2개(교과서 + 무료 리뷰)를 갖춰 제외.

## 별도 — 데이터용 (근거가 아니라 뇌줄기 핵 크기·경계 자료)

성연이 데이터를 주기로 했으므로 **일단 보류**. 필요해지면:
- Paxinos, Huang, Sengul & Watson. *Atlas of the Human Brainstem*. Elsevier 2012, ISBN 9780080925219
- Olszewski & Baxter. *Cytoarchitecture of the Human Brain Stem* (3판 2014, Karger; 2판 ISBN 9783805522106)

## 받는 곳

`~/Downloads/atlas-refs/` 에 넣어 주세요. 파일명은 자유입니다. 전자책은 필요한 장만 PDF로 저장해도 됩니다(Haines라면 척수·뇌줄기·감각계·운동계 장과 각 장 끝의 임상 상자).
