# 5. 기하 모형 위치·치수 (속귀·신경절·목동맥)

오른쪽 기준 MNI RAS(mm). `axis`는 모형의 긴 축/고리 법선이 향하는 방향. 치수는 교과서값. 위치가 수 mm 이상 틀리거나 방향이 반대면 적어 주세요.

| id | 이름 | 모형 | 중심 (x,y,z) | 축 | 치수 | 답변 |
|---|---|---|---|---|---|---|
| so-cochlea | 달팽이 | cochlea | [35, -29, -26] | [0.6, 0.75, -0.3] | {} |  |
| so-basilar-membrane | 바닥막 | basilar-membrane | [35, -29, -26] | [0.6, 0.75, -0.3] | {} |  |
| so-organ-corti | 코르티기관 | organ-corti | [35, -29, -26] | [0.6, 0.75, -0.3] | {} |  |
| so-tectorial-membrane | 덮개막 | tectorial-membrane | [35, -29, -26] | [0.6, 0.75, -0.3] | {} |  |
| so-stria-vascularis | 혈관줄무늬 | stria-vascularis | [35, -29, -26] | [0.6, 0.75, -0.3] | {} |  |
| pn-spiral-ganglion | 나선신경절 | spiral-ganglion | [35, -29, -26] | [0.6, 0.75, -0.3] | {} |  |
| so-horizontal-canal | 가쪽반고리관 (수평) | semicircular-canal | [41, -35, -20] | [0, -0.5, 0.87] | {} |  |
| so-anterior-canal | 앞반고리관 | semicircular-canal | [38, -31, -16] | [-0.7, 0.7, 0.0] | {} |  |
| so-posterior-canal | 뒤반고리관 | semicircular-canal | [42, -38, -23] | [0.7, 0.7, 0] | {} |  |
| so-utricle | 타원주머니 | ellipsoid | [38, -33, -21] | [0, -0.5, 0.87] | {"radii": [3.0, 2.0, 1.5]} |  |
| so-saccule | 둥근주머니 | ellipsoid | [36, -31, -24] | [0, 0, 1] | {"radii": [1.5, 1.2, 1.8]} |  |
| pn-vestibular-ganglion | 안뜰신경절 (Scarpa) | spindle | [31, -30, -26] | [1, 0.2, 0] | {"length": 5, "radius": 1.8} |  |
| pn-geniculate-ganglion | 무릎신경절 | disc | [35, -28, -22] | [1, 0, 0] | {"radius": 1.5, "thickness": 1.0} |  |
| pn-trigeminal-ganglion | 삼차신경절 | crescent | [20, -10, -32] | [0.2, 0.3, 0.93] | {"radius": 6.0, "degrees": 150, "thickness": [2.5, 1.5], "flatten": 0.6} |  |
| pn-nodose-ganglion | 미주신경 아래신경절 | spindle | [18, -26, -64] | [0.1, -0.2, -1] | {"length": 16, "radius": 3.0} |  |
| pn-petrosal-ganglion | 혀인두신경 아래신경절 | spindle | [15, -30, -52] | [0, 0, -1] | {"length": 6, "radius": 2.0} |  |
| pn-superior-cervical | 위목신경절 | spindle | [22, -30, -88] | [0, 0.15, -1] | {"length": 25, "radius": 4.0} |  |
| pn-ciliary-ganglion | 섬모체신경절 | disc | [29, 38, -28] | [0, 1, 0] | {"radius": 1.5, "thickness": 0.8} |  |
| pn-pterygopalatine | 날개입천장신경절 | disc | [24, 20, -44] | [1, 0, 0] | {"radius": 3.0, "thickness": 1.5} |  |
| pn-submandibular | 턱밑신경절 | disc | [33, 12, -76] | [0, 0, 1] | {"radius": 2.0, "thickness": 1.0} |  |
| pn-otic | 귀신경절 | disc | [24, -6, -50] | [1, 0, 0] | {"radius": 2.5, "thickness": 1.0} |  |
| so-carotid-baroreceptor | 목동맥팽대 압력수용기 | spindle | [28, -20, -102] | [0.1, 0.1, 1] | {"length": 14, "radius": 4.5, "sharpness": 0.5} |  |
| so-carotid-body | 목동맥소체 화학수용기 | ellipsoid | [27, -22, -104] | [0, 0, 1] | {"radii": [2.5, 1.5, 3.0]} |  |
