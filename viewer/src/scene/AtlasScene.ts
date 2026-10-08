import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';
import type { Manifest, ManifestJoint, ManifestMesh, ManifestStructure, Vec3 } from '../types';
import { IntroParticles } from './IntroParticles';
import { applySolidState, ghostFocusDistance, ghostMaterial, haloMaterial, sceneFloor, sceneReveal, solidMaterial, type MeshState } from './materials';
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
  /** drawn as an outline until chosen: cortical areas overlap each other on the same gyri, and the
   *  spinal cord runs down through the mist sea */
  isOutline: boolean;
  state: MeshState;
}

export type ViewPreset = 'anterior' | 'posterior' | 'left' | 'right' | 'superior' | 'oblique' | 'body';

/** Atlas data is RAS mm (z up); three.js is y up. Anterior ends up on -z. */
export const rasToThree = ([x, y, z]: Vec3) => new THREE.Vector3(x, z, -y);

const BRAIN_CENTER = rasToThree([0, -20, 8]);
const HOME_DISTANCE = 520;
/** the whole body (BodyParts3D ghost): its middle and how far back the camera must stand to take it in */
const BODY_CENTER = rasToThree([0, -90, -720]);
const BODY_DISTANCE = 3400;
const VIEW_DIRECTIONS: Record<ViewPreset, THREE.Vector3> = {
  anterior: new THREE.Vector3(0, 0, -1),
  posterior: new THREE.Vector3(0, 0, 1),
  left: new THREE.Vector3(-1, 0, 0),
  right: new THREE.Vector3(1, 0, 0),
  superior: new THREE.Vector3(0, 1, 0.001),
  oblique: new THREE.Vector3(-0.75, 0.35, -0.6).normalize(),
  body: new THREE.Vector3(-0.35, 0.08, -0.93).normalize(),
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
  private readonly camera = new THREE.PerspectiveCamera(32, 1, 1, 20000);
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
  /** the slice image laid on the cut face */
  private sectionCap: THREE.Mesh | null = null;
  private readonly cutPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);
  private cutEnabled = false;
  private fly: { fromTarget: THREE.Vector3; toTarget: THREE.Vector3; fromPos: THREE.Vector3; toPos: THREE.Vector3; t: number } | null = null;
  private intro: Intro | null = null;
  private lastFrameMs = performance.now();
  private time = 0;
  private lastActivity = 0;
  /** where the mist surface should be: at rest under the brain, lower when the focus is on the body */
  private seaGoal = 0;
  /** the "몸 드러내기" toggle: while on, the mist stays below the feet whatever is in focus */
  private bodyRevealed = false;
  /** limb joints of the schematic body: pivot groups in the atlas (RAS) frame, with current and goal angles */
  private readonly joints = new Map<string, { info: ManifestJoint; group: THREE.Group; angle: number; goal: number }>();
  private framing = { x: 0.5, y: 0.5, scale: 1 };
  private framingGoal = { x: 0.5, y: 0.5, scale: 1 };
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
    sceneFloor.value = this.background.seaLevel;
    this.seaGoal = this.background.seaLevel;

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
    this.controls.maxDistance = 4500; // far enough to take in the whole body
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
      // groups drawn as ghosts until chosen: the shells and cortex, and everything that would otherwise bury
      // the nuclei — the tract tubes, the body shell, muscles and viscera
      const GHOST_GROUPS = new Set(['cortex', 'spinal-cord', 'tracts', 'body-shell', 'muscles', 'viscera']);
      const isOutline = isShell || GHOST_GROUPS.has(structure.group);
      const baseColor = structure.color ? new THREE.Color(structure.color) : structureColor(manifest.groups[structure.group].color, indexInGroup.get(structure.id)!, isShell);
      if (!object.geometry.attributes.normal) object.geometry.computeVertexNormals();
      object.geometry.computeBoundsTree();
      const entry: AtlasEntry = {
        info, structure, object, baseColor, isShell, isOutline, state: 'normal', halo: null,
        solid: solidMaterial(baseColor), ghost: ghostMaterial(baseColor, isShell),
      };
      object.userData.entry = entry;
      this.entries.set(info.id, entry);
    });
    const missing = manifest.meshes.filter((m) => !this.entries.has(m.id)).map((m) => m.id);
    if (missing.length) throw new Error(`meshes listed in the manifest but absent from the GLB: ${missing.join(', ')}`);

    this.buildJoints(gltf.scene, manifest.joints ?? []);
    this.buildPupils(gltf.scene);
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

  /** Pivot groups for the limb joints, built in the GLB's own (RAS) frame before it is rotated to y-up.
   *  A joint's group sits at its pivot and holds the bone segment it moves; child joints are attached
   *  inside it, so flexing the shoulder carries the elbow, wrist and hand along. */
  private buildJoints(atlasRoot: THREE.Object3D, joints: ManifestJoint[]) {
    const ordered = [...joints].sort((a, b) => depth(a) - depth(b));
    function depth(j: ManifestJoint): number {
      let d = 0;
      for (let p = j.parent; p; d++) p = joints.find((x) => x.id === p)?.parent ?? null;
      return d;
    }
    atlasRoot.updateMatrixWorld(true);
    for (const info of ordered) {
      const moved = (info.segments ?? [info.segment]).map((id) => this.entries.get(id)).filter((e): e is AtlasEntry => !!e);
      if (!moved.length) continue;
      const group = new THREE.Group();
      group.name = `joint:${info.id}`;
      const parentJoint = info.parent ? this.joints.get(info.parent) : undefined;
      // a child joint's group lives inside its parent's group, so its position is the pivot relative to
      // the parent's pivot (the parent is unrotated while the chain is built)
      const base = parentJoint ? parentJoint.info.pivot : [0, 0, 0];
      group.position.set(info.pivot[0] - base[0], info.pivot[1] - base[1], info.pivot[2] - base[2]);
      (parentJoint?.group ?? atlasRoot).add(group);
      group.updateMatrixWorld(true);
      for (const e of moved) group.attach(e.object); // keeps each mesh where it is; only the parent changes
      this.joints.set(info.id, { info, group, angle: 0, goal: 0 });
    }
  }

  /** the iris rings, each on a pivot at its centre so the pupil can be scaled: side -> {group, scale, goal} */
  private readonly pupils = new Map<string, { group: THREE.Group; scale: number; goal: number }>();
  /** each eyeball with its parts on a pivot at the globe's centre: side -> {group, current and goal rotation (deg about z, x)} */
  private readonly eyes = new Map<string, { group: THREE.Group; rot: [number, number]; goal: [number, number] }>();
  /** the lenses on pivots at their centre, scaled along the eye axis for accommodation */
  private readonly lenses = new Map<string, { group: THREE.Group; k: number; goal: number }>();

  private static readonly EYE_PARTS = new Set(['so-eyeball', 'so-lens', 'so-iris', 'so-cornea', 'so-retina', 'so-nasal-retina', 'so-temporal-retina', 'so-ciliary-body']);

  private buildPupils(atlasRoot: THREE.Object3D) {
    // 1. the globes: a pivot at each eyeball's centre carrying every part of that eye
    for (const entry of this.entries.values()) {
      if (entry.structure.id !== 'so-eyeball') continue;
      const group = new THREE.Group();
      group.name = `eye:${entry.info.side}`;
      const c = entry.info.centroid;
      group.position.set(c[0], c[1], c[2]);
      atlasRoot.add(group);
      group.updateMatrixWorld(true);
      this.eyes.set(entry.info.side, { group, rot: [0, 0], goal: [0, 0] });
    }
    for (const entry of this.entries.values()) {
      if (!AtlasScene.EYE_PARTS.has(entry.structure.id)) continue;
      const eye = this.eyes.get(entry.info.side);
      if (eye) eye.group.attach(entry.object);
    }
    // 2. inside each eye: the iris on its own pivot (pupil size) and the lens on its own (accommodation)
    for (const entry of this.entries.values()) {
      if (entry.structure.id !== 'so-iris' && entry.structure.id !== 'so-lens') continue;
      const eye = this.eyes.get(entry.info.side);
      const parent = eye?.group ?? atlasRoot;
      const base = eye ? this.entries.get(`so-eyeball.${entry.info.side}`)!.info.centroid : [0, 0, 0];
      const group = new THREE.Group();
      const c = entry.info.centroid;
      group.position.set(c[0] - base[0], c[1] - base[1], c[2] - base[2]);
      parent.add(group);
      group.updateMatrixWorld(true);
      group.attach(entry.object);
      if (entry.structure.id === 'so-iris') this.pupils.set(entry.info.side, { group, scale: 1, goal: 1 });
      else this.lenses.set(entry.info.side, { group, k: 0, goal: 0 });
    }
  }

  /** skeletal muscles on pivots at their centre: contraction scales them along their long axis */
  private readonly muscles = new Map<string, { group: THREE.Group; axis: THREE.Vector3; k: number; goal: number }>();

  private musclePivot(entry: AtlasEntry) {
    let m = this.muscles.get(entry.info.id);
    if (m) return m;
    const group = new THREE.Group();
    const parent = entry.object.parent!;
    // the pivot sits at the muscle's centroid, inside whatever already holds the mesh (a joint group or the atlas)
    const worldC = rasToThree(entry.info.centroid);
    const localC = parent.worldToLocal(this.root.localToWorld(worldC.clone()));
    group.position.copy(localC);
    parent.add(group);
    group.updateMatrixWorld(true);
    group.attach(entry.object);
    const size = [0, 1, 2].map((i) => entry.info.bboxMax[i] - entry.info.bboxMin[i]);
    const longest = size.indexOf(Math.max(...size));
    const axis = new THREE.Vector3(longest === 0 ? 1 : 0, longest === 1 ? 1 : 0, longest === 2 ? 1 : 0);
    m = { group, axis, k: 0, goal: 0 };
    this.muscles.set(entry.info.id, m);
    return m;
  }

  /** Contract the given skeletal muscles (shorter along their long axis, thicker across); others relax. */
  setContractions(meshIds: Iterable<string>) {
    const want = new Set(meshIds);
    for (const id of want) {
      const entry = this.entries.get(id);
      if (entry && entry.structure.group === 'muscles') this.musclePivot(entry).goal = 1;
    }
    for (const [id, m] of this.muscles) if (!want.has(id)) m.goal = 0;
    this.poke();
  }

  /** Turn the eyes: per side [degrees about the vertical axis (+ = toward the nose), degrees of elevation]. */
  setEyeRotations(goals: Record<string, [number, number]>) {
    for (const [side, e] of this.eyes) e.goal = goals[side] ?? [0, 0];
    this.poke();
  }

  /** Lens accommodation per side: 0 at rest, 1 fully thickened. */
  setLenses(goals: Record<string, number>) {
    for (const [side, l] of this.lenses) l.goal = goals[side] ?? 0;
    this.poke();
  }

  /** Pupil size per side as a scale of the iris ring: < 1 constricts, > 1 dilates, 1 at rest. */
  setPupils(scales: Record<string, number>) {
    for (const [side, p] of this.pupils) p.goal = scales[side] ?? 1;
    this.poke();
  }

  /** Mesh ids of the bone segments a joint moves: its own and those of every joint distal to it. */
  jointChainMeshIds(jointId: string): string[] {
    const out: string[] = [];
    const walk = (id: string) => {
      const j = this.joints.get(id);
      if (!j) return;
      out.push(...(j.info.segments ?? [j.info.segment]));
      for (const [cid, c] of this.joints) if (c.info.parent === id) walk(cid);
    };
    walk(jointId);
    return out;
  }

  /** Flex (positive degrees) or extend the given joints; every joint not named returns to rest. */
  setJointAngles(angles: Record<string, number>) {
    for (const [id, j] of this.joints) j.goal = angles[id] ?? 0;
    this.poke();
  }

  /** Assign a state to every mesh. Shells are always drawn as ghosts unless made active/involved. */
  setStates(stateOf: (entry: AtlasEntry) => MeshState) {
    for (const entry of this.entries.values()) {
      let state = stateOf(entry);
      if (entry.isOutline && state === 'normal') state = 'ghost';
      // the skin is the body's outline and is never solid: solid it would wall off everything inside
      if (entry.structure.id === 'body-skin') state = 'ghost';
      entry.state = state;
      const ghost = state === 'ghost';
      entry.object.material = ghost ? entry.ghost : entry.solid;
      // ghosts after solids; shells last so inner ghosts are not tinted twice by sort flips
      entry.object.renderOrder = ghost ? (entry.isShell ? 20 : entry.isOutline ? 15 : 10) : 0;
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

  /**
   * Lay the 2D slice on the cut face so the structures around the pathway can be read in place.
   * `canvas` is the slice in anatomical orientation (see SectionPanel.capCanvas); its pixel grid is
   * `pixelMm` wide per pixel, covering RAS x in [xMin, -xMin] and y in [yMin, yMax].
   */
  setSectionCap(canvas: HTMLCanvasElement | null, extent?: { xMin: number; yMin: number; yMax: number; pixelMm: number }) {
    if (this.sectionCap) {
      this.sectionCap.removeFromParent();
      (this.sectionCap.material as THREE.MeshBasicMaterial).map?.dispose();
      (this.sectionCap.material as THREE.Material).dispose();
      this.sectionCap.geometry.dispose();
      this.sectionCap = null;
    }
    this.poke();
    if (!canvas || !extent) return;
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.minFilter = THREE.LinearFilter;
    const w = canvas.width * extent.pixelMm;
    const d = canvas.height * extent.pixelMm;
    const cap = new THREE.Mesh(
      new THREE.PlaneGeometry(w, d),
      new THREE.MeshBasicMaterial({ map: texture, transparent: true, opacity: 0.92, side: THREE.DoubleSide, depthWrite: false }),
    );
    // PlaneGeometry lies in its local xy with the image top at +y; rotated flat, +y points to -z,
    // which is RAS +y (anterior). Centre: x = 0 (midline), RAS y = middle of the slice.
    cap.rotation.x = -Math.PI / 2;
    cap.position.set(0, this.cutPlane.constant - 0.15, -(extent.yMin + extent.yMax) / 2);
    cap.renderOrder = 25;
    cap.raycast = () => {};
    this.sectionCap = cap;
    this.root.add(cap);
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
    if (preset === 'body') {
      // the whole body: the mist sinks under the feet and the camera backs off
      this.seaGoal = BODY_CENTER.y - 900;
      this.flyTo(BODY_CENTER.clone(), BODY_CENTER.clone().addScaledVector(VIEW_DIRECTIONS.body, BODY_DISTANCE), animate);
      return;
    }
    const toPos = BRAIN_CENTER.clone().addScaledVector(VIEW_DIRECTIONS[preset], HOME_DISTANCE);
    this.seaGoal = this.background.seaLevel;
    this.flyTo(BRAIN_CENTER.clone(), toPos, animate);
  }

  /** Keep the whole body above the mist (on) or let the mist cover it again (off). */
  revealBody(on: boolean) {
    this.bodyRevealed = on;
    this.poke();
  }

  get isBodyRevealed() {
    return this.bodyRevealed;
  }

  /** Frame the given meshes, keeping the current viewing direction. */
  focus(meshIds: Iterable<string>) {
    const box = new THREE.Box3();
    for (const id of meshIds) {
      const entry = this.entries.get(id);
      // the whole-body skin is in sensory pathways as "the skin", but framing it would shrink everything
      // else to a dot; it is a ghost anyway
      if (!entry || entry.structure.id === 'body-skin') continue;
      box.expandByPoint(rasToThree(entry.info.bboxMin));
      box.expandByPoint(rasToThree(entry.info.bboxMax));
    }
    if (box.isEmpty()) return;
    // the sea sinks below whatever is in focus, so a muscle or an organ is seen with the body around it
    this.seaGoal = Math.min(this.background.seaLevel, box.min.y - 80);
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
   * Put the subject where the panels leave room: `x` and `y` are where the orbit centre lands, as fractions
   * of the stage's width and height, and `scale` (<= 1) draws everything that much smaller. Done with a view offset, so the
   * camera, the controls and picking carry on as if nothing happened.
   */
  setFraming(x: number, scale: number, y = 0.5) {
    this.framingGoal = { x, y, scale };
    if (this.reducedMotion.matches || !this.framed) {
      this.framing = { x, y, scale };
      this.applyFraming();
    }
    this.framed = true;
    this.poke();
  }

  /** where the subject is being drawn right now (for tests) */
  get framingNow() { return { ...this.framing }; }

  private applyFraming() {
    const { clientWidth: w, clientHeight: h } = this.canvas.parentElement!;
    if (!w || !h) return;
    const { x, y, scale } = this.framing;
    if (Math.abs(x - 0.5) < 1e-4 && Math.abs(y - 0.5) < 1e-4 && Math.abs(scale - 1) < 1e-4) this.camera.clearViewOffset();
    // the canvas is a window onto a *smaller* virtual image: the frustum widens by 1/scale, so everything
    // is drawn `scale` times its size, and the offsets put the optical axis at (x, y) of the canvas
    else this.camera.setViewOffset(w * scale, h * scale, (w * scale) / 2 - x * w, (h * scale) / 2 - y * h, w, h);
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
    const reframing = Math.abs(this.framing.x - this.framingGoal.x) > 5e-4 || Math.abs(this.framing.y - this.framingGoal.y) > 5e-4
      || Math.abs(this.framing.scale - this.framingGoal.scale) > 5e-4;
    const busy = reframing || this.intro !== null || this.fly !== null || this.downAt !== null || this.background.rippling || time - this.lastActivity < IDLE_AFTER_S;
    this.frameParity ^= 1;
    if (!busy && this.frameParity) return;

    if (this.intro) this.stepIntro(dt);
    if (reframing) {
      const k = 1 - Math.exp(-dt * 8);
      this.framing.x += (this.framingGoal.x - this.framing.x) * k;
      this.framing.y += (this.framingGoal.y - this.framing.y) * k;
      this.framing.scale += (this.framingGoal.scale - this.framing.scale) * k;
      this.applyFraming();
    } else if (this.framing.x !== this.framingGoal.x || this.framing.y !== this.framingGoal.y || this.framing.scale !== this.framingGoal.scale) {
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
    const ease = this.reducedMotion.matches ? 1 : 1 - Math.exp(-dt * 4);
    for (const [side, e] of this.eyes) {
      if (Math.abs(e.rot[0] - e.goal[0]) < 0.05 && Math.abs(e.rot[1] - e.goal[1]) < 0.05) continue;
      e.rot = [e.rot[0] + (e.goal[0] - e.rot[0]) * ease, e.rot[1] + (e.goal[1] - e.rot[1]) * ease];
      // GLB frame is RAS: +z up, +x right. Turning toward the nose: the right eye's anterior pole (+y) goes to -x,
      // a positive rotation about +z; the left eye the opposite. Elevation is a positive rotation about +x.
      const toward = side === 'R' ? 1 : -1;
      const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(THREE.MathUtils.degToRad(e.rot[1]), 0, THREE.MathUtils.degToRad(toward * e.rot[0]), 'XYZ'));
      e.group.quaternion.copy(q);
      this.poke();
    }
    for (const m of this.muscles.values()) {
      if (Math.abs(m.k - m.goal) < 0.002) continue;
      m.k += (m.goal - m.k) * ease;
      const along = 1 - 0.12 * m.k, across = 1 + 0.22 * m.k;
      m.group.scale.set(m.axis.x ? along : across, m.axis.y ? along : across, m.axis.z ? along : across);
      this.poke();
    }
    for (const l of this.lenses.values()) {
      if (Math.abs(l.k - l.goal) < 0.002) continue;
      l.k += (l.goal - l.k) * ease;
      l.group.scale.set(1 - 0.08 * l.k, 1 + 0.35 * l.k, 1 - 0.08 * l.k); // thicker along the eye axis (+y), a little narrower
      this.poke();
    }
    for (const p of this.pupils.values()) {
      if (Math.abs(p.scale - p.goal) < 0.002) continue;
      p.scale += (p.goal - p.scale) * (this.reducedMotion.matches ? 1 : 1 - Math.exp(-dt * 4));
      p.group.scale.setScalar(p.scale);
      this.poke();
    }
    for (const j of this.joints.values()) {
      if (Math.abs(j.angle - j.goal) < 0.05) continue;
      const k = this.reducedMotion.matches ? 1 : 1 - Math.exp(-dt * 4);
      j.angle += (j.goal - j.angle) * k;
      const axis = new THREE.Vector3(...j.info.axis).normalize();
      j.group.quaternion.setFromAxisAngle(axis, THREE.MathUtils.degToRad(j.angle * j.info.flexSign));
      this.poke();
    }
    const seaTarget = this.bodyRevealed ? Math.min(this.seaGoal, BODY_CENTER.y - 900) : this.seaGoal;
    if (Math.abs(this.background.surfaceY - seaTarget) > 0.5) {
      const k = this.reducedMotion.matches ? 1 : 1 - Math.exp(-dt * 3);
      this.background.setLevel(this.background.surfaceY + (seaTarget - this.background.surfaceY) * k);
      sceneFloor.value = this.background.surfaceY;
      this.poke();
    }

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
