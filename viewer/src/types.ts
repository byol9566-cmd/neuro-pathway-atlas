export type Side = 'L' | 'R' | 'M';
export type OriginSide = 'L' | 'R';
export type RelativeSide = 'ipsi' | 'contra';
export type Vec3 = [number, number, number];

export interface LocalizedText {
  ko: string;
  en?: string;
}

export interface ManifestMesh {
  id: string;
  structureId: string;
  side: Side;
  /** MNI-aligned RAS, mm */
  centroid: Vec3;
  bboxMin: Vec3;
  bboxMax: Vec3;
  volumeMm3: number;
  faces: number;
  /** true when the mesh is a stand-in ellipsoid rather than atlas-derived geometry */
  approx: boolean;
  /** Korean name of the Visible-Human-segmented organ this part was cut from by geometry (not segmented itself) */
  derived?: string;
  /** free-text caveat from the pipeline (e.g. the cord was re-posed to a vertical axis) */
  note?: string;
  centerline?: Vec3[];
}

export interface ManifestStructure {
  id: string;
  group: string;
  name: LocalizedText;
  tract: boolean;
  approx: boolean;
  atlas: string;
  /** atlas label ids merged into this structure (empty for outlines and non-NextBrain sources) */
  labels: number[];
  meshIds: string[];
  /** optional colour override (e.g. the brown iris inside the sensory-organ group) */
  color?: string;
}

/** a limb joint of the schematic body: rotating it about `axis` (RAS) through `pivot` moves `segment`
 *  and, through the chain of child joints, everything distal to it */
export interface ManifestJoint {
  id: string;
  joint: string;
  side: 'L' | 'R';
  name: LocalizedText;
  pivot: Vec3;
  axis: Vec3;
  /** +1 when a positive angle is flexion about +x, -1 when flexion is the other way (knee, ankle) */
  flexSign: number;
  segment: string;
  /** every mesh the joint moves: the bone, its skin piece, the muscles riding on it */
  segments?: string[];
  parent: string | null;
}

export interface Manifest {
  space: string;
  attribution: { atlas: string; title: string; citation: string; license: string; url: string }[];
  groups: Record<string, { name: LocalizedText; color: string }>;
  structures: ManifestStructure[];
  meshes: ManifestMesh[];
  joints?: ManifestJoint[];
}

/** what a pathway step does to the body: a joint flexes (positive degrees) or extends (negative),
 *  or a pupil constricts / dilates */
export interface StepEffect {
  joint?: string;
  side: RelativeSide;
  angle?: number;
  pupil?: 'constrict' | 'dilate';
  /** the eyeball turns: abduction/adduction about the vertical axis, elevation/depression about the lateral */
  eye?: 'abduct' | 'adduct' | 'elevate' | 'depress';
  /** the lens thickens for near vision */
  lens?: 'accommodate';
  /** a muscle of the step (structure id, or '*' for all of them) that relaxes or is only sensed, so it does
   *  not contract; every other mu-* structure of the step contracts */
  muscle?: string;
  action?: 'contract' | 'relax' | 'none';
}

export interface PathwayStructureRef {
  id: string;
  side: RelativeSide;
}

export interface PathwayStep {
  id: string;
  title: LocalizedText;
  description: LocalizedText;
  neuronOrder?: number;
  decussation?: boolean;
  transmitter?: string;
  structures: PathwayStructureRef[];
  missing?: LocalizedText;
  effects?: StepEffect[];
}

export interface Pathway {
  id: string;
  category: string;
  name: LocalizedText;
  summary: LocalizedText;
  origin: LocalizedText;
  defaultOriginSide: OriginSide;
  reviewStatus: 'draft' | 'reviewed';
  /** how the reviewer's dataset grounds it (lecture-grounded, lecture-hypothesis, ...) */
  evidenceStatus?: string;
  processType?: string;
  /** at least one step lights up a mesh; the others are text-only mechanisms */
  has3d?: boolean;
  steps: PathwayStep[];
  lesions: { level: LocalizedText; deficit: LocalizedText; side?: string }[];
}

export interface PathwayCategory {
  id: string;
  name: LocalizedText;
}
