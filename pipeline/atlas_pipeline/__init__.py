"""Atlas label volumes -> per-structure surface meshes (GLB) + manifest for the viewer."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "raw"
CONTENT_DIR = REPO_ROOT / "content"
OUT_DIR = REPO_ROOT / "viewer" / "public" / "data"
