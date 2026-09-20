import * as THREE from 'three';

export type MeshState = 'normal' | 'ghost' | 'involved' | 'active';

const GHOST_VERT = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vView;
  varying float vDepth;
  #include <clipping_planes_pars_vertex>
  void main() {
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vNormal = normalize(normalMatrix * normal);
    vView = normalize(-mvPosition.xyz);
    vDepth = -mvPosition.z;
    gl_Position = projectionMatrix * mvPosition;
    #include <clipping_planes_vertex>
  }
`;

// Alpha comes almost entirely from the silhouette (fresnel) term, so dozens of stacked ghosts stay
// readable and the missing depth sort is not noticeable: faces seen head-on contribute ~uBase.
const GHOST_FRAG = /* glsl */ `
  uniform vec3 uColor;
  uniform float uBase;
  uniform float uRim;
  uniform float uPower;
  uniform float uHover;
  uniform float uFocusDistance;
  varying vec3 vNormal;
  varying vec3 vView;
  varying float vDepth;
  #include <clipping_planes_pars_fragment>
  void main() {
    #include <clipping_planes_fragment>
    float facing = abs(dot(normalize(vNormal), normalize(vView)));
    float rim = pow(1.0 - facing, uPower);
    // Zoomed in, the camera sits inside the outlines and every layer between it and the subject
    // is seen at a grazing angle, which reads as fog. Fade what lies in front of the focus point;
    // zoomed out (whole brain in view) the fade is switched off so the near outline stays visible.
    float zoomedIn = 1.0 - smoothstep(180.0, 420.0, uFocusDistance);
    float behindFocus = smoothstep(0.55 * uFocusDistance, 1.05 * uFocusDistance, vDepth);
    float fade = mix(1.0, mix(0.06, 1.0, behindFocus), zoomedIn);
    float alpha = (uBase + uRim * rim) * fade + uHover * (0.1 + 0.3 * rim);
    gl_FragColor = vec4(mix(uColor, vec3(1.0), uHover * 0.4), alpha);
  }
`;

/** camera-to-orbit-target distance, shared by every ghost material */
export const ghostFocusDistance = { value: 500 };

export function ghostMaterial(color: THREE.Color, shell: boolean): THREE.ShaderMaterial {
  const tint = color.clone().lerp(new THREE.Color('#b8c4d4'), shell ? 0.7 : 0.45);
  return new THREE.ShaderMaterial({
    vertexShader: GHOST_VERT,
    fragmentShader: GHOST_FRAG,
    uniforms: {
      uColor: { value: tint },
      uBase: { value: shell ? 0.025 : 0.006 },
      uRim: { value: shell ? 0.42 : 0.13 },
      uPower: { value: shell ? 2.2 : 2.6 },
      uHover: { value: 0 },
      uFocusDistance: ghostFocusDistance,
    },
    transparent: true,
    depthWrite: false,
    side: THREE.FrontSide,
    clipping: true, // honour the section plane's cut (see AtlasScene.setSectionCut)
  });
}

export function solidMaterial(color: THREE.Color): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0.0 });
}

/** Per-frame look of a solid material for a given state; `pulse` is 0..1. */
export function applySolidState(
  mat: THREE.MeshStandardMaterial, base: THREE.Color, state: MeshState, hovered: boolean, pulse: number,
) {
  mat.color.copy(base);
  if (state === 'involved') mat.color.lerp(new THREE.Color('#ffffff'), 0.15).multiplyScalar(0.62);
  const glow = state === 'active' ? 0.35 + 0.3 * pulse : 0;
  mat.emissive.copy(base).multiplyScalar(glow + (hovered ? 0.35 : 0));
}
