import { describe, expect, it } from 'vitest';
import pathwaysJson from '../../content/pathways.json';
import structuresJson from '../../content/structures.json';
import { meshFor, pathwayMeshIds, pathwayRoute, resolveSide, stepMeshIds } from '../src/pathways';
import type { ManifestMesh, Pathway, Vec3 } from '../src/types';

function mesh(id: string, centroid: Vec3, centerline?: Vec3[]): ManifestMesh {
  const [structureId, side] = id.split('.');
  return {
    id, structureId, side: side as ManifestMesh['side'], centroid,
    bboxMin: centroid, bboxMax: centroid, volumeMm3: 1, faces: 1, approx: false, centerline,
  };
}

const lookup = (...meshes: ManifestMesh[]) => new Map(meshes.map((m) => [m.id, m]));

const crossing: Pathway = {
  id: 'p', category: 'test', name: { ko: 'p' }, summary: { ko: '' }, origin: { ko: '' },
  defaultOriginSide: 'R', reviewStatus: 'draft', lesions: [],
  steps: [
    { id: 's1', title: { ko: '' }, description: { ko: '' }, structures: [{ id: 'nuc', side: 'ipsi' }] },
    { id: 's2', title: { ko: '' }, description: { ko: '' }, structures: [] },
    { id: 's3', title: { ko: '' }, description: { ko: '' }, structures: [{ id: 'tract', side: 'contra' }] },
  ],
};

describe('side resolution', () => {
  it('maps ipsi/contra relative to the origin side', () => {
    expect(resolveSide('ipsi', 'L')).toBe('L');
    expect(resolveSide('contra', 'L')).toBe('R');
    expect(resolveSide('contra', 'R')).toBe('L');
  });

  it('falls back to a midline mesh', () => {
    const meshes = lookup(mesh('raphe.M', [0, 0, 0]));
    expect(meshFor('raphe', 'L', meshes)?.id).toBe('raphe.M');
  });

  it('flips every mesh when the origin side flips', () => {
    const meshes = lookup(mesh('nuc.L', [-1, 0, 0]), mesh('nuc.R', [1, 0, 0]), mesh('tract.L', [-1, 0, 5]), mesh('tract.R', [1, 0, 5]));
    expect([...pathwayMeshIds(crossing, 'R', meshes)]).toEqual(['nuc.R', 'tract.L']);
    expect([...pathwayMeshIds(crossing, 'L', meshes)]).toEqual(['nuc.L', 'tract.R']);
  });

  it('reports unknown structures instead of silently skipping them', () => {
    expect(() => stepMeshIds(crossing.steps[0], 'L', lookup())).toThrow(/nuc/);
  });
});

describe('route', () => {
  it('orients a tract centerline to continue from the previous point', () => {
    const line: Vec3[] = [[-1, 0, 30], [-1, 0, 20], [-1, 0, 10]]; // stored top-down
    const meshes = lookup(mesh('nuc.R', [1, 0, 0]), mesh('tract.L', [-1, 0, 20], line));
    const route = pathwayRoute(crossing, 'R', meshes);
    expect(route.points).toEqual([[1, 0, 0], [-1, 0, 10], [-1, 0, 20], [-1, 0, 30]]);
    expect(route.stepEnd).toEqual([0, 0, 3]); // the mesh-less step adds no points
  });

  it('orients a leading centerline so that it ends next to what follows', () => {
    const first: Pathway = { ...crossing, steps: [
      { id: 'a', title: { ko: '' }, description: { ko: '' }, structures: [{ id: 'tract', side: 'ipsi' }] },
      { id: 'b', title: { ko: '' }, description: { ko: '' }, structures: [{ id: 'nuc', side: 'ipsi' }] },
    ] };
    const line: Vec3[] = [[0, 0, 0], [0, 0, 10], [0, 0, 20]];
    const meshes = lookup(mesh('tract.L', [0, 0, 10], line), mesh('nuc.L', [0, 0, -5]));
    expect(pathwayRoute(first, 'L', meshes).points).toEqual([[0, 0, 20], [0, 0, 10], [0, 0, 0], [0, 0, -5]]);
  });
});

describe('content integrity', () => {
  const structureIds = new Set(structuresJson.structures.map((s) => s.id));

  it('every pathway references structures that exist', () => {
    for (const p of pathwaysJson.pathways) {
      for (const step of p.steps) {
        for (const ref of step.structures) {
          expect(structureIds.has(ref.id), `${p.id}/${step.id} -> ${ref.id}`).toBe(true);
          expect(['ipsi', 'contra']).toContain(ref.side);
        }
      }
    }
  });

  it('structure ids are unique and groups are defined', () => {
    expect(structureIds.size).toBe(structuresJson.structures.length);
    for (const s of structuresJson.structures) expect(Object.keys(structuresJson.groups)).toContain(s.group);
  });
});
