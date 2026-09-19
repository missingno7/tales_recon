"""Download one declared research candidate, pin it, inventory ZIP members.

Never executes archives or compiler binaries. Not part of normal verification.
First acquisition is trust-on-first-use and cannot prove historical selection.
"""
from pathlib import Path, PurePosixPath
import io
import json
import sys
import urllib.request
import zipfile
from common import require, sha256, write_json

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://www.aztecmuseum.ca/aztecc50a.zip'


def main():
    archive = ROOT / 'toolchain/downloads/aztecc50a.zip'
    lock = ROOT / 'toolchain/candidate-lock.json'
    if archive.exists():
        data = archive.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=30) as response:
            data = response.read(20000001)
        require(len(data) <= 20000000, 'candidate exceeds download size limit')
    z = zipfile.ZipFile(io.BytesIO(data))
    entries = []
    for info in z.infolist():
        name = PurePosixPath(info.filename)
        require(not name.is_absolute() and '..' not in name.parts and ':' not in info.filename
                and '\\' not in info.filename, 'unsafe archive path')
        require(info.file_size <= 20000000, 'oversized archive member')
        if not info.is_dir():
            content = z.read(info)
            entries.append(dict(path=info.filename, size=len(content), sha256=sha256(content)))
    identity = dict(schema_version=1, candidate='Aztec C Amiga 5.0a', provenance_class='ANALYSIS_ONLY',
        provenance_status='archived distribution candidate; game compiler selection unproven',
        url=URL, archive=archive.relative_to(ROOT).as_posix(), size=len(data), sha256=sha256(data), members=entries)
    if lock.exists():
        require(json.loads(lock.read_text()) == identity, 'candidate identity mismatch; refusing to change lock')
    else:
        write_json(lock, identity)
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(data)
    print(json.dumps(identity, indent=2))


if __name__ == '__main__':
    main()
