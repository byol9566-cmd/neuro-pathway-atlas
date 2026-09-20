#!/usr/bin/env bash
# Build and publish the static viewer to Vercel. The meshes are generated locally (see ../README.md),
# so we upload the built folder instead of letting Vercel build from git.
# The staging folder's name becomes the Vercel project name; its .vercel/ link is kept between runs.
set -euo pipefail
cd "$(dirname "$0")"
test -f public/data/atlas.glb || { echo "public/data/atlas.glb missing: run the pipeline build first" >&2; exit 1; }
npm run build
stage=.deploy/neuro-pathway-atlas
mkdir -p "$stage"
find "$stage" -mindepth 1 -maxdepth 1 ! -name .vercel -exec rm -rf {} +
cp -R dist/. "$stage"/
npx vercel deploy "$stage" --prod --yes
