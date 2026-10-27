import pathwaysJson from '../../content/pathways.json';
import { renderCircuit, type Circuit } from './circuit';
import { pathwayMeshIds, pathwayRoute, resolveSide, stepMeshIds, type PathwayRoute } from './pathways';
import { AtlasScene, type AtlasEntry, type ViewPreset } from './scene/AtlasScene';
import { SectionPanel, type SectionHit, type SectionMeta } from './sections/SectionPanel';
import './style.css';
import type { Manifest, ManifestMesh, ManifestStructure, OriginSide, Pathway, PathwayCategory } from './types';

type Mode =
  | { kind: 'explore' }
  | { kind: 'structure'; structureId: string }
  | { kind: 'pathway'; pathwayId: string; origin: OriginSide; step: number; playing: boolean };
type PathwayMode = Extract<Mode, { kind: 'pathway' }>;

const PATHWAYS = pathwaysJson.pathways as Pathway[];
const CATEGORIES = ((pathwaysJson as { categories?: PathwayCategory[] }).categories ?? []) as PathwayCategory[];
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
    if (window.matchMedia('(max-width: 900px)').matches) return; // a fixed sheet on phones
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
    // whichever of up / cancel comes first ends the drag and takes both listeners with it
    const up = () => {
      handle.removeEventListener('pointermove', move);
      handle.removeEventListener('pointerup', up);
      handle.removeEventListener('pointercancel', up);
      panel.classList.remove('dragging');
      onMoved();
    };
    handle.addEventListener('pointermove', move);
    handle.addEventListener('pointerup', up);
    handle.addEventListener('pointercancel', up);
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
    const onPlaying = () => loading.classList.add('with-film');
    const settle = (played: boolean) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(patience);
      // a late `playing` (after the patience ran out) must not bring the film back over the scene
      video.removeEventListener('playing', onPlaying);
      if (!played) {
        video.pause();
        loading.classList.remove('with-film');
      }
      resolve(played);
    };
    finish = () => settle(!video.paused);
    // no picture after a few seconds (slow link, blocked autoplay): carry on without it
    const patience = window.setTimeout(() => video.currentTime === 0 && settle(false), 5000);
    video.addEventListener('error', () => settle(false));
    video.addEventListener('playing', onPlaying, { once: true });
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
  let announced = -1;
  const showProgress = (fraction: number | null) => {
    loadingBar.classList.toggle('indeterminate', fraction === null);
    if (fraction === null) return;
    loadingBar.style.transform = `scaleX(${fraction})`;
    // the caption is #loading's live region: it changes at quarter steps, not on every chunk received
    const quarter = Math.min(4, Math.floor(fraction * 4));
    if (quarter === announced) return;
    announced = quarter;
    loadingCaption.textContent = `신경로를 밝히는 중 · ${quarter * 25}%`;
  };
  showProgress(0);

  const manifestUrl = `${BASE}data/manifest.json`;
  const manifestResponse = await fetch(manifestUrl);
  if (!manifestResponse.ok) throw new Error(`${manifestUrl} 응답 ${manifestResponse.status} — 아틀라스 데이터가 배포되지 않았습니다`);
  const manifest: Manifest = await manifestResponse.json().catch(() => {
    throw new Error(`${manifestUrl}이(가) JSON이 아닙니다 — 아틀라스 데이터가 배포되지 않았습니다`);
  });
  const meshLookup = new Map<string, ManifestMesh>(manifest.meshes.map((m) => [m.id, m]));
  const structures = new Map<string, ManifestStructure>(manifest.structures.map((s) => [s.id, s]));

  const scene = new AtlasScene($<HTMLCanvasElement>('#canvas'));
  await scene.load(manifest, `${BASE}data/atlas.glb`, showProgress);
  showProgress(1);

  let mode: Mode = { kind: 'explore' };
  let route: PathwayRoute | null = null;
  let timer: number | undefined;

  const pathwayOf = (m: PathwayMode) => PATHWAYS.find((p) => p.id === m.pathwayId)!;
  /** what is selected, ignoring the step, the origin side and playback: '' while exploring */
  const subjectOf = (m: Mode) => (m.kind === 'pathway' ? `p:${m.pathwayId}` : m.kind === 'structure' ? `s:${m.structureId}` : '');

  function setMode(next: Mode, opts: { focus?: boolean } = {}) {
    const prev = mode;
    mode = next;
    window.clearInterval(timer);

    if (mode.kind !== 'pathway') {
      scene.setJointAngles({});
      scene.setPupils({});
      scene.setEyeRotations({});
      scene.setLenses({});
      scene.setContractions([]);
    }
    if (mode.kind === 'explore') {
      scene.setStates(() => 'normal');
      scene.setRoute(null);
      route = null;
      scene.settleSea(); // a focus may have sunk it; nothing is lit now
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
      // what this step does to the body: the named joints flex or extend (the rest return to rest), and
      // the bones they move are shown so the movement can be seen
      const angles: Record<string, number> = {};
      const pupils: Record<string, number> = {};
      const eyes: Record<string, [number, number]> = {};
      const lenses: Record<string, number> = {};
      // the step's skeletal muscles contract, except those an effect marks as relaxing or merely sensed
      const contracting = new Set([...active].filter((id) => id.startsWith('mu-')));
      const relaxed = new Set<string>();
      for (const fx of pathway.steps[m.step].effects ?? []) {
        if (!fx.muscle || fx.action === 'contract') continue;
        const hit = [...contracting].filter((id) => fx.muscle === '*' || id === `${fx.muscle}.${resolveSide(fx.side, m.origin)}` || id === `${fx.muscle}.M`);
        for (const id of hit) {
          contracting.delete(id);
          if (fx.action === 'relax') relaxed.add(id);
        }
      }
      for (const fx of pathway.steps[m.step].effects ?? []) {
        const side = resolveSide(fx.side, m.origin);
        if (fx.joint && fx.angle !== undefined) {
          angles[`${fx.joint}.${side}`] = fx.angle;
          for (const id of scene.jointChainMeshIds(`${fx.joint}.${side}`)) active.add(id);
        }
        if (fx.pupil) pupils[side] = fx.pupil === 'constrict' ? 0.6 : 1.5;
        if (fx.eye) {
          const a = fx.angle ?? 15;
          const cur = eyes[side] ?? [0, 0];
          eyes[side] = fx.eye === 'adduct' ? [cur[0] + a, cur[1]] : fx.eye === 'abduct' ? [cur[0] - a, cur[1]] : fx.eye === 'elevate' ? [cur[0], cur[1] + a] : [cur[0], cur[1] - a];
          active.add(`so-eyeball.${side}`);
        }
        if (fx.lens) { lenses[side] = 1; active.add(`so-lens.${side}`); }
      }
      scene.setStates((e) => (active.has(e.info.id) ? 'active' : involved.has(e.info.id) ? 'involved' : 'ghost'));
      scene.setJointAngles(angles);
      scene.setPupils(pupils);
      scene.setEyeRotations(eyes);
      scene.setLenses(lenses);
      scene.setContractions(contracting, relaxed);

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
    renderRail();
    renderHint();
    renderCallouts();
    // the section jumps to a new selection's level; stepping keeps the slice the user chose
    syncSection(subjectOf(prev) !== subjectOf(mode));
  }


  const startPathway = (p: Pathway) => setMode({ kind: 'pathway', pathwayId: p.id, origin: p.defaultOriginSide, step: 0, playing: false });

  // ---------- sidebar ----------
  const sidebar = $('#sidebar');
  const search = el('input', { type: 'search', placeholder: '경로·구조 검색 (한글/영문)', id: 'search' });
  const pathwayList = el('div', { className: 'groups' });
  const structureList = el('div', { className: 'groups' });
  const groupToggles: HTMLInputElement[] = [];
  /** fold or unfold a sidebar group; its chevron's aria-expanded follows */
  const setFolded = (group: Element, folded: boolean) => {
    group.classList.toggle('collapsed', folded);
    group.querySelector('.fold')?.setAttribute('aria-expanded', String(!folded));
  };
  sidebar.append(
    el('header', { className: 'brand' },
      el('span', { className: 'brand-star' }, '✦'),
      el('div', {}, el('h1', {}, '신경경로 아틀라스'), el('p', { className: 'badge' }, '시제품 · 내용 검수 전'))),
    search,
    el('h2', {}, '신경경로'), pathwayList,
    el('h2', {}, '구조'), structureList,
    attributionBlock(),
    licencesBlock(),
  );

  // pathways grouped by category, in the order the content file gives; text-only mechanisms sort last
  // within their category and are marked, so the reader knows nothing will light up
  const categoryOrder = CATEGORIES.length ? CATEGORIES : [...new Set(PATHWAYS.map((p) => p.category))].map((id) => ({ id, name: { ko: id } }));
  for (const cat of categoryOrder) {
    const members = PATHWAYS.filter((p) => p.category === cat.id);
    if (!members.length) continue;
    const items = el('div', { className: 'list' });
    for (const p of members) {
      const btn = el('button', { className: 'item pathway' + (p.has3d === false ? ' text-only' : '') },
        el('strong', {}, p.name.ko), el('small', {}, p.has3d === false ? `${p.name.en ?? ''} · 설명만` : p.name.en ?? ''));
      btn.dataset.pathway = p.id;
      btn.dataset.search = `${p.name.ko} ${p.name.en ?? ''}`.toLowerCase();
      btn.onclick = () => startPathway(p);
      items.append(btn);
    }
    const fold = el('button', { className: 'fold', type: 'button', title: '펼치기/접기', ariaLabel: `${cat.name.ko} 목록` }, '›');
    const n3d = members.filter((p) => p.has3d !== false).length;
    const section = el('section', { className: 'group' },
      el('label', {}, cat.name.ko, el('small', {}, n3d === members.length ? String(members.length) : `${n3d}+${members.length - n3d}`), fold), items);
    section.dataset.category = cat.id;
    setFolded(section, members.length > 8);
    fold.onclick = (e) => { e.preventDefault(); setFolded(section, !section.classList.contains('collapsed')); };
    pathwayList.append(section);
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
      const tag = s.atlas === 'model' ? '모형' : s.approx ? '근사' : null;
      const btn = el('button', { className: 'item structure' }, swatch, el('span', {}, s.name.ko), ...(tag ? [el('em', {}, tag)] : []));
      btn.dataset.structure = s.id;
      btn.dataset.search = `${s.name.ko} ${s.name.en ?? ''}`.toLowerCase();
      btn.onclick = () => setMode({ kind: 'structure', structureId: s.id }, { focus: true });
      items.append(btn);
    }
    const groupSwatch = el('span', { className: 'swatch' });
    groupSwatch.style.background = group.color;
    // long groups start folded; the chevron unfolds them, and so does selecting one of their structures
    const fold = el('button', { className: 'fold', type: 'button', title: '펼치기/접기', ariaLabel: `${group.name.ko} 목록` }, '›');
    const section = el('section', { className: 'group' }, el('label', {}, toggle, groupSwatch, group.name.ko, el('small', {}, String(members.length)), fold), items);
    section.dataset.group = groupId;
    setFolded(section, members.length > 14);
    fold.onclick = (e) => { e.preventDefault(); setFolded(section, !section.classList.contains('collapsed')); };
    structureList.append(section);
  }

  const filterStructures = () => {
    const q = search.value.trim().toLowerCase();
    for (const btn of sidebar.querySelectorAll<HTMLElement>('.item.structure, .item.pathway')) btn.hidden = !!q && !btn.dataset.search!.includes(q);
    for (const g of sidebar.querySelectorAll<HTMLElement>('.group')) {
      g.hidden = !g.querySelector('.item:not([hidden])');
      if (q) setFolded(g, false); // a search result must be visible
    }
  };
  search.oninput = filterStructures;
  /** '/' and the skip link: on a phone the lists share the sheet with the selection, so go back to them */
  const focusSearch = () => {
    if (getComputedStyle(sidebar).display === 'none') setMode({ kind: 'explore' });
    $('#app').classList.remove('dock-min');
    search.focus();
  };
  $('#skip-to-search').onclick = (e) => {
    e.preventDefault();
    focusSearch();
  };

  function renderSidebarState() {
    for (const b of sidebar.querySelectorAll<HTMLElement>('.item')) {
      const current = (mode.kind === 'pathway' && b.dataset.pathway === mode.pathwayId) ||
        (mode.kind === 'structure' && b.dataset.structure === mode.structureId);
      b.classList.toggle('current', current);
      if (current) b.setAttribute('aria-current', 'true');
      else b.removeAttribute('aria-current');
      if (!current) continue;
      const group = b.closest('.group');
      if (group) setFolded(group, false);
      // scroll the list itself: scrollIntoView would also scroll the (overflow: hidden) page on a phone
      const r = b.getBoundingClientRect();
      const s = sidebar.getBoundingClientRect();
      if (s.height && (r.top < s.top || r.bottom > s.bottom)) sidebar.scrollTop += r.top - s.top - (s.height - r.height) / 2;
    }
  }


  function attributionBlock() {
    const box = el('details', { className: 'attribution' }, el('summary', {}, '데이터 출처'));
    for (const a of manifest.attribution) {
      const title = a.url ? el('a', { href: a.url, target: '_blank', rel: 'noreferrer' }, a.title) : el('span', {}, a.title);
      box.append(el('p', {}, title, ` — ${a.license}. ${a.citation}`));
    }
    box.append(el('p', {}, '오른쪽 반구는 왼쪽 반구 아틀라스를 좌우 반전해 만든 것입니다.'));
    return box;
  }

  /** The MIT notices the bundled libraries ask for, and the credits for the fonts and the opening film. */
  function licencesBlock() {
    const box = el('details', { className: 'attribution' }, el('summary', {}, '오픈소스 · 폰트 · 영상'));
    const entry = (name: string, url: string, note: string) => box.append(el('p', {}, el('a', { href: url, target: '_blank', rel: 'noreferrer' }, name), ` — ${note}`));
    entry('three.js', 'https://github.com/mrdoob/three.js/blob/dev/LICENSE', 'MIT License. Copyright © 2010–2026 three.js authors.');
    entry('three-mesh-bvh', 'https://github.com/gkjohnson/three-mesh-bvh/blob/master/LICENSE', 'MIT License. Copyright © 2018 Garrett Johnson.');
    entry('Pretendard', 'https://github.com/orioncactus/pretendard', 'SIL Open Font License 1.1.');
    entry('JetBrains Mono', 'https://www.jetbrains.com/lp/mono/', 'SIL Open Font License 1.1.');
    entry('오프닝 영상', 'https://motionsites.ai', 'Motionsites AI 무료 프롬프트에 포함된 영상.');
    box.append(el('p', {}, 'MIT 라이선스: 위 저작권 표시와 함께 소프트웨어를 자유롭게 사용·복제·수정·배포할 수 있으며, 소프트웨어는 어떠한 보증 없이 제공됩니다.'));
    return box;
  }

  // ---------- detail panel ----------
  // Built once per subject (a structure, or a pathway). Stepping, playing and flipping the origin side only
  // patch what changed, so focus, scroll position and the circuit box's open state stay where they were.
  const detail = $('#detail');
  let panel: { key: string; update: (m: PathwayMode) => void; dispose: () => void } | null = null;
  /** the 회로도 box, open or shut as the reader last left it this session (null: they have not touched it) */
  let circuitOpen: boolean | null = (() => {
    try {
      const saved = sessionStorage.getItem('atlas.circuit');
      return saved === null ? null : saved === '1';
    } catch {
      return null;
    }
  })();

  const compact = window.matchMedia('(max-width: 900px)');

  /** Slide (and, when it gets tight, shrink) the brain into whatever room the open panels leave. */
  function frameSubject() {
    const stage = $('#stage');
    const floating = $('#section');
    const { clientWidth: width, clientHeight: height } = stage;
    if (!width || !height) return;
    const box = stage.getBoundingClientRect();
    let [left, right, top, bottom] = [0, width, 0, height];
    if (compact.matches) {
      // phone layout: the panels sit outside the stage; only the section sheet covers part of it
      Object.assign(floating.style, { left: '', top: '', right: '', bottom: '' });
      top = $('#toolbar').getBoundingClientRect().bottom - box.top;
      if (!floating.hidden) {
        const rect = floating.getBoundingClientRect();
        if (rect.width > width * 0.8) bottom = rect.top - box.top;
        else right = rect.left - box.left;
      }
    } else {
      floating.classList.toggle('beside-detail', !$('#detail').hidden);
      for (const panel of [$('#sidebar'), $('#detail'), floating]) {
        if (panel.hidden) continue;
        const rect = panel.getBoundingClientRect();
        if (rect.left + rect.width / 2 < box.left + width / 2) left = Math.max(left, rect.right - box.left + 12);
        else right = Math.min(right, rect.left - box.left - 12);
      }
    }
    const roomX = Math.max(right - left, 1);
    const roomY = Math.max(bottom - top, 1);
    // at scale 1 the brain is drawn about 0.72 stage heights wide and 0.7 tall, whatever the stage's shape
    const scale = Math.min(1, Math.max(0.45, Math.min(roomX / (0.72 * height), roomY / (0.7 * height))));
    scene.setFraming((left + right) / 2 / width, scale, (top + bottom) / 2 / height);
    stage.style.setProperty('--subject-x', `${(left + right) / 2}px`);
    stage.style.setProperty('--subject-room', `${roomX}px`);
  }
  new ResizeObserver(frameSubject).observe($('#stage')); // the stage fills the window: this covers window resizes
  compact.addEventListener('change', frameSubject);

  function renderDetail() {
    const key = subjectOf(mode);
    if (panel && panel.key === key) {
      if (mode.kind === 'pathway') panel.update(mode);
      return;
    }
    panel?.dispose();
    panel = null;
    detail.hidden = mode.kind === 'explore';
    $('#app').classList.toggle('has-detail', !detail.hidden);
    if (!detail.hidden) $('#app').classList.remove('dock-min'); // a fresh selection is there to be read
    detail.replaceChildren();
    detail.scrollTop = 0; // and read from its title
    frameSubject();
    if (mode.kind === 'explore') return;
    const close = el('button', { className: 'close', title: '닫기 (Esc)', ariaLabel: '닫기' }, '×');
    close.onclick = () => setMode({ kind: 'explore' });
    detail.append(close);
    if (mode.kind === 'structure') {
      renderStructure(structures.get(mode.structureId)!);
      panel = { key, update: () => {}, dispose: () => {} };
    } else {
      panel = { key, ...renderPathway(mode) };
    }
    staggered(detail);
  }


  function renderStructure(s: ManifestStructure) {
    const meshes = s.meshIds.map((id) => meshLookup.get(id)!);
    const usedIn = PATHWAYS.filter((p) => p.steps.some((st) => st.structures.some((r) => r.id === s.id)));
    detail.append(
      el('p', { className: 'eyebrow' }, manifest.groups[s.group].name.ko),
      el('h2', {}, s.name.ko),
      el('p', { className: 'sub' }, s.name.en ?? ''));
    const note = meshes.find((m) => m.note)?.note;
    if (s.approx && !note) detail.append(el('p', { className: 'warn' }, '근사 형상: 아틀라스 라벨이 너무 작아 위치만 라벨에서 가져오고 모양은 타원체로 대신했습니다.'));
    const derivedFrom = meshes.find((m) => m.derived)?.derived;
    if (derivedFrom) detail.append(el('p', { className: 'warn' }, `부분 형상: Visible Human 절편에서 분할한 ${derivedFrom}의 표면을 교과서 기하로 잘라 만든 영역입니다. 경계는 근사입니다.`));
    if (note) detail.append(el('p', { className: 'warn' }, note));
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

  /** Builds the pathway panel's skeleton; the returned `update` patches it for a step, play state or origin. */
  function renderPathway(m: PathwayMode) {
    const p = pathwayOf(m);
    // handlers read the live mode: the skeleton outlives the mode it was built for
    const live = () => mode as PathwayMode;
    const go = (step: number) => setMode({ ...live(), step, playing: false });
    detail.append(el('p', { className: 'eyebrow' }, '신경경로'), el('h2', {}, p.name.ko), el('p', { className: 'sub' }, p.name.en ?? ''));
    if (p.reviewStatus === 'draft') detail.append(el('p', { className: 'warn' }, '초안: 아직 전문가 검수를 거치지 않은 설명입니다.'));
    if (p.has3d === false) detail.append(el('p', { className: 'missing' }, '이 항목은 3D로 표시할 구조가 없어 설명만 제공합니다.'));
    detail.append(el('p', {}, p.summary.ko));

    const sides = el('div', { className: 'segmented', role: 'group', ariaLabel: '시작하는 쪽' });
    const sideButtons = (['L', 'R'] as const).map((side) => {
      const b = el('button', { type: 'button' }, SIDE_LABEL[side]);
      b.dataset.origin = side;
      b.onclick = () => setMode({ ...live(), origin: side });
      sides.append(b);
      return b;
    });
    detail.append(el('div', { className: 'origin' }, el('span', {}, p.origin.ko), sides));

    // the circuit diagram: every step as a node, the signal's wires between them (crossings and
    // inhibitory endings marked). For pathways with no 3D structures this is the picture, so it always opens.
    const summary = el('summary', {}, '회로도');
    const circuitBox = el('details', { className: 'circuit-box', open: p.has3d === false || (circuitOpen ?? p.category === 'cellular') });
    summary.onclick = () => {
      circuitOpen = !circuitBox.open; // the click has not toggled it yet
      try { sessionStorage.setItem('atlas.circuit', circuitOpen ? '1' : '0'); } catch { /* private mode: this page only */ }
    };
    detail.append(circuitBox);
    let circuit: Circuit | null = null;
    let circuitSide: OriginSide | null = null;

    const steps = el('ol', { className: 'steps' });
    const items = p.steps.map((st, i) => {
      const head = el('button', { className: 'step-head', type: 'button' }, st.title.ko);
      head.onclick = () => go(i);
      return steps.appendChild(el('li', {}, head));
    });
    detail.append(steps);
    let body: HTMLElement | null = null;
    let bodyFor = '';

    const prev = el('button', { type: 'button' }, '← 이전');
    prev.onclick = () => go(live().step - 1);
    const play = el('button', { className: 'primary', type: 'button' });
    play.onclick = () => togglePlay(live());
    const next = el('button', { type: 'button' }, '다음 →');
    next.onclick = () => go(live().step + 1);
    detail.append(el('div', { className: 'transport' }, prev, play, next));

    detail.append(el('h3', {}, '병변과 증상'));
    const lesions = el('dl', { className: 'lesions' });
    for (const l of p.lesions) lesions.append(el('dt', {}, l.level.ko), el('dd', {}, l.deficit.ko));
    detail.append(lesions);

    const update = (m: PathwayMode) => {
      sides.style.setProperty('--index', m.origin === 'L' ? '0' : '1');
      for (const b of sideButtons) {
        b.classList.toggle('on', b.dataset.origin === m.origin);
        b.setAttribute('aria-pressed', String(b.dataset.origin === m.origin));
      }
      // the cell names depend on the side, so a new side redraws the diagram; a new step only re-marks it
      if (m.origin !== circuitSide) {
        circuit?.dispose();
        circuit = renderCircuit(p, { origin: m.origin, step: m.step, meshes: meshLookup, structures, onStep: go });
        circuitBox.replaceChildren(summary, circuit.root);
        circuitSide = m.origin;
      } else circuit!.setStep(m.step);
      items.forEach((li, i) => {
        li.className = i === m.step ? 'on' : i < m.step ? 'done' : '';
        if (i === m.step) li.setAttribute('aria-current', 'step');
        else li.removeAttribute('aria-current');
      });
      if (bodyFor !== `${m.step}${m.origin}`) {
        body?.remove();
        body = stepBody(p.steps[m.step], m.origin);
        items[m.step].append(body);
        bodyFor = `${m.step}${m.origin}`;
      }
      const last = m.step === p.steps.length - 1;
      // a transport button that just became disabled would drop the focus to <body>: hand it to 재생
      const stranded = (document.activeElement === prev && m.step === 0) || (document.activeElement === next && last);
      prev.disabled = m.step === 0;
      next.disabled = last;
      play.textContent = m.playing ? '일시정지' : '재생';
      if (stranded) play.focus();
    };
    update(m);
    return { update, dispose: () => circuit?.dispose() };
  }

  /** The open step's tags, description and what is missing from the atlas. */
  function stepBody(st: Pathway['steps'][number], origin: OriginSide) {
    const body = el('div', { className: 'step-body' });
    const tags = el('p', { className: 'tags' });
    if (st.neuronOrder) tags.append(el('span', {}, `${st.neuronOrder}차 뉴런`));
    if (st.decussation) tags.append(el('span', { className: 'cross' }, '교차'));
    const shown = new Set<string>();
    for (const id of stepMeshIds(st, origin, meshLookup)) {
      const mesh = meshLookup.get(id)!;
      shown.add(mesh.structureId);
      tags.append(el('span', { className: 'struct' }, `${structures.get(mesh.structureId)!.name.ko} · ${SIDE_LABEL[mesh.side]}`));
    }
    // a structure the atlas has no mesh for still gets named, muted, so the learner knows it belongs here
    for (const ref of st.structures) {
      if (shown.has(ref.id)) continue;
      tags.append(el('span', { className: 'struct no-mesh' }, structures.get(ref.id)?.name.ko ?? ref.id, el('em', {}, '3D 없음')));
    }
    body.append(tags, el('p', {}, st.description.ko));
    if (st.missing) body.append(el('p', { className: 'missing' }, st.missing.ko));
    return body;
  }

  function togglePlay(m: PathwayMode) {
    const last = m.step === pathwayOf(m).steps.length - 1;
    setMode({ ...m, step: !m.playing && last ? 0 : m.step, playing: !m.playing });
  }

  // ---------- stage: step rail, hint, callouts ----------
  const rail = $('#rail');
  const railTitle = el('span', { className: 'rail-title' });
  let railFor = '';
  let ticks: HTMLButtonElement[] = [];
  /** The ticks are built once per pathway (a focused tick keeps its focus); steps only move the marks. */
  function renderRail() {
    rail.hidden = mode.kind !== 'pathway';
    if (mode.kind !== 'pathway') {
      railFor = '';
      return;
    }
    const m = mode;
    const p = pathwayOf(m);
    if (railFor !== p.id) {
      railFor = p.id;
      const box = el('div', { className: 'rail-ticks' });
      ticks = p.steps.map((st, i) => {
        const tick = el('button', { className: 'tick', type: 'button', title: st.title.ko, ariaLabel: `${i + 1}단계 ${st.title.ko}` }, String(i + 1).padStart(2, '0'));
        tick.onclick = () => setMode({ ...(mode as PathwayMode), step: i, playing: false });
        return box.appendChild(tick);
      });
      rail.replaceChildren(box, railTitle);
    }
    ticks.forEach((tick, i) => {
      tick.classList.toggle('on', i === m.step);
      tick.classList.toggle('done', i < m.step);
      if (i === m.step) tick.setAttribute('aria-current', 'step');
      else tick.removeAttribute('aria-current');
    });
    railTitle.textContent = p.steps[m.step].title.ko;
  }

  const hint = $('#hint');
  function renderHint() {
    const touch = window.matchMedia('(pointer: coarse)').matches;
    hint.textContent = touch
      ? (mode.kind === 'explore' ? '구조를 탭 · 드래그 회전 · 두 손가락 확대' : mode.kind === 'structure' ? '다른 구조를 탭해 옮겨 가세요' : '')
      : mode.kind === 'explore' ? '구조를 클릭하거나 경로를 선택하세요 · 드래그 회전 · 휠 확대'
      : mode.kind === 'structure' ? '다른 구조를 클릭해 옮겨 가세요 · Esc 선택 해제'
      : mode.playing ? '경로 재생 중 · Space 일시정지'
      : '← → 단계 이동 · Space 재생 · Esc 나가기';
  }

  const labels = $('#labels');
  type Callout = { node: HTMLElement; label: HTMLElement; entry: AtlasEntry; w: number; h: number; x: number; y: number; visible: boolean; dy: number };
  let callouts: Callout[] = [];
  function renderCallouts() {
    labels.replaceChildren();
    const active = [...scene.entries.values()].filter((e) => e.state === 'active' && !e.isShell).slice(0, MAX_CALLOUTS);
    callouts = active.map((entry) => {
      const label = el('span', {}, `${entry.structure.name.ko} · ${SIDE_LABEL[entry.info.side]}`);
      const node = el('div', { className: 'callout' }, el('i', {}), label);
      labels.append(node);
      return { node, label, entry, w: 0, h: 0, x: 0, y: 0, visible: false, dy: 0 };
    });
  }
  scene.onFrame = () => {
    for (const c of callouts) {
      const p = scene.project(c.entry.info.centroid);
      Object.assign(c, p);
      c.node.style.opacity = p.visible ? '1' : '0';
      c.node.style.transform = `translate(${p.x.toFixed(1)}px, ${p.y.toFixed(1)}px)`;
      if (!c.w) [c.w, c.h] = [c.label.offsetWidth, c.label.offsetHeight]; // measured once it has a size
    }
    // labels of nearby structures (the head in 전신) would stack: from the lowest up, a label that meets one
    // already placed rises above it. Every label sits at the same offset from its point, so the points stand in.
    const placed: { x: number; y: number; w: number; h: number }[] = [];
    for (const c of callouts.filter((c) => c.visible).sort((a, b) => b.y - a.y)) {
      let y = c.y;
      for (let pass = 0, moved = true; moved && pass < MAX_CALLOUTS; pass++) {
        moved = false;
        for (const o of placed) {
          if (c.x < o.x + o.w + 4 && o.x < c.x + c.w + 4 && y < o.y + o.h + 2 && o.y < y + c.h + 2) {
            y = o.y - c.h - 2;
            moved = true;
          }
        }
      }
      placed.push({ x: c.x, y, w: c.w, h: c.h });
      const dy = Math.round(y - c.y);
      if (dy !== c.dy) c.label.style.setProperty('--dy', `${(c.dy = dy)}px`);
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
    // fluid spaces read as "empty": a deep translucent blue-black, distinct from unlabelled black
    if (/ventricle|aqueduct|foramen|cistern|choroid/.test(sectionMeta!.labels[label].name)) return [18, 26, 44];
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
      const zoomOut = el('button', { title: '축소', ariaLabel: '단면 축소' }, '−');
      zoomOut.onclick = () => section!.setZoom(sectionZoom = Math.max(1, sectionZoom / 1.6));
      const zoomIn = el('button', { title: '확대 (Ctrl+휠)', ariaLabel: '단면 확대' }, '+');
      zoomIn.onclick = () => section!.setZoom(sectionZoom = Math.min(12, sectionZoom * 1.6));
      const brainstem = el('button', { title: '뇌줄기 확대' }, '뇌줄기');
      brainstem.onclick = () => { sectionZoom = 3.2; section!.centerOn(0, -32, sectionZoom); };
      const cut = el('input', { type: 'checkbox', id: 'section-cut' });
      cut.onchange = () => { scene.setSectionCut(cut.checked); refreshCap(); };
      const close = el('button', { title: '단면 닫기', ariaLabel: '단면 닫기' }, '×');
      close.onclick = closeSection;
      header.append(section.readoutElement, el('span', { className: 'spacer' }), zoomOut, zoomIn, brainstem,
        el('label', { className: 'cut', title: '3D에서 이 높이 위쪽을 잘라 냅니다' }, cut, '자르기'), close);
      section.onSliceChange = (z) => scene.setSectionPlane(z);
      section.onPaint = () => refreshCap();
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
    sectionToggle.setAttribute('aria-pressed', 'true');
    $('#stage').classList.add('with-section');
    if (compact.matches) $('#app').classList.add('dock-min'); // the sheet needs the height the panel was using
    frameSubject();
  }

  /** The cut face shows the current slice while the 3D cut is on. */
  function refreshCap() {
    if (!section || !sectionMeta || !scene.sectionCut || sectionRoot.hidden) return scene.setSectionCap(null);
    scene.setSectionCap(section.capCanvas(), sectionMeta);
  }

  function closeSection() {
    sectionRoot.hidden = true;
    scene.setSectionPlane(null);
    scene.setSectionCut(false);
    scene.setSectionCap(null);
    const cut = document.querySelector<HTMLInputElement>('#section-cut');
    if (cut) cut.checked = false;
    sectionToggle.classList.remove('on');
    sectionToggle.setAttribute('aria-pressed', 'false');
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
  stats.title = '초당 프레임 · 그리기 호출 수 · 그린 삼각형 수 (성능 확인용)';
  scene.onStats = ({ fps, calls, triangles }) => {
    stats.textContent = `${fps.toFixed(0)} fps · draw ${calls} · ${(triangles / 1000).toFixed(0)}k tri`;
    stats.dataset.fps = fps.toFixed(1);
  };

  // ---------- toolbar ----------
  const toolbar = $('#toolbar');
  const views: [ViewPreset, string][] = [['oblique', '기본 시점'], ['left', '왼쪽'], ['right', '오른쪽'], ['anterior', '앞'], ['posterior', '뒤'], ['superior', '위']];
  const viewGroup = el('div', { className: 'button-group' });
  for (const [preset, label] of views) {
    const b = el('button', {}, label);
    b.onclick = () => scene.setView(preset);
    viewGroup.append(b);
  }
  // 전신: the body stands in the mist with only the head above it; this toggle sinks the mist under the
  // feet (and steps back once to take the body in); pressed again, the mist covers the body again
  const bodyToggle = el('button', { title: '안개를 발 아래로 내려 몸 전체를 봅니다. 다시 누르면 원래대로.' }, '전신');
  bodyToggle.setAttribute('aria-pressed', 'false');
  bodyToggle.onclick = () => {
    const on = !scene.isBodyRevealed;
    scene.revealBody(on);
    bodyToggle.classList.toggle('on', on);
    bodyToggle.setAttribute('aria-pressed', String(on));
  };
  viewGroup.append(bodyToggle);
  // 자유 시점: the camera stops following selections and pathways; the view buttons still move it
  const freeToggle = el('button', { title: '켜면 구조·경로를 골라도 카메라가 움직이지 않습니다. 시점 버튼은 그대로 동작.' }, '자유 시점');
  freeToggle.setAttribute('aria-pressed', 'false');
  freeToggle.onclick = () => {
    scene.freeCamera = !scene.freeCamera;
    freeToggle.classList.toggle('on', scene.freeCamera);
    freeToggle.setAttribute('aria-pressed', String(scene.freeCamera));
  };
  const sectionToggle = el('button', { className: 'section-toggle', disabled: !sectionMeta, title: sectionMeta ? '가로 단면 패널' : '단면 데이터 없음 (빌드 필요)' }, '단면');
  sectionToggle.setAttribute('aria-pressed', 'false');
  sectionToggle.onclick = () => (sectionRoot.hidden ? openSection() : closeSection());
  const reset = el('button', { title: '숨긴 그룹·선택·검색·전신·자유 시점·시점을 처음 상태로' }, '초기화');
  reset.onclick = () => {
    if (scene.isBodyRevealed) bodyToggle.click();
    if (scene.freeCamera) freeToggle.click();
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
  const helpToggle = el('button', { title: '단축키와 조작법', ariaLabel: '단축키와 조작법', className: 'help-toggle' }, '?');
  helpToggle.setAttribute('aria-expanded', 'false');
  helpToggle.setAttribute('aria-controls', 'help');
  helpToggle.onclick = () => {
    help.hidden = !help.hidden;
    // under the toolbar, however many rows it has wrapped to
    if (!help.hidden) help.style.top = `${toolbar.offsetTop + toolbar.offsetHeight + 8}px`;
    helpToggle.classList.toggle('on', !help.hidden);
    helpToggle.setAttribute('aria-expanded', String(!help.hidden));
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
  // the stats ride at the toolbar's end, so they wrap with it and never meet the hint or the panels
  toolbar.append(viewGroup, el('div', { className: 'button-group' }, freeToggle, sectionToggle, reset, helpToggle), stats);

  window.addEventListener('keydown', (e) => {
    if (scene.introPlaying) return scene.skipIntro();
    if (e.ctrlKey || e.metaKey || e.altKey) return; // browser and system shortcuts
    const target = e.target instanceof Element ? e.target : null;
    if (target?.closest('input, textarea, select')) {
      if (e.key === 'Escape') (target as HTMLElement).blur();
      return;
    }
    // a focused control answers its own activation keys: Space/Enter press the button, not 재생 as well.
    // Arrows and Esc still step and leave, so a clicked (hence focused) 다음 does not trap them.
    if ((e.key === ' ' || e.key === 'Enter') && target?.closest('button, summary, a')) return;
    if (e.key === '/') {
      e.preventDefault();
      focusSearch();
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
      framing: () => scene.framingNow,
      sea: () => scene.seaState,
      freeCamera: () => scene.freeCamera,

      muscleGoals: () => scene.muscleGoals,
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
  const dockToggle = $<HTMLButtonElement>('#dock-toggle');
  const syncDockToggle = () => {
    const closed = app.classList.contains('dock-min');
    dockToggle.textContent = closed ? '⌃ 패널 열기' : '⌄ 패널 접기';
    dockToggle.setAttribute('aria-expanded', String(!closed));
  };
  dockToggle.onclick = () => app.classList.toggle('dock-min');
  new MutationObserver(syncDockToggle).observe(app, { attributes: true, attributeFilter: ['class'] });
  syncDockToggle();
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
