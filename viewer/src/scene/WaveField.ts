import * as THREE from 'three';
import { GPUComputationRenderer, type Variable } from 'three/examples/jsm/misc/GPUComputationRenderer.js';

// A height field stepped on the GPU: each texel keeps its height (x) and its previous height (y), and
// the classic two-buffer scheme `next = (n + s + e + w) / 2 - previous` propagates waves at one fixed
// speed. Unlike analytic rings these collide, interfere and linger before fading.
const STEP = /* glsl */ `
  uniform vec4 uDrop;      // xy: position in uv, z: strength (0 = no drop this step), w: radius in uv
  uniform float uDamping;

  void main() {
    vec2 cell = 1.0 / resolution.xy;
    vec2 uv = gl_FragCoord.xy * cell;
    vec4 here = texture2D(heightmap, uv);
    float around = texture2D(heightmap, uv + vec2(cell.x, 0.0)).x + texture2D(heightmap, uv - vec2(cell.x, 0.0)).x
                 + texture2D(heightmap, uv + vec2(0.0, cell.y)).x + texture2D(heightmap, uv - vec2(0.0, cell.y)).x;
    float next = (around * 0.5 - here.y) * uDamping;

    // a drop pushes the surface down in a small Gaussian dimple
    vec2 d = uv - uDrop.xy;
    next -= uDrop.z * exp(-dot(d, d) / max(uDrop.w * uDrop.w, 1e-6));

    // soak waves up near the border instead of bouncing them back into view
    float edge = min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y));
    next *= mix(0.9, 1.0, smoothstep(0.0, 0.08, edge));

    gl_FragColor = vec4(next, here.x, 0.0, 1.0);
  }
`;

const STEPS_PER_SECOND = 60;
const ZERO = new THREE.Vector4();

/** Square wave simulation; what the square is mapped onto (here: a patch of the mist sea) is up to the caller. */
export class WaveField {
  /** 1x1 black until the simulation exists, so shaders can always sample it */
  texture: THREE.Texture;
  readonly texel: number;
  private readonly gpu: GPUComputationRenderer | null = null;
  private readonly variable: Variable | null = null;
  private pending: THREE.Vector4[] = [];
  private carry = 0;
  /** seconds of visible motion left; lets the render loop go back to idle once the surface is still */
  private energy = 0;

  constructor(renderer: THREE.WebGLRenderer, size = 384, damping = 0.991) {
    const blank = new THREE.DataTexture(new Uint8Array([0, 0, 0, 255]), 1, 1);
    blank.needsUpdate = true;
    this.texture = blank;
    this.texel = 1 / size;

    const gpu = new GPUComputationRenderer(size, size, renderer);
    // half floats: rendering to and linearly filtering them is core WebGL2, no float extensions needed
    gpu.setDataType(THREE.HalfFloatType);
    const variable = gpu.addVariable('heightmap', STEP, gpu.createTexture());
    gpu.setVariableDependencies(variable, [variable]);
    variable.minFilter = variable.magFilter = THREE.LinearFilter;
    variable.wrapS = variable.wrapT = THREE.ClampToEdgeWrapping;
    Object.assign(variable.material.uniforms, { uDrop: { value: new THREE.Vector4() }, uDamping: { value: damping } });
    const error = gpu.init();
    if (error) {
      console.warn('wave field disabled:', error);
      return;
    }
    this.gpu = gpu;
    this.variable = variable;
  }

  get active() { return this.energy > 0; }

  /** Disturb the surface at (u, v) in 0..1; `radius` is in the same units. */
  drop(u: number, v: number, strength: number, radius: number) {
    if (!this.gpu || u < 0 || u > 1 || v < 0 || v > 1) return;
    if (this.pending.length < 24) this.pending.push(new THREE.Vector4(u, v, strength, radius));
    this.energy = 7;
  }

  update(dt: number) {
    if (!this.gpu || !this.variable || !this.active) return;
    this.energy -= dt;
    this.carry += dt * STEPS_PER_SECOND;
    const steps = Math.min(4, Math.floor(this.carry));
    this.carry -= steps;
    const drop = this.variable.material.uniforms.uDrop.value as THREE.Vector4;
    for (let i = 0; i < steps; i++) {
      drop.copy(this.pending.shift() ?? ZERO);
      this.gpu.compute();
    }
    this.texture = this.gpu.getCurrentRenderTarget(this.variable).texture;
  }

  dispose() {
    if (this.gpu) this.gpu.dispose(); // owns the render targets `texture` points into
    else this.texture.dispose();

  }
}

