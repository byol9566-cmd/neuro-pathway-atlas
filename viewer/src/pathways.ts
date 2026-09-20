import type { ManifestMesh, OriginSide, Pathway, PathwayStep, RelativeSide, Vec3 } from './types';

export function resolveSide(relative: RelativeSide, origin: OriginSide): OriginSide {
  if (relative === 'ipsi') return origin;
  return origin === 'L' ? 'R' : 'L';
}

type MeshLookup = Map<string, ManifestMesh>;

/** Mesh for a structure on the requested side; midline-only structures fall back to their single mesh. */
export function meshFor(structureId: string, side: OriginSide, meshes: MeshLookup): ManifestMesh | undefined {
  return meshes.get(`${structureId}.${side}`) ?? meshes.get(`${structureId}.M`);
}

export function stepMeshIds(step: PathwayStep, origin: OriginSide, meshes: MeshLookup): string[] {
  const ids: string[] = [];
  for (const ref of step.structures) {
    const mesh = meshFor(ref.id, resolveSide(ref.side, origin), meshes);
    if (!mesh) throw new Error(`pathway step ${step.id}: no mesh for ${ref.id}`);
    ids.push(mesh.id);
  }
  return ids;
}

export function pathwayMeshIds(pathway: Pathway, origin: OriginSide, meshes: MeshLookup): Set<string> {
  return new Set(pathway.steps.flatMap((s) => stepMeshIds(s, origin, meshes)));
}

const dist2 = (a: Vec3, b: Vec3) => (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2;

export interface PathwayRoute {
  /** RAS mm */
  points: Vec3[];
  /** index of the last route point belonging to each step (or -1 while no point exists yet) */
  stepEnd: number[];
}

/**
 * Polyline the signal follows: nuclei contribute their centroid, tracts and other elongated structures
 * their centerline, flipped so that it continues from wherever the route currently ends. The very
 * first centerline has nothing before it, so it is oriented to end near whatever comes next.
 */
export function pathwayRoute(pathway: Pathway, origin: OriginSide, meshes: MeshLookup): PathwayRoute {
  const pieces = pathway.steps.map((step) =>
    stepMeshIds(step, origin, meshes).map((id): Vec3[] => {
      const mesh = meshes.get(id)!;
      return mesh.centerline && mesh.centerline.length >= 2 ? mesh.centerline : [mesh.centroid];
    }),
  );
  const flat = pieces.flat();
  const nearestEnd = (from: Vec3, piece: Vec3[]) => Math.min(dist2(from, piece[0]), dist2(from, piece[piece.length - 1]));

  const points: Vec3[] = [];
  const stepEnd: number[] = [];
  let seen = 0;
  for (const stepPieces of pieces) {
    for (const piece of stepPieces) {
      const last = points[points.length - 1];
      const next = flat[seen + 1];
      const head = piece[0];
      const tail = piece[piece.length - 1];
      let reversed = false;
      if (last !== undefined) reversed = dist2(last, tail) < dist2(last, head);
      else if (next !== undefined) reversed = nearestEnd(head, next) < nearestEnd(tail, next);
      points.push(...(reversed ? [...piece].reverse() : piece));
      seen++;
    }
    stepEnd.push(points.length - 1);
  }
  return { points, stepEnd };
}
