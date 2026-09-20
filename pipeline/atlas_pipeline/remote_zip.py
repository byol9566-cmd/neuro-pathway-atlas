"""Read single members out of a remote zip over HTTP range requests.

NextBrain's `3dAtlas.zip` is 397 MB but we only need the 13 MB label volume and its lookup table.
"""

import io
import urllib.request
import zipfile


class HttpRangeFile(io.RawIOBase):
    """Seekable read-only file backed by `Range:` requests.

    Every read re-requests the original URL: Figshare redirects to a pre-signed S3 link that expires
    within seconds, so the redirect target cannot be cached.
    """

    def __init__(self, url: str, timeout: float = 120):
        self.url = url
        self.timeout = timeout
        self.pos = 0
        self.bytes_fetched = 0
        with self._open("bytes=0-0") as r:
            self.size = int(r.headers["Content-Range"].split("/")[1])

    def _open(self, byte_range: str):
        req = urllib.request.Request(self.url, headers={"Range": byte_range})
        return urllib.request.urlopen(req, timeout=self.timeout)

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self.pos, io.SEEK_END: self.size}[whence]
        self.pos = base + offset
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size or len(b) == 0:
            return 0
        end = min(self.pos + len(b), self.size) - 1
        with self._open(f"bytes={self.pos}-{end}") as r:
            data = r.read()
        b[: len(data)] = data
        self.pos += len(data)
        self.bytes_fetched += len(data)
        return len(data)


def extract_members(url: str, members: dict[str, "os.PathLike"], buffer_size: int = 4 << 20) -> int:
    """Copy `members` ({name in zip: destination path}) out of the zip at `url`. Returns bytes fetched."""
    import shutil
    from pathlib import Path

    raw = HttpRangeFile(url)
    with zipfile.ZipFile(io.BufferedReader(raw, buffer_size=buffer_size)) as z:
        for name, dest in members.items():
            dest = Path(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + ".part")
            with z.open(name) as src, open(tmp, "wb") as out:
                shutil.copyfileobj(src, out, 1 << 20)
            tmp.replace(dest)
    return raw.bytes_fetched
