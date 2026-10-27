import type { OriginSide } from '../types';

export interface SectionMeta {
  axis: 'axial';
  pixelMm: number;
  width: number;
  height: number;
  /** RAS mm of image column 0 (lateral edge of the LEFT hemisphere); the last column is the midline */
  xMin: number;
  xMax: number;
  yMin: number;
  /** RAS mm of image row 0 (anterior) */
  yMax: number;
  zStart: number;
  zStep: number;
  count: number;
  labels: Record<string, { name: string; color: [number, number, number] }>;
}

export interface SectionHit {
  label: number;
  side: OriginSide;
  xMm: number;
  yMm: number;
}

/** RGBA for a label on one side of the brain. */
export type LabelPainter = (label: number, side: OriginSide) => [number, number, number];

const MAX_LABEL = 2048;
const BACKGROUND = 0xff1b140f; // ABGR of #0f141b
const CACHE_SIZE = 24;

function decodeLabels(image: HTMLImageElement, width: number, height: number): Uint16Array {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
  ctx.drawImage(image, 0, 0);
  const rgba = ctx.getImageData(0, 0, width, height).data;
  const labels = new Uint16Array(width * height);
  for (let i = 0; i < labels.length; i++) labels[i] = rgba[i * 4] | (rgba[i * 4 + 1] << 8);
  return labels;
}

/**
 * 2D view of the atlas label volume at one axial level. Only the left hemisphere is stored; the right
 * half of the brain is its mirror image (as in the 3D scene). Displayed in radiological convention:
 * anterior up, the patient's left on the viewer's right.
 */
export class SectionPanel {
  onHover: (hit: SectionHit | null, clientX: number, clientY: number) => void = () => {};
  onPick: (hit: SectionHit | null) => void = () => {};
  onSliceChange: (zMm: number) => void = () => {};
  /** the slice on screen changed (new slice loaded or recoloured) */
  onPaint: () => void = () => {};

  private readonly canvas = document.createElement('canvas');
  private readonly ctx: CanvasRenderingContext2D;
  private readonly viewport = document.createElement('div');
  private readonly slider = document.createElement('input');
  private readonly readout = document.createElement('span');
  private readonly error = document.createElement('p');
  private readonly cache = new Map<number, Uint16Array>();
  private readonly pending = new Map<number, Promise<Uint16Array>>();
  private readonly tables: Record<OriginSide, Uint32Array> = { L: new Uint32Array(MAX_LABEL), R: new Uint32Array(MAX_LABEL) };
  private index: number;
  private current: Uint16Array | null = null;
  private zoom = 1;
  private pan = { x: 0, y: 0 }; // canvas pixels at the viewport centre, relative to the canvas centre
  private drag: { x: number; y: number; moved: number } | null = null;

  constructor(private readonly root: HTMLElement, private readonly meta: SectionMeta, private readonly baseUrl: string, painter: LabelPainter) {
    this.canvas.width = meta.width * 2;
    this.canvas.height = meta.height;
    this.ctx = this.canvas.getContext('2d')!;
    this.index = this.indexOf(0);
    this.setPainter(painter);

    this.viewport.className = 'section-viewport';
    this.viewport.append(this.canvas);
    for (const [cls, text] of [['mark-r', 'R'], ['mark-l', 'L'], ['mark-a', '앞'], ['mark-p', '뒤']]) {
      const mark = document.createElement('span');
      mark.className = `section-mark ${cls}`;
      mark.textContent = text;
      this.viewport.append(mark);
    }
    this.error.className = 'section-error';
    this.error.setAttribute('role', 'alert');
    this.error.hidden = true;
    this.viewport.append(this.error);
    this.slider.type = 'range';
    this.slider.min = '0';
    this.slider.max = String(meta.count - 1);
    this.slider.className = 'section-slider';
    this.slider.setAttribute('aria-label', '단면 높이');
    this.slider.oninput = () => this.setIndex(Number(this.slider.value));
    this.readout.className = 'section-readout';

    const body = document.createElement('div');
    body.className = 'section-body';
    body.append(this.viewport, this.slider);
    this.root.append(body);

    this.viewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      if (e.ctrlKey || e.metaKey) this.setZoom(this.zoom * (e.deltaY < 0 ? 1.25 : 0.8));
      else this.setIndex(this.index + (e.deltaY < 0 ? 1 : -1) * (e.shiftKey ? 5 : 1));
    }, { passive: false });
    this.viewport.addEventListener('pointerdown', (e) => {
      this.drag = { x: e.clientX, y: e.clientY, moved: 0 };
      this.viewport.setPointerCapture(e.pointerId);
    });
    this.viewport.addEventListener('pointermove', (e) => {
      if (this.drag) {
        const scale = this.displayScale();
        this.pan.x -= (e.clientX - this.drag.x) / scale;
        this.pan.y -= (e.clientY - this.drag.y) / scale;
        this.drag.moved += Math.abs(e.clientX - this.drag.x) + Math.abs(e.clientY - this.drag.y);
        this.drag.x = e.clientX;
        this.drag.y = e.clientY;
        this.layout();
      } else {
        this.onHover(this.hitAt(e.clientX, e.clientY), e.clientX, e.clientY);
      }
    });
    this.viewport.addEventListener('pointerup', (e) => {
      const wasClick = this.drag !== null && this.drag.moved < 5;
      this.drag = null;
      if (wasClick) this.onPick(this.hitAt(e.clientX, e.clientY));
    });
    // a gesture the browser takes over (scroll, system swipe) ends the drag without a pick
    for (const type of ['pointercancel', 'lostpointercapture']) this.viewport.addEventListener(type, () => (this.drag = null));
    this.viewport.addEventListener('pointerleave', () => this.onHover(null, 0, 0));
    new ResizeObserver(() => this.layout()).observe(this.viewport);

    this.reveal();
  }

  /** Show the current slice; a slice that will not load says so in the panel instead of failing silently. */
  private reveal() {
    this.show().then(() => (this.error.hidden = true), (err) => {
      console.warn(err);
      this.error.textContent = '단면을 불러오지 못했습니다';
      this.error.hidden = false;
    });
  }

  get readoutElement() { return this.readout; }
  get zMm() { return this.meta.zStart + this.index * this.meta.zStep; }

  private indexOf(zMm: number) {
    return Math.min(this.meta.count - 1, Math.max(0, Math.round((zMm - this.meta.zStart) / this.meta.zStep)));
  }

  setZ(zMm: number) { this.setIndex(this.indexOf(zMm)); }

  private setIndex(index: number) {
    const clamped = Math.min(this.meta.count - 1, Math.max(0, index));
    if (clamped === this.index && this.current) return;
    this.index = clamped;
    this.reveal();

  }

  /** New colours (selection changed): rebuild the lookup tables and repaint the current slice. */
  setPainter(painter: LabelPainter) {
    for (const side of ['L', 'R'] as const) {
      const table = this.tables[side];
      table.fill(BACKGROUND);
      for (const key of Object.keys(this.meta.labels)) {
        const label = Number(key);
        const [r, g, b] = painter(label, side);
        table[label] = (255 << 24) | (b << 16) | (g << 8) | r;
      }
    }
    this.paint();
  }

  setZoom(zoom: number) {
    this.zoom = Math.min(12, Math.max(1, zoom));
    if (this.zoom === 1) this.pan = { x: 0, y: 0 };
    this.layout();
  }

  /** Centre the view on a point given in RAS mm (x < 0 is the patient's left). */
  centerOn(xMm: number, yMm: number, zoom?: number) {
    const { height, pixelMm, yMax } = this.meta;
    // the midline is the canvas centre and the patient's left is drawn on the right half,
    // so canvas x grows as RAS x decreases
    this.pan = { x: -xMm / pixelMm, y: (yMax - yMm) / pixelMm - height / 2 };
    if (zoom) this.zoom = zoom;
    this.layout();
  }

  /** Label under a RAS mm position on the current slice (for tests and tooling). */
  labelAtMm(xMm: number, yMm: number): number {
    if (!this.current) return 0;
    const col = Math.round((-Math.abs(xMm) - this.meta.xMin) / this.meta.pixelMm);
    const row = Math.round((this.meta.yMax - yMm) / this.meta.pixelMm);
    if (col < 0 || col >= this.meta.width || row < 0 || row >= this.meta.height) return 0;
    return this.current[row * this.meta.width + col];
  }

  private load(index: number): Promise<Uint16Array> {
    const cached = this.cache.get(index);
    if (cached) return Promise.resolve(cached);
    let job = this.pending.get(index);
    if (!job) {
      job = new Promise<Uint16Array>((resolve, reject) => {
        const image = new Image();
        image.onload = () => {
          const labels = decodeLabels(image, this.meta.width, this.meta.height);
          this.cache.set(index, labels);
          if (this.cache.size > CACHE_SIZE) this.cache.delete(this.cache.keys().next().value!);
          this.pending.delete(index);
          resolve(labels);
        };
        image.onerror = () => { this.pending.delete(index); reject(new Error(`section ${index} failed to load`)); };
        image.src = `${this.baseUrl}${String(index).padStart(4, '0')}.png`;
      });
      this.pending.set(index, job);
    }
    return job;
  }

  private async show() {
    const index = this.index;
    this.slider.value = String(index);
    this.readout.textContent = `z = ${this.zMm.toFixed(1)} mm`;
    this.onSliceChange(this.zMm);
    const labels = await this.load(index);
    if (index !== this.index) return; // the user scrolled on while this slice was loading
    this.current = labels;
    this.paint();
    for (const near of [index + 1, index - 1, index + 2, index - 2]) {
      if (near >= 0 && near < this.meta.count) void this.load(near).catch(() => {});
    }
  }

  private paint() {
    const labels = this.current;
    if (!labels) return;
    const { width, height } = this.meta;
    const out = this.ctx.createImageData(width * 2, height);
    const px = new Uint32Array(out.data.buffer);
    const { L, R } = this.tables;
    for (let row = 0; row < height; row++) {
      const src = row * width;
      const dst = row * width * 2;
      for (let col = 0; col < width; col++) {
        const label = labels[src + col];
        // outline: darken where the label changes towards the midline or downwards
        const edge = label !== 0 && ((col + 1 < width && labels[src + col + 1] !== label) || (row + 1 < height && labels[src + width + col] !== label));
        let left = R[label];
        let right = L[label];
        if (edge) {
          left = darken(left);
          right = darken(right);
        }
        px[dst + col] = left; // patient's right hemisphere: lateral edge at the far left
        px[dst + width * 2 - 1 - col] = right; // patient's left hemisphere, mirrored
      }
    }
    this.ctx.putImageData(out, 0, 0);
    this.onPaint();
  }

  /**
   * The current slice in anatomical orientation for the 3D cut face: patient's left on the left,
   * anterior at the top, unlabelled voxels transparent so empty space (outside the tissue, ventricles
   * without a label) stays see-through. Pixel size = meta.pixelMm; width spans xMin..-xMin.
   */
  capCanvas(): HTMLCanvasElement | null {
    const labels = this.current;
    if (!labels) return null;
    const { width, height } = this.meta;
    const canvas = document.createElement('canvas');
    canvas.width = width * 2;
    canvas.height = height;
    const ctx = canvas.getContext('2d')!;
    const out = ctx.createImageData(width * 2, height);
    const px = new Uint32Array(out.data.buffer);
    const { L, R } = this.tables;
    for (let row = 0; row < height; row++) {
      const src = row * width;
      const dst = row * width * 2;
      for (let col = 0; col < width; col++) {
        const label = labels[src + col];
        if (!label) continue; // transparent
        const edge = (col + 1 < width && labels[src + col + 1] !== label) || (row + 1 < height && labels[src + width + col] !== label);
        let left = L[label];
        let right = R[label];
        if (edge) {
          left = darken(left);
          right = darken(right);
        }
        px[dst + col] = left; // atlas data are the left hemisphere: x from xMin up to the midline
        px[dst + width * 2 - 1 - col] = right; // right hemisphere, mirrored
      }
    }
    ctx.putImageData(out, 0, 0);
    return canvas;
  }

  private displayScale() {
    const fit = Math.min(this.viewport.clientWidth / this.canvas.width, this.viewport.clientHeight / this.canvas.height);
    return (fit || 1) * this.zoom;
  }

  private layout() {
    const scale = this.displayScale();
    // keep the image from being dragged entirely out of view
    const limitX = this.canvas.width / 2;
    const limitY = this.canvas.height / 2;
    this.pan.x = Math.min(limitX, Math.max(-limitX, this.pan.x));
    this.pan.y = Math.min(limitY, Math.max(-limitY, this.pan.y));
    const tx = this.viewport.clientWidth / 2 - (this.canvas.width / 2 + this.pan.x) * scale;
    const ty = this.viewport.clientHeight / 2 - (this.canvas.height / 2 + this.pan.y) * scale;
    this.canvas.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
    this.canvas.style.imageRendering = scale > 1.5 ? 'pixelated' : 'auto';
  }

  private hitAt(clientX: number, clientY: number): SectionHit | null {
    if (!this.current) return null;
    const rect = this.canvas.getBoundingClientRect();
    const cx = Math.floor(((clientX - rect.left) / rect.width) * this.canvas.width);
    const cy = Math.floor(((clientY - rect.top) / rect.height) * this.canvas.height);
    const { width, height, pixelMm, xMin, yMax } = this.meta;
    if (cx < 0 || cx >= width * 2 || cy < 0 || cy >= height) return null;
    const side: OriginSide = cx < width ? 'R' : 'L';
    const col = cx < width ? cx : width * 2 - 1 - cx;
    const label = this.current[cy * width + col];
    if (!label) return null;
    const xLeft = xMin + col * pixelMm; // RAS x in the stored (left) hemisphere
    return { label, side, xMm: side === 'L' ? xLeft : -xLeft, yMm: yMax - cy * pixelMm };
  }
}

function darken(abgr: number): number {
  const r = (abgr & 0xff) * 0.55;
  const g = ((abgr >> 8) & 0xff) * 0.55;
  const b = ((abgr >> 16) & 0xff) * 0.55;
  return ((255 << 24) | (b << 16) | (g << 8) | r) >>> 0;
}
