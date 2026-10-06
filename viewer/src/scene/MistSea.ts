import * as THREE from 'three';
import { WaveField } from './WaveField';

// The backdrop, after the reference the owner picked (mesh3d.gallery/the-state-of-the-gallery): not a
// sky but a sea. A huge horizontal sheet of mist lies below the brain and rolls in slow swells towards
// a horizon; motes float above it, thicker in the distance; and a click on the sheet leaves fine contour
// ripples that spread and fade. (It used to answer the moving pointer too; the owner found that too busy.)

/** World-space swell height in -1..1, shared by the sheet and by the motes that float on it. */
const SWELL = /* glsl */ `
  uniform float uFlow;   // how far the swell pattern has travelled (mm)
  uniform float uMorph;  // slow evolution of the pattern itself
  uniform vec2 uFlowDir;

  float hash2(vec2 p) {
    p = fract(p * vec2(0.1031, 0.1030));
    p += dot(p, p.yx + 33.33);
    return fract((p.x + p.y) * p.x);
  }
  float vnoise(vec3 x) {
    vec3 i = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    float n = i.x + i.y * 57.0 + i.z * 113.0;
    #define H(o) fract(sin(n + o) * 43758.5453)
    return mix(mix(mix(H(0.0), H(1.0), f.x), mix(H(57.0), H(58.0), f.x), f.y),
               mix(mix(H(113.0), H(114.0), f.x), mix(H(170.0), H(171.0), f.x), f.y), f.z);
  }
  float swell(vec2 xz, float seed) {
    vec2 p = (xz - uFlowDir * uFlow) * 0.0021;
    float h = vnoise(vec3(p, uMorph + seed)) * 0.62
            + vnoise(vec3(p * 2.3 + 7.1, uMorph * 1.3 + seed)) * 0.27
            + vnoise(vec3(p * 5.1 - 3.7, uMorph * 1.7 + seed)) * 0.11;
    return h * 2.0 - 1.0;
  }
`;

const SHEET_VERT = /* glsl */ `
  ${SWELL}
  uniform float uSeed;
  uniform float uAmplitude;
  uniform sampler2D uWaves;
  uniform vec3 uPatch;   // xz centre and size (mm) of the square the wave field covers
  varying vec3 vWorld;
  varying float vHeight;
  varying vec2 vPatchUv;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vHeight = swell(world.xz, uSeed);
    vPatchUv = (world.xz - uPatch.xy) / uPatch.z + 0.5;
    float ripple = texture2D(uWaves, clamp(vPatchUv, 0.0, 1.0)).x;
    world.y += vHeight * uAmplitude + ripple * 5.0;
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const SHEET_FRAG = /* glsl */ `
  precision highp float;
  uniform vec3 uDeep;
  uniform vec3 uBright;
  uniform vec3 uCenter;
  uniform float uLevel;
  uniform float uBrightness;
  uniform float uLineFrequency;
  uniform sampler2D uWaves;
  uniform float uWaveTexel;
  varying vec3 vWorld;
  varying float vHeight;
  varying vec2 vPatchUv;

  void main() {
    vec3 normal = normalize(cross(dFdx(vWorld), dFdy(vWorld)));
    vec3 toEye = cameraPosition - vWorld;
    float eyeDistance = length(toEye);
    // mist seen edge-on piles up: that is what makes the bright band along the horizon and the lit crests
    float graze = pow(1.0 - abs(dot(normal, toEye / eyeDistance)), 2.6);
    float ridge = smoothstep(0.3, 0.95, vHeight * 0.5 + 0.5);
    float density = 0.26 + 0.5 * ridge * ridge + 0.3 * graze * (0.3 + ridge); // readable from above, not only edge-on

    float r = length(vWorld.xz - uCenter.xz);
    float fade = (1.0 - smoothstep(600.0, 2500.0, r))    // dissolve into the dark well before the sheet's edge
               * smoothstep(40.0, 300.0, eyeDistance)     // nothing smeared across the lens
               * mix(0.6, 1.0, smoothstep(140.0, 460.0, r)); // a little thinner right under the subject
    vec3 color = mix(uDeep, uBright, clamp(ridge * 0.75 + graze * 0.5, 0.0, 1.0));

    // pointer ripples, drawn as contour lines of the wave height: many hair-thin rings from one smooth wave
    float inside = step(0.0, vPatchUv.x) * step(vPatchUv.x, 1.0) * step(0.0, vPatchUv.y) * step(vPatchUv.y, 1.0);
    float h = texture2D(uWaves, vPatchUv).x;
    vec2 slope = vec2(texture2D(uWaves, vPatchUv + vec2(uWaveTexel, 0.0)).x - texture2D(uWaves, vPatchUv - vec2(uWaveTexel, 0.0)).x,
                      texture2D(uWaves, vPatchUv + vec2(0.0, uWaveTexel)).x - texture2D(uWaves, vPatchUv - vec2(0.0, uWaveTexel)).x);
    float envelope = sqrt(h * h + dot(slope, slope) * 2.0);
    float phase = h * uLineFrequency;
    float width = clamp(fwidth(phase) * 1.2, 0.04, 0.5);            // keep lines ~1px however steep the wave
    float line = 1.0 - smoothstep(0.0, width, abs(fract(phase) - 0.5));
    line *= smoothstep(0.008, 0.04, envelope) * inside * (1.0 - smoothstep(0.35, 0.6, fwidth(phase)));
    vec3 film = 0.5 + 0.5 * cos(6.28318 * (phase * 0.27 + vec3(0.0, 0.33, 0.67))); // a breath of oil-film hue, no more
    color = mix(color, mix(uBright * 1.3, film, 0.1), line * 0.55);
    density += line * 0.22 + envelope * 0.35 * inside;

    // film grain, like the reference's fine noise in the glow
    float grain = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    density *= 0.88 + 0.24 * grain;

    gl_FragColor = vec4(color, density * fade * uLevel * uBrightness);
  }
`;

const MOTE_VERT = /* glsl */ `
  ${SWELL}
  attribute float aLift;
  attribute float aSize;
  attribute float aPhase;
  uniform float uTime;
  uniform float uAmplitude;
  uniform float uSeaLevel;
  uniform float uRadius;
  uniform vec3 uCenter;
  uniform float uPixelRatio;
  uniform float uViewHeight;
  uniform float uCeiling;
  uniform float uSubjectRadius;
  varying float vAlpha;
  varying float vBlur;
  void main() {
    // motes ride the flow and wrap around, so the field never runs out
    vec2 xz = position.xz + uFlowDir * uFlow * 1.6;
    xz = mod(xz + uRadius, 2.0 * uRadius) - uRadius;
    float surface = uSeaLevel + swell(xz + uCenter.xz, 0.0) * uAmplitude;
    float bob = sin(uTime * (0.3 + aPhase) + aPhase * 30.0) * 5.0;
    float height = surface + aLift + bob;
    vec4 mv = viewMatrix * vec4(xz.x + uCenter.x, height, xz.y + uCenter.z, 1.0);
    gl_Position = projectionMatrix * mv;
    float depth = max(-mv.z, 1.0);
    float px = aSize * uPixelRatio * uViewHeight / depth;
    gl_PointSize = clamp(px, 1.0, 46.0 * uPixelRatio);
    float r = length(xz);
    // close motes are big, soft and faint; distant ones are pin-sharp
    vBlur = smoothstep(7.0, 28.0, px / uPixelRatio);
    vAlpha = (1.0 - smoothstep(0.7, 1.0, r / uRadius)) * smoothstep(30.0, 170.0, depth)
           * mix(1.0, 0.3, vBlur) * (0.72 + 0.28 * sin(uTime * (0.5 + aPhase) + aPhase * 50.0));
    // the subject stays clear: nothing floats as high as its underside, and nothing is drawn on a line
    // of sight that passes through it, in front of it or behind
    vec3 subject = (viewMatrix * vec4(uCenter, 1.0)).xyz;
    vec3 sight = normalize(mv.xyz);
    float miss = length(subject - sight * dot(subject, sight));
    vAlpha *= (1.0 - smoothstep(uCeiling - 30.0, uCeiling, height)) * smoothstep(uSubjectRadius, uSubjectRadius * 1.45, miss);
  }
`;

const MOTE_FRAG = /* glsl */ `
  precision mediump float;
  uniform vec3 uColor;
  uniform float uLevel;
  varying float vAlpha;
  varying float vBlur;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float disc = 1.0 - smoothstep(mix(0.55, 0.0, vBlur), 1.0, d);
    gl_FragColor = vec4(uColor, disc * vAlpha * uLevel);
  }
`;

/** How strong the backdrop stays once the entrance is over. */
export const SETTLED_LEVEL = 0.85;

const SEA_DROP = 143; // mm below the brain's centre: swells never reach the brainstem
const SUBJECT_UNDERSIDE = 82; // mm below the centre: motes fade out before they reach this height
const SUBJECT_RADIUS = 110; // mm: lines of sight passing closer to the centre than this carry no motes
const SHEET_RADIUS = 2800;
const PATCH_SIZE = 1500; // mm: the square around the subject where the pointer can stir the surface
const BASE_FLOW = 26; // mm per second

export class MistSea {
  readonly group = new THREE.Group();
  /** 0..1 master brightness, driven by the intro */
  level = SETTLED_LEVEL;
  private readonly waves: WaveField;
  private readonly sheets: THREE.ShaderMaterial[] = [];
  private readonly motes: THREE.ShaderMaterial;
  private readonly plane: THREE.Plane;
  private readonly shared = { uFlow: { value: 0 }, uMorph: { value: 0 }, uFlowDir: { value: new THREE.Vector2(0.78, 0.62) } };
  private readonly hit = new THREE.Vector3();
  private surgeLeft = 0;

  /** world y of the resting surface */
  readonly seaLevel: number;
  /** world y of the surface right now (it sinks to uncover the body when something below is in focus) */
  surfaceY: number;
  private readonly sheetMeshes: THREE.Mesh[] = [];
  private readonly sheetOffsets: number[] = [];

  constructor(private readonly center: THREE.Vector3, renderer: THREE.WebGLRenderer) {
    this.waves = new WaveField(renderer, 384, 0.978); // fades within a couple of seconds
    const seaLevel = center.y - SEA_DROP;
    this.seaLevel = seaLevel;
    this.surfaceY = seaLevel;
    this.plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -seaLevel);

    const geometry = new THREE.PlaneGeometry(SHEET_RADIUS * 2, SHEET_RADIUS * 2, 300, 300).rotateX(-Math.PI / 2);
    // two sheets a little apart, out of step with each other: the folds overlap like veils
    for (const [seed, offset, amplitude, brightness] of [[0, 0, 46, 1], [19.7, -34, 60, 0.55]]) {
      const material = new THREE.ShaderMaterial({
        vertexShader: SHEET_VERT,
        fragmentShader: SHEET_FRAG,
        uniforms: {
          ...this.shared,
          uSeed: { value: seed },
          uAmplitude: { value: amplitude },
          uBrightness: { value: brightness },
          uLevel: { value: 1 },
          uDeep: { value: new THREE.Color('#34353a') },
          uBright: { value: new THREE.Color('#e6e8ec') },
          uCenter: { value: center.clone() },
          uPatch: { value: new THREE.Vector3(center.x, center.z, PATCH_SIZE) },
          uWaves: { value: this.waves.texture },
          uWaveTexel: { value: this.waves.texel },
          uLineFrequency: { value: 30 },
        },
        transparent: true,
        depthWrite: false,
        side: THREE.DoubleSide,
        blending: THREE.AdditiveBlending,
      });
      const sheet = new THREE.Mesh(geometry, material);
      sheet.position.set(center.x, seaLevel + offset, center.z);
      sheet.frustumCulled = false;
      sheet.renderOrder = -800;
      sheet.raycast = () => {};
      this.sheets.push(material);
      this.sheetMeshes.push(sheet);
      this.sheetOffsets.push(offset);
      this.group.add(sheet);
    }

    const count = 42000;
    const radius = 1500;
    const position = new Float32Array(count * 3);
    const lift = new Float32Array(count);
    const size = new Float32Array(count);
    const phase = new Float32Array(count);
    let s = 1234567;
    const rand = () => ((s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296);
    for (let i = 0; i < count; i++) {
      position.set([(rand() * 2 - 1) * radius, 0, (rand() * 2 - 1) * radius], i * 3);
      lift[i] = 4 + 90 * rand() ** 2.6; // most hug the surface, a few drift up, none as high as the subject
      size[i] = 1.7 + 3.0 * rand() ** 2.4; // mostly pin-points, now and then a bigger one
      phase[i] = rand();
    }
    const moteGeometry = new THREE.BufferGeometry();
    moteGeometry.setAttribute('position', new THREE.BufferAttribute(position, 3));
    moteGeometry.setAttribute('aLift', new THREE.BufferAttribute(lift, 1));
    moteGeometry.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
    moteGeometry.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
    this.motes = new THREE.ShaderMaterial({
      vertexShader: MOTE_VERT,
      fragmentShader: MOTE_FRAG,
      uniforms: {
        ...this.shared,
        uTime: { value: 0 },
        uAmplitude: { value: 46 },
        uSeaLevel: { value: seaLevel },
        uRadius: { value: radius },
        uCenter: { value: center.clone() },
        uPixelRatio: { value: 1 },
        uViewHeight: { value: 900 },
        uCeiling: { value: center.y - SUBJECT_UNDERSIDE },
        uSubjectRadius: { value: SUBJECT_RADIUS },
        uColor: { value: new THREE.Color('#f3f4f6') },
        uLevel: { value: 1 },
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const points = new THREE.Points(moteGeometry, this.motes);
    points.frustumCulled = false;
    points.renderOrder = -700;
    points.raycast = () => {};
    this.group.add(points);
  }

  /** True while the surface is still moving from a touch: keep rendering at full rate. */
  get rippling() { return this.waves.active || this.surgeLeft > 0; }

  /** A click on the sea along `ray`: a ring where it landed, and the whole sea rushes towards the viewer for a moment. */
  surge(ray: THREE.Ray) {
    if (!ray.intersectPlane(this.plane, this.hit)) return;
    this.waves.drop((this.hit.x - this.center.x) / PATCH_SIZE + 0.5, (this.hit.z - this.center.z) / PATCH_SIZE + 0.5, 0.22, 0.012);
    this.surgeLeft = 1.8;
  }

  /** One ring from directly under the subject (the brain's arrival). */
  centerRipple() {
    this.waves.drop(0.5, 0.5, 0.4, 0.03);
  }

  /** `time` should stand still when the user prefers reduced motion. */
  /** Move the surface to world y (the sheets, the hit plane and the motes follow). */
  setLevel(y: number) {
    if (y === this.surfaceY) return;
    this.surfaceY = y;
    this.sheetMeshes.forEach((sheet, i) => { sheet.position.y = y + this.sheetOffsets[i]; });
    this.plane.constant = -y;
    this.motes.uniforms.uSeaLevel.value = y;
  }

  update(time: number, dt: number, pixelRatio: number, viewHeight: number) {
    this.waves.update(dt);
    // the rush: flow speeds up sharply, then eases back
    const rush = this.surgeLeft > 0 ? Math.sin((1 - this.surgeLeft / 1.8) * Math.PI) ** 2 * 520 : 0;
    this.surgeLeft = Math.max(0, this.surgeLeft - dt);
    this.shared.uFlow.value += dt * (BASE_FLOW + rush);
    this.shared.uMorph.value = time * 0.05;
    for (const sheet of this.sheets) {
      sheet.uniforms.uLevel.value = this.level;
      sheet.uniforms.uWaves.value = this.waves.texture;
    }
    const m = this.motes.uniforms;
    m.uTime.value = time;
    m.uPixelRatio.value = pixelRatio;
    m.uViewHeight.value = viewHeight;
    m.uLevel.value = this.level;
  }
}
