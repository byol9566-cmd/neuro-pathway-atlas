# 성연 검수 묶음 — 2026-10-27

뷰어: https://neuro-pathway-atlas.vercel.app (경로 247개, 구조 313개). 아래 순서대로 보면 되고, **틀린 것만** `ANSWERS.csv`에 한 줄씩(시트 이름 · 행 id · O/X · 수정안 · 근거) 적어 주면 내가 표만 고쳐 다시 생성한다. 맞으면 안 적어도 됨.
`ANSWERS.csv`는 UTF-8(BOM 포함)이라 Excel에서 더블클릭으로 바로 열려도 한글이 깨지지 않는다. 저장할 때 형식은 그대로 CSV로.

| 순서 | 파일 | 내용 | 왜 필요한가 |
|---|---|---|---|
| 1 | `1_pathway_drafts_and_decisions/` | 경로 32개 설명 초안(2_pathways·3_steps·4_lesions csv, 안내는 0_guide.txt)과 **판정 시트 48건**(6_decisions.csv — 출처끼리 어긋나는 쟁점, 입장 중 고르기) | 판정이 와야 설명 문장을 확정해 뷰어 247개 경로 설명 교체를 시작할 수 있음 (가장 급함) |
| 2 | `2a_tracts_cross_section_positions.md`, `2b_cranial_nerve_waypoints.md` | 아틀라스에 없어 교과서 단면 위치로 그린 척수·뇌줄기 섬유로 12개, 뇌신경 15개 경유점 | 뷰어 경로 재생 선이 이 위치를 따라감 |
| 3 | `3_body_effects_joints_eyes_targets.md` | 경로 마지막 단계의 관절 굽힘·폄, 안구 회전, 동공, 단계별 근육·장기 종착 | 팔다리·눈이 움직이는 연출의 근거 |
| 4 | `4_autonomic_waypoints_cord_segments.md` | 교감줄기·내장신경·골반내장신경 경유점, 척수 분절·IML·클라크기둥 z 범위 | 자율신경 경로 31개 |
| 5 | `5_parametric_models_inner_ear_ganglia.md` | 달팽이·반고리관·신경절·목동맥 모형의 위치·치수 | 근사 모형의 위치 확인 |
| 6 | `6_ref_brainstem_nuclei_coordinate_search.md` | RVLM·CVLM·거대세포핵·피개그물핵 좌표 문헌 조사 결과(참고) | 좌표가 실린 교과서·아틀라스(Olszewski & Baxter 1954 등)를 도서관에서 볼 수 있으면 알려 주기 |
| 7 | `7_viewer_screenshots/` | 뷰어 화면 캡처(경로 재생·몸 보기) | 뷰어를 열기 어려울 때 참고 |

좌표계: 전부 MNI152 RAS(mm) — x 오른쪽+, y 앞+, z 위+; 앞맞교차 근처가 원점. 큰구멍 z≈−56, T1 척추뼈 z≈−177, L1 z≈−478.
뷰어에서 보는 법: 좌측 "구조" 목록에서 이름을 누르면 그 구조만 켜지고 카메라가 이동한다. "모형"/"근사" 꼬리표가 붙은 건 데이터가 아니라 모형. 경로는 "재생"으로 단계별 이동, 각 단계 상세에 어떤 구조·3D 없는 이름이 들어가는지 적혀 있다.
현황 숫자: 경로 단계 677개 중 실제 주행선을 따르는 단계 160개, 근사 타원체로 남은 구조 4개(입쪽배가쪽숨뇌 (RVLM)·꼬리쪽배가쪽숨뇌 (CVLM)·거대세포그물핵·피개그물핵).
