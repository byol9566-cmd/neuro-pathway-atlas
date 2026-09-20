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
}

export interface Manifest {
  space: string;
  attribution: { atlas: string; title: string; citation: string; license: string; url: string }[];
  groups: Record<string, { name: LocalizedText; color: string }>;
  structures: ManifestStructure[];
  meshes: ManifestMesh[];
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
  structures: PathwayStructureRef[];
  missing?: LocalizedText;
}

export interface Pathway {
  id: string;
  category: string;
  name: LocalizedText;
  summary: LocalizedText;
  origin: LocalizedText;
  defaultOriginSide: OriginSide;
  reviewStatus: 'draft' | 'reviewed';
  steps: PathwayStep[];
  lesions: { level: LocalizedText; deficit: LocalizedText }[];
}
