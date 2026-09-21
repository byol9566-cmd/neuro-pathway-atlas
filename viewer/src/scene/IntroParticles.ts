import * as THREE from 'three';

const VERT = /* glsl */ `
  attribute vec3 aStart;
  attribute float aDelay;
  attribute float aSize;
  uniform float uProgress;
  uniform float uPixelRatio;
  uniform vec3 uCenter;
  varying float vAlpha;
  void main() {
    float t = clamp((uProgress - aDelay) / (1.0 - 0.4), 0.0, 1.0);
    float e = 1.0 - pow(1.0 - t, 4.0); // ease-out: fast approach, gentle settle
    vec3 p = mix(aStart, position, e);
    // unwind a slow swirl around the vertical axis as the point arrives
    float a = (1.0 - e) * 1.4;
    vec3 q = p - uCenter;
    p = uCenter + vec3(q.x * cos(a) - q.z * sin(a), q.y, q.x * sin(a) + q.z * cos(a));
    vec4 mvPosition = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mvPosition;
    gl_PointSize = aSize * uPixelRatio * (1.0 + 1.6 * (1.0 - e));
    vAlpha = smoothstep(0.0, 0.12, t) * mix(0.35, 1.0, e);
  }
`;

const FRAG = /* glsl */ `
  precision mediump float;
  uniform float uOpacity;
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float disc = 1.0 - smoothstep(0.2, 1.0, d);
    gl_FragColor = vec4(vec3(0.93, 0.95, 1.0), disc * vAlpha * uOpacity);
  }
`;

/**
 * Points that start scattered in space and settle onto the surface of the given meshes.
 * `uProgress` 0..1 drives the convergence, `uOpacity` fades the cloud out once the real meshes show.
 */
export class IntroParticles {
  readonly points: THREE.Points;
  private readonly material: THREE.ShaderMaterial;

  constructor(meshes: THREE.Mesh[], center: THREE.Vector3, count = 9000) {
    const total = meshes.reduce((n, m) => n + m.geometry.attributes.position.count, 0);
    const target = new Float32Array(count * 3);
    const start = new Float32Array(count * 3);
    const delay = new Float32Array(count);
    const size = new Float32Array(count);
    const v = new THREE.Vector3();
    let written = 0;
    for (const mesh of meshes) {
      const pos = mesh.geometry.attributes.position;
      const share = Math.min(count - written, Math.round((count * pos.count) / total));
      for (let i = 0; i < share; i++, written++) {
        // vertices may be quantised and the mesh sits under rotated parents: go through the world matrix
        v.fromBufferAttribute(pos, Math.floor(Math.random() * pos.count)).applyMatrix4(mesh.matrixWorld);
        target.set([v.x, v.y, v.z], written * 3);
        const u = Math.random() * 2 - 1;
        const phi = Math.random() * Math.PI * 2;
        const r = 320 + Math.random() * 520;
        const k = Math.sqrt(1 - u * u);
        start.set([center.x + r * k * Math.cos(phi), center.y + r * u * 0.7, center.z + r * k * Math.sin(phi)], written * 3);
        delay[written] = Math.random() * 0.4;
        size[written] = 1.4 + Math.random() * 1.8;
      }
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(target.subarray(0, written * 3), 3));
    geometry.setAttribute('aStart', new THREE.BufferAttribute(start.subarray(0, written * 3), 3));
    geometry.setAttribute('aDelay', new THREE.BufferAttribute(delay.subarray(0, written), 1));
    geometry.setAttribute('aSize', new THREE.BufferAttribute(size.subarray(0, written), 1));
    this.material = new THREE.ShaderMaterial({
      vertexShader: VERT,
      fragmentShader: FRAG,
      uniforms: { uProgress: { value: 0 }, uOpacity: { value: 1 }, uPixelRatio: { value: 1 }, uCenter: { value: center.clone() } },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.points = new THREE.Points(geometry, this.material);
    this.points.frustumCulled = false;
    this.points.renderOrder = 40;
  }

  set(progress: number, opacity: number, pixelRatio: number) {
    const u = this.material.uniforms;
    u.uProgress.value = progress;
    u.uOpacity.value = opacity;
    u.uPixelRatio.value = pixelRatio;
  }

  dispose() {
    this.points.geometry.dispose();
    this.material.dispose();
  }
}
