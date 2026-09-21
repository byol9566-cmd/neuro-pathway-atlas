import * as THREE from 'three';

const VERT = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

// uv.x runs along the tube. Everything past uReveal is hidden; bright dashes travel towards it.
const FRAG = /* glsl */ `
  uniform float uTime;
  uniform float uReveal;
  uniform float uDashes;
  uniform vec3 uColor;
  varying vec2 vUv;
  void main() {
    if (vUv.x > uReveal) discard;
    float wave = fract(vUv.x * uDashes - uTime * 0.9);
    float dash = smoothstep(0.0, 0.15, wave) * (1.0 - smoothstep(0.45, 0.6, wave));
    vec3 col = mix(uColor * 0.55, vec3(1.0), dash * 0.85);
    gl_FragColor = vec4(col, 0.55 + 0.45 * dash);
  }
`;

export class PathwayCurve {
  readonly object: THREE.Mesh;
  private readonly material: THREE.ShaderMaterial;
  /** fraction of the curve length reached at each route point */
  private readonly pointU: number[];
  private target = 0;

  constructor(points: THREE.Vector3[], radius = 0.7) {
    const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal');
    const length = curve.getLength();
    this.material = new THREE.ShaderMaterial({
      vertexShader: VERT,
      fragmentShader: FRAG,
      uniforms: {
        uTime: { value: 0 },
        uReveal: { value: 0 },
        uDashes: { value: Math.max(4, length / 9) },
        uColor: { value: new THREE.Color('#a0e7ff') }, // starlight accent: tracts themselves are yellow
      },
      transparent: true,
      depthTest: false, // the route must read through every solid structure it passes
      depthWrite: false,
    });
    const segments = Math.min(1200, Math.max(64, Math.round(length * 2)));
    this.object = new THREE.Mesh(new THREE.TubeGeometry(curve, segments, radius, 8, false), this.material);
    this.object.renderOrder = 100;

    // centripetal CatmullRom is not arc-length parameterised per control point, so measure it
    const cumulative = [0];
    for (let i = 1; i < points.length; i++) cumulative.push(cumulative[i - 1] + points[i].distanceTo(points[i - 1]));
    const total = cumulative[cumulative.length - 1] || 1;
    this.pointU = cumulative.map((c) => c / total);
  }

  /** Reveal the route up to route point `index` (-1 hides it). */
  revealTo(index: number) {
    this.target = index < 0 ? 0 : this.pointU[Math.min(index, this.pointU.length - 1)];
    // a route that ends on its very first point would otherwise be invisible
    if (index >= 0 && this.target === 0) this.target = 0.001;
  }

  update(time: number, dt: number) {
    const u = this.material.uniforms;
    u.uTime.value = time;
    const current = u.uReveal.value as number;
    u.uReveal.value = current > this.target ? this.target : Math.min(this.target, current + dt * 0.6);
  }

  dispose() {
    this.object.geometry.dispose();
    this.material.dispose();
  }
}
