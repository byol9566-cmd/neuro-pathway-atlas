import * as THREE from 'three';

export type MeshState = 'normal' | 'ghost' | 'involved' | 'active';

/** camera-to-orbit-target distance, shared by every ghost material */
export const ghostFocusDistance = { value: 500 };
/** 0..1 master fade used by the intro; shared by every ghost and halo material */
export const sceneReveal = { value: 1 };
/** world y of the mist sea: ghosts sink into it (the spinal cord runs far below the brain) */
export const sceneFloor = { value: -1e9 };

const GHOST_VERT = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vView;
  varying float vDepth;
  varying float vWorldY;
  #include <clipping_planes_pars_vertex>
  void main() {
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vWorldY = (modelMatrix * vec4(position, 1.0)).y;
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
  uniform float uReveal;
  uniform float uFloorY;
  varying vec3 vNormal;
  varying vec3 vView;
  varying float vDepth;
  varying float vWorldY;
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
    // close up, dozens of outlines cross the view at once: thin them so the subject stays the brightest thing
    fade *= mix(1.0, 0.55, zoomedIn);
    // whatever reaches below the mist sea dissolves into it over ~12 cm
    fade *= smoothstep(uFloorY - 120.0, uFloorY + 10.0, vWorldY);
    float alpha = ((uBase + uRim * rim) * fade + uHover * (0.1 + 0.3 * rim)) * uReveal;
    // the rim itself leans towards starlight so the outline reads as lit from behind
    vec3 color = mix(uColor, vec3(0.92, 0.95, 1.0), rim * 0.55 + uHover * 0.4);
    gl_FragColor = vec4(color, alpha);
  }
`;

export function ghostMaterial(color: THREE.Color, shell: boolean): THREE.ShaderMaterial {
  const tint = color.clone().lerp(new THREE.Color('#c9ced9'), shell ? 0.62 : 0.42);
  return new THREE.ShaderMaterial({
    vertexShader: GHOST_VERT,
    fragmentShader: GHOST_FRAG,
    uniforms: {
      uColor: { value: tint },
      uBase: { value: shell ? 0.022 : 0.006 },
      uRim: { value: shell ? 0.5 : 0.13 },
      uPower: { value: shell ? 2.3 : 2.6 },
      uHover: { value: 0 },
      uFocusDistance: ghostFocusDistance,
      uReveal: sceneReveal,
      uFloorY: sceneFloor,
    },
    transparent: true,
    depthWrite: false,
    side: THREE.FrontSide,
    clipping: true, // honour the section plane's cut (see AtlasScene.setSectionCut)
  });
}

const HALO_VERT = /* glsl */ `
  uniform float uSize;
  varying float vFacing;
  #include <clipping_planes_pars_vertex>
  void main() {
    // inflate along the normal; with BackSide rendering only the band outside the silhouette shows
    vec4 mvPosition = modelViewMatrix * vec4(position + normal * uSize, 1.0);
    vFacing = abs(dot(normalize(normalMatrix * normal), normalize(-mvPosition.xyz)));
    gl_Position = projectionMatrix * mvPosition;
    #include <clipping_planes_vertex>
  }
`;

const HALO_FRAG = /* glsl */ `
  uniform vec3 uColor;
  uniform float uStrength;
  uniform float uReveal;
  varying float vFacing;
  #include <clipping_planes_pars_fragment>
  void main() {
    #include <clipping_planes_fragment>
    // brightest right next to the structure, falling to nothing at the inflated shell's own edge
    gl_FragColor = vec4(uColor, uStrength * pow(vFacing, 1.6) * uReveal);
  }
`;

/** Cheap glow for active structures: an inflated, additive back-face shell. No post-processing pass. */
export function haloMaterial(color: THREE.Color, sizeMm: number): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: HALO_VERT,
    fragmentShader: HALO_FRAG,
    uniforms: {
      uColor: { value: color.clone().lerp(new THREE.Color('#a0e7ff'), 0.45) },
      uSize: { value: sizeMm },
      uStrength: { value: 0.5 },
      uReveal: sceneReveal,
    },
    transparent: true,
    depthWrite: false,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    clipping: true,
  });
}

export function solidMaterial(color: THREE.Color): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.0 });
}

const WHITE = new THREE.Color('#ffffff');

/** Per-frame look of a solid material for a given state; `pulse` is 0..1. */
export function applySolidState(
  mat: THREE.MeshStandardMaterial, base: THREE.Color, state: MeshState, hovered: boolean, pulse: number,
) {
  mat.color.copy(base);
  if (state === 'involved') mat.color.lerp(WHITE, 0.15).multiplyScalar(0.62);
  const glow = state === 'active' ? 0.35 + 0.3 * pulse : 0;
  mat.emissive.copy(base).multiplyScalar(glow + (hovered ? 0.35 : 0));
}
