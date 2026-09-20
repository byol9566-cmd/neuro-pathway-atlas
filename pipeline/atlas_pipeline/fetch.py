"""Download the atlas files the build needs into data/raw/. Idempotent: existing files are kept.

Sources (both CC0):
- NextBrain, UCL Figshare doi:10.5522/04/24243835 -- `3dAtlas.zip` (only two members are fetched)
- Harvard Ascending Arousal Network Atlas v2.0, Zenodo record 8161638
"""

import shutil
import urllib.request

from . import DATA_DIR
from .remote_zip import extract_members

NEXTBRAIN_ZIP = "https://ndownloader.figshare.com/files/42561616"
NEXTBRAIN_MEMBERS = {
    "3dAtlas/atlas.labels.argmax.nii.gz": "nextbrain/atlas.labels.argmax.nii.gz",
    "3dAtlas/lut.freeview.txt": "nextbrain/lut.freeview.txt",
    "3dAtlas/readme.txt": "nextbrain/readme.txt",
}

AAN_BASE = "https://zenodo.org/api/records/8161638/files/{name}/content"
AAN_FILES = [
    "AAN_LC_L_MNI152_1mm_v2p0.nii",
    "AAN_LC_R_MNI152_1mm_v2p0.nii",
    "AAN_DR_MNI152_1mm_v2p0.nii",
    "README.md",
]


def fetch_nextbrain():
    todo = {k: DATA_DIR / v for k, v in NEXTBRAIN_MEMBERS.items() if not (DATA_DIR / v).exists()}
    if not todo:
        print("nextbrain: up to date")
        return
    n = extract_members(NEXTBRAIN_ZIP, todo)
    print(f"nextbrain: fetched {len(todo)} file(s), {n / 1e6:.1f} MB over the wire")


def fetch_aan():
    for name in AAN_FILES:
        dest = DATA_DIR / "aan" / name
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(AAN_BASE.format(name=name), timeout=120) as r, open(tmp, "wb") as out:
            shutil.copyfileobj(r, out, 1 << 20)
        tmp.replace(dest)
        print(f"aan: {name} ({dest.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    fetch_nextbrain()
    fetch_aan()
