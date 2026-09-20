import pathwaysJson from '../../content/pathways.json';
import { pathwayMeshIds, pathwayRoute, stepMeshIds, type PathwayRoute } from './pathways';
import { AtlasScene, type ViewPreset } from './scene/AtlasScene';
import { SectionPanel, type SectionHit, type SectionMeta } from './sections/SectionPanel';
import './style.css';
import type { Manifest, ManifestMesh, ManifestStructure, OriginSide, Pathway } from './types';

type Mode =
  | { kind: 'explore' }
  | { kind: 'structure'; structureId: string }
  | { kind: 'pathway'; pathwayId: string; origin: OriginSide; step: number; playing: boolean };

const PATHWAYS = pathwaysJson.pathways as Pathway[];
const SIDE_LABEL: Record<string, string> = { L: '왼쪽', R: '오른쪽', M: '정중' };
const STEP_SECONDS = 4;

const $ = <T extends HTMLElement>(sel: string) => document.querySelector<T>(sel)!;
function el<K extends keyof HTMLElementTagNameMap>(tag: K, props: Record<string, unknown> = {}, ...children: (Node | string)[]): HTMLElementTagNameMap[K] {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

async function main() {
  const manifest: Manifest = await (await fetch(`${import.meta.env.BASE_URL}data/manifest.json`)).json();
  const meshLookup = new Map<string, ManifestMesh>(manifest.meshes.map((m) => [m.id, m]));
  const structures = new Map<string, ManifestStructure>(manifest.structures.map((s) => [s.id, s]));

  const scene = new AtlasScene($<HTMLCanvasElement>('#canvas'));
  await scene.load(manifest, `${import.meta.env.BASE_URL}data/atlas.glb`);
  $('#loading').hidden = true;

  let mode: Mode = { kind: 'explore' };
  let route: PathwayRoute | null = null;
  let timer: number | undefined;

  const pathwayOf = (m: Extract<Mode, { kind: 'pathway' }>) => PATHWAYS.find((p) => p.id === m.pathwayId)!;

  function setMode(next: Mode, opts: { focus?: boolean } = {}) {
    const prev = mode;
    mode = next;
    window.clearInterval(timer);

    if (mode.kind === 'explore') {
      scene.setStates(() => 'normal');
      scene.setRoute(null);
      route = null;
    } else if (mode.kind === 'structure') {
      const ids = new Set(structures.get(mode.structureId)!.meshIds);
      scene.setStates((e) => (ids.has(e.info.id) ? 'active' : 'ghost'));
      scene.setRoute(null);
      route = null;
      if (opts.focus) scene.focus(ids);
    } else {
      const m = mode;
      const pathway = pathwayOf(m);
      const involved = pathwayMeshIds(pathway, m.origin, meshLookup);
      const active = new Set(stepMeshIds(pathway.steps[m.step], m.origin, meshLookup));
      scene.setStates((e) => (active.has(e.info.id) ? 'active' : involved.has(e.info.id) ? 'involved' : 'ghost'));

      const routeChanged = prev.kind !== 'pathway' || prev.pathwayId !== m.pathwayId || prev.origin !== m.origin;
      if (routeChanged) {
        route = pathwayRoute(pathway, m.origin, meshLookup);
        scene.setRoute(route.points);
        scene.focus(involved);
      }
      scene.revealRouteTo(route!.stepEnd[m.step]);

      if (m.playing) {
        timer = window.setInterval(() => {
          if (mode.kind !== 'pathway') return;
          const last = mode.step >= pathwayOf(mode).steps.length - 1;
          setMode({ ...mode, step: last ? mode.step : mode.step + 1, playing: !last });
        }, STEP_SECONDS * 1000);
      }
    }
    renderSidebarState();
    renderDetail();
    syncSection(true);
  }

  // ---------- sidebar ----------
  const sidebar = $('#sidebar');
  const search = el('input', { type: 'search', placeholder: '구조 검색 (한글/영문)', id: 'search' });
  const pathwayList = el('div', { className: 'list' });
  const structureList = el('div', { className: 'groups' });
  sidebar.append(
    el('header', {},
      el('h1', {}, '신경경로 3D 아틀라스'),
      el('p', { className: 'badge' }, '시제품 · 내용 검수 전')),
    el('h2', {}, '신경경로'), pathwayList,
    el('h2', {}, '구조'), search, structureList,
  );

  for (const p of PATHWAYS) {
    const btn = el('button', { className: 'item pathway' }, el('strong', {}, p.name.ko), el('small', {}, p.name.en ?? ''));
    btn.dataset.pathway = p.id;
    btn.onclick = () => setMode({ kind: 'pathway', pathwayId: p.id, origin: p.defaultOriginSide, step: 0, playing: false });
    pathwayList.append(btn);
  }

  for (const [groupId, group] of Object.entries(manifest.groups)) {
    const members = manifest.structures.filter((s) => s.group === groupId);
    if (!members.length) continue;
    const toggle = el('input', { type: 'checkbox', checked: true });
    toggle.onchange = () => scene.setGroupVisible(groupId, toggle.checked);
    const swatch = el('span', { className: 'swatch' });
    swatch.style.background = group.color;
    const items = el('div', { className: 'list' });
    for (const s of members) {
      const btn = el('button', { className: 'item structure' }, s.name.ko, ...(s.approx ? [el('em', {}, '근사')] : []));
      btn.dataset.structure = s.id;
      btn.dataset.search = `${s.name.ko} ${s.name.en ?? ''}`.toLowerCase();
      btn.onclick = () => setMode({ kind: 'structure', structureId: s.id }, { focus: true });
      items.append(btn);
    }
    structureList.append(el('section', { className: 'group' }, el('label', {}, toggle, swatch, group.name.ko, el('small', {}, String(members.length))), items));
  }

  search.oninput = () => {
    const q = search.value.trim().toLowerCase();
    for (const btn of structureList.querySelectorAll<HTMLElement>('.structure')) btn.hidden = !!q && !btn.dataset.search!.includes(q);
    for (const g of structureList.querySelectorAll<HTMLElement>('.group')) g.hidden = !g.querySelector('.structure:not([hidden])');
  };

  function renderSidebarState() {
    for (const b of sidebar.querySelectorAll<HTMLElement>('.item')) {
      b.classList.toggle('current',
        (mode.kind === 'pathway' && b.dataset.pathway === mode.pathwayId) ||
        (mode.kind === 'structure' && b.dataset.structure === mode.structureId));
    }
  }

  // ---------- detail panel ----------
  const detail = $('#detail');

  function renderDetail() {
    detail.replaceChildren();
    if (mode.kind === 'explore') {
      detail.append(
        el('h2', {}, '사용법'),
        el('ul', { className: 'help' },
          el('li', {}, '왼쪽에서 ', el('b', {}, '신경경로'), '를 고르면 참여 구조만 남고 나머지는 투명해집니다.'),
          el('li', {}, '구조를 클릭하면 그 구조만 강조됩니다. 빈 곳을 클릭하면 해제됩니다.'),
          el('li', {}, '드래그: 회전 · 휠: 확대 · 우클릭 드래그: 이동'),
          el('li', {}, '경로 재생 중 ← → 키로 단계를 넘길 수 있습니다. Esc: 나가기')),
        attributionBlock());
      return;
    }
    const close = el('button', { className: 'close', title: '닫기 (Esc)' }, '×');
    close.onclick = () => setMode({ kind: 'explore' });
    detail.append(close);
    if (mode.kind === 'structure') renderStructure(structures.get(mode.structureId)!);
    else renderPathway(mode);
  }

  function renderStructure(s: ManifestStructure) {
    const meshes = s.meshIds.map((id) => meshLookup.get(id)!);
    const usedIn = PATHWAYS.filter((p) => p.steps.some((st) => st.structures.some((r) => r.id === s.id)));
    detail.append(
      el('p', { className: 'eyebrow' }, manifest.groups[s.group].name.ko),
      el('h2', {}, s.name.ko),
      el('p', { className: 'sub' }, s.name.en ?? ''));
    if (s.approx) detail.append(el('p', { className: 'warn' }, '근사 형상: 아틀라스 라벨이 너무 작아 위치만 라벨에서 가져오고 모양은 타원체로 대신했습니다.'));
    const rows = el('dl', {});
    for (const m of meshes) {
      rows.append(el('dt', {}, `${SIDE_LABEL[m.side]} 부피`), el('dd', {}, `${m.volumeMm3.toLocaleString()} mm³`),
        el('dt', {}, `${SIDE_LABEL[m.side]} 중심 (MNI)`), el('dd', {}, m.centroid.map((v) => v.toFixed(1)).join(', ')));
    }
    rows.append(el('dt', {}, '출처'), el('dd', {}, manifest.attribution.find((a) => a.atlas === s.atlas)?.title ?? s.atlas));
    detail.append(rows);
    if (usedIn.length) {
      detail.append(el('h3', {}, '이 구조가 참여하는 경로'));
      for (const p of usedIn) {
        const btn = el('button', { className: 'item' }, p.name.ko);
        btn.onclick = () => setMode({ kind: 'pathway', pathwayId: p.id, origin: p.defaultOriginSide, step: 0, playing: false });
        detail.append(btn);
      }
    }
  }

  function renderPathway(m: Extract<Mode, { kind: 'pathway' }>) {
    const p = pathwayOf(m);
    detail.append(el('p', { className: 'eyebrow' }, '신경경로'), el('h2', {}, p.name.ko), el('p', { className: 'sub' }, p.name.en ?? ''));
    if (p.reviewStatus === 'draft') detail.append(el('p', { className: 'warn' }, '초안: 아직 전문가 검수를 거치지 않은 설명입니다.'));
    detail.append(el('p', {}, p.summary.ko));

    const sides = el('div', { className: 'segmented' });
    for (const side of ['L', 'R'] as const) {
      const b = el('button', { className: side === m.origin ? 'on' : '' }, SIDE_LABEL[side]);
      b.dataset.origin = side;
      b.onclick = () => setMode({ ...m, origin: side });
      sides.append(b);
    }
    detail.append(el('div', { className: 'origin' }, el('span', {}, p.origin.ko), sides));

    const steps = el('ol', { className: 'steps' });
    p.steps.forEach((st, i) => {
      const li = el('li', { className: i === m.step ? 'on' : i < m.step ? 'done' : '' });
      const head = el('button', { className: 'step-head' }, st.title.ko);
      head.onclick = () => setMode({ ...m, step: i, playing: false });
      li.append(head);
      if (i === m.step) {
        const tags = el('p', { className: 'tags' });
        if (st.neuronOrder) tags.append(el('span', {}, `${st.neuronOrder}차 뉴런`));
        if (st.decussation) tags.append(el('span', { className: 'cross' }, '교차'));
        for (const id of stepMeshIds(st, m.origin, meshLookup)) {
          const mesh = meshLookup.get(id)!;
          tags.append(el('span', { className: 'struct' }, `${structures.get(mesh.structureId)!.name.ko} · ${SIDE_LABEL[mesh.side]}`));
        }
        li.append(tags, el('p', {}, st.description.ko));
        if (st.missing) li.append(el('p', { className: 'missing' }, st.missing.ko));
      }
      steps.append(li);
    });
    detail.append(steps);

    const prev = el('button', { disabled: m.step === 0 }, '← 이전');
    prev.onclick = () => setMode({ ...m, step: m.step - 1, playing: false });
    const play = el('button', { className: 'primary' }, m.playing ? '일시정지' : '재생');
    play.onclick = () => setMode({ ...m, step: !m.playing && m.step === p.steps.length - 1 ? 0 : m.step, playing: !m.playing });
    const next = el('button', { disabled: m.step === p.steps.length - 1 }, '다음 →');
    next.onclick = () => setMode({ ...m, step: m.step + 1, playing: false });
    detail.append(el('div', { className: 'transport' }, prev, play, next));

    detail.append(el('h3', {}, '병변과 증상'));
    const lesions = el('dl', { className: 'lesions' });
    for (const l of p.lesions) lesions.append(el('dt', {}, l.level.ko), el('dd', {}, l.deficit.ko));
    detail.append(lesions);
  }

  function attributionBlock() {
    const box = el('div', { className: 'attribution' }, el('h3', {}, '데이터 출처'));
    for (const a of manifest.attribution) {
      box.append(el('p', {}, el('a', { href: a.url, target: '_blank', rel: 'noreferrer' }, a.title), ` — ${a.license}. ${a.citation}`));
    }
    box.append(el('p', {}, '오른쪽 반구는 왼쪽 반구 아틀라스를 좌우 반전해 만든 것입니다.'));
    return box;
  }

  // ---------- stage ----------
  const tooltip = $('#tooltip');

  // ---------- 2D section panel ----------
  const BASE = import.meta.env.BASE_URL;
  const sectionRoot = $('#section');
  const sectionMeta: SectionMeta | null = await fetch(`${BASE}data/sections/axial/meta.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const labelToStructure = new Map<number, string>();
  for (const s of manifest.structures) for (const label of s.labels ?? []) labelToStructure.set(label, s.id);
  let section: SectionPanel | null = null;

  const mix = (c: number[], target: number, t: number) => c.map((v) => Math.round(v + (target - v) * t)) as [number, number, number];

  /** Colour of an atlas label in the 2D section, mirroring what the 3D scene is doing with it. */
  function paintLabel(label: number, side: 'L' | 'R'): [number, number, number] {
    const lut = sectionMeta!.labels[label].color;
    const entry = scene.entries.get(`${labelToStructure.get(label)}.${side}`);
    if (!entry) return mode.kind === 'explore' ? mix(lut, 40, 0.55) : mix([0.3 * lut[0] + 0.59 * lut[1] + 0.11 * lut[2]].flatMap((g) => [g, g, g]), 20, 0.72);
    const base = entry.baseColor.toArray().map((v) => Math.round(Math.sqrt(v) * 255)); // linear -> ~sRGB
    if (entry.state === 'active') return mix(base, 255, 0.25);
    if (entry.state === 'ghost') return mix(base, 45, 0.78);
    return base as [number, number, number];
  }

  function describeHit(hit: SectionHit) {
    const structure = structures.get(labelToStructure.get(hit.label) ?? '');
    const allen = sectionMeta!.labels[hit.label].name.replace(/_/g, ' ');
    return `${structure ? `${structure.name.ko} — ` : ''}${allen} · ${SIDE_LABEL[hit.side]}`;
  }

  function openSection() {
    if (!sectionMeta) return;
    sectionRoot.hidden = false;
    if (!section) {
      const header = el('header', { className: 'section-header' }, el('strong', {}, '가로 단면'));
      sectionRoot.append(header);
      section = new SectionPanel(sectionRoot, sectionMeta, `${BASE}data/sections/axial/`, paintLabel);
      const zoomOut = el('button', { title: '축소' }, '−');
      zoomOut.onclick = () => section!.setZoom(sectionZoom = Math.max(1, sectionZoom / 1.6));
      const zoomIn = el('button', { title: '확대 (Ctrl+휠)' }, '+');
      zoomIn.onclick = () => section!.setZoom(sectionZoom = Math.min(12, sectionZoom * 1.6));
      const brainstem = el('button', { title: '뇌줄기 확대' }, '뇌줄기');
      brainstem.onclick = () => { sectionZoom = 3.2; section!.centerOn(0, -32, sectionZoom); };
      const cut = el('input', { type: 'checkbox', id: 'section-cut' });
      cut.onchange = () => scene.setSectionCut(cut.checked);
      const close = el('button', { title: '단면 닫기' }, '×');
      close.onclick = closeSection;
      header.append(section.readoutElement, el('span', { className: 'spacer' }), zoomOut, zoomIn, brainstem,
        el('label', { className: 'cut', title: '3D에서 이 높이 위쪽을 잘라 냅니다' }, cut, '3D 자르기'), close);
      section.onSliceChange = (z) => scene.setSectionPlane(z);
      section.onHover = (hit, x, y) => {
        tooltip.hidden = !hit;
        if (!hit) return;
        tooltip.textContent = describeHit(hit);
        tooltip.style.transform = `translate(${x + 14}px, ${y + 14}px)`;
      };
      section.onPick = (hit) => {
        const entry = hit && scene.entries.get(`${labelToStructure.get(hit.label)}.${hit.side}`);
        scene.onPick(entry ?? null);
      };
    }
    scene.setSectionPlane(section.zMm);
    syncSection(true);
    sectionToggle.classList.add('on');
  }

  function closeSection() {
    sectionRoot.hidden = true;
    scene.setSectionPlane(null);
    scene.setSectionCut(false);
    const cut = document.querySelector<HTMLInputElement>('#section-cut');
    if (cut) cut.checked = false;
    sectionToggle.classList.remove('on');
  }

  let sectionZoom = 1;
  /** Repaint the section for the current mode; optionally jump to the level of what is being highlighted. */
  function syncSection(follow: boolean) {
    if (!section || sectionRoot.hidden) return;
    section.setPainter(paintLabel);
    if (!follow) return;
    const focus = [...scene.entries.values()].find((e) => e.state === 'active' && !e.isShell && e.structure.labels?.length);
    if (!focus) return;
    section.setZ(focus.info.centroid[2]);
    if (sectionZoom > 1) section.centerOn(focus.info.centroid[0], focus.info.centroid[1]);
  }

  scene.onHover = (entry, x, y) => {
    tooltip.hidden = !entry;
    if (!entry) return;
    tooltip.textContent = `${entry.structure.name.ko} · ${SIDE_LABEL[entry.info.side]}`;
    tooltip.style.transform = `translate(${x + 14}px, ${y + 14}px)`;
  };
  scene.onPick = (entry) => {
    if (mode.kind === 'pathway') {
      // stay inside the pathway: clicking one of its structures jumps to the step that uses it
      if (!entry) return;
      const m = mode;
      const step = pathwayOf(m).steps.findIndex((st) => stepMeshIds(st, m.origin, meshLookup).includes(entry.info.id));
      if (step >= 0) setMode({ ...m, step, playing: false });
      return;
    }
    if (entry) setMode({ kind: 'structure', structureId: entry.structure.id });
    else if (mode.kind === 'structure') setMode({ kind: 'explore' });
  };
  const stats = $('#stats');
  scene.onStats = ({ fps, calls, triangles }) => {
    stats.textContent = `${fps.toFixed(0)} fps · draw ${calls} · ${(triangles / 1000).toFixed(0)}k tri`;
    stats.dataset.fps = fps.toFixed(1);
  };

  const toolbar = $('#toolbar');
  const views: [ViewPreset, string][] = [['oblique', '기본'], ['left', '왼쪽'], ['right', '오른쪽'], ['anterior', '앞'], ['posterior', '뒤'], ['superior', '위']];
  for (const [preset, label] of views) {
    const b = el('button', {}, label);
    b.onclick = () => scene.setView(preset);
    toolbar.append(b);
  }
  const sectionToggle = el('button', { className: 'section-toggle', disabled: !sectionMeta, title: sectionMeta ? '가로 단면 패널' : '단면 데이터가 없습니다 (pipeline 빌드 필요)' }, '단면');
  sectionToggle.onclick = () => (sectionRoot.hidden ? openSection() : closeSection());
  toolbar.append(sectionToggle);

  window.addEventListener('keydown', (e) => {
    if (e.target instanceof HTMLInputElement) return;
    if (e.key === 'Escape') setMode({ kind: 'explore' });
    if (mode.kind !== 'pathway') return;
    const count = pathwayOf(mode).steps.length;
    if (e.key === 'ArrowRight' && mode.step < count - 1) setMode({ ...mode, step: mode.step + 1, playing: false });
    if (e.key === 'ArrowLeft' && mode.step > 0) setMode({ ...mode, step: mode.step - 1, playing: false });
  });

  setMode({ kind: 'explore' });

  // handle for e2e tests and console poking
  Object.assign(window, {
    __atlas: {
      get mode() { return mode; },
      meshCount: scene.entries.size,
      states: () => Object.fromEntries([...scene.entries].map(([id, e]) => [id, e.state])),
      setMode,
      setView: (v: ViewPreset) => scene.setView(v, false),
      section: {
        open: openSection,
        get z() { return section?.zMm; },
        setZ: (z: number) => section?.setZ(z),
        labelAtMm: (x: number, y: number) => section?.labelAtMm(x, y),
      },
    },
  });
}

main().catch((err) => {
  console.error(err);
  const loading = $('#loading');
  loading.hidden = false;
  loading.classList.add('error');
  loading.textContent = `불러오기 실패: ${err instanceof Error ? err.message : err}`;
});
