"""Download the atlas files the build needs into data/raw/. Idempotent: existing files are kept.

Sources (both CC0):
- NextBrain, UCL Figshare doi:10.5522/04/24243835 -- `3dAtlas.zip` (only two members are fetched)
- Harvard Ascending Arousal Network Atlas v2.0, Zenodo record 8161638
"""

import io
import json
import re
import shutil
import urllib.request
import zipfile

from . import CONTENT_DIR, DATA_DIR
from .remote_zip import HttpRangeFile, extract_members

NEXTBRAIN_ZIP = "https://ndownloader.figshare.com/files/42561616"
NEXTBRAIN_MEMBERS = {
    "3dAtlas/atlas.labels.argmax.nii.gz": "nextbrain/atlas.labels.argmax.nii.gz",
    "3dAtlas/lut.freeview.txt": "nextbrain/lut.freeview.txt",
    "3dAtlas/readme.txt": "nextbrain/readme.txt",
}

# Per-label probability maps of the same atlas (scipy sparse, same 0.2 mm grid as the argmax volume).
# The archive is 2.5 GB; the ~150 labels the nuclei and tracts use add up to ~70 MB.
NEXTBRAIN_CODE_ZIP = "https://ndownloader.figshare.com/files/42561625"
PROB_DIR = DATA_DIR / "nextbrain" / "prob"

AAN_BASE = "https://zenodo.org/api/records/8161638/files/{name}/content"
AAN_FILES = [
    "AAN_LC_L_MNI152_1mm_v2p0.nii",
    "AAN_LC_R_MNI152_1mm_v2p0.nii",
    "AAN_DR_MNI152_1mm_v2p0.nii",
    "AAN_Brainstem_MNI152_1mm_v2p0.nii",  # the combined volume (one label per nucleus): build.load_aan_labels
    "README.md",
]


def check_size(path):
    """a download that ended early can leave an empty file that every later run would take as done"""
    if path.stat().st_size == 0:
        path.unlink()
        raise RuntimeError(f"{path} downloaded empty; removed it, re-run the fetch")


def fetch_nextbrain():
    todo = {k: DATA_DIR / v for k, v in NEXTBRAIN_MEMBERS.items() if not (DATA_DIR / v).exists()}
    if not todo:
        print("nextbrain: up to date")
        return
    n = extract_members(NEXTBRAIN_ZIP, todo)
    for dest in todo.values():
        check_size(dest)
    print(f"nextbrain: fetched {len(todo)} file(s), {n / 1e6:.1f} MB over the wire")


def probability_labels() -> list[int]:
    """Atlas labels behind every structure that is meshed from probabilities (not outlines, not strided cortex)."""
    present = {int(line.split("\t")[0]) for line in (CONTENT_DIR.parent / "docs" / "data" / "nextbrain-argmax-labels.tsv").read_text().splitlines()[1:]}
    wanted: set[int] = set()
    for s in json.loads((CONTENT_DIR / "structures.json").read_text())["structures"]:
        src = s["source"]
        if src["atlas"] != "nextbrain" or "shell" in src or src.get("stride", 1) > 1:
            continue
        wanted.update(src.get("labels", []))
        for lo, hi in src.get("labelRanges", []):
            wanted.update(i for i in range(lo, hi + 1) if i in present)
    return sorted(wanted)


def fetch_nextbrain_probabilities():
    todo = [lab for lab in probability_labels() if not (PROB_DIR / f"{lab}.npz").exists()]
    if not todo and (PROB_DIR / "size.npy").exists():
        print("nextbrain probabilities: up to date")
        return
    PROB_DIR.mkdir(parents=True, exist_ok=True)
    raw = HttpRangeFile(NEXTBRAIN_CODE_ZIP)
    with zipfile.ZipFile(io.BufferedReader(raw, buffer_size=4 << 20)) as z:
        names = z.namelist()
        order_file = next(n for n in names if n.endswith("data/atlas_names_and_labels.yaml"))
        # the n-th entry of the yaml (1-based) is stored as atlas/label_<n>.npz
        order = [int(x) for x in re.findall(r":\s*(\d+)\s*$", z.read(order_file).decode(), re.M)]
        members = {int(re.search(r"label_(\d+)\.npz$", n).group(1)): n for n in names if re.search(r"/atlas/label_\d+\.npz$", n)}
        (PROB_DIR / "size.npy").write_bytes(z.read(next(n for n in names if n.endswith("atlas/size.npy"))))
        for lab in todo:
            dest = PROB_DIR / f"{lab}.npz"
            tmp = dest.with_suffix(".part")
            tmp.write_bytes(z.read(members[order.index(lab) + 1]))
            check_size(tmp)
            tmp.replace(dest)
    print(f"nextbrain probabilities: fetched {len(todo)} label(s), {raw.bytes_fetched / 1e6:.0f} MB over the wire")


def fetch_aan():
    for name in AAN_FILES:
        dest = DATA_DIR / "aan" / name
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(AAN_BASE.format(name=name), timeout=120) as r, open(tmp, "wb") as out:
            shutil.copyfileobj(r, out, 1 << 20)
        check_size(tmp)
        tmp.replace(dest)
        print(f"aan: {name} ({dest.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    fetch_nextbrain()
    fetch_nextbrain_probabilities()
    fetch_aan()
