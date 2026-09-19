"""Download one declared research candidate, pin it, inventory ZIP members.

Never executes archives or compiler binaries. Not part of normal verification.
First acquisition is trust-on-first-use and cannot prove historical selection.
"""
from pathlib import Path, PurePosixPath
import argparse
import io
import json
import sys
import urllib.request
import zipfile
from common import require, sha256, write_json

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://www.aztecmuseum.ca/aztecc50a.zip'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from', dest='local_archive', type=Path,
                    help='import a user-supplied archive without network access')
    args = ap.parse_args()
    archive = ROOT / 'toolchain/downloads/aztecc50a.zip'
    lock = ROOT / 'toolchain/candidate-lock.json'
    if args.local_archive:
        data = args.local_archive.read_bytes()
    elif archive.exists():
        data = archive.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=30) as response:
            data = response.read(20000001)
    require(len(data) <= 20000000, 'candidate exceeds download size limit')
    z = zipfile.ZipFile(io.BytesIO(data))
    entries = []
    seen = set()
    require(sum(i.file_size for i in z.infolist()) <= 100000000, 'archive exceeds expanded size limit')
    for info in z.infolist():
        name = PurePosixPath(info.filename)
        require(not name.is_absolute() and '..' not in name.parts and ':' not in info.filename
                and '\\' not in info.filename, 'unsafe archive path')
        require(info.filename.casefold() not in seen, 'duplicate archive member')
        seen.add(info.filename.casefold())
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
    if args.local_archive:
        receipt = ROOT / 'toolchain/acquisition.json'
        if not receipt.exists():
            source = args.local_archive.resolve()
            write_json(receipt, dict(schema_version=1, method='USER_SUPPLIED_LOCAL_ARCHIVE',
                source_path=source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else str(source),
                archive_sha256=sha256(data), catalog_url=URL,
                limitation='Catalog URL identifies the candidate, not independently authenticated download provenance.'))
    print(f'Pinned {len(entries)} archive members, {len(data)} bytes, SHA-256 {sha256(data)}')


if __name__ == '__main__':
    main()
