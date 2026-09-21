import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';
import type { Manifest, ManifestMesh, ManifestStructure, Vec3 } from '../types';
import { IntroParticles } from './IntroParticles';
import { applySolidState, ghostFocusDistance, ghostMaterial, haloMaterial, sceneReveal, solidMaterial, type MeshState } from './materials';
import { PathwayCurve } from './pathwayCurve';
import { MistSea, SETTLED_LEVEL } from './MistSea';

THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

export interface AtlasEntry {
  info: ManifestMesh;
  structure: ManifestStructure;
  object: THREE.Mesh;
  baseColor: THREE.Color;
  solid: THREE.MeshStandardMaterial;
  ghost: THREE.ShaderMaterial;
  halo: THREE.Mesh | null;
  isShell: boolean;
  state: MeshState;
}

export type ViewPreset = 'anterior' | 'posterior' | 'left' | 'right' | 'superior' | 'oblique';

/** Atlas data is RAS mm (z up); three.js is y up. Anterior ends up on -z. */
export const rasToThree = ([x, y, z]: Vec3) => new THREE.Vector3(x, z, -y);

const BRAIN_CENTER = rasToThree([0, -20, 8]);
const HOME_DISTANCE = 520;
const VIEW_DIRECTIONS: Record<ViewPreset, THREE.Vector3> = {
  anterior: new THREE.Vector3(0, 0, -1),
  posterior: new THREE.Vector3(0, 0, 1),
  left: new THREE.Vector3(-1, 0, 0),
  right: new THREE.Vector3(1, 0, 0),
  superior: new THREE.Vector3(0, 1, 0.001),
  oblique: new THREE.Vector3(-0.75, 0.35, -0.6).normalize(),
};
const ACCENT = '#a0e7ff';
/** after this long without input the loop drops to every other frame (pulses and drift stay smooth enough) */
const IDLE_AFTER_S = 3;

const smooth = (a: number, b: number, t: number) => {
  const k = Math.min(1, Math.max(0, (t - a) / (b - a)));
  return k * k * (3 - 2 * k);
};
const easeInOutCubic = (k: number) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);

function structureColor(groupColor: string, indexInGroup: number, isShell: boolean): THREE.Color {
  const c = new THREE.Color(groupColor);
  if (isShell) return c;
  // spread neighbours (e.g. thalamic nuclei) apart in hue/lightness so they stay distinguishable
  const hsl = { h: 0, s: 0, l: 0 };
  c.getHSL(hsl);
  const k = indexInGroup % 6;
  return c.setHSL((hsl.h + (k - 2.5) * 0.022 + 1) % 1, hsl.s, THREE.MathUtils.clamp(hsl.l + ((indexInGroup % 3) - 1) * 0.07, 0.3, 0.75));
}

interface Intro {
  t: number;
  duration: number;
  full: boolean;
  rippled: boolean;
  particles: IntroParticles | null;
  fromPos: THREE.Vector3;
  toPos: THREE.Vector3;
  resolve: () => void;
}

export class AtlasScene {
  readonly entries = new Map<string, AtlasEntry>();
  onHover: (entry: AtlasEntry | null, x: number, y: number) => void = () => {};
  onPick: (entry: AtlasEntry | null) => void = () => {};
  onStats: (stats: { fps: number; calls: number; triangles: number }) => void = () => {};
  /** called once per rendered frame, after the camera has settled for that frame */
  onFrame: () => void = () => {};

  private readonly renderer: THREE.WebGLRenderer;
  private readonly scene = new THREE.Scene();
  private readonly camera = new THREE.PerspectiveCamera(32, 1, 1, 6000);
  private readonly controls: OrbitControls;
  private readonly root = new THREE.Group();
  private readonly background: MistSea;
  private readonly raycaster = new THREE.Raycaster();
  private readonly pointer = new THREE.Vector2();
  private readonly hiddenGroups = new Set<string>();
  private readonly reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  private pointerDirty = false;
  private pointerClient = { x: 0, y: 0 };
  private downAt: { x: number; y: number } | null = null;
  private hovered: AtlasEntry | null = null;
  private route: PathwayCurve | null = null;
  private readonly sectionPlane = new THREE.Group();
  private readonly cutPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);
  private cutEnabled = false;
  private fly: { fromTarget: THREE.Vector3; toTarget: THREE.Vector3; fromPos: THREE.Vector3; toPos: THREE.Vector3; t: number } | null = null;
  private intro: Intro | null = null;
  private lastFrameMs = performance.now();
  private time = 0;
  private lastActivity = 0;
  private framing = { x: 0.5, scale: 1 };
  private framingGoal = { x: 0.5, scale: 1 };
  private framed = false;
  private frameParity = 0;
  private frames = 0;
  private statsAt = 0;

  constructor(private readonly canvas: HTMLCanvasElement) {
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor('#030304');
    this.raycaster.firstHitOnly = true;
    this.background = new MistSea(BRAIN_CENTER, this.renderer);

    this.scene.add(new THREE.HemisphereLight('#e8ecff', '#2c2a4a', 1.1));
    const key = new THREE.DirectionalLight('#ffffff', 2.0);
    key.position.set(-0.4, 0.6, 1);
    this.camera.add(key);
    this.scene.add(this.background.group, this.camera, this.root);
    this.buildSectionPlane();

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.12;
    this.controls.minDistance = 30;
    this.controls.maxDistance = 1200;
    this.controls.addEventListener('start', () => (this.fly = null));
    this.controls.addEventListener('change', () => this.poke());
    this.setView('oblique', false);

    new ResizeObserver(() => this.resize()).observe(canvas.parentElement!);
    this.resize();

    canvas.addEventListener('pointermove', (e) => {
      const rect = canvas.getBoundingClientRect();
      this.pointer.set(((e.clientX - rect.left) / rect.width) * 2 - 1, -((e.clientY - rect.top) / rect.height) * 2 + 1);
      this.pointerClient = { x: e.clientX, y: e.clientY };
      this.pointerDirty = true;
      this.poke();
      // the sea answers the pointer wherever it passes over it (not while the intro is still playing)
      if (!this.intro && !this.reducedMotion.matches) {
        this.raycaster.setFromCamera(this.pointer, this.camera);
        this.background.stir(this.raycaster.ray);
      }
    });
    canvas.addEventListener('pointerleave', () => this.setHovered(null));
    canvas.addEventListener('pointerdown', (e) => (this.downAt = { x: e.clientX, y: e.clientY }));
    canvas.addEventListener('pointerup', (e) => {
      const moved = this.downAt ? Math.hypot(e.clientX - this.downAt.x, e.clientY - this.downAt.y) : 99;
      this.downAt = null;
      if (moved >= 5 || this.intro) return;
      const hit = this.raycast();
      // empty space answers too: a ring where the click landed, and the sea rushes in for a moment
      if (!hit && !this.reducedMotion.matches) {
        this.raycaster.setFromCamera(this.pointer, this.camera);
        this.background.surge(this.raycaster.ray);
      }
      this.onPick(hit);
    });
  }

  async load(manifest: Manifest, glbUrl: string, onProgress: (fraction: number | null) => void = () => {}) {
    const loader = new GLTFLoader();
    loader.setMeshoptDecoder(MeshoptDecoder);
    const gltf = await loader.loadAsync(glbUrl, (e) => onProgress(e.lengthComputable && e.total > 0 ? e.loaded / e.total : null));

    // GLTFLoader sanitises node names ("thal-vpl.L" -> "thal-vplL"), so match on the sanitised form
    const bySanitised = new Map(manifest.meshes.map((m) => [THREE.PropertyBinding.sanitizeNodeName(m.id), m]));
    const structures = new Map(manifest.structures.map((s) => [s.id, s]));
    const indexInGroup = new Map<string, number>();
    const groupCounts = new Map<string, number>();
    for (const s of manifest.structures) {
      indexInGroup.set(s.id, groupCounts.get(s.group) ?? 0);
      groupCounts.set(s.group, (groupCounts.get(s.group) ?? 0) + 1);
    }

    gltf.scene.traverse((obj) => {
      const object = obj as THREE.Mesh;
      if (!object.isMesh) return;
      const info = bySanitised.get(object.name) ?? bySanitised.get(object.parent?.name ?? '');
      if (!info) return;
      const structure = structures.get(info.structureId)!;
      const isShell = structure.group === 'shell';
      const baseColor = structureColor(manifest.groups[structure.group].color, indexInGroup.get(structure.id)!, isShell);
      if (!object.geometry.attributes.normal) object.geometry.computeVertexNormals();
      object.geometry.computeBoundsTree();
      const entry: AtlasEntry = {
        info, structure, object, baseColor, isShell, state: 'normal', halo: null,
        solid: solidMaterial(baseColor), ghost: ghostMaterial(baseColor, isShell),
      };
      object.userData.entry = entry;
      this.entries.set(info.id, entry);
    });
    const missing = manifest.meshes.filter((m) => !this.entries.has(m.id)).map((m) => m.id);
    if (missing.length) throw new Error(`meshes listed in the manifest but absent from the GLB: ${missing.join(', ')}`);

    gltf.scene.rotation.x = -Math.PI / 2; // RAS -> y-up, see rasToThree
    this.root.add(gltf.scene);
    this.root.updateMatrixWorld(true);
    this.setStates(() => 'normal');
    // everything starts invisible; `transparent` must be set before the first compile, because an
    // opaque MeshStandardMaterial is built with OPAQUE defined and then ignores `opacity`
    for (const e of this.entries.values()) {
      e.solid.transparent = true;
      e.solid.opacity = 0;
    }
    sceneReveal.value = 0;
    this.background.level = 0;
    this.renderer.setAnimationLoop(() => this.frame());
  }

  /**
   * Bring the scene in from black. `full` plays the particle convergence and the dolly-in (first visit);
   * otherwise it is a short fade. With prefers-reduced-motion everything simply appears.
   */
  playIntro(full: boolean): Promise<void> {
    if (this.reducedMotion.matches) {
      sceneReveal.value = 1;
      this.background.level = SETTLED_LEVEL;
      this.finishReveal();
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      const toPos = this.camera.position.clone();
      const fromPos = toPos.clone();
      let particles: IntroParticles | null = null;
      if (full) {
        // start further out and a little round to the side, then settle into the home view
        fromPos.sub(BRAIN_CENTER).applyAxisAngle(new THREE.Vector3(0, 1, 0), -0.5).multiplyScalar(820 / HOME_DISTANCE).add(BRAIN_CENTER);
        const shells = [...this.entries.values()].filter((e) => e.isShell).map((e) => e.object);
        particles = new IntroParticles(shells, BRAIN_CENTER);
        this.root.add(particles.points);
        this.camera.position.copy(fromPos);
      }
      this.controls.enabled = false;
      this.intro = { t: 0, duration: full ? 3.4 : 0.9, full, rippled: false, particles, fromPos, toPos, resolve };
    });
  }

  /** Jump to the end of the intro (any click or key press). */
  skipIntro() {
    if (this.intro) this.intro.t = this.intro.duration;
  }

  get introPlaying() { return this.intro !== null; }

  private stepIntro(dt: number) {
    const intro = this.intro!;
    intro.t = Math.min(intro.duration, intro.t + dt);
    const t = intro.t;
    let reveal: number;
    if (intro.full) {
      // the sea comes up with the first light and eases to its everyday level once the brain is there
      this.background.level = smooth(0, 1.1, t) * (1 + (SETTLED_LEVEL - 1) * smooth(2.5, 3.4, t));
      reveal = smooth(1.9, 3.1, t);
      if (!intro.rippled && t > 2.2) {
        intro.rippled = true;
        this.background.centerRipple(); // the brain's arrival sends one ring out across the sea
      }
      intro.particles!.set(smooth(0.25, 2.35, t) * 0.999, 1 - smooth(2.3, 3.2, t), this.renderer.getPixelRatio());
      this.camera.position.lerpVectors(intro.fromPos, intro.toPos, easeInOutCubic(smooth(0.1, 3.1, t)));
    } else {
      this.background.level = SETTLED_LEVEL * smooth(0, 0.6, t);
      reveal = smooth(0.1, 0.9, t);
    }
    sceneReveal.value = reveal;
    for (const e of this.entries.values()) e.solid.opacity = reveal;

    if (t >= intro.duration) {
      this.finishReveal();
      if (intro.particles) {
        this.root.remove(intro.particles.points);
        intro.particles.dispose();
      }
      this.camera.position.copy(intro.toPos);
      this.controls.enabled = true;
      this.intro = null;
      intro.resolve();
    }
  }

  private finishReveal() {
    for (const e of this.entries.values()) {
      e.solid.transparent = false;
      e.solid.opacity = 1;
      e.solid.needsUpdate = true;
    }
  }

  /** Assign a state to every mesh. Shells are always drawn as ghosts unless made active/involved. */
  setStates(stateOf: (entry: AtlasEntry) => MeshState) {
    for (const entry of this.entries.values()) {
      let state = stateOf(entry);
      if (entry.isShell && state === 'normal') state = 'ghost';
      entry.state = state;
      const ghost = state === 'ghost';
      entry.object.material = ghost ? entry.ghost : entry.solid;
      // ghosts after solids; shells last so inner ghosts are not tinted twice by sort flips
      entry.object.renderOrder = ghost ? (entry.isShell ? 20 : 10) : 0;
      this.setHalo(entry, state === 'active' && !entry.isShell);
    }
    this.applyVisibility();
    this.poke();
  }

  private setHalo(entry: AtlasEntry, on: boolean) {
    if (on && !entry.halo) {
      const size = rasToThree(entry.info.bboxMax).distanceTo(rasToThree(entry.info.bboxMin));
      // the mesh node may carry a dequantisation scale, so express the halo width in its local units
      const localPerMm = 1 / entry.object.getWorldScale(new THREE.Vector3()).x;
      entry.halo = new THREE.Mesh(entry.object.geometry, haloMaterial(entry.baseColor, THREE.MathUtils.clamp(size * 0.05, 0.5, 2.5) * localPerMm));
      entry.halo.renderOrder = 2;
      entry.halo.raycast = () => {};
      entry.object.add(entry.halo);
    }
    if (entry.halo) entry.halo.visible = on;
  }

  setGroupVisible(group: string, visible: boolean) {
    if (visible) this.hiddenGroups.delete(group);
    else this.hiddenGroups.add(group);
    this.applyVisibility();
    this.poke();
  }

  private applyVisibility() {
    for (const entry of this.entries.values()) {
      // a hidden group still shows the meshes a pathway or selection needs
      const forced = entry.state === 'active' || entry.state === 'involved';
      entry.object.visible = forced || !this.hiddenGroups.has(entry.structure.group);
    }
  }

  private buildSectionPlane() {
    const w = 176, d = 210; // mm: a little larger than the brain's footprint
    const fill = new THREE.Mesh(
      new THREE.PlaneGeometry(w, d),
      new THREE.MeshBasicMaterial({ color: ACCENT, transparent: true, opacity: 0.06, side: THREE.DoubleSide, depthWrite: false }),
    );
    fill.rotation.x = -Math.PI / 2;
    const outline = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints([[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([x, z]) => new THREE.Vector3((x * w) / 2, 0, (z * d) / 2))),
      new THREE.LineBasicMaterial({ color: ACCENT, transparent: true, opacity: 0.65 }),
    );
    fill.renderOrder = outline.renderOrder = 30;
    this.sectionPlane.add(fill, outline);
    this.sectionPlane.position.set(BRAIN_CENTER.x, 0, BRAIN_CENTER.z);
    this.sectionPlane.visible = false;
    this.root.add(this.sectionPlane);
  }

  /** Show the axial section plane at RAS z (mm), or hide it with null. */
  setSectionPlane(zMm: number | null) {
    this.sectionPlane.visible = zMm !== null;
    this.poke();
    if (zMm === null) return;
    // RAS z is three.js y. The indicator sits a hair below the cut so the cut does not clip it away.
    this.sectionPlane.position.y = zMm - 0.05;
    this.cutPlane.constant = zMm;
  }

  /** Cut away everything above the section plane so the level being viewed in 2D is exposed in 3D. */
  setSectionCut(enabled: boolean) {
    this.cutEnabled = enabled;
    this.renderer.clippingPlanes = enabled ? [this.cutPlane] : [];
    // a cut mesh is an open shell: draw its inside too, otherwise you see straight through it
    for (const e of this.entries.values()) e.solid.side = enabled ? THREE.DoubleSide : THREE.FrontSide;
    this.poke();
  }

  get sectionCut() { return this.cutEnabled; }

  structureColor(structureId: string): THREE.Color | undefined {
    return (this.entries.get(`${structureId}.L`) ?? this.entries.get(`${structureId}.M`))?.baseColor;
  }

  setRoute(pointsRas: Vec3[] | null) {
    if (this.route) {
      this.root.remove(this.route.object);
      this.route.dispose();
      this.route = null;
    }
    if (pointsRas && pointsRas.length >= 2) {
      this.route = new PathwayCurve(pointsRas.map(rasToThree));
      this.root.add(this.route.object);
    }
    this.poke();
  }

  revealRouteTo(pointIndex: number) {
    this.route?.revealTo(pointIndex);
    this.poke();
  }

  setView(preset: ViewPreset, animate = true) {
    const toPos = BRAIN_CENTER.clone().addScaledVector(VIEW_DIRECTIONS[preset], HOME_DISTANCE);
    this.flyTo(BRAIN_CENTER.clone(), toPos, animate);
  }

  /** Frame the given meshes, keeping the current viewing direction. */
  focus(meshIds: Iterable<string>) {
    const box = new THREE.Box3();
    for (const id of meshIds) {
      const entry = this.entries.get(id);
      if (!entry) continue;
      box.expandByPoint(rasToThree(entry.info.bboxMin));
      box.expandByPoint(rasToThree(entry.info.bboxMax));
    }
    if (box.isEmpty()) return;
    const sphere = box.getBoundingSphere(new THREE.Sphere());
    const radius = Math.max(sphere.radius, 22); // keep enough surroundings in view to stay oriented
    const distance = (radius / Math.sin(THREE.MathUtils.degToRad(this.camera.fov / 2))) * 1.25;
    const direction = this.camera.position.clone().sub(this.controls.target).normalize();
    this.flyTo(sphere.center, sphere.center.clone().addScaledVector(direction, distance), true);
  }

  /** Screen position (CSS px within the canvas) of a point given in RAS mm. */
  project(ras: Vec3): { x: number; y: number; visible: boolean } {
    const v = rasToThree(ras).project(this.camera);
    const rect = this.canvas.getBoundingClientRect();
    return { x: ((v.x + 1) / 2) * rect.width, y: ((1 - v.y) / 2) * rect.height, visible: v.z > -1 && v.z < 1 && Math.abs(v.x) < 1.05 && Math.abs(v.y) < 1.05 };
  }

  private flyTo(toTarget: THREE.Vector3, toPos: THREE.Vector3, animate: boolean) {
    this.poke();
    if (!animate || this.reducedMotion.matches) {
      this.fly = null;
      this.controls.target.copy(toTarget);
      this.camera.position.copy(toPos);
      this.controls.update();
      return;
    }
    this.fly = { fromTarget: this.controls.target.clone(), toTarget, fromPos: this.camera.position.clone(), toPos, t: 0 };
  }

  private poke() {
    this.lastActivity = this.time;
  }

  /**
   * Put the subject where the panels leave room: `x` is where the orbit centre lands, as a fraction of the
   * stage width, and `scale` (<= 1) draws everything that much smaller. Done with a view offset, so the
   * camera, the controls and picking carry on as if nothing happened.
   */
  setFraming(x: number, scale: number) {
    this.framingGoal = { x, scale };
    if (this.reducedMotion.matches || !this.framed) {
      this.framing = { x, scale };
      this.applyFraming();
    }
    this.framed = true;
    this.poke();
  }

  private applyFraming() {
    const { clientWidth: w, clientHeight: h } = this.canvas.parentElement!;
    if (!w || !h) return;
    const { x, scale } = this.framing;
    if (Math.abs(x - 0.5) < 1e-4 && Math.abs(scale - 1) < 1e-4) this.camera.clearViewOffset();
    else this.camera.setViewOffset(w / scale, h / scale, w / scale / 2 - x * w, (h / scale - h) / 2, w, h);
  }

  private resize() {
    const parent = this.canvas.parentElement!;
    const { clientWidth: w, clientHeight: h } = parent;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.applyFraming();
    this.poke();
  }

  private raycast(): AtlasEntry | null {
    this.raycaster.setFromCamera(this.pointer, this.camera);
    // solid structures win over ghosts; shells are never pickable (they would swallow every click)
    const tiers: AtlasEntry[][] = [[], []];
    for (const e of this.entries.values()) {
      if (!e.object.visible || e.isShell) continue;
      tiers[e.state === 'ghost' ? 1 : 0].push(e);
    }
    for (const tier of tiers) {
      const hit = this.raycaster.intersectObjects(tier.map((e) => e.object), false)[0];
      if (hit) return hit.object.userData.entry as AtlasEntry;
    }
    return null;
  }

  private setHovered(entry: AtlasEntry | null) {
    if (entry === this.hovered && !entry) return;
    this.hovered = entry;
    this.canvas.style.cursor = entry ? 'pointer' : 'grab';
    this.onHover(entry, this.pointerClient.x, this.pointerClient.y);
  }

  private frame() {
    const now = performance.now();
    const dt = Math.min((now - this.lastFrameMs) / 1000, 0.1);
    this.lastFrameMs = now;
    const time = (this.time += dt);

    // nothing but slow drift and pulses to show: every other frame is plenty
    const reframing = Math.abs(this.framing.x - this.framingGoal.x) > 5e-4 || Math.abs(this.framing.scale - this.framingGoal.scale) > 5e-4;
    const busy = reframing || this.intro !== null || this.fly !== null || this.downAt !== null || this.background.rippling || time - this.lastActivity < IDLE_AFTER_S;
    this.frameParity ^= 1;
    if (!busy && this.frameParity) return;

    if (this.intro) this.stepIntro(dt);
    if (reframing) {
      const k = 1 - Math.exp(-dt * 8);
      this.framing.x += (this.framingGoal.x - this.framing.x) * k;
      this.framing.scale += (this.framingGoal.scale - this.framing.scale) * k;
      this.applyFraming();
    } else if (this.framing.x !== this.framingGoal.x || this.framing.scale !== this.framingGoal.scale) {
      this.framing = { ...this.framingGoal };
      this.applyFraming();
    }
    if (this.fly) {
      this.fly.t = Math.min(1, this.fly.t + dt / 0.7);
      const k = 1 - Math.pow(1 - this.fly.t, 3);
      this.controls.target.lerpVectors(this.fly.fromTarget, this.fly.toTarget, k);
      this.camera.position.lerpVectors(this.fly.fromPos, this.fly.toPos, k);
      if (this.fly.t >= 1) this.fly = null;
    }
    this.controls.update();
    ghostFocusDistance.value = this.camera.position.distanceTo(this.controls.target);

    if (this.pointerDirty && !this.downAt && !this.intro) {
      this.pointerDirty = false;
      this.setHovered(this.raycast());
    }

    const still = this.reducedMotion.matches;
    const pulse = still ? 0.5 : 0.5 + 0.5 * Math.sin(time * 3.2);
    for (const e of this.entries.values()) {
      if (e.state !== 'ghost') applySolidState(e.solid, e.baseColor, e.state, e === this.hovered, pulse);
      else e.ghost.uniforms.uHover.value = e === this.hovered ? 1 : 0;
    }
    this.route?.update(still ? 0 : time, still ? 1 : dt);
    this.camera.updateMatrixWorld();
    this.background.update(still ? 40 : time, still ? 0 : dt, this.renderer.getPixelRatio(), this.canvas.clientHeight);
    this.renderer.render(this.scene, this.camera);
    this.onFrame();

    this.frames++;
    if (time - this.statsAt >= 0.5) {
      const info = this.renderer.info.render;
      this.onStats({ fps: this.frames / (time - this.statsAt), calls: info.calls, triangles: info.triangles });
      this.frames = 0;
      this.statsAt = time;
    }
  }
}
