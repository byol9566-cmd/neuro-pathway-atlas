# 성연 데이터셋(2026-10-02) ↔ 우리 근거 대조 보고

대응표 `mapping.json`(우리 32 ↔ 성연 131). 차이 62건 — 심각도 {'high': 14, 'medium': 14, 'low': 34}, 종류 {'contradiction': 11, 'granularity': 35, 'terminology': 6, 'origin-definition': 2, 'addition': 8}. 성연 쪽 근거는 강의 정리본(우리에게 PDF 없음, 확인 불가)이고, 우리 쪽은 `merged/`의 A급 인용. **누가 맞는지는 여기서 정하지 않는다** — 성연에게 되묻거나 판정 시트(검수시트2/6_판정)로 넘길 항목.

## 0. 메인 세션 검토 요약 (2026-10-03)

에이전트가 high로 올린 14건을 직접 읽고 분류한 결과:

**A. 실제 모순 6건 — 성연 데이터가 우리 A급 근거와 반대로 단정함.** 전부 검수시트2의 `6_판정.csv`에 이미 올라간 쟁점이라, 성연 데이터는 그 쟁점의 "강의 쪽 입장"을 확인해 준 셈. 판정이 오면 한 번에 정리됨.
1. **적색척수로**(`rubrospinal`, `decorticate-rigidity`): 사람에 뚜렷한 하행로로 모델링 ↔ Nieuwenhuys "사람 척수에서 확인되지 않음". 제피질경직 설명도 이 가정에 기댐.
2. **통증·온도의 시상 중계핵**(`spinothalamic-lateral`, `trigeminal-pain`): VPL/VPM 단독 ↔ Nieuwenhuys·Willis는 VMpo(및 판내핵 등) 병행.
3. **Ia 억제 사이뉴런**(`reciprocal-inhibition`): 글리신 ↔ Nieuwenhuys는 GABA성, VII층.
4. **턱반사 좌우**(`jaw-jerk`): 같은쪽만 ↔ A·B급 모두 중뇌삼차핵→양쪽 삼차운동핵(양쪽 씹기근 수축). 이건 판정 시트에 없던 새 항목 → 추가 필요.

**B. 모순이 아니라 공백 5건 — 성연 데이터가 핵·구분을 생략함**(정리본에 없는 핵은 만들지 않았다고 명시). 우리 근거로 채우면 됨: 각막반사 R1/R2 구분, Horner 병변 국소화(병변 항목 자체가 비어 있음), 수면 flip-flop의 VLPO·vlPAG, 압수용기·배뇨의 Barrington/Onuf(변연 배치), 코르티솔 다발층.

**C. 성연이 일부러 열어 둔 것 3건 — 오히려 우리 B급 서술보다 신중함**: 수평 홱보기의 FEF→PPRF 직접 투사("확정하지 않음" ↔ Nieuwenhuys도 "약하다"), 미각 중추의 좌우(양측 표시는 교차 주장이 아니라고 메모; 우리 A급은 비교차), 덮개앞핵→EW 투사 비중(양쪽 ↔ "주로 반대쪽" — 둘 다 양측 투사라는 틀은 같음). 심각도 medium으로 내림.

**D. 우리 쪽이 약한 것 2건**: 해마 CA3→CA1의 교차 여부(우리 근거도 인용 불가), 안뜰 시상 표적(VPL/VPM vs VPS/VPI — 우리 내부 미해결). 성연 데이터를 탓할 수 없음.

**결론**: 성연 데이터셋은 구조(경로·단계·참여 구조·좌우)는 믿고 가져와도 되고, 문장은 우리 근거로 다시 쓰되 A의 6곳은 판정 전까지 "출처에 따라 다름"으로 표기. 성연에게 되물을 것: 판정 시트 48건 + 턱반사 좌우 1건.

## 1. high — 그대로 두면 틀린 내용을 가르치게 되는 차이

14건

### anterolateral-system-spinothalamic-tract ← spinothalamic-lateral / spinothalamic-lateral-3  `contradiction`

- **성연**: 반대쪽 VPL이 통각·온도 신호의 시상 중계핵으로 제시되며(2차 뉴런), 다른 중계핵은 언급되지 않는다.  ⟨lecture-grounded; om-2 p.8,9,16⟩
- **우리**: Nieuwenhuys(A급)는 통각·온도 전도의 주 중계핵은 VMpo이며 VPL에는 산발적 종말만 있다고 명시. Willis&Westlund(A급)도 VPL·VPI·POm·CL(가쪽/판내핵)과 별도로 VMpo(안쪽시상)가 lamina I 특이 투사의 표적이라고 구분해 보고.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The main relay nucleus for the conduction of pain and temperature is the VMpo”; Willis 1997 J Clin Neurophysiol (A): “The particular nuclei of termination include the VPL, VPI, and POm nuclei in the lateral”
- 메모: 성연 자료는 VPL을 유일한 통각·온도 중계핵으로 제시(StatPearls B급 수준의 단순화와 동일); 우리 A급 근거는 VMpo를 주 중계핵으로 보거나 최소한 VPL과 병렬적인 별도 표적으로 구분함. 학습 도구에서 핵 이름이 달라지는 고위험 차이.

### ascending-arousal-system-flip-flop ← sleep-rem / sleep-rem-1, sleep-rem-3 (및 sleep-nrem-1)  `granularity`

- **성연**: REM ON은 '콜린성(PPT/LDT) 활동 증가 + LC/솔기 모노아민 감소'로, REM OFF는 '모노아민 관련 상태로 전환'이라고만 기술. 비REM을 주도하는 핵의 이름(VLPO)이나 flip-flop(상호억제) 스위치 모델, REM을 끄는 구체적 GABA성 핵(vlPAG 등)의 이름이 이 데이터셋 전체에 전혀 등장하지 않음.  ⟨lecture-model-needs-expert-review (sleep-rem) / lecture-grounded (sleep-nrem, aras); om-2 p.89-91⟩
- **우리**: 배쪽가쪽시각교차앞핵(VLPO; GABA/갈라닌 공발현 및 비-갈라닌 GABA성 뉴런)이 TMN·LC·솔기핵·바닥앞뇌·vlPAG/LDT-PPT에 억제성 투사를 보내 각성계와 상호억제(flip-flop) 관계를 형성하고, REM 개시 시 배쪽수도관주위회색질(vlPAG)의 GABA성 'REM-off' 뉴런이 억제되어 LDT/PPT 콜린성 REM-촉진 회로가 탈억제된다고 명시. 단, 우리 자료 내부에도 이견이 공존: Nieuwenhuys는 REM-off 기능을 vlPAG가 아니라 LC/솔기 자체(국소 GABA 요소에 의해 억제됨)에 돌리고, Saper 2010은 vlPAG/LPT의 하류 표적을 LDT/PPT가 아니라 교뇌 밑가쪽등쪽핵(SLD, sublaterodorsal nucleus)으로 봄.
- 근거: Wang 2026 Frontiers in Neuroscience (A): “sleep–wake control has classically been conceptualized through the "flip-flop switch"”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Thus a reciprocal inhibitory interaction likely exists between the sleep-promoting”; Wang 2026 Frontiers in Neuroscience (A): “inhibition of vlPAG GABAergic REM-off neurons disinhibits pontine REM-promoting”
- 메모: 브리핑이 지정한 'REM-off 핵과 flip-flop(VLPO) 모델' 항목. 성연 쪽 이 경로(ascending-arousal-system-flip-flop) 데이터셋 전체에서 'VLPO'라는 명칭이 한 번도 나오지 않음 — 제목은 'flip-flop'인데 핵심 스위치 기전이 빠져 있음. 모순이라기보다 누락.

### central-vestibular-pathways ← vestibular-perception / vestibular-perception-2  `terminology`

- **성연**: 시상 중계핵을 'VPL·VPM'(thal-vpl, thal-vpm, 양쪽)으로 명시한다. 원문이 좌우·개별핵을 충분히 지정하지 않아 양측 VP 표시로 보류했다고 밝힌다.  ⟨evidenceStatus: lecture-grounded; om-2 p.49⟩
- **우리**: 우리 쪽은 B급(StatPearls)이 'VPL·VPM·VPI로 이루어진 ventral posterior complex'라고 하는 반면, A급 Nieuwenhuys는 영장류에서 '(VPL/VPM이 아니라) VPS(ventral posterior superior)·VPI(ventral posterior inferior) 주변부(shell)'에 종지한다고 서술해 핵 이름 자체가 다르다 — merged conflicts에 명시된 내부 쟁점.
- 근거: StatPearls (NBK557380) (B): “Within the thalamus, vestibular signals are primarily processed in the ventral posterior c”; Nieuwenhuys 2008 Springer (4th ed.) (A): “In primates the vestibulothalamic fibres terminate bilaterally in the shell surrounding th”
- 메모: 지시사항의 '안뜰 시상 표적' 주목 항목. 성연 쪽은 B급 명칭(VPL/VPM)만 채택해 A급(Nieuwenhuys, VPS/VPI)과의 핵 이름 불일치를 반영하지 않는다.

### corneal-blink-reflex ← corneal-reflex / corneal-reflex-2  `granularity`

- **성연**: 삼차 감각 중계를 '삼차척수핵(bs-spinal-trigeminal)' 단일 핵으로만 기술하고, 이것이 양쪽 얼굴핵을 모집한다고만 서술한다. R1(초기, 같은쪽)과 R2(후기, 양쪽)를 구분하지 않고 하나의 단계로 뭉뚱그린다.  ⟨evidenceStatus: lecture-partial-plus-standard-completion; om-1 p.22, om-2 p.54⟩
- **우리**: 우리 쪽은 R1(초기, 같은쪽 위주)과 R2(후기, 양쪽)를 구분한다. A급 Nieuwenhuys는 R1이 '삼차신경 주감각핵과 삼차척수핵 둘 다'에서 중계되고, R2는 별도의 '다리뇌·숨뇌 깜빡임 중추'에서 중계된다고 본다. 반면 B급 StatPearls 중 하나는 주감각핵, 다른 하나는 삼차척수핵이라 하여 중계핵 자체를 두고도 내부 쟁점(conflicts)이 있다.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The early, ipsilateral (R1) component of the blink reflex is relayed by interneurons locat”; Nieuwenhuys 2008 Springer (4th ed.) (A): “The late, bilateral (R2) component of the blink reflex is relayed by interneurons in the p”; Lee 2025 Frontiers in Surgery (A): “an afferent impulse from either free nerve endings or mechanoreceptors within the corneal ”
- 메모: 지시사항의 'R1/R2 중계핵' 주목 항목. 성연 쪽은 R1/R2를 나누지 않아 월렌버그 증후군처럼 R1은 정상이고 R2만 양쪽에서 지연되는 임상 패턴(우리 쪽 lesions에 Kimura 1972 A급으로 등재)을 이 경로 안에서 구별해 가르칠 수 없다. 또한 주감각핵(principal sensory nucleus) 경로 자체가 성연 쪽에는 전혀 없다.

### extrapyramidal-descending-tracts ← rubrospinal / rubrospinal-1  `contradiction`

- **성연**: 적색핵척수로가 사람에서도 뚜렷한 하행로로 존재한다고 모델링(출발핵=적색핵, 중뇌 배쪽피개교차에서 교차, 반대쪽 척수 앞뿔의 알파·감마운동뉴런·목근육까지 도달). 요약에는 '사람에서는 역할이 제한적'이라고만 완화해서 적음.  ⟨lecture-grounded; om-2 p.3,63⟩
- **우리**: merged conflicts에 이미 기록된 특별 주의 항목: 원 배치(StatPearls B급)는 적색핵척수로가 중뇌 배쪽피개교차에서 교차해 굽힘근 알파·감마운동뉴런에 시냅스한다고 기술하지만, Nieuwenhuys(A급)는 '적색핵척수로는 대부분의 포유류에서는 뚜렷한 섬유다발로 존재하지만 사람 척수에서는 식별할 수 없다'고 명시하며, '사람 뇌에는 적색핵숨뇌로(rubrobulbar)만 있을 가능성이 있고 적색핵척수로는 한 번도 입증된 적이 없다'고 단언.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The rubrospinal tract, which is present in most mammals as a distinct bundle of coarse fib”; Nieuwenhuys 2008 Springer (4th ed.) (A): “A rubrobulbar tract probably exists in the human brain, but the presence of a rubrospinal ”
- 메모: 특별 주의 항목. '역할이 제한적'이라는 완화 표현은 '사람에서 입증된 적이 없다'는 A급 근거의 강한 부정과 다른 수준의 주장 — 학습 도구에서 사람에게 없는 경로를 뚜렷한 핵·교차·종착부로 가르치게 되는 고위험 차이.

### extrapyramidal-descending-tracts ← decorticate-rigidity / decorticate-rigidity-1  `contradiction`

- **성연**: 제피질경직(decorticate posturing)의 상지 굽힘 기전을 '보존된 rubrospinal과 신전근 하행망의 균형'으로 설명하며 tr-rubrospinal을 구조 참조로 명시.  ⟨lecture-model-with-cautions; om-2 p.4,64,65,75⟩
- **우리**: merged lesions의 decorticate posturing 설명 자체는 StatPearls(B급, Lee 2022)의 '적색핵 위쪽 손상이 겉질척수로·적색핵척수로를 방해한다'는 고전 모형을 그대로 인용하지만, 같은 merged 파일의 A급 근거(Nieuwenhuys)는 사람에게 적색핵척수로가 입증되지 않았다고 하므로 이 교육모형 자체가 우리 A급 근거와 긴장 관계에 있음.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “A rubrobulbar tract probably exists in the human brain, but the presence of a rubrospinal ”
- 메모: rubrospinal 존재 여부 쟁점이 decorticate posturing 교육모형에도 그대로 이어짐 — 동일 쟁점의 2차 노출.

### gustatory-pathway ← gustatory-central / gustatory-central-3  `contradiction`

- **성연**: 시상 VPM 이후를 ipsi+contra 양쪽 구조참조로 표시하며, "원문에 미각 중추교차 세부 없음; ipsi에서 both로 바뀌는 것은 교차 확정 표시가 아님"이라고 메모해 중추 미각경로를 양측(bilateral) 망처럼 둔다.  ⟨evidenceStatus: lecture-grounded; om-1 p.17,22,23, om-2 p.33,34⟩
- **우리**: 우리 쪽은 1차(고립로핵)부터 4차(미각겉질·안와전두겉질)까지 모든 단계에서 laterality='ipsilateral', decussation.present=false로 명시한다. A급 Nieuwenhuys는 미각을 '교차하지 않는 예외' 감각계로 특정해 서술한다("이 연결들은 미각 경로를 제외하고 대부분 교차한다"). B급 내부에서도 Gibbons(순수 같은쪽)와 Obiefuna(교차+비교차 혼재)가 엇갈려 merged conflicts에 등재돼 있다.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The rostral, gustatory portion of the solitary nucleus gives rise to an uncrossed ascendin”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Most of these connections, with the exception of the pathway for taste, are crossed.”; Gibbons 2023 StatPearls [Internet] (B): “The third-order fibers travel ipsilaterally through the posterior limb of the internal cap”
- 메모: 지시사항의 '미각 경로 좌우성(비교차)' 주목 항목. 미각은 교과서적으로 '교차하지 않는 유일한 예외 감각계'로 가르치는 포인트인데, 성연 쪽이 불확실성 때문에 양쪽으로 열어두면 이 특이성이 가려진다. (성연 쪽의 신중한 태도 자체는 자료 부족 때문이라 '틀렸다'고 단정하지 않음 — 판단은 하지 않는다는 원칙에 따름.)

### horizontal-conjugate-gaze-saccade-circuit ← cortical-gaze-control / cortical-gaze-control-2  `contradiction`

- **성연**: "FEF→PPRF 직접 주행·saccade별 교차세부는 원문의 기능표만으로 확정하지 않는다"면서 PPRF·III·IV·VI·MLF를 양쪽(ipsi+contra) 구조참조로만 걸어두고, FEF가 반대쪽 PPRF로 직접·강하게 투사한다고 단정하지 않는다.  ⟨evidenceStatus: lecture-partial-plus-standard-completion; om-1 p.20,33, om-2 p.1,67,77⟩
- **우리**: 우리 쪽 1단계(order 1)는 'FEF → 반대쪽 PPRF(수평단속운동)' 직접 교차투사를 기본 주장(laterality: contralateral, decussation: present)으로 명시한다. 다만 A급 Nieuwenhuys는 'PPRF에 대한 FEF 신경지배는 약하며 단속운동생성기를 표적으로 하지 않는다'고 하여, 수평단속운동은 riMLF(수직)처럼 FEF가 강하게 직접 지배하는 것이 아니라는 내부 쟁점을 conflicts에 남겨두었다.
- 근거: StatPearls (NBK441970) (B): “Saccades are initiated by the frontal eye field (FEF), which sends signals to the contrala”; Nieuwenhuys 2008 Springer (4th ed.) (A): “The innervation of the PPRF is weak and does not target the saccade generator.”
- 메모: 지시사항의 'FEF→PPRF vs FEF→위둔덕(SC)' 주목 항목. 두 데이터셋 모두 위둔덕(superior colliculus)을 이 경로의 중계로 명시하지는 않지만, 성연 쪽의 '교차세부 미확정' 서술은 우리 A급(Nieuwenhuys)의 'PPRF행 FEF 신경지배가 약하다'는 의심과 방향이 같고, 우리 쪽 대표 주장(B급, 반대쪽으로 강하게 직접투사)과는 어긋난다. 학습 도구가 '반대쪽 PPRF로 직접·강하게 투사'라고만 가르치면 A급 근거의 단서가 빠진다.

### jaw-jerk-reflex ← jaw-jerk / jaw-jerk-2 / jaw-jerk-3  `contradiction`

- **성연**: 삼차운동핵·V3·씹기근 구조참조를 모두 'ipsi'로만 걸어, 편측 자극이 같은쪽 씹기근 수축만 일으키는 편측(일측성) 반사처럼 기술한다 ("주요 단일시냅스 구심–운동 연결").  ⟨evidenceStatus: lecture-partial-plus-standard-completion; om-1 p.17,18, om-2 p.59⟩
- **우리**: 우리 쪽은 중뇌삼차핵 뉴런의 축삭이 '양쪽' 삼차운동핵에 중계되어(decussation present, laterality: bilateral) 양쪽 씹기근이 함께 수축한다고 본다. A급 Nieuwenhuys: '중뇌핵에서 나온 흥분성 경로는 양쪽 턱닫음근 운동뉴런에 접근한다.'
- 근거: StatPearls (NBK539823) (B): “pseudounipolar afferent fibers from stretch receptors relay information directly to the ce”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Excitatory pathways from the mesencephalic nucleus thus have access to motoneurons innerva”
- 메모: 교차 방향/편측·양측 여부를 가르치는 핵심 항목. 성연 쪽대로면 '한쪽만 턱을 닫는 반사'처럼 읽히는데, 우리 쪽 B·A급 근거는 모두 양쪽 씹기근이 함께 수축한다고 명시한다.

### papez-circuit-trisynaptic-hippocampal ← hippocampal-trisynaptic / hippocampal-trisynaptic-3  `contradiction`

- **성연**: CA3(이끼섬유 다음 단계) → Schaffer곁가지 → CA1은 동측(ipsi)만 표시되어 교차 없는 단일반구 경로로 모델링됨.  ⟨lecture-grounded; om-2 p.83-84⟩
- **우리**: CA3→Schaffer곁가지→CA1 단계를 laterality:bilateral, decussation:present(일부 Schaffer/연합섬유가 해마맞교차를 통해 반대측 해마로 건너간다)로 기술.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “These collaterals are collectively known as Schaffer collaterals.”
- 메모: 단, 우리 merged 파일 자체의 unsourced 항목에 'Schaffer/연합섬유가 해마맞교차의 교차 성분이라는 구체적 주장은 정확히 그 표현으로 확인되지 않음'이라고 적혀 있어, 이 decussation 주장은 우리 쪽에서도 근거가 약함(명시 인용 없음). 교차 방향에 대한 주장이 두 자료 간 다르다는 점은 분명하므로 기록함.

### pupillary-light-reflex ← pupillary-light-reflex / pupillary-light-reflex-2  `contradiction`

- **성연**: "덮개앞핵은 양쪽 EW핵에 투사한다" — 같은쪽/반대쪽 투사가 대등한 것처럼(직접반사=같은쪽, 공감반사=반대쪽을 동등 비중으로) 서술한다.  ⟨evidenceStatus: lecture-grounded; om-1 p.25, om-2 p.19⟩
- **우리**: 우리 쪽 A급 근거(McDougal 2015)는 덮개앞올리브핵(PON)이 양쪽 EW가 아니라 '반대쪽으로 우세하게(predominantly contralaterally)' 투사한다고 보고하며, 이를 B급 StatPearls의 '양쪽 동등' 서술과 상충하는 내부 쟁점으로 merged 파일의 conflicts에 등재해 두었다.
- 근거: McDougal 2015 Comprehensive Physiology (A): “the PON projects predominantly contralaterally to the EW by way of the posterior commissur”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Axons of neurons of the olivary pretectal nucleus project to the Edinger-Westphal nuclei o”
- 메모: 지시사항의 '덮개앞→EW 좌우성' 주목 항목. 성연 쪽은 '양쪽에 투사'까지만 말해 대등 투사처럼 읽히지만, 우리 A급 근거 중 하나(McDougal)는 반대쪽 우세를 보고해 내부적으로도 쟁점(conflicts)으로 남아있다. 성연 쪽 서술은 우리의 B급 서술과는 맞고 A급 McDougal과는 어긋난다.

### spinal-reflex-arcs ← reciprocal-inhibition / reciprocal-inhibition-2  `contradiction`

- **성연**: Ia 억제성사이뉴런이 길항근 알파운동뉴런에 출력할 때 전달물질이 글라이신(glycine)이라고 명시(사이뉴런 자체의 전달물질·위치는 언급 없음).  ⟨lecture-grounded; om-2 p.11,56,58⟩
- **우리**: merged conflicts에 이미 기록된 특별 주의 항목: 원 배치(StatPearls B급)는 Ia 억제성사이뉴런이 '아세틸콜린'을 쓰며 뒤뿔 lamina III에 위치하고, 길항근 시냅스는 글라이신성이라고 기술. 반면 Nieuwenhuys(A급)는 이 사이뉴런이 'GABA성'이며 운동핵 바로 등쪽인 lamina VII에 위치한다고 명시 — 전달물질 정체성과 위치 모두 다름.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “Collaterals of the Ia fibres terminate on inhibitory (gamma-aminobutyric acid, GABA, -cont”
- 메모: 특별 주의 항목. 성연 자료는 B급 쪽(글라이신 출력)과 같은 편이며 A급의 'GABA성 사이뉴런·lamina VII' 주장은 전혀 반영되지 않음 — 사이뉴런의 전달물질 정체성을 가르치는 학습 도구에서 고위험 차이.

### sympathetic-pathway-to-the-eye-horner-syndrome ← autonomic-pupil-dilation / (lesions, pathway-level)  `granularity`

- **성연**: 두 하위 경로 모두 'lesions': [] — 병변·증상·쪽 정보가 전혀 없다. 호너증후군이라는 이름, 안검하수·동공축소·무한증(ptosis/miosis/anhidrosis) 삼주징도 언급되지 않는다.  ⟨evidenceStatus: lecture-partial-plus-standard-completion / lecture-plus-correction; om-1 p.25, om-2 p.19,99,100⟩
- **우리**: 우리 쪽은 1차(시상하부~척수)/2차(척수~위목신경절)/3차(위목신경절~눈) 뉴런 중 어디가 손상됐는지에 따라 무한증(anhidrosis) 범위가 달라진다는 병변 국소화 규칙을 B·A급 근거로 상세히 기술한다: 1차=온몸 같은쪽, 2차=같은쪽 얼굴, 3차=같은쪽 눈썹 주변 국한. 모두 side: ipsilateral.
- 근거: Khan 2023 StatPearls [Internet], StatPearls Publishing (B): “First-order neuron lesions may cause anhidrosis involving the ipsilateral side of the body”; Kanagalingam 2015 Eye and Brain (A): “Horner syndrome consists of unilateral ptosis, an ipsilateral miotic but normally reactive”
- 메모: 지시사항의 '병변-증상-쪽' 주목 항목. 경로 이름이 'Horner syndrome'을 담고 있는데 성연 쪽 데이터에는 이 증후군의 임상 국소화 규칙 자체가 없어, 학습 도구에서 가장 중요한 임상 포인트가 빠질 위험이 있다(모순은 아니고 누락).

### trigeminal-somatosensory-pathways ← trigeminal-pain / trigeminal-pain-3  `contradiction`

- **성연**: 삼차신경척수핵에서 나온 통각·온도 신호는 (교차 후) 반대쪽 VPM에서 중계되어 S1으로 간다 — VPM이 유일한 시상 중계핵으로 제시됨.  ⟨lecture-grounded; om-1 p.17,18,22 / om-2 p.9,16⟩
- **우리**: Nieuwenhuys(A급)는 삼차신경척수핵 중 통각·온도를 담당하는 꼬리쪽아핵(pars caudalis)의 삼차시상 섬유는 척수시상로에 합류해 주로 판내핵군·VMpo·꼬리쪽 안쪽등쪽핵(MD)·배쪽뒤핵 복합체의 쉘로 종착하며 VPM이 주된 종착지가 아니라고 명시(merged conflicts에 이미 기록).
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “Trigeminothalamic fibres from all layers of the subnucleus caudalis of the spinal nucleus ”
- 메모: 척수시상로의 VPL/VMpo 이슈와 같은 패턴: 성연 자료(= 원 StatPearls B급과 동일한 단순화)는 통각 경로의 시상 종착지를 VPM 하나로 제시하지만, 우리 A급 근거는 VMpo·판내핵 등 별도 표적을 명시.

## 2. medium — 표현·범위·강조의 차이

14건

### amygdala-fear-circuit ← fear-auditory-cued / fear-auditory-cued-4  `granularity`

- **성연**: CeA 출력이 그물체·PAG·시상하부로 가는 것을 '뇌줄기·시상하부 공포반응'으로 뭉뚱그려 기술하며, 구체적 백질다발 이름(배측/복측 경로)은 명시하지 않음.  ⟨lecture-grounded; om-2 p.104-107⟩
- **우리**: CeA(및 BLA) 출력을 배측 경로(stria terminalis, 즉 dorsal amygdalofugal pathway → 중격·시상하부)와 복측 경로(ventral amygdalofugal pathway → 중격·시상하부·내측등쪽시상핵)로 구분하고, 추가로 BNST를 경유하는 지속성 불안 경로를 별도 단계로 기술. CeA→PAG 직접투사도 별도 근거로 확인됨.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The stria terminalis , i.e. the dorsal amygdalofugal pathway, emerges”; AbuHasan 2023 StatPearls [Internet] (B): “the ventral route via the ventral amygdalofugal pathway which terminates”; Janak 2015 Nature (A): “cells with learning-induced synaptic enhancement project directly to”
- 메모: 모순 아님. 브리핑이 지정한 '편도체 출력로(분계선조/배쪽편도이탈로)와 중심핵→PAG 투사' 항목에 해당. PAG를 향한 투사 자체는 성연 쪽(bs-pag 구조 포함)도 동일하게 포함하므로 그 부분은 일치.

### baroreceptor-reflex ← baroreflex-sympathetic / baroreflex-sympathetic-2 / baroreflex-sympathetic-3  `granularity`

- **성연**: NTS→CVLM, CVLM→RVLM 각 단계에서 구조참조를 ipsi와 contra 양쪽에 동시에 달아, 이 중계 자체가 처음부터 양쪽으로 투사되는 것처럼 표현한다.  ⟨evidenceStatus: lecture-grounded; om-1 p.23, om-2 p.53⟩
- **우리**: 우리 쪽은 'decussation.present: false'로 교차(decussation) 자체는 없다고 명시하고, NTS-CVLM-RVLM 사슬은 '대체로 같은쪽 숨뇌 사슬로 기술되지만 자율신경 출력은 양쪽에서 조절된다'고 단서를 달아, 양측성이 섬유 교차가 아니라 다른 방식(예: 급을 이루는 투사)으로 생긴다고 본다.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “An inhibitory pathway from the nucleus of the solitary tract (red) terminates on a group o”
- 메모: 모순이라기보다 표현 차이이지만, '교차가 있는가'를 가르치는 맥락에서는 혼동 소지가 있어 medium으로 표시.

### central-autonomic-control-micturition ← autonomic-micturition / autonomic-micturition-2  `granularity`

- **성연**: 저장↔배뇨 상태 전환을 교감/부교감/체성 출력의 균형으로만 기술하며, 중추에서 이 균형을 조정하는 교뇌배뇨중추(Barrington 핵, PMC)나 PAG 중계는 전혀 이름을 붙이지 않음. 원문 자체가 중추 배뇨중계핵을 제시하지 않아 '임의의 추가핵을 만들지 않았다'고 명시(의도적 생략).  ⟨lecture-grounded (autonomic-micturition-2는 lecture-plus-correction 그룹에 속함); om-2 p.100⟩
- **우리**: 방광 신장수용기 구심신호가 PAG를 중계핵으로 거쳐(PAG→사천부 운동신경 직접연결은 없음) 교뇌배뇨중추(Barrington 핵, PMC)에 도달하고, PMC가 (1) 엉치부교감 전신경세포를 흥분시켜 배뇨근을 수축시키는 동시에 (2) 상 운동신경(Onuf 핵, 엉치앞뿔)을 억제해 외요도조임근을 이완시키는 이중 경로로 저장↔배뇨를 전환한다고 구체적으로 명시.
- 근거: Fowler 2008 Nature Reviews Neuroscience (A): “Neurons in the PMC receive input from the PAG and from the anterior and”; Nieuwenhuys 2008 Springer (4th ed.) (A): “It projects bilaterally to the sacral intermediolateral nucleus and the”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Relaxation of the urethral sphincter is produced by inhibitory interneurons”
- 메모: 브리핑이 지정한 '교뇌배뇨중추(Barrington)와 Onuf 핵' 항목. 모순은 아님 — 성연 쪽은 자료에 없는 내용을 추측해 넣지 않겠다고 밝히고 의도적으로 생략했으며, 이 경로 데이터셋 전체(autonomic-micturition, parasympathetic-sacral)에서 'Barrington', 'PMC', 'PAG', 'Onuf' 명칭이 한 번도 등장하지 않음.

### central-vestibular-pathways ← vestibulospinal-medial / vestibulospinal-medial-2  `granularity`

- **성연**: MVST(안쪽안뜰척수로) '하나의 경로'가 MLF를 통해 양측으로 분산 하행한다고 본다(단일 경로의 양측성).  ⟨evidenceStatus: lecture-grounded; om-2 p.3,61⟩
- **우리**: 우리 쪽 B급도 'MVST가 양측으로 간다'고 하지만, A급 Nieuwenhuys는 MVST 자체는 '같은쪽'에 위치하고, 교차 성분은 별도로 명명된 '교차안뜰척수로(crossed vestibulospinal tract)'라는 다른 경로가 담당한다고 본다(두 경로가 합쳐져야 양측 효과) — merged conflicts에 등재.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The medial vestibulospinal tract is located ipsilaterally in the dorsolateral bulbar MLF a”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Fibres of the crossed vestibulospinal tract decussate at their level of origin and become ”
- 메모: 결과(목근육 양측 조절)는 같지만 '교차가 있는 경로가 몇 개인지'를 가르치는 맥락에서는 차이가 날 수 있음.

### corticospinal-tracts ← corticospinal-lateral / corticospinal-lateral-3  `granularity`

- **성연**: 피라미드교차에서 대부분(약 80~90%)이 교차해 반대쪽 가쪽겉질척수로로 하행한다고 단일 수치로 제시.  ⟨lecture-grounded; om-1 p.21 / om-2 p.3,65,68,69⟩
- **우리**: merged conflicts에 이미 기록된 미해결 충돌: StatPearls 내에서도 '90% 이상'(Javed) vs '70~80%'(Khan) 두 수치가 상충하고, Nieuwenhuys(A급)는 인간에 대한 수치를 제시하지 않으며 '부분적(partial) 교차'라고만 기술(원숭이 자료로만 '10% 비교차 ≈ 90% 교차' 수치 제공, 동물 자료임을 명시). Lemon 2019(A급)는 전체 교차율 대신 부위별 차이(손/팔 영역 98% 교차 vs 다리 영역 약 10% 동측 종착)를 보고.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “In monkeys 10% of the dorsolateral pyramidal tract is uncrossed, and a similar percentage ”; Lemon 2019 F1000Res (A): “A somewhat different picture emerges for the corticospinal projection from the leg area of”
- 메모: 특별 주의 항목(피라미드교차 비율). 성연 자료의 80~90%는 StatPearls 두 수치 사이의 절충처럼 보이나, 우리 A급 근거는 인간 전체 교차율에 대해 확정된 단일 수치를 제공하지 않고 신체 부위별로 다르다고 봄 — 단일 수치로 가르치면 과도한 정밀성을 암시할 위험.

### descending-pain-modulation ← pain-descending-norepinephrine / pain-descending-norepinephrine-2  `granularity`

- **성연**: PAG가 '청색반점(locus coeruleus)' 관련 하행 조절계만 모집한다고 서술 — 노르아드레날린성 하행 경로의 근원을 LC 하나로 제시.  ⟨lecture-grounded; om-2 p.15,17,18⟩
- **우리**: merged conflicts에 기록된 바, StatPearls(B급)는 'PAG-LC 경로'로 단순화하지만 Nieuwenhuys(A급)와 Willis&Westlund(A급)는 노르아드레날린성 하행 투사의 근원을 더 넓은 숨뇌다리 카테콜아민세포군 A5·A6(=LC)·A7로 보며, Kolliker-Fuse핵의 동측 투사도 별도로 기여한다고 기술.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “Noradrenergic cells situated in rhombencephalic catecholaminergic cell groups A5, A6 and A”; Willis 1997 J Clin Neurophysiol (A): “Noradrenergic projections to all regions of the spinal cord arise almost entirely from the”
- 메모: 성연 자료는 우리 쪽 B급 단순화와 같은 편(LC 단독)이고, 우리 A급 근거는 더 넓은 A5/A6/A7 체계를 주장(우리 내부에도 미해결 충돌로 기록됨). 특별 주의 항목(노르아드레날린성 하행계)에 해당.

### dopamine-reward-pathways ← nigrostriatal / nigrostriatal-2, nigrostriatal-3  `granularity`

- **성연**: D1(Gs/olf, 직접경로 촉진)·D2(Gi, 간접경로 억제) 수용체의 반대 작용과, 도파민 소실 시 직접경로 약화+간접경로 항진으로 GPi→시상(VL)→일차운동겉질 경로의 시상겉질 운동출력이 감소한다는 고전 운동모형을 구체적으로 기술. evidenceStatus=lecture-plus-internal-correction(1차 자료 p.43의 '직접↑/간접↓' 표기가 2차 자료 p.71과 충돌해 2차 쪽으로 교정).  ⟨lecture-plus-internal-correction; om-1 p.42-43 / om-2 p.71⟩
- **우리**: 흑색질치밀부→선조체(putamen/caudate) 도파민 투사만 기술(laterality: ipsilateral, neurotransmitter: dopamine)하며, D1/D2 직접·간접경로 기전이나 도파민 소실의 회로효과는 전혀 모델링하지 않음. 파킨슨병 손상 항목도 lesions 배열에 없음 — unsourced 항목에 '흑질선조체 도파민뉴런 변성이 파킨슨병의 고전적 해부학적 기질이라는 것은 이 배치에서 인용 가능한 출처로 확인하지 못함'이라고만 기록.
- 근거: (우리 근거 없음)
- 메모: 모순은 아님(비교 대상 자체가 우리 쪽에 없음). 성연 쪽의 '교정'은 자신들의 1차/2차 강의자료 간 내부 불일치를 2차 쪽으로 맞춘 것으로, 우리 A급 근거와 직접 충돌하지 않음. D1촉진/D2억제 및 도파민 소실 시 간접경로 항진이라는 설명 자체는 표준 고전 모형과 부합.

### gag-pharyngeal-and-cough-reflex ← gag-reflex / (lesions, pathway-level)  `granularity`

- **성연**: 병변을 'IX 또는 X 반사활' 하나로 묶어 '구역반사 장애; X 운동이상에서는 연하·발성 장애 동반 가능'이라고만 적고, 어느 쪽에 결손이 나타나는지(side) 기재하지 않는다.  ⟨evidenceStatus: lecture-grounded; om-1 p.23⟩
- **우리**: 우리 쪽은 IX(구심) 손상과 X(원심) 손상을 분리해 각각 쪽을 명시한다: IX 한쪽 손상 → '손상쪽을 자극했을 때만' 반사 소실(구심 결손, ipsilateral); X 한쪽 손상 → '어느 쪽을 자극하든' 목젖·물렁입천장이 손상쪽으로 치우침(원심 결손, 병변쪽으로 편위).
- 근거: Sivakumar 2023 StatPearls [Internet], StatPearls Publishing (B): “If the glossopharyngeal (IX) nerve is damaged on 1 side, there is no response when touched”; Sivakumar 2023 StatPearls [Internet], StatPearls Publishing (B): “If the vagus (X) nerve is damaged and either side is touched, the soft palate elevates and”
- 메모: 지시사항의 '병변-증상-쪽' 주목 항목. 성연 쪽이 틀린 것은 아니지만(모순 아님), IX/X를 구분하지 않고 쪽 정보를 빼서 '목젖이 병변쪽으로 치우친다'는 고전적 임상 소견을 가르칠 수 없다.

### horizontal-vestibulo-ocular-reflex ← hvor / hvor-1  `terminology`

- **성연**: 1차 구심이 '안쪽안뜰핵(medial vestibular nucleus)'에만 닿는다고 기술(상위안뜰핵 언급 없음).  ⟨evidenceStatus: lecture-grounded; om-2 p.46,48,49,50,51,74⟩
- **우리**: 우리 쪽 B급 근거는 '위·안쪽 안뜰핵(superior and medial vestibular nuclei)' 둘 다로 기술하는데, A급 Nieuwenhuys는 더 구체적으로 '안쪽안뜰핵의 거대세포부(MVmc)'만 수평반고리관 중계소라고 명시해 B급 서술과 merged 파일 conflicts에 등재된 내부 쟁점이 있다.
- 근거: Jefferies 2025 StatPearls [Internet], StatPearls Publishing (B): “Activation of the superior and medial vestibular nuclei during head rotation generates imp”; Nieuwenhuys 2008 Springer (4th ed.) (A): “Horizontal canal fibres terminate on two groups of excitatory neurons located in the MVmc,”
- 메모: 성연 쪽의 '안쪽안뜰핵만' 서술은 우리 A급(Nieuwenhuys, MVmc)과 더 가깝고 B급(상위+안쪽)과는 다르다 — 핵 이름을 가르치는 맥락이라 medium.

### hypothalamo-pituitary-axes ← hypothalamic-anterior-pituitary / hypothalamic-anterior-pituitary-3  `granularity`

- **성연**: ACTH·TSH·성선자극호르몬 등이 작용하는 표적샘을 모두 묶어 'end-adrenal-cortex(부신겉질)'로만 표시하고, 코르티솔을 만드는 구체적 구역(피질대)은 명시하지 않음.  ⟨lecture-grounded; om-1 p.39⟩
- **우리**: ACTH가 부신겉질의 다발층(zona fasciculata)에 있는 멜라노코르틴2수용체(MC2R)에 작용해 코르티솔을 생성한다고 구역까지 특정. 우리 자료 내부에는 과거 B급 출처 간 충돌이 있었음(한쪽은 zona fasciculata, 다른 한쪽은 zona reticularis를 지목); A급 Herman 2016이 zona fasciculata로 해소함. Nieuwenhuys(A급)는 구역을 특정하지 않고 '부신겉질의 요소들'이라고만 기술.
- 근거: Herman 2016 Comprehensive Physiology (A): “At the adrenal cortex, ACTH acts on melanocortin 2 receptors (MC2R) in”
- 메모: 모순 아님(성연 쪽은 구역을 아예 특정하지 않았을 뿐). 브리핑이 지정한 '코르티솔을 만드는 부신 구역(zona fasciculata)' 항목에 해당. 우리 자료의 B급 출처 하나(Bear 2022 StatPearls, zona reticularis)는 A급 Herman 2016과 충돌했지만 A급으로 해소되었으며, 성연 쪽 데이터에는 애초에 이 오류가 없음(구역 미명시).

### papez-circuit-trisynaptic-hippocampal ← papez / papez-5  `granularity`

- **성연**: 띠다발(cingulum)을 통해 해마곁·속후각겉질에 연결된 뒤 관통로를 통해 '해마'로 되돌아간다고만 기술하며, 닫히는 지점으로 subiculum을 명시하지 않음(subiculum은 papez-1에서 출력 기원으로만 언급).  ⟨lecture-plus-existing-draft (메모: 완전한 파페츠 고리는 기존 데이터와 표준 해부학 보완); om-1 p.12,27,35,37,41 / om-2 p.78-80⟩
- **우리**: 삼중시냅스 고리는 CA1→subiculum에서 닫히는 것으로 명시(8단계). 다만 subiculum의 역할 자체에 두 입장이 공존: (1) 고전적 4번째 출력단, (2) 해마·시상·겉질 입력을 재분배하는 통합 허브. 추가로 Nieuwenhuys는 CA1/subicular 출력을 받는 속후각 심층세포가 다시 표층으로 곁가지를 보내는 '두 번째 닫힘 경로'를, Aggleton은 subiculum 뉴런이 띠겉질(area 29)과 유두체 양쪽에 곁가지를 보내는 병렬 분기를 보고함.
- 근거: Gao 2026 Hippocampus (A): “the subiculum has been considered the "fourth leg" and output region of”; Aggleton 2022 Neuroscience & Biobehavioral Reviews (A): “many of the same subiculum neurons that innervate area 29 have”
- 메모: 모순은 아니며 세부도의 차이. 브리핑에서 지정한 'Papez 고리의 닫히는 경로와 subiculum' 항목에 해당.

### spinal-reflex-arcs ← crossed-extension-reflex / crossed-extension-reflex-1  `granularity`

- **성연**: 교차폄반사(사지)의 정중선 교차 사이뉴런 회로를 확립된 사실처럼 기술.  ⟨lecture-grounded; om-2 p.58⟩
- **우리**: merged unsourced 메모: 사지의 일반화된 교차폄 상호연결 회로는 이번 세션에서 연 문헌 어디에도 그 표현대로 기술되어 있지 않음(고전적 교육내용으로만 존재). Nieuwenhuys는 사지가 아닌 목 분절에서 lamina VIII 교차성사이뉴런(글라이신성, 반대쪽 목 운동뉴런 억제)이라는 유사하지만 별개인 회로만 구체적으로 기술.
- 근거: (우리 근거 없음)
- 메모: 교차폄반사 자체의 존재를 반박하는 것은 아니며, 우리 쪽이 사지 버전에 대한 1차 문헌 근거를 아직 확보하지 못했다는 출처 공백. 성연 자료는 이를 공백 표시 없이 확정된 회로로 제시.

### spinocerebellar-tracts ← spinocerebellar-ventral / spinocerebellar-ventral-1  `contradiction`

- **성연**: 앞척수소뇌로는 '척수 운동망 관련 정보'를 전달한다고 서술(고유감각이라는 말을 쓰지 않음).  ⟨lecture-partial-plus-standard-completion; om-1 p.48,49⟩
- **우리**: merged conflicts에 이미 기록된 미해결 충돌: Koh 2023(B급)은 VSCT가 '고유감각이 아니라 운동 정보'를 전달한다고 하나, Kang 2023(A급)과 Shams 2024(B급)는 VSCT가 (양측성) 구심성 고유감각 정보를 전달한다고 기술.
- 근거: Kang 2023 Korean Journal of Neurotrauma (A): “The anterior spinocerebellar tract conveys unconscious proprioception to the lower extremi”
- 메모: 성연 자료는 우리 쪽 B급(Koh) 입장과 같은 편에 서 있고, 우리 A급(Kang) 근거와는 상충. 우리 내부적으로도 미해결 충돌이라 '모순'으로 표시하되 심각도는 high보다 낮춤.

### trigeminal-somatosensory-pathways ← trigeminal-pain / trigeminal-pain-2  `granularity`

- **성연**: 2차 뉴런 출력의 교차는 '뇌줄기 삼차감각핵 출력 교차'로 단일하게 기술되며 아핵별 교차 수준 차이는 언급되지 않는다.  ⟨lecture-grounded; om-1 p.17,18,22 / om-2 p.9,16⟩
- **우리**: Nieuwenhuys(A급)에 따르면 주감각핵·pars oralis·pars interpolaris 유래 섬유는 다리뇌 수준에서 교차하지만, pars caudalis(통각·온도) 유래 섬유는 숨뇌 꼬리쪽에서 교차해 척수시상로에 합류한다 — 아핵에 따라 교차 수준이 다름.
- 근거: Nieuwenhuys 2008 Springer (4th ed.) (A): “The caudal subnucleus gives rise to ascending fibres, which cross in the caudal medulla ob”
- 메모: 교차 위치의 세분화 차이. 아핵별 교차 수준을 구분하지 않으면 통각 경로의 해부학적 위치를 오도할 수 있어 medium으로 표시.

## 3. low — 세분화·용어 차이 (참고)

34건

| 우리 경로 | 성연 경로·단계 | 종류 | 성연 쪽 | 우리 쪽 |
|---|---|---|---|---|
| accommodation-convergence-near-reflex | accommodation accommodation-1 | granularity | 시각입력이 (중간 경로를 명시하지 않고) 바로 양쪽 EW·눈돌림핵으로 이어진다고 단순화한다. 피질-덮개앞 중계 경로의 세부, 그리고 '근접반응 중추가 빛반사 덮개앞핵보다 더 배쪽에 있다'는 논점은  | 우리 쪽은 시각겉질·위둔덕/덮개앞영역을 거친 상위(피질-중뇌) 중계 후 EW·눈돌림핵에 닿는다고 보며, B급(Motlagh 2022)은 근접반응 중뇌중추가 빛반사 덮개앞핵보다 '더 배쪽'이라 명시하 |
| amygdala-fear-circuit | fear-auditory-cued fear-auditory-cued-1 | origin-definition | MGN·A1·LA를 ipsi/contra 양쪽 모두에 표시하여 좌우 병렬회로로 모델링(청각입력이 본래 양측성이므로). | 같은 단계를 laterality: ipsilateral 단일 표기로만 기술(반대측 사본 없음). |
| amygdala-fear-circuit | fear-auditory-cued fear-auditory-cued (lesions) | granularity | 편도체 관련망 손상 → 공포표현·얼굴 공포 인식 등 장애 가능(쪽 명시 없음, 증후군 이름 없음). | 양쪽 편도체/내측측두엽 손상 → Klüver-Bucy 증후군(과다구강행동·과다성욕·초변형증·유순·과식증·시각실인증·기억상실). 단, C급(Bala 2024)과 A급(Sah 2003) 출처 간 증상  |
| anterolateral-system-spinothalamic-tract | spinothalamic-lateral spinothalamic-lateral-2 | granularity | 2차 축삭의 척수 교차(앞백색맞교차)는 '입력 분절에 인접한 수준'에서 일어난다. | merged courseVia는 'a few spinal segments above the level of entry'로 기술(StatPearls B급 '2분절 위' 근거와 일치); Willis&W |
| anterolateral-system-spinothalamic-tract | spinothalamic-lateral spinothalamic-anterior | granularity | 가쪽척수시상로(통각·온도)와 앞척수시상로(거친촉각·압각)를 처음부터 별개의 명명된 경로로 나누어 각각 3단계로 기술한다. | merged anterolateral-system-spinothalamic-tract는 spinothalamic·spinoreticular·spinotectal 성분을 '하나의 경로'로 통합 기술하 |
| ascending-arousal-system-flip-flop | sleep-rem sleep-rem-2 | addition | REM 중 빠른 눈움직임을 일차시각겉질(V1) 등 겉질망의 활성 상태와 동반되는 것으로 기술하고, 동안신경·갓돌림신경을 표적 구조로 나열. | 해당 사항 없음 — 우리 merged 자료는 REM 안구운동의 생성기전(뇌줄기 안구운동 버스트생성기 등)을 다루지 않음. |
| baroreceptor-reflex | baroreflex-vagal (pathway-level) | granularity | 성연 쪽은 압력반사를 미주(부교감) 가지(baroreflex-vagal)와 교감억제 가지(baroreflex-sympathetic)로 완전히 분리된 두 경로로 나누고, 추가로 visceral-aff | 우리 쪽은 하나의 압력수용기반사 경로 안에서 1차(구심)→2차(NTS)가 CVLM/RVLM 교감 축과 의문핵/미주신경 등쪽운동핵 부교감 축으로 갈라지는 5단계 통합 경로로 기술한다. |
| baroreceptor-reflex | visceral-afferent (whole sub-pathway) | addition | 목동맥소체 화학수용기·흉복부 내장감각 등 압력수용기 이외의 IX/X 내장구심 전반을 다루는 별도 경로. | 우리 압력수용기반사 경로에는 화학수용기·흉복부 내장감각 일반은 포함하지 않는다(압력수용기 구심만 범위). |
| baroreceptor-reflex | vagal-parasympathetic (whole sub-pathway) | addition | 미주신경 등쪽운동핵 기원 절전뉴런 → 벽속부교감신경절 → 내장·샘 효과기라는 범용 미주 부교감 원심로(심장에 국한되지 않음)를 별도로 기재. | 우리 경로는 심장 미주출력(심박수 저하)만 다루며, 샘 분비 등 다른 내장효과기로의 일반 미주 원심로는 포함하지 않는다. |
| basal-ganglia-circuits | basal-ganglia-direct basal-ganglia-direct-1 | granularity | 겉질 입력원을 '중심앞이랑(일차운동겉질)'만으로 한정해 표시. | merged 1단계는 겉질 입력원을 운동·전두·마루엽 제3·5층(전운동·보조운동영역 포함)으로 더 넓게 기술하며, MSN이 물질P/GABA(직접경로)·엔케팔린/GABA(간접경로) 두 아형으로 나뉜다 |
| central-auditory-pathway | auditory-central auditory-central-3 | granularity | 달팽이핵 이후 위올리브·가쪽섬유띠 단계에서 구조참조를 ipsi+contra 동등하게 걸어, 어느 쪽이 더 우세한 중계인지 비중을 표시하지 않는다. | 우리 쪽은 사다리꼴체 교차가 '대부분 반대쪽, 일부만 같은쪽'이라고 비중까지 명시한다(구상세포는 같은쪽 LSO+양쪽 MSO, 구형세포는 반대쪽 MNTB로 교차라는 세부도 포함). |
| central-autonomic-control-micturition | autonomic-micturition autonomic-micturition-1 | addition | 저장 상태에서 교감출력이 배뇨근 이완과 '방광목/근위요도 수축'을 돕는다고 기술(evidenceStatus=lecture-plus-correction; 원문의 '교감→내요도조임근 이완'이라는 표기를 | 해당 사항 없음 — 우리 merged 자료는 저장기 교감신경의 방광목/근위요도·배뇨근 효과기 수준 약리작용(알파/베타 수용체 등)을 다루지 않고, 하행 교감경로를 일반적인 시상하부→IML 기술(원래 |
| cerebellar-circuits | olivocerebellar olivocerebellar-3 | terminology | 오름섬유(올리브소뇌)가 푸르키네세포에 글루탐산을 전달물질로 사용한다고 명시. | merged conflicts에 기록된 특별 주의 항목(오름섬유 전달물질): StatPearls(B급, 원 배치)는 '오름섬유는 아스파르트산을 주 흥분성 전달물질로 쓴다'고 하나, Nieuwenhu |
| cerebellar-circuits | cerebellar-purkinje-output cerebellar-purkinje-output-1 | granularity | 소뇌 벌레·꼭지핵 병변의 결손에 좌우(side)를 명시하지 않음(자세·균형 장애로만 기술). | Nieuwenhuys(A급)는 벌레 손상 시 '양측성(bilateral) 축성 운동실조'가 두드러진다고 명시적으로 양측으로 기술. |
| cerebellar-circuits | cerebellovestibular cerebelloreticular | granularity | 꼭지핵의 출력을 안뜰핵 연결(cerebellovestibular)과 그물체 연결(cerebelloreticular)로 별도의 두 경로로 나누어 제시. | merged 6단계는 꼭지핵 출력의 종착지를 'Vestibular nuclei / reticular formation'으로 하나의 단계에 묶어 기술. |
| circadian-retinohypothalamic-scn-pineal | circadian-retina-scn circadian-retina-scn-2 | origin-definition | 정중선 SCN을 '한쪽으로 고정하지 않고 양측망으로 표현'한다는 표시상의 선택으로 서술(해부학적 교차를 명시적 사실로 주장하지는 않음). | ipRGC→망막시상하부로 단계 자체를 laterality: bilateral, decussation: present=true로 명시하며, 'RHT의 상당 성분이 시각교차에서 교차해 양쪽 SCN을 모 |
| circadian-retinohypothalamic-scn-pineal | scn-pineal scn-pineal-2 | granularity | PVN–척수 중간가쪽세포기둥(IML)–위목신경절 연결을 한 단계로 묶어 기술(evidenceStatus 메모: '표준 신경해부학 보완'이며 SCN→솔방울샘 직결 단일축삭이 아님을 강조). | PVN→IML(절전교감, 3단계)과 IML→위목신경절(절후교감, 4단계)을 별개 단계로 분리해 각각 근거를 제시. |
| corticobulbar-tract | corticobulbar corticobulbar-2 | granularity | 삼차신경 운동핵은 양측성 입력을 받는다고 구조적으로 ipsi+contra 둘 다 표시(다른 대부분 운동핵과 동일 취급). | merged conflicts에 기록: StatPearls(B급)는 '양측 입력으로 씹기근이 보존된다'고 설명하지만 Nieuwenhuys(A급, 원숭이 추적 연구 인용)는 삼차신경 운동핵에 대한 직 |
| corticospinal-tracts | corticospinal-lateral corticospinal-lateral-1 | addition | CST의 겉질 기원에 M1·전운동영역뿐 아니라 몸감각겉질·마루영역(제5층)도 포함된다고 서술. | merged 1단계는 기원을 '일차운동겉질(BA4), 전운동·보조운동영역 기여'로만 기술하고 몸감각·마루겉질 기여는 언급하지 않음. |
| dcml-pathway | dcml dcml-1 | granularity | 쐐기다발은 대략 T6 이상에서 존재하며, 널판다발(하지·하부몸통)과 쐐기다발(상지·상부몸통)은 신체부위별 대안 경로로 뚜렷이 나뉜다. | 원 배치(StatPearls, B급)는 T7을 경계로 한 뚜렷한 분절 구분을 제시하나, Nieuwenhuys(A급)는 점진적 전환을 기술하며 흉부 일부 섬유가 널판다발·쐐기다발 사이 중간 위치를 차 |
| dcml-pathway | dcml dcml-5 | addition | 시상겉질축삭이 속섬유막 뒤다리와 방사관(corona radiata)을 모두 경유해 S1에 도달한다. | merged 3단계 courseVia는 'posterior limb of internal capsule'만 명시하고 방사관은 언급하지 않는다. |
| dcml-pathway | somatosensory-cortical-processing somatosensory-cortical-processing-2 | granularity | BA3b의 출력이 BA1(질감 처리)과 BA2(크기·형태 처리)로 병렬 전달되는 피질내 처리 단계가 별도로 존재한다. | merged dcml-pathway의 3단계는 중심뒤이랑 BA 3,1,2를 구분 없이 하나의 종착점으로만 기술하며, BA3b→BA1/BA2 병렬처리 단계는 없다. |
| descending-pain-modulation | opioid-analgesia opioid-analgesia-1 | addition | 오피오이드(뮤 수용체)가 PAG 내 GABA성 입력·방출을 억제해 PAG 하행출력뉴런을 '탈억제'한다는 구체적 세포기전을 명시. | merged 1단계는 PAG 회로에 GABA가 존재한다고만 나열("glutamate (ascending); serotonin, norepinephrine, dopamine, enkephalin, G |
| dopamine-reward-pathways | mesolimbic-dopamine mesolimbic-dopamine-1 | addition | VTA 도파민뉴런이 국소 GABA 입력(cell-vta-gaba)과 흥분입력의 조절을 받는다고 명시. | VTA 도파민뉴런을 중뇌둘레/중뇌겉질 투사의 세포체로만 기술하며 국소 GABA성 조절회로는 기술하지 않음. |
| extrapyramidal-descending-tracts | vestibulospinal-medial vestibulospinal-medial-2 | granularity | 안쪽안뜰척수로가 '하행 MLF(내측종속)'를 통해 목·상부흉부에 이른다고 주행 경로를 구체화. | merged 2단계는 안쪽안뜰척수로의 주행 경로를 별도로 명시하지 않고 기원(Schwalbe nucleus)과 종착(목·상지 근육)만 기술. |
| gustatory-pathway | gustatory-central gustatory-central-3 | terminology | 시상 중계핵을 'VPM'으로만 표기한다(소세포부 VPMpc 세분 없음). | 우리 쪽은 'VPMpc(소세포부, parvicellular division)'로 더 세분해 표기하며, A급 Nieuwenhuys는 'VPp(미각 담당 소세포 VPM 꼬리쪽 절반)'라는 동의어를 쓴다 |
| horizontal-vestibulo-ocular-reflex | hvor-inhibition (whole sub-pathway) | granularity | 길항근 억제(같은쪽 갓돌림핵 억제 → 같은쪽 가쪽곧은근 이완 / 반대쪽 안쪽곧은근 이완)를 hvor 본경로와 별도의 독립 하위경로로 기재한다. | 우리 쪽은 같은 억제성 push-pull 기전(반대쪽 흥분/같은쪽 억제, 글리신·GABA성)을 본경로의 4번째 step(order 4, neuronOrder 2)으로 통합해 기술한다. |
| hypothalamo-pituitary-axes | hypothalamic-anterior-pituitary hypothalamic-anterior-pituitary-3 | granularity | 표적호르몬의 음성되먹임을 '시상하부·앞엽'으로만 기술. | 코르티솔의 음성되먹임이 시상하부(PVH)와 뇌하수체앞엽뿐 아니라 해마에도 선택적으로 작용한다고 명시. |
| jaw-jerk-reflex | jaw-jerk jaw-jerk-2 | terminology | 중뇌삼차핵→삼차운동핵 연결을 '단일시냅스'로만 서술한다. | 우리 쪽 B급은 단일시냅스로 보지만, A급 Nieuwenhuys는 일부 곁가지가 위삼차핵(supratrigeminal nucleus)을 거쳐 이차시냅스하는 성분도 있어 순수 단일시냅스가 아닐 수 있 |
| olfactory-pathway | olfactory-central olfactory-central-3 | granularity | 일차후각망이 눈확이마겉질·시상(배가운데핵, MD)·시상하부·해마와 연결되며 '시상이 이 상위처리의 일부에 참여할 수 있다'고 한다. | 우리 쪽은 후각이 '필수적인(obligatory) 시상 중계 없이' 겉질에 도달하는 유일한 감각계라고 강조한다(A급 Nieuwenhuys: 후각 외 모든 감각은 특정 시상핵을 거친다). 다만 이것이 |
| papez-circuit-trisynaptic-hippocampal | papez papez (lesions) | granularity | 양쪽 해마·뇌활 손상 → 새 서술기억 형성 장애 (단일하게 뭉뚱그림). | 손상 부위별로 증후군을 구분: (1) 양쪽 내측측두엽 광범위 절제(H.M.) → 전반적 전향기억상실, (2) 유두체/전시상/유두시상로(티아민 결핍) → Wernicke-Korsakoff 증후군(전향 |
| spinocerebellar-tracts | spinocerebellar-ventral spinocerebellar-ventral-1 | granularity | 2차 뉴런의 위치를 'DRG → 척수'로만 표기하고 별도 세포집단을 지정하지 않는다. | merged 3단계는 VSCT 2차 뉴런을 요추부 반대쪽 척수경계세포(contralateral spinal border cells of the lumbar cord)로 구체화(Nieuwenhuys  |
| trigeminal-somatosensory-pathways | trigeminal-touch trigeminal-touch-2 | granularity | 분별촉각 2차 뉴런 출력은 '주로 교차'하여 반대쪽 삼차시상로로 가며, 구강 일부 촉각에 양측 투사가 있다고만 서술(구체적 두 다발 이름 없음). | merged은 같은쪽 등쪽삼차시상로(DTTT, 주감각핵에서 기원, 구강 내부 정보, 비교차)와 반대쪽 배쪽삼차시상로(VTTT, 주감각핵·척수삼차핵에서 기원, 교차)를 별개 명명 경로로 구분. |
| visual-pathway | visual-nasal visual-nasal-2 / visual-temporal-2 | terminology | 코쪽 섬유만 시각교차에서 교차하고 관자쪽 섬유는 같은쪽에 남는다; 시야 위쪽은 새발톱고랑 아래 둑, 아래쪽은 위 둑에 투사된다. | 완전히 같음: 코쪽(교차)·관자쪽(비교차) 반분, 위시야→아래 둑(혀이랑)·아래시야→위 둑(쐐기) 매핑이 B·A급 근거와 정확히 일치한다. |

## 4. 성연 데이터에만 있는 내용 (우리 근거 범위 밖)

- visceral-afferent (baroreceptor-reflex 관련): 압력수용기 외 화학수용기·흉복부 내장감각까지 포괄하는 IX/X 내장구심 경로(범위 확장).
- vagal-parasympathetic (baroreceptor-reflex 관련): 심장에 국한되지 않는 범용 미주 부교감 원심로(절전→신경절→효과기).
- vestibular-nystagmus (horizontal-vestibulo-ocular-reflex 관련): VOR 느린상/빠른상 구분과 '빠른상=안진 방향' 정의, 급성 말초안뜰 소실 시 자발안진의 빠른상이 정상쪽이라는 임상 규칙 — 우리 merged 근거에는 없음.
- caloric-warm (horizontal-vestibulo-ocular-reflex 관련): 온도안진 검사: 따뜻한 물은 같은쪽(검사귀) 빠른상을 유발 — 우리 merged 근거에는 온도안진 자체가 없음.
- caloric-cold (horizontal-vestibulo-ocular-reflex 관련): 온도안진 검사: 차가운 물은 반대쪽 빠른상을 유발(COWS 규칙 언급) — 우리 merged 근거에 없음.
- semicircular-push-pull (horizontal-vestibulo-ocular-reflex 관련): 회전 시작·등속 적응·정지 시 양쪽 반고리관 구심발화가 상반되게 변하는 생리(밀기-당기기) — 우리 merged 근거에 없음.
- vor-adaptation (horizontal-vestibulo-ocular-reflex 관련): 안뜰(이끼섬유)·망막오차(하올리브 오름섬유) 입력이 소뇌 푸르키네 가소성을 통해 VOR 이득을 학습 조정하는 경로 — 우리 merged 근거에 없음(소뇌 회로는 별도 경로 cerebellar-circuits에서 다룰 수 있음).
- jaw-opening-reflex (jaw-jerk-reflex 관련): 구강 내 통증성 자극 → 삼차 구심 → 사이뉴런 경유 → 삼차운동핵(턱벌림근) 출력이라는 다중시냅스 '턱벌림반사'를 별도 경로로 제시 — 우리 jaw-jerk-reflex merged 근거에는 이 반사 자체가 없음(원문도 '세부 미확정'으로 표시).
- visceral-afferent (gag-pharyngeal-and-cough-reflex 관련): 압력수용기·화학수용기·흉복부 내장감각까지 포괄하는 범용 IX/X 내장구심 경로(baroreceptor-reflex에도 중복 매핑) — 우리 gag/cough 근거 범위 밖.
- sympathetic-head-neck (sympathetic-pathway-to-the-eye-horner-syndrome 관련): 위목신경절 절후출력이 동공확대근 외에 심장·혈관(ef-heart-vessels)에도 작용한다고 명시 — 우리 쪽 눈 교감경로 merged 근거의 범위(눈) 밖.
- visual-dorsal (visual-pathway 관련): 등쪽흐름(Where): V1→V2→MT/V5→마루연합겉질. 공간·움직임·시각운동안내 처리, 마루연합겉질 손상 시 움직임·공간처리 장애 — 우리 merged 근거에는 등쪽/배쪽 흐름 자체가 없음(V1 이후는 위둔덕·덮개앞핵·시교차위핵으로 가는 비-무릎핵경로만 있음).
- visual-ventral (visual-pathway 관련): 배쪽흐름(What): V1→V2→V4→아래관자겉질. 물체 형태·색·정체 인식, 아래관자겉질 손상 시 시각실인증·얼굴인식장애 — 우리 merged 근거에 없음.
- visual-cortical-feedback (visual-pathway 관련): V1 층별 병렬출력: 제4층(LGN 입력)→제2·3층(외줄무늬겉질行)과 별도로 제5층(위둔덕行)·제6층(LGN 되먹임行)이 동시에 나간다는 V1 미세회로 — 우리 merged 근거는 V1을 단일 종착점으로만 다루고 이런 층별 분기를 모델링하지 않음.
- visual-m (visual-pathway 관련): M(큰세포)/P(작은세포)/K(먼지세포) 경로를 LGN 층(1·2 / 3~6 / 주층사이)과 V1 표적층(4Cα / 4Cβ / 색상블롭)까지 세분 — 우리 merged 근거(LGN M1/M2, P3~P6 눈쪽 매핑)와 상충하지 않고 더 세분화된 추가 내용.
- auditory-tonotopy (central-auditory-pathway 관련): 바닥막의 위치부호(바닥=고주파/꼭대기=저주파)와 나선신경절의 발화율·phase locking을 통한 주파수·강도 부호화 — 우리 merged 근거에는 달팽이 내 주파수부호화 메커니즘 자체가 없음.
- acoustic-attenuation-reflex (central-auditory-pathway 관련): 큰 소리 → 달팽이핵 → 양쪽 VII(등자근)·V3(고막긴장근) 운동출력 → 중이근 수축이라는 음향감쇠반사 — 우리 central-auditory-pathway merged 근거에는 이 반사 자체가 없음(올리브달팽이 하행계는 있지만 중이근반사는 별개).
- vestibular-postural-reflex (central-vestibular-pathways 관련): 기울임·안뜰 불균형에 따라 양쪽 폄근·굽힘근 출력이 반대로 바뀌는 자세교정반사(목·안뜰 입력→양측 척수운동망) — 우리 central-vestibular-pathways merged 근거에는 이 자세반사 자체가 없음.
- vestibulo-autonomic (central-vestibular-pathways 관련): 안뜰핵 입력이 NTS·CVLM·RVLM·다리뇌팔핵을 거쳐 IML 교감출력(자세변화 시 혈압조절)에 영향을 준다는 안뜰-교감반사 — 우리 merged 근거에 없음.
- otolith-tilt (central-vestibular-pathways 관련): utricle/saccule 평형반(striola)의 방향배열에 따른 유모세포 흥분·억제라는 말초 이석기관 수용기 수준의 세부 — 우리 central-vestibular-pathways merged 근거는 중추경로 중심이라 이 말초 수용 메커니즘을 다루지 않음.
- olfactory-combinatorial-code (olfactory-pathway 관련): 한 ORN=한 수용체 종류, 같은 수용체 ORN의 토리 수렴, 농도에 따른 발화율·잠복기·모집범위 변화, 이상겉질의 희소(sparse) 분산표현이라는 후각의 조합·농도 부호화 메커니즘 — 우리 merged 근거에는 이 부호화 메커니즘 자체가 없음.
- declarative-memory-input (papez-circuit-trisynaptic-hippocampal 관련): 연합겉질(전전두·마루·아래관자)→해마곁/후각곁/속후각→해마 결합·출력 경로(서술기억 공고화 입력망); 우리 자료에 해당 단계 없음.
- systems-consolidation (papez-circuit-trisynaptic-hippocampal 관련): 해마-겉질 상호작용에 따른 기억의 체계 공고화 모델(시간에 따른 ACC 의존성 증가); 우리 자료에 없음.
- spatial-memory (papez-circuit-trisynaptic-hippocampal 관련): 속후각 격자세포-해마 장소세포 집단에 의한 공간항법/위치기억 부호화; 우리 자료에 없음.
- association-cingulum (papez-circuit-trisynaptic-hippocampal 관련): 띠다발을 통한 동측 연합겉질 연결을 파페츠와 별도 항목으로 분리해 기술(내용은 papez-4/5와 중복).
- fear-return (amygdala-fear-circuit 관련): 소거 후 공포 재발현 패러다임(재설치·자발적회복·renewal)과 vmPFC 관여; 우리 자료에 없음.
- amygdala-thalamic-ltp (amygdala-fear-circuit 관련): 시상-LA 시냅스 LTP의 세포/분자기전(NMDA/VDCC, 시냅스후 발현, 시냅스전/후 GABA_B 억제성 관문); 우리 자료에 이 수준의 세포기전 기술 없음.
- vta-gaba-feedback (dopamine-reward-pathways 관련): NAc GABA성 MSN 출력이 VTA로 되먹임되고, VTA 국소 GABA세포가 도파민뉴런 발화를 억제하는 억제성 조절 루프; 우리 자료에 없음(우리 쪽은 VTA→NAc/PFC 원심성 투사만 기술).
- rem-atonia (ascending-arousal-system-flip-flop 관련): REM 관련 뇌줄기망→척수 억제성사이뉴런→알파운동뉴런 억제에 의한 REM 무긴장 기전과 REM 행동장애(RBD) 손상; 우리 자료는 vlPAG/LDT-PPT까지만 기술하고 척수 수준 무긴장 기전이나 RBD 손상 항목이 없음.
- thalamocortical-oscillation (ascending-arousal-system-flip-flop 관련): 시상 중계핵-시상그물핵-겉질 재귀연결에 의한 EEG 동기화/진동 기전(시상겉질 루프); 우리 자료에 없음(우리 쪽은 각성계 핵 자체의 투사만 다룸).
- autonomic-micturition (central-autonomic-control-micturition 관련): 저장-배뇨 상태 전환을 교감(배뇨근 이완+방광목 수축)·부교감(S2-4, 배뇨근 수축)·체성(음부신경, 외조임근 수축) 3계통 출력의 균형으로 기술하는 저장기 약리/효과기 수준 세부; 우리 자료에는 이 수준의 저장기 교감 효과기 기술이 없음.
- circadian-retina-scn (circadian-retinohypothalamic-scn-pineal 관련): SCN 시계출력이 솔방울샘 경로 외에도 수면-각성·신경내분비 리듬 전반을 조정한다는 일반적 요약; 우리 자료는 SCN→솔방울샘 멜라토닌 축에만 범위를 한정.
- somatosensory-cortical-processing (dcml-pathway 관련): 시상 VP(VPL/VPM)→S1 4층(BA3b)→BA1·BA2 병렬 피질내 처리 경로 전체가 merged dcml-pathway에는 없음.
- pain-affective (anterolateral-system-spinothalamic-tract 관련): 통증의 정서·인지 처리 경로(척수그물로→그물체→시상 중계→ACC·섬겉질·PFC 양측 네트워크)와 통증상징불능 병변이 merged에는 없음.
- pain-gate-control (anterolateral-system-spinothalamic-tract 관련): Aβ 무해촉각 입력이 뒤뿔 아교질의 억제성사이뉴런을 통해 통각 전달(가쪽척수시상로)을 줄이는 관문조절설이 merged에는 없음.
- trigeminocerebellar (trigeminal-somatosensory-pathways 관련): 얼굴·턱 감각입력이 삼차중뇌핵 관련 경로를 거쳐 아래소뇌다리로 소뇌(벌레·곁벌레부위 과립세포)에 전달되는 삼차소뇌 경로 전체가 merged trigeminal-somatosensory-pathways에는 없음.
- pain-gate-control (descending-pain-modulation 관련): Aβ 무해촉각 입력의 뒤뿔 관문조절(아교질 억제성사이뉴런)이 하행 통각조절과 별도 모형으로 제시되나 merged descending-pain-modulation에는 해당 모형이 없음(anterolateral-system 비교에서도 동일하게 추가 항목으로 표시).
- cranial-v-motor (corticobulbar-tract 관련): 삼차신경 운동핵→V3→씹기근의 LMN 최종경로가 merged corticobulbar-tract에는 (1단계의 일반 언급 외) 별도 단계로 없음.
- cranial-ix-x-motor (corticobulbar-tract 관련): 의문핵→IX(붓인두근)·X(인두·후두근)의 LMN 최종경로가 merged corticobulbar-tract에는 별도 단계로 없음(핵 이름은 unsourced 메모에만 언급됨).
- cranial-xi-motor (corticobulbar-tract 관련): 더부신경 척수핵→XI→목빗근·등세모근의 LMN 최종경로가 merged corticobulbar-tract에는 별도 단계로 없음.
- procedural-memory (basal-ganglia-circuits 관련): 전전두·마루연합겉질→선조체 학습(습관·절차기억)→시상겉질 되먹임 경로가 merged basal-ganglia-circuits(직접·간접·과직접 운동루프 중심)에는 없음.
- stn-dbs-network (basal-ganglia-circuits 관련): STN 부근 전기자극이 국소뉴런·통과축삭·바닥핵-시상겉질망 활동에 미치는 영향(DBS 모형)이 merged에는 없음.
- reticulocerebellar (cerebellar-circuits 관련): 피개그물핵→소뇌겉질(양측) 구심 입력 경로가 merged cerebellar-circuits에는 없음.
- tectocerebellar (cerebellar-circuits 관련): 위둔덕→소뇌겉질(양측) 구심 입력 경로가 merged에는 없음.
- corticorubral (cerebellar-circuits 관련): 일차운동겉질→적색핵(양측, 교차 불명) 연결이 merged cerebellar-circuits에는 없음.
- cerebellar-mossy-circuit (cerebellar-circuits 관련): 골지세포가 과립세포 입력을 억제하는 소뇌겉질 내부 되먹임 가지(골지 억제회로)가 merged에는 없음.
- corticoreticular (extrapyramidal-descending-tracts 관련): 전운동영역(PMA, 양측)→그물체 연결이 merged extrapyramidal-descending-tracts에는 없음.
- gamma-loop (spinal-reflex-arcs 관련): 감마운동뉴런→방추속근섬유→Ia→알파운동뉴런의 감마고리(신장반사 감도 조절)가 merged spinal-reflex-arcs에는 없음.
- renshaw-inhibition (spinal-reflex-arcs 관련): 알파운동뉴런 재귀 곁가지(ACh)→렌쇼세포→글라이신성 되먹임억제 회로가 merged에는 없음.
- alpha-gamma-coactivation (spinal-reflex-arcs 관련): 수의운동 중 알파·감마운동뉴런 공동활성(방추 감각 민감도 유지 기전)이 merged에는 없음.

## 5. 기준쪽(origin) 정의 비교

- baroreceptor-reflex: 같음: 양쪽 다 '혈압 변화를 감지(자극받는) 압력수용기 쪽'을 기준쪽(origin)으로 삼는다(theirs defaultOriginSide=L은 예시일 뿐 정의 자체는 동일).
- pupillary-light-reflex: 같음: 양쪽 다 origin을 '빛을 비춘 눈'으로 정의한다(theirs origin.ko = ours draft origin_ko 모두 동일 문구).
- horizontal-vestibulo-ocular-reflex: 핵심 hvor 경로는 둘 다 origin='머리가 도는 쪽'으로 같다. 다만 theirs는 하위 경로마다 origin 정의를 바꾼다: vestibular-nystagmus는 '흥분이 상대적으로 큰 안뜰기관 쪽', caloric-warm/cold는 '검사하는 귀 쪽', vor-adaptation은 '오류를 조절하는 소뇌반구' — 모두 생리학적으로 타당한 맥락별 재정의이며 모순은 아니다(origin-definition 성격). ours merged 파일에는 caloric/nystagmus에 대응하는 경로 자체가 없어 직접 비교 불가.
- horizontal-conjugate-gaze-saccade-circuit: origin 정의가 하위 경로마다 다르다: cortical-gaze-control은 origin='눈운동을 계획하는 대뇌반구'(FEF 쪽 기준) 인데, cranial-vi-motor·cranial-iii-motor는 origin='출력받는 근육 쪽'(말초 근육 기준)으로 바뀐다. 같은 ipsi/contra 라벨이 하위 경로에 따라 가리키는 실제 쪽이 달라질 수 있어 origin-definition 성격의 차이로 분류(모순 아님, 주의 필요).
- corneal-blink-reflex: 같음: 양쪽 다 origin을 '각막을 자극받는 눈 쪽'으로 정의한다.
- jaw-jerk-reflex: jaw-jerk 본경로는 origin='늘어난 씹기근 쪽'으로 같은 개념이다. 다만 cranial-v-motor는 origin='출력받는 근육 쪽'으로 기준을 바꾼다(origin-definition 성격, 모순 아님).
- gag-pharyngeal-and-cough-reflex: gag-reflex/cough-reflex는 origin='자극받는 쪽'으로 ours와 같다. cranial-ix-x-motor는 origin='출력받는 근육 쪽'으로 바뀌고, swallowing/cough-reflex는 origin을 '자극 부위 쪽 또는 회로 표시 기준'으로 모호하게 둔다 — origin-definition 성격의 차이로, 모순은 아니지만 좌우 라벨 해석 시 주의 필요.
- accommodation-convergence-near-reflex: theirs origin='주시하는 눈 또는 표시 반구'로 모호하게 두 기준을 병기한다. ours는 전 과정을 양쪽(bilateral) 공조 반응으로만 기술해 origin 개념 자체가 약하다 — 실질적 차이는 없음(둘 다 결과가 항상 양쪽).
- sympathetic-pathway-to-the-eye-horner-syndrome: theirs origin='출력받는 눈 쪽'(또는 '머리·목 쪽')으로, ours의 전 과정이 같은쪽(ipsilateral, uncrossed)으로만 진행한다는 것과 실질적으로 같다. 교차가 전혀 없으므로 origin 정의 차이가 결과에 영향을 주지 않음.
- visual-pathway: theirs 안에서도 origin 기준이 바뀐다: visual-nasal/visual-temporal은 origin='빛을 받는 눈 쪽'(눈 기준, ours와 동일)인데, visual-m/p/k·visual-dorsal·visual-ventral·visual-cortical-feedback은 origin을 '시각입력을 처리하는 반구'(중추 반구 기준)로 바꾼다(visual-m-1 설명에 '이 경로의 기준은 눈이 아니라 중추 반구다'라고 명시). 같은 'ipsi/contra' 라벨이 하위 경로에 따라 눈 쪽을 가리키는지 반구 쪽을 가리키는지 달라지므로 origin-definition 성격의 주의가 필요(모순은 아님).
- central-auditory-pathway: 같음: 모든 theirs 하위 경로가 origin='소리를 받는(또는 먼저/더 크게 받는) 귀 쪽'으로 ours의 귀 기준 ipsi/contra와 일치한다. 확인 결과: 속섬유막 렌즈핵밑부분(sublenticular)을 지나는 청각부챗살 서술은 theirs auditory-central-5와 ours order 6(Nieuwenhuys A급 'traverses the sublenticular portion of the internal capsule')가 정확히 일치 — 차이 없음(지시사항 주목 항목 확인 완료).
- central-vestibular-pathways: 대부분 origin='안뜰입력을 받는 쪽'으로 ours의 귀(안뜰기관) 기준과 같다. 다만 vestibulospinal-lateral/medial은 origin을 '하행 출력을 내는 뇌줄기 핵 쪽'으로 바꾼다 — 안뜰핵 쪽과 자극받은 귀 쪽이 보통 같으므로(안뜰핵은 같은쪽 귀 입력을 받음) 실질적 차이는 적지만 명시적으로 다른 기준이다(origin-definition).
- gustatory-pathway: 같음: 둘 다 origin='맛 자극을 받는 쪽'.
- olfactory-pathway: 같음: 둘 다 origin='냄새를 받는 코 쪽'. 핵심 내용(같은쪽 진행, 시상을 거치지 않고 일차후각겉질에 바로 도달, 이상겉질·후각결절·편도체·속후각겉질로 분산)이 정확히 일치.
- papez-circuit-trisynaptic-hippocampal: 동일: 양쪽 모두 '표시할(정보를 받는) 해마반구'를 기준으로 ipsi를 정의하며, Papez 고리 자체는 교차를 주장하지 않는 점에서 일치.
- amygdala-fear-circuit: 표시 관례 차이: 성연 쪽은 양측성 회로로 보고 각 단계마다 ipsi/contra 구조를 둘 다 나열(교차를 주장하는 것은 아니고 '좌우 평행회로'를 함께 표시). 우리 쪽은 단계마다 laterality:ipsilateral 단일경로만 기술하고 반대측 사본을 별도로 표시하지 않음. 교차가 없다는 점 자체는 양쪽이 일치.
- dopamine-reward-pathways: 성연 쪽 데이터셋 내부가 일관되지 않음: mesolimbic-dopamine/mesocortical-dopamine/vta-gaba-feedback은 origin을 '표시할 회로의 쪽(양측성 표시 기준)'으로 정의해 각 단계에 ipsi·contra 구조를 모두 나열하지만, nigrostriatal만 '도파민 출력을 내는 반구'로 정의해 ipsi만 표시. 우리 쪽은 전 단계 laterality: ipsilateral(세포체 기준 동측) 단일 표기로 nigrostriatal 쪽 정의와 더 가까움.
- ascending-arousal-system-flip-flop: 일치: 양쪽 모두 이 경로 전체를 본질적으로 양측(정중선 포함)성으로 간주. 성연 쪽은 각 단계에 ipsi/contra 구조를 모두 나열하고, 우리 쪽도 거의 모든 단계를 laterality: bilateral로 기술하며 decussation은 어느 쪽도 주장하지 않음.
- hypothalamo-pituitary-axes: 일치: 양쪽 모두 이 축을 정중선/양측 구조로 간주(성연 쪽 ipsi+contra 병렬 표시, 우리 쪽 laterality: bilateral/midline). 교차 주장 없음.
- central-autonomic-control-micturition: 표시 관례 차이만 있음: autonomic-micturition·parasympathetic-sacral 모두 '표시할 회로의 쪽' 또는 '출력받는 골반장기 쪽'을 기준으로 하며, 우리 쪽 laterality(ipsilateral/bilateral)와 실질적으로 충돌하지 않음.
- circadian-retinohypothalamic-scn-pineal: 부분 일치: circadian-retina-scn은 '빛을 받는 눈 쪽'(망막 기준), scn-pineal은 '표시할 회로의 쪽'(일반 표시 기준)으로 서로 다른 origin 정의를 쓰지만, SCN 단계부터는 둘 다 양측(ipsi+contra) 구조로 전환해 사실상 우리 쪽의 laterality: bilateral(1·2단계)과 일치. 전체적으로 SCN→PVN→IML→위목신경절→솔방울샘 연쇄의 구조·순서는 양쪽 데이터셋이 서로 잘 들어맞음(브리핑 지정 항목 중 가장 일치도가 높음).
- dcml-pathway: 두 쪽 모두 origin을 '자극을 받는 몸 쪽(자극이 가해지는 신체 측)'으로 정의한다. 우리 merged의 laterality 표기(ipsilateral/contralateral)도 같은 기준(자극측 대비)이라 정의 충돌 없음.
- anterolateral-system-spinothalamic-tract: 통증 경로(spinothalamic-lateral/anterior)는 '자극을 받는 몸 쪽'을 origin으로 정의해 우리 laterality 기준과 동일. pain-affective는 양측·정중선 회로라 origin이 '표시할 회로의 쪽(기준점일 뿐)'으로 다르게 정의되는데, 이는 정의 충돌이 아니라 해당 회로가 본질적으로 양측성이라는 점을 반영한 것.
- trigeminal-somatosensory-pathways: 두 쪽 모두 origin을 '자극을 받는 얼굴 쪽'(통증·촉각) 또는 '감각·운동정보를 보내는 몸 쪽'(삼차소뇌)으로 정의하며 우리 laterality 기준과 동일.
- spinocerebellar-tracts: 두 쪽 모두 origin을 '감각·운동정보를 보내는 몸 쪽'으로 정의하며 동일 기준.
- descending-pain-modulation: 세로토닌·노르에피네프린 경로는 '표시할 회로의 쪽(양측성 회로의 표시 기준)'으로, opioid-analgesia는 '통증입력을 받는 몸 쪽'으로 정의. 양측성 회로라는 전제는 merged의 laterality: bilateral과 일치하여 정의 충돌 없음.
- corticospinal-tracts: 두 쪽 모두 origin을 '운동명령을 생성하는 대뇌반구'로 정의, 우리 laterality 기준(피질 기준 ipsi/contra)과 동일.
- corticobulbar-tract: corticobulbar는 '운동명령을 생성하는 대뇌반구', 각 뇌신경 LMN 출력 경로는 '출력받는 근육 쪽'으로 정의 — 둘 다 우리 laterality 기준(피질/근육 어느 쪽을 기준점으로 할지 명시)과 호환되며 충돌 없음.
- basal-ganglia-circuits: 모든 theirs 경로가 origin을 '회로를 표시/학습/자극할 대뇌반구'로 정의하며, 직접·간접·흑색질선조체 회로가 사실상 전부 동측(ipsilateral) 루프라는 점에서 우리 laterality 기준과 일치. 충돌 없음.
- cerebellar-circuits: 경로별로 '운동/출력을 보내는 대뇌·소뇌반구' 또는 '연결을 시작하는 구조 쪽'으로 정의되며 모두 우리 기준(겉질겉다리뇌소뇌는 반대쪽 소뇌, 소뇌출력은 반대쪽 겉질 — 이중교차로 최종 동측)과 호환. 충돌 없음.
- extrapyramidal-descending-tracts: 각 경로의 origin을 '하행 출력을 내는 뇌줄기 핵 쪽' 또는 '자세 이상을 관찰하는 몸 쪽'으로 정의. 뇌줄기 핵 기준 좌우는 우리 laterality 기준(핵/구조 기준)과 호환되어 정의 자체의 충돌은 없음.
- spinal-reflex-arcs: 모든 경로가 origin을 '늘어난/수축하는/조절되는/장력이 증가한/유해자극을 받는 근육·팔다리 쪽'으로 정의하며 우리 laterality 기준(동측 반사 다수, 교차폄반사만 반대쪽)과 호환.
