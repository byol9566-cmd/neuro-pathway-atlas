import pathwaysJson from '../../content/pathways.json';
import { pathwayMeshIds, pathwayRoute, stepMeshIds, type PathwayRoute } from './pathways';
import { AtlasScene, type AtlasEntry, type ViewPreset } from './scene/AtlasScene';
import { SectionPanel, type SectionHit, type SectionMeta } from './sections/SectionPanel';
import './style.css';
import type { Manifest, ManifestMesh, ManifestStructure, OriginSide, Pathway } from './types';

type Mode =
  | { kind: 'explore' }
  | { kind: 'structure'; structureId: string }
  | { kind: 'pathway'; pathwayId: string; origin: OriginSide; step: number; playing: boolean };
type PathwayMode = Extract<Mode, { kind: 'pathway' }>;

const PATHWAYS = pathwaysJson.pathways as Pathway[];
const SIDE_LABEL: Record<string, string> = { L: '왼쪽', R: '오른쪽', M: '정중' };
const STEP_SECONDS = 4;
const MAX_CALLOUTS = 6;
const BASE = import.meta.env.BASE_URL;

const $ = <T extends HTMLElement>(sel: string) => document.querySelector<T>(sel)!;
function el<K extends keyof HTMLElementTagNameMap>(tag: K, props: Record<string, unknown> = {}, ...children: (Node | string)[]): HTMLElementTagNameMap[K] {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}
/** Children fade up one after another (see `.rise` in the stylesheet). */
function staggered(parent: HTMLElement) {
  [...parent.children].forEach((child, i) => {
    child.classList.add('rise');
    (child as HTMLElement).style.setProperty('--i', String(Math.min(i, 12)));
  });
}

/** Lets `panel` be dragged around inside `bounds` by its `handle`; a double click sends it back to where the stylesheet docks it. */
function makeDraggable(panel: HTMLElement, handle: HTMLElement, bounds: HTMLElement, onMoved: () => void) {
  handle.addEventListener('pointerdown', (down) => {
    if (down.button !== 0 || (down.target as HTMLElement).closest('button, input, label')) return;
    const box = bounds.getBoundingClientRect();
    const rect = panel.getBoundingClientRect();
    const grabX = down.clientX - rect.left;
    const grabY = down.clientY - rect.top;
    handle.setPointerCapture(down.pointerId);
    panel.classList.add('dragging');
    const move = (e: PointerEvent) => {
      const x = Math.min(Math.max(e.clientX - grabX - box.left, 0), box.width - rect.width);
      const y = Math.min(Math.max(e.clientY - grabY - box.top, 0), box.height - rect.height);
      Object.assign(panel.style, { left: `${x}px`, top: `${y}px`, right: 'auto', bottom: 'auto' });
    };
    const up = () => {
      handle.removeEventListener('pointermove', move);
      panel.classList.remove('dragging');
      onMoved();
    };
    handle.addEventListener('pointermove', move);
    handle.addEventListener('pointerup', up, { once: true });
    handle.addEventListener('pointercancel', up, { once: true });
  });
  handle.addEventListener('dblclick', (e) => {
    if ((e.target as HTMLElement).closest('button, input, label')) return;
    Object.assign(panel.style, { left: '', top: '', right: '', bottom: '' });
    onMoved();
  });
}

// The opening film (public/media/intro.mp4: H.264, 10 s, silent). Every failure path falls back to the
// particle entrance alone.
const INTRO_FILM = `${BASE}media/intro.mp4`;
const FILM_HANDOVER_S = 1.5; // the scene starts taking over this long before the film's last frame

/** Plays the film across the loading screen. `done` settles when it is time to hand over to the scene. */
function playFilm(loading: HTMLElement) {
  const video = $<HTMLVideoElement>('#intro-video');
  let finish = () => {};
  const done = new Promise<boolean>((resolve) => {
    let settled = false;
    const settle = (played: boolean) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(patience);
      if (!played) loading.classList.remove('with-film');
      resolve(played);
    };
    finish = () => settle(!video.paused);
    // no picture after a few seconds (slow link, blocked autoplay): carry on without it
    const patience = window.setTimeout(() => video.currentTime === 0 && settle(false), 5000);
    video.addEventListener('error', () => settle(false));
    video.addEventListener('playing', () => loading.classList.add('with-film'), { once: true });
    video.addEventListener('timeupdate', () => video.duration - video.currentTime <= FILM_HANDOVER_S && settle(true));
    video.addEventListener('ended', () => settle(true));
    video.src = INTRO_FILM;
    video.play().catch(() => settle(false));
  });
  return { done, skip: () => finish() };
}

async function main() {
  const firstVisit = (() => {
    try {
      const seen = sessionStorage.getItem('atlas.intro') === '1';
      sessionStorage.setItem('atlas.intro', '1');
      return !seen;
    } catch {
      return true;
    }
  })();
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const film = firstVisit && !calm ? playFilm($('#loading')) : null;

  const loadingBar = $('#loading-bar');
  const loadingCaption = $('#loading-caption');
  const showProgress = (fraction: number | null) => {
    loadingBar.classList.toggle('indeterminate', fraction === null);
    if (fraction === null) return;
    loadingBar.style.transform = `scaleX(${fraction})`;
    loadingCaption.textContent = `신경로를 밝히는 중 · ${Math.round(fraction * 100)}%`;
  };
  showProgress(0);

  const manifest: Manifest = await (await fetch(`${BASE}data/manifest.json`)).json();
  const meshLookup = new Map<string, ManifestMesh>(manifest.meshes.map((m) => [m.id, m]));
  const structures = new Map<string, ManifestStructure>(manifest.structures.map((s) => [s.id, s]));

  const scene = new AtlasScene($<HTMLCanvasElement>('#canvas'));
  await scene.load(manifest, `${BASE}data/atlas.glb`, showProgress);
  showProgress(1);

  let mode: Mode = { kind: 'explore' };
  let route: PathwayRoute | null = null;
  let timer: number | undefined;

  const pathwayOf = (m: PathwayMode) => PATHWAYS.find((p) => p.id === m.pathwayId)!;

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
    renderDetail(prev);
    renderRail();
    renderHint();
    renderCallouts();
    syncSection(true);
  }

  const startPathway = (p: Pathway) => setMode({ kind: 'pathway', pathwayId: p.id, origin: p.defaultOriginSide, step: 0, playing: false });

  // ---------- sidebar ----------
  const sidebar = $('#sidebar');
  const search = el('input', { type: 'search', placeholder: '구조 검색 (한글/영문)', id: 'search' });
  const pathwayList = el('div', { className: 'list' });
  const structureList = el('div', { className: 'groups' });
  const groupToggles: HTMLInputElement[] = [];
  sidebar.append(
    el('header', { className: 'brand' },
      el('span', { className: 'brand-star' }, '✦'),
      el('div', {}, el('h1', {}, '신경경로 아틀라스'), el('p', { className: 'badge' }, '시제품 · 내용 검수 전'))),
    el('h2', {}, '신경경로'), pathwayList,
    el('h2', {}, '구조'), search, structureList,
    attributionBlock(),
  );

  for (const p of PATHWAYS) {
    const btn = el('button', { className: 'item pathway' }, el('strong', {}, p.name.ko), el('small', {}, p.name.en ?? ''));
    btn.dataset.pathway = p.id;
    btn.onclick = () => startPathway(p);
    pathwayList.append(btn);
  }

  for (const [groupId, group] of Object.entries(manifest.groups)) {
    const members = manifest.structures.filter((s) => s.group === groupId);
    if (!members.length) continue;
    const toggle = el('input', { type: 'checkbox', checked: true });
    toggle.onchange = () => scene.setGroupVisible(groupId, toggle.checked);
    toggle.dataset.group = groupId;
    groupToggles.push(toggle);
    const items = el('div', { className: 'list' });
    for (const s of members) {
      const swatch = el('span', { className: 'swatch' });
      swatch.style.background = `#${scene.structureColor(s.id)?.getHexString() ?? '888888'}`;
      const btn = el('button', { className: 'item structure' }, swatch, el('span', {}, s.name.ko), ...(s.approx ? [el('em', {}, '근사')] : []));
      btn.dataset.structure = s.id;
      btn.dataset.search = `${s.name.ko} ${s.name.en ?? ''}`.toLowerCase();
      btn.onclick = () => setMode({ kind: 'structure', structureId: s.id }, { focus: true });
      items.append(btn);
    }
    const groupSwatch = el('span', { className: 'swatch' });
    groupSwatch.style.background = group.color;
    structureList.append(el('section', { className: 'group' }, el('label', {}, toggle, groupSwatch, group.name.ko, el('small', {}, String(members.length))), items));
  }

  const filterStructures = () => {
    const q = search.value.trim().toLowerCase();
    for (const btn of structureList.querySelectorAll<HTMLElement>('.structure')) btn.hidden = !!q && !btn.dataset.search!.includes(q);
    for (const g of structureList.querySelectorAll<HTMLElement>('.group')) g.hidden = !g.querySelector('.structure:not([hidden])');
  };
  search.oninput = filterStructures;

  function renderSidebarState() {
    for (const b of sidebar.querySelectorAll<HTMLElement>('.item')) {
      b.classList.toggle('current',
        (mode.kind === 'pathway' && b.dataset.pathway === mode.pathwayId) ||
        (mode.kind === 'structure' && b.dataset.structure === mode.structureId));
    }
  }

  function attributionBlock() {
    const box = el('details', { className: 'attribution' }, el('summary', {}, '데이터 출처'));
    for (const a of manifest.attribution) {
      box.append(el('p', {}, el('a', { href: a.url, target: '_blank', rel: 'noreferrer' }, a.title), ` — ${a.license}. ${a.citation}`));
    }
    box.append(el('p', {}, '오른쪽 반구는 왼쪽 반구 아틀라스를 좌우 반전해 만든 것입니다.'));
    return box;
  }

  // ---------- detail panel ----------
  const detail = $('#detail');

  /** Slide (and, when it gets tight, shrink) the brain into whatever room the open panels leave. */
  function frameSubject() {
    const stage = $('#stage');
    const floating = $('#section');
    const { clientWidth: width, clientHeight: height } = stage;
    if (!width || window.matchMedia('(max-width: 900px)').matches) {
      scene.setFraming(0.5, 1);
      for (const name of ['--subject-x', '--subject-room']) stage.style.removeProperty(name);
      return;
    }
    floating.classList.toggle('beside-detail', !$('#detail').hidden);
    const origin = stage.getBoundingClientRect().left;
    let left = 0;
    let right = width;
    for (const panel of [$('#sidebar'), $('#detail'), floating]) {
      if (panel.hidden) continue;
      const rect = panel.getBoundingClientRect();
      if (rect.left + rect.width / 2 < origin + width / 2) left = Math.max(left, rect.right - origin + 12);
      else right = Math.min(right, rect.left - origin - 12);
    }
    const room = Math.max(right - left, 1);
    scene.setFraming((left + right) / 2 / width, Math.min(1, Math.max(0.6, room / (0.72 * height))));
    stage.style.setProperty('--subject-x', `${(left + right) / 2}px`);
    stage.style.setProperty('--subject-room', `${room}px`);
  }
  window.addEventListener('resize', frameSubject);

  function renderDetail(prev: Mode) {
    detail.hidden = mode.kind === 'explore';
    frameSubject();
    detail.replaceChildren();
    if (mode.kind === 'explore') return;
    const close = el('button', { className: 'close', title: '닫기 (Esc)' }, '×');
    close.onclick = () => setMode({ kind: 'explore' });
    detail.append(close);
    if (mode.kind === 'structure') renderStructure(structures.get(mode.structureId)!);
    else renderPathway(mode);
    // moving between steps of the same pathway should not replay the whole panel entrance
    const sameSubject = prev.kind === 'pathway' && mode.kind === 'pathway' && prev.pathwayId === mode.pathwayId;
    if (!sameSubject) staggered(detail);
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
      rows.append(el('dt', {}, `${SIDE_LABEL[m.side]} 부피`), el('dd', { className: 'num' }, `${m.volumeMm3.toLocaleString()} mm³`),
        el('dt', {}, `${SIDE_LABEL[m.side]} 중심 (MNI)`), el('dd', { className: 'num' }, m.centroid.map((v) => v.toFixed(1)).join(', ')));
    }
    rows.append(el('dt', {}, '출처'), el('dd', {}, manifest.attribution.find((a) => a.atlas === s.atlas)?.title ?? s.atlas));
    detail.append(rows);
    if (usedIn.length) {
      detail.append(el('h3', {}, '이 구조가 참여하는 경로'));
      for (const p of usedIn) {
        const btn = el('button', { className: 'item pathway' }, el('strong', {}, p.name.ko));
        btn.onclick = () => startPathway(p);
        detail.append(btn);
      }
    }
  }

  function renderPathway(m: PathwayMode) {
    const p = pathwayOf(m);
    detail.append(el('p', { className: 'eyebrow' }, '신경경로'), el('h2', {}, p.name.ko), el('p', { className: 'sub' }, p.name.en ?? ''));
    if (p.reviewStatus === 'draft') detail.append(el('p', { className: 'warn' }, '초안: 아직 전문가 검수를 거치지 않은 설명입니다.'));
    detail.append(el('p', {}, p.summary.ko));

    const sides = el('div', { className: 'segmented' });
    sides.style.setProperty('--index', m.origin === 'L' ? '0' : '1');
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
        const body = el('div', { className: 'step-body' });
        const tags = el('p', { className: 'tags' });
        if (st.neuronOrder) tags.append(el('span', {}, `${st.neuronOrder}차 뉴런`));
        if (st.decussation) tags.append(el('span', { className: 'cross' }, '교차'));
        for (const id of stepMeshIds(st, m.origin, meshLookup)) {
          const mesh = meshLookup.get(id)!;
          tags.append(el('span', { className: 'struct' }, `${structures.get(mesh.structureId)!.name.ko} · ${SIDE_LABEL[mesh.side]}`));
        }
        body.append(tags, el('p', {}, st.description.ko));
        if (st.missing) body.append(el('p', { className: 'missing' }, st.missing.ko));
        li.append(body);
      }
      steps.append(li);
    });
    detail.append(steps);

    const prev = el('button', { disabled: m.step === 0 }, '← 이전');
    prev.onclick = () => setMode({ ...m, step: m.step - 1, playing: false });
    const play = el('button', { className: 'primary' }, m.playing ? '일시정지' : '재생');
    play.onclick = () => togglePlay(m);
    const next = el('button', { disabled: m.step === p.steps.length - 1 }, '다음 →');
    next.onclick = () => setMode({ ...m, step: m.step + 1, playing: false });
    detail.append(el('div', { className: 'transport' }, prev, play, next));

    detail.append(el('h3', {}, '병변과 증상'));
    const lesions = el('dl', { className: 'lesions' });
    for (const l of p.lesions) lesions.append(el('dt', {}, l.level.ko), el('dd', {}, l.deficit.ko));
    detail.append(lesions);
  }

  function togglePlay(m: PathwayMode) {
    const last = m.step === pathwayOf(m).steps.length - 1;
    setMode({ ...m, step: !m.playing && last ? 0 : m.step, playing: !m.playing });
  }

  // ---------- stage: step rail, hint, callouts ----------
  const rail = $('#rail');
  function renderRail() {
    rail.hidden = mode.kind !== 'pathway';
    rail.replaceChildren();
    if (mode.kind !== 'pathway') return;
    const m = mode;
    const p = pathwayOf(m);
    const ticks = el('div', { className: 'rail-ticks' });
    p.steps.forEach((st, i) => {
      const tick = el('button', { className: `tick ${i === m.step ? 'on' : i < m.step ? 'done' : ''}`, title: st.title.ko }, String(i + 1).padStart(2, '0'));
      tick.onclick = () => setMode({ ...m, step: i, playing: false });
      ticks.append(tick);
    });
    rail.append(ticks, el('span', { className: 'rail-title' }, p.steps[m.step].title.ko));
  }

  const hint = $('#hint');
  function renderHint() {
    hint.textContent =
      mode.kind === 'explore' ? '구조를 클릭하거나 경로를 선택하세요 · 드래그 회전 · 휠 확대'
      : mode.kind === 'structure' ? '다른 구조를 클릭해 옮겨 가세요 · Esc 선택 해제'
      : mode.playing ? '경로 재생 중 · Space 일시정지'
      : '← → 단계 이동 · Space 재생 · Esc 나가기';
  }

  const labels = $('#labels');
  let callouts: { node: HTMLElement; entry: AtlasEntry }[] = [];
  function renderCallouts() {
    labels.replaceChildren();
    const active = [...scene.entries.values()].filter((e) => e.state === 'active' && !e.isShell).slice(0, MAX_CALLOUTS);
    callouts = active.map((entry) => {
      const node = el('div', { className: 'callout' }, el('i', {}), el('span', {}, `${entry.structure.name.ko} · ${SIDE_LABEL[entry.info.side]}`));
      labels.append(node);
      return { node, entry };
    });
  }
  scene.onFrame = () => {
    for (const { node, entry } of callouts) {
      const p = scene.project(entry.info.centroid);
      node.style.opacity = p.visible ? '1' : '0';
      node.style.transform = `translate(${p.x.toFixed(1)}px, ${p.y.toFixed(1)}px)`;
    }
  };

  // ---------- 2D section panel ----------
  const tooltip = $('#tooltip');
  const sectionRoot = $('#section');
  const sectionMeta: SectionMeta | null = await fetch(`${BASE}data/sections/axial/meta.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const labelToStructure = new Map<number, string>();
  for (const s of manifest.structures) for (const label of s.labels ?? []) labelToStructure.set(label, s.id);
  let section: SectionPanel | null = null;
  let sectionZoom = 1;

  const mixTo = (c: number[], target: number[], t: number) => c.map((v, i) => Math.round(v + (target[i] - v) * t)) as [number, number, number];
  const DEEP = [18, 19, 26];

  /** Colour of an atlas label in the 2D section, mirroring what the 3D scene is doing with it. */
  function paintLabel(label: number, side: 'L' | 'R'): [number, number, number] {
    const lut = sectionMeta!.labels[label].color;
    const entry = scene.entries.get(`${labelToStructure.get(label)}.${side}`);
    if (!entry) {
      if (mode.kind === 'explore') return mixTo(lut, [50, 52, 62], 0.6);
      const grey = 0.3 * lut[0] + 0.59 * lut[1] + 0.11 * lut[2];
      return mixTo([grey, grey, grey * 1.06], DEEP, 0.74);
    }
    const base = entry.baseColor.toArray().map((v) => Math.round(Math.sqrt(v) * 255)); // linear -> ~sRGB
    if (entry.state === 'active') return mixTo(base, [255, 255, 255], 0.25);
    if (entry.state === 'ghost') return mixTo(base, DEEP, 0.78);
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
      const header = el('header', { className: 'section-header', title: '끌어서 옮기기 · 더블클릭하면 제자리로' },
        el('span', { className: 'grip', ariaHidden: 'true' }, '⠿'), el('strong', {}, '가로 단면'));
      sectionRoot.append(header);
      makeDraggable(sectionRoot, header, $('#stage'), frameSubject);
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
        el('label', { className: 'cut', title: '3D에서 이 높이 위쪽을 잘라 냅니다' }, cut, '자르기'), close);
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
    $('#stage').classList.add('with-section');
    frameSubject();
  }

  function closeSection() {
    sectionRoot.hidden = true;
    scene.setSectionPlane(null);
    scene.setSectionCut(false);
    const cut = document.querySelector<HTMLInputElement>('#section-cut');
    if (cut) cut.checked = false;
    sectionToggle.classList.remove('on');
    $('#stage').classList.remove('with-section');
    frameSubject();
  }

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

  // ---------- pointer feedback ----------
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

  // ---------- toolbar ----------
  const toolbar = $('#toolbar');
  const views: [ViewPreset, string][] = [['oblique', '기본'], ['left', '왼쪽'], ['right', '오른쪽'], ['anterior', '앞'], ['posterior', '뒤'], ['superior', '위']];
  const viewGroup = el('div', { className: 'button-group' });
  for (const [preset, label] of views) {
    const b = el('button', {}, label);
    b.onclick = () => scene.setView(preset);
    viewGroup.append(b);
  }
  const sectionToggle = el('button', { className: 'section-toggle', disabled: !sectionMeta, title: sectionMeta ? '가로 단면 패널' : '단면 데이터가 없습니다 (pipeline 빌드 필요)' }, '단면');
  sectionToggle.onclick = () => (sectionRoot.hidden ? openSection() : closeSection());
  const reset = el('button', { title: '숨긴 그룹·선택·시점을 처음 상태로' }, '기본값으로');
  reset.onclick = () => {
    for (const t of groupToggles) {
      t.checked = true;
      scene.setGroupVisible(t.dataset.group!, true);
    }
    search.value = '';
    filterStructures();
    setMode({ kind: 'explore' });
    scene.setView('oblique');
  };
  const help = $('#help');
  const helpToggle = el('button', { title: '단축키와 조작법', className: 'help-toggle' }, '?');
  helpToggle.onclick = () => {
    help.hidden = !help.hidden;
    helpToggle.classList.toggle('on', !help.hidden);
  };
  help.append(
    el('h3', {}, '조작법'),
    el('dl', { className: 'keys' },
      el('dt', {}, '드래그'), el('dd', {}, '회전'),
      el('dt', {}, '휠'), el('dd', {}, '확대·축소'),
      el('dt', {}, '우클릭 드래그'), el('dd', {}, '이동'),
      el('dt', {}, '클릭'), el('dd', {}, '구조 선택 (빈 곳: 해제)'),
      el('dt', {}, '← →'), el('dd', {}, '경로의 이전·다음 단계'),
      el('dt', {}, 'Space'), el('dd', {}, '경로 재생·일시정지'),
      el('dt', {}, 'Esc'), el('dd', {}, '선택·경로에서 나가기'),
      el('dt', {}, '/'), el('dd', {}, '구조 검색')),
    el('p', { className: 'sub' }, '단면 패널: 휠로 높이 이동, Ctrl+휠로 확대, 드래그로 이동.'));
  toolbar.append(viewGroup, el('div', { className: 'button-group' }, sectionToggle, reset, helpToggle));

  window.addEventListener('keydown', (e) => {
    if (scene.introPlaying) return scene.skipIntro();
    if (e.target instanceof HTMLInputElement) {
      if (e.key === 'Escape') (e.target as HTMLInputElement).blur();
      return;
    }
    if (e.key === '/') {
      e.preventDefault();
      search.focus();
      return;
    }
    if (e.key === 'Escape') {
      if (!help.hidden) helpToggle.click();
      else setMode({ kind: 'explore' });
    }
    if (mode.kind !== 'pathway') return;
    const count = pathwayOf(mode).steps.length;
    if (e.key === 'ArrowRight' && mode.step < count - 1) setMode({ ...mode, step: mode.step + 1, playing: false });
    if (e.key === 'ArrowLeft' && mode.step > 0) setMode({ ...mode, step: mode.step - 1, playing: false });
    if (e.key === ' ') {
      e.preventDefault();
      togglePlay(mode);
    }
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

  // ---------- entrance ----------
  const loading = $('#loading');
  const app = $('#app');
  frameSubject();
  let filmed = false;
  if (film) {
    // everything is loaded; the film runs on to its end unless the visitor would rather get going
    loadingCaption.textContent = '클릭하면 바로 시작합니다';
    const hurry = () => film.skip();
    window.addEventListener('pointerdown', hurry, { once: true });
    window.addEventListener('keydown', hurry, { once: true });
    filmed = await film.done;
    window.removeEventListener('pointerdown', hurry);
    window.removeEventListener('keydown', hurry);
  }
  loading.classList.add('leaving');
  window.setTimeout(() => {
    loading.hidden = true;
    const video = $<HTMLVideoElement>('#intro-video');
    video.pause();
    video.removeAttribute('src');
    video.load(); // lets go of the download
  }, calm ? 0 : filmed ? 1500 : 650);
  if (calm) loading.hidden = true;
  const skip = () => scene.skipIntro();
  window.addEventListener('pointerdown', skip, { once: true });
  await scene.playIntro(firstVisit);
  window.removeEventListener('pointerdown', skip);
  app.classList.add('ui-in');
}

main().catch((err) => {
  console.error(err);
  const loading = $('#loading');
  loading.hidden = false;
  loading.classList.remove('leaving');
  loading.classList.add('error');
  $('#loading-caption').textContent = `불러오기 실패: ${err instanceof Error ? err.message : err}`;
});
