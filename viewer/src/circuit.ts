// A circuit diagram drawn from a pathway's steps: one node per step (its structures as the cell bodies),
// connectors between consecutive steps, a crossing glyph where a step decussates and a flat (inhibitory)
// end where the transmitter is GABA or glycine. It is the pathway's 2D "회로도" — the thing to read when the
// steps are synapses inside one structure and the 3D scene can only point at a centroid (retina, cerebellar
// cortex, hippocampus, basal ganglia), and a map of the whole route for every other pathway.
import type { ManifestMesh, ManifestStructure, OriginSide, Pathway } from './types';
import { stepMeshIds } from './pathways';

const INHIBITORY = /GABA|글리신|glycine|억제/i;

export interface CircuitOptions {
  origin: OriginSide;
  step: number;
  meshes: Map<string, ManifestMesh>;
  structures: Map<string, ManifestStructure>;
  onStep: (index: number) => void;
}

function h<K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text = ''): HTMLElementTagNameMap[K] {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text) n.textContent = text;
  return n;
}

/** Builds the diagram; connectors are laid out once the nodes have their boxes. */
export function renderCircuit(pathway: Pathway, opts: CircuitOptions): HTMLElement {
  const root = h('div', 'circuit');
  const grid = h('div', 'circuit-grid');
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'circuit-wires');
  root.append(svg, grid);

  const nodes: HTMLElement[] = pathway.steps.map((st, i) => {
    const node = h('button', `circuit-node${i === opts.step ? ' on' : i < opts.step ? ' done' : ''}`);
    node.type = 'button';
    node.onclick = () => opts.onStep(i);
    const head = h('div', 'circuit-head');
    head.append(h('span', 'circuit-index', String(i + 1)), h('span', 'circuit-title', st.title.ko));
    node.append(head);
    const cells = h('div', 'circuit-cells');
    const names = new Set<string>();
    for (const id of stepMeshIds(st, opts.origin, opts.meshes)) {
      const mesh = opts.meshes.get(id);
      const s = mesh && opts.structures.get(mesh.structureId);
      if (s) names.add(s.name.ko.replace(/\s*\(.*?\)\s*/g, ''));
    }
    if (!names.size && st.missing) {
      const m = st.missing.ko.match(/없음:\s*([^·3]+)/);
      if (m) names.add(m[1].trim());
    }
    for (const n of [...names].slice(0, 3)) cells.append(h('span', 'circuit-cell', n));
    if (names.size > 3) cells.append(h('span', 'circuit-cell more', `+${names.size - 3}`));
    if (cells.childElementCount) node.append(cells);
    const meta: string[] = [];
    if (st.neuronOrder) meta.push(`${st.neuronOrder}차`);
    if (st.transmitter) meta.push(st.transmitter);
    if (meta.length) node.append(h('div', 'circuit-meta', meta.join(' · ')));
    grid.append(node);
    return node;
  });

  const draw = () => {
    const box = root.getBoundingClientRect();
    if (!box.width) return;
    svg.setAttribute('viewBox', `0 0 ${box.width} ${box.height}`);
    svg.setAttribute('width', String(box.width));
    svg.setAttribute('height', String(box.height));
    svg.innerHTML = '';
    for (let i = 0; i < nodes.length - 1; i++) {
      const a = nodes[i].getBoundingClientRect();
      const b = nodes[i + 1].getBoundingClientRect();
      const from = { x: a.left + a.width / 2 - box.left, y: a.bottom - box.top };
      const to = { x: b.left + b.width / 2 - box.left, y: b.top - box.top };
      const sameRow = Math.abs(a.top - b.top) < 4;
      let d: string;
      if (sameRow) {
        const y = a.top + a.height / 2 - box.top;
        d = `M ${a.right - box.left} ${y} L ${b.left - box.left} ${y}`;
      } else {
        const midY = from.y + (to.y - from.y) / 2;
        d = `M ${from.x} ${from.y} C ${from.x} ${midY}, ${to.x} ${midY}, ${to.x} ${to.y}`;
      }
      const step = pathway.steps[i + 1];
      const inhibitory = INHIBITORY.test(step.transmitter ?? '');
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      path.setAttribute('class', `wire${i < opts.step ? ' lit' : ''}${inhibitory ? ' inhib' : ''}`);
      path.setAttribute('marker-end', inhibitory ? 'url(#circuit-bar)' : 'url(#circuit-arrow)');
      svg.append(path);
      if (step.decussation) {
        // a small X at the middle of the wire: the signal crosses the midline here
        const mid = sameRow
          ? { x: (a.right + b.left) / 2 - box.left, y: a.top + a.height / 2 - box.top }
          : { x: (from.x + to.x) / 2, y: from.y + (to.y - from.y) / 2 };
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'cross-mark');
        g.innerHTML = `<circle cx="${mid.x}" cy="${mid.y}" r="7"/><path d="M ${mid.x - 3.5} ${mid.y - 3.5} L ${mid.x + 3.5} ${mid.y + 3.5} M ${mid.x + 3.5} ${mid.y - 3.5} L ${mid.x - 3.5} ${mid.y + 3.5}"/>`;
        svg.append(g);
      }
    }
    // a loop: the last step returns to a structure of the first (basal ganglia loops, Papez, VOR adaptation)
    const first = new Set(pathway.steps[0].structures.map((r) => r.id));
    const last = pathway.steps[pathway.steps.length - 1];
    if (nodes.length > 2 && last.structures.some((r) => first.has(r.id))) {
      const a = nodes[nodes.length - 1].getBoundingClientRect();
      const b = nodes[0].getBoundingClientRect();
      const x0 = a.left + a.width / 2 - box.left, y0 = a.bottom - box.top;
      const x1 = b.left + b.width / 2 - box.left, y1 = b.top - box.top;
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M ${x0} ${y0} C ${x0} ${y0 + 26}, ${-14} ${y0 + 26}, ${-14} ${(y0 + y1) / 2} S ${x1} ${y1 - 22}, ${x1} ${y1}`);
      path.setAttribute('class', 'wire loop');
      path.setAttribute('marker-end', 'url(#circuit-arrow)');
      svg.append(path);
    }
    svg.insertAdjacentHTML('afterbegin', `<defs>
      <marker id="circuit-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"/></marker>
      <marker id="circuit-bar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 6 0 L 6 10" stroke-width="2.5"/></marker>
    </defs>`);
  };
  requestAnimationFrame(draw);
  new ResizeObserver(draw).observe(root);
  return root;
}
