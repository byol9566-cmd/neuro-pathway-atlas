# 3D 자료 조사 종합 (2026-10-04)

세 조사(`survey-3d-atlases-2026-10.md`, `survey-multiplane-sections-2026-10.md`, `survey-3d-model-vendors-2026-10.md`)와 `tractography-atlases.md`의 결론. 라이선스 핵심은 메인 세션이 원문으로 재확인한 것만 ✅.

## 질문 1 — 상업 이용 가능한 3D 뇌 모델이 더 있는가
있다. 우선순위 순:

| 자료 | 내용 | 라이선스 | 상업 | 우리에게 더해 주는 것 |
|---|---|---|---|---|
| **Visible Human (NLM)** | 냉동절편 RGB 0.33mm(남 1mm·여 0.33mm 간격) + CT·MRI | 라이선스 불필요 ✅(NLM: "license is no longer required") | 가능 | 주석은 없음 → **직접 분할** 중(눈·시각신경·뇌하수체·척수·뼈미로·신경절). 진행 상황은 `docs/placeholders-to-detailed-3d.md` |
| **FreeSurfer 아틀라스**(시상핵 25~50·해마 아영역 13·편도 핵 9·뇌줄기 4구획) | 확률 아틀라스, 어떤 T1에든 적용 → MNI 템플릿에 적용하면 MNI 라벨 | FreeSurfer Software License(MGH) ✅: 재배포·서브라이선스 허용, "Any commercialization … at the sole risk of the party" — 금지 아님, 고지 의무 | 가능(고지) | 시상·편도·해마 세분 |
| **SPL/NAC Brain Atlas**(Open Anatomy, 300+ 구조, 시상하부·소뇌 구획 포함) | 한 명의 MRI 기반 라벨 | 3D Slicer License Part B(같은 MGH/BWH 계열) ⚠️ 에이전트 확인 | 가능으로 보임 | 시상하부 핵, 소뇌 소엽 |
| **CerebrA**(Manera 2020) | 102 구역, MNI 2009c | CC BY 4.0 ⚠️ | 가능 | 뇌줄기 전체·소뇌 벌레 소엽 |
| **AAL3** | SN·VTA·적색핵·청색반점·솔기핵·시상 세분 | GPL(2024 readme) ⚠️ | 가능하나 카피레프트 | 좌표 참고용으로만 |
| **HCP1065 트랙토그래피**(Yeh) | 섬유 다발 .trk, MNI | CC BY-SA 4.0 ✅ | 가능(파생 데이터 SA) | 겉질척수로·안쪽섬유띠·척수시상로 등 **실제 주행** — Codex 과제로 변환 중 |
| Pandora WM atlas | 216 다발 확률 지도 | CC BY 4.0 ⚠️ | 가능 | 섬유로 보조 |
| AHEAD 2022 | 피질하 17구조 3D 조직학 | CC BY 4.0 ⚠️ | 가능 | MASSP와 중복 |
| Z-Anatomy | 뇌줄기 핵·간뇌·뇌신경 메시(Blender) | CC BY-SA 4.0 ⚠️ | 가능(SA) | 품질 미확인, 받아서 봐야 함 |

막힌 것: Brainstem Navigator·THOMAS(라이선스 명시 없음 → 저자 문의 필요), Neuromorphometrics(유료), Brainnetome·Hammers 원본(비상업), Nowinski(상용 제품), BigBrain·Julich-Brain(CC BY-NC-SA), Allen 성인 절편(비상업, 허가 필요), Visible Korean·MSU 컬렉션(비상업), TurboSquid/CGTrader(앱 내 "추출 불가" 조항), Visible Body·Kenhub 등(제3자 라이선스 없음).

## 질문 2 — 세로·가로 단면이 모두 있는 자료
**상업 이용 가능한 것은 없다.** 세 방향 주석 절편은 Mai/Paxinos 아틀라스(Elsevier, 유료·미확인)뿐. 진짜 3D 조직 볼륨(어느 방향이든 자를 수 있음)은 NextBrain(CC0, 우리 백본)·AHEAD(CC BY)·BigBrain(비상업)뿐.

## 결정에 참고
- 뇌줄기 소핵의 정밀 모양은 어떤 공개 자료에도 없다. 위치는 문헌 좌표(Qwen 과제 A)·AAN으로, 모양은 Allen 정합본(비상업)이나 타원체.
- 다음에 넣기 좋은 순서: ① Visible Human 분할(눈·뇌하수체·척수·뼈미로·신경절) → ② FreeSurfer 시상·편도·해마 세분 → ③ HCP1065 섬유로 → ④ SPL/NAC·CerebrA 보조.
