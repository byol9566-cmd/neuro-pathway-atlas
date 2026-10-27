#!/usr/bin/env bash
# The whole pipeline in order, from the raw downloads to viewer/public/data (see pipeline/README.md).
#
#   pipeline/run_all.sh [--dry-run] [--from STAGE] [--to STAGE] [--skip STAGE ...]
#
# Stages: fetch canal vhp-register vhp-project tracts content build nerves nerves-build
# Stops at the first failing command. --dry-run prints the commands without running anything.
# Not included (manual, see the README): BodyParts3D download + to_mni.json, vhp_segment.py (needs SAM
# targets), integrate_structures.py / integrate_pathways.py (one-off imports of the reviewer's dataset).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="pipeline/.venv/bin/python"
export PYTHONPATH="pipeline${PYTHONPATH:+:$PYTHONPATH}"
STAGES=(fetch canal vhp-register vhp-project tracts content build nerves nerves-build)

DRY=0; FROM=""; TO=""; SKIP=" "
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --from) FROM="$2"; shift ;;
    --to) TO="$2"; shift ;;
    --skip) SKIP="$SKIP$2 "; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done
for s in "$FROM" "$TO" $SKIP; do
  [ -z "$s" ] || [[ " ${STAGES[*]} " == *" $s "* ]] || { echo "unknown stage: $s (stages: ${STAGES[*]})" >&2; exit 2; }
done

run() {
  echo "+ $*"
  [ "$DRY" = 1 ] || "$@"
}

started=0; [ -z "$FROM" ] && started=1
for stage in "${STAGES[@]}"; do
  [ "$stage" = "$FROM" ] && started=1
  if [ "$started" = 1 ] && [[ "$SKIP" != *" $stage "* ]]; then
    echo "== $stage"
    case "$stage" in
      fetch)  # NextBrain argmax + probability maps, Harvard AAN
        run "$PY" -m atlas_pipeline.fetch ;;
      canal)  # vertebral canal axis from BodyParts3D -> data/derived/bp3d/canal_axis.json
        run "$PY" pipeline/bp3d_canal_axis.py ;;
      vhp-register)  # cryosection stack + MNI registration -> data/raw/vhp/vhp_to_mni.tfm
        run "$PY" pipeline/vhp_stack_register.py ;;
      vhp-project)  # every VHP mask -> MNI, then vhp_derive.py (eye/pituitary parts, straight cord)
        run "$PY" pipeline/vhp_to_mni_all.py ;;
      tracts)  # HCP1065 bundles -> centerlines -> tract pieces (reads the straight cord)
        run "$PY" -m pipeline.tracts.bundle_centerlines --in data/raw/hcp1065 --out data/derived/tracts/centerlines.json --step-mm 2
        run "$PY" pipeline/tracts/prepare_tracts.py ;;
      content)  # content/*.json edits that need no built meshes
        for s in integrate_vhp apply_models tracts/apply_to_content apply_axis_tracts apply_body apply_body_targets apply_effects; do
          run "$PY" "pipeline/$s.py" --write
        done ;;
      build)  # full build: every mesh -> data/derived/meshes (cache) + viewer/public/data
        run "$PY" -m atlas_pipeline.build ;;
      nerves)  # place nerves on the centroids the full build just cached
        run "$PY" pipeline/apply_cranial_nerves.py --write
        run "$PY" pipeline/apply_autonomic.py --write ;;
      nerves-build)  # rebuild only the nerves those two scripts wrote (their modelNote starts with the script's NOTE)
        ids=$("$PY" -c 'import sys; sys.path.insert(0, "pipeline")
import apply_autonomic as a, apply_cranial_nerves as c
from atlas_pipeline.content import load_structures
print(" ".join(s["id"] for s in load_structures()["structures"] if s["source"].get("modelNote", "").startswith((a.NOTE, c.NOTE))))')
        # shellcheck disable=SC2086
        run "$PY" -m atlas_pipeline.build --only $ids ;;
    esac
  fi
  [ "$stage" = "$TO" ] && break
done
[ "$started" = 1 ] || { echo "stage $FROM not reached" >&2; exit 2; }
