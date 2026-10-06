#!/usr/bin/env bash
# Build and publish the static viewer to Vercel. The meshes are generated locally (see ../README.md),
# so we upload the built folder instead of letting Vercel build from git.
# The staging folder's name becomes the Vercel project name; its .vercel/ link is kept between runs.
set -euo pipefail
cd "$(dirname "$0")"
test -f public/data/atlas.glb || { echo "public/data/atlas.glb missing: run the pipeline build first" >&2; exit 1; }
npm run build
link=.deploy/neuro-pathway-atlas/.vercel
# Deploy from outside the repository: inside it the CLI attaches the git commit to the deployment, and
# Vercel blocks the build (TEAM_ACCESS_REQUIRED) when the commit author's e-mail is not on the team.
stage="${TMPDIR:-/tmp}/neuro-pathway-atlas-deploy/neuro-pathway-atlas"
rm -rf "$stage"
mkdir -p "$stage"
cp -R dist/. "$stage"/
test -d "$link" && cp -R "$link" "$stage"/.vercel
# the first upload of a new build sometimes ends in "Not authorized" after the missing files are sent;
# a second call then succeeds immediately
(cd "$stage" && (npx --yes vercel deploy . --prod --yes < /dev/null || npx --yes vercel deploy . --prod --yes < /dev/null))
mkdir -p "$(dirname "$link")" && rm -rf "$link" && cp -R "$stage"/.vercel "$link"
