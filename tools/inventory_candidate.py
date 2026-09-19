"""Inventory a pinned Aztec candidate without executing any guest code.

Malformed disks remain explicit failures. Only completely validated disks may
be extracted. In particular this never relaxes the game-fixture OFS parser.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import zipfile

from common import FormatError, json_bytes, require, sha256, write_json
from ofs import OFSDisk

ROOT = Path(__file__).resolve().parents[1]


def file_kind(data):
    if data.startswith(b'\0\0\x03\xf3'):
        return 'AMIGA_HUNK_EXECUTABLE'
    if data.startswith(b'MZ'):
        if len(data) >= 64:
            offset = int.from_bytes(data[60:64], 'little')
            if 64 <= offset <= len(data) - 4 and data[offset:offset + 4] == b'PE\0\0':
                return 'WINDOWS_PE'
        return 'DOS_MZ_OR_LEGACY_WINDOWS_NOT_NATIVE_PE'
    if data.startswith(b'cj'):
        return 'MANX_OBJECT_OR_LIBRARY_CANDIDATE'
    return 'DATA_OR_SOURCE'


def inventory(archive, lock):
    raw = archive.read_bytes()
    require(sha256(raw) == lock['sha256'] and len(raw) == lock['size'], 'candidate archive lock mismatch')
    disks, extracted, executables, libraries = [], {}, [], []
    with zipfile.ZipFile(archive) as z:
        actual = [dict(path=i.filename, size=i.file_size, sha256=sha256(z.read(i)))
                  for i in z.infolist() if not i.is_dir()]
        require(actual == lock['members'], 'candidate member lock mismatch')
        for member in sorted(actual, key=lambda x: x['path']):
            if not member['path'].lower().endswith('.adf'):
                continue
            data = z.read(member['path'])
            disk = OFSDisk(data)
            entry = dict(member=member['path'], sha256=member['sha256'])
            try:
                manifest = disk.parse()
            except FormatError as e:
                entry.update(status='REJECTED_BY_STRICT_PARSER', error=str(e), extracted_files=0,
                    policy='No repair, no partial extraction, no promotion of this disk to a trusted dependency.')
                disks.append(entry)
                continue
            entry.update(status='VALIDATED', volume=manifest['volume'], file_count=len(disk.files),
                         filesystem_manifest=manifest)
            for name, content in sorted(disk.files.items()):
                qualified = manifest['volume'] + ':' + name
                require(qualified not in extracted, 'duplicate extracted candidate path')
                extracted[qualified] = content
                kind = file_kind(content)
                info = dict(path=qualified, size=len(content), sha256=sha256(content), format=kind)
                if kind == 'AMIGA_HUNK_EXECUTABLE':
                    info.update(windows_native=False, required_host='AmigaOS/m68k or compatible emulator',
                        version_strings=[m.group().decode('ascii') for m in re.finditer(rb'[ -~]{12,}',content)
                            if any(w in m.group() for w in (b'Aztec C Version',b'Aztec 68000 Assembler',b'Aztec C68K Linker'))])
                    executables.append(info)
                elif name.lower().endswith('.lib'):
                    libraries.append(info)
            disks.append(entry)
    return dict(schema_version=1, archive_sha256=lock['sha256'], provenance_class='ANALYSIS_ONLY',
        execution_performed=False, historical_toolchain_selected=False, disks=disks,
        validated_disks=sum(d['status']=='VALIDATED' for d in disks),
        rejected_disks=sum(d['status']!='VALIDATED' for d in disks),
        validated_files=len(extracted), executables=executables, libraries=libraries,
        other_archive_members=[m for m in lock['members'] if not m['path'].lower().endswith('.adf')],
        non_disk_member_policy='Inventoried only; not extracted or used.'), extracted


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    ap.add_argument('--extract', action='store_true')
    args=ap.parse_args(argv)
    require(not (args.check and args.extract), '--check cannot extract')
    lock=json.loads((ROOT/'toolchain/candidate-lock.json').read_text())
    report, files=inventory(ROOT/lock['archive'],lock)
    path=ROOT/'evidence/toolchain/aztec-5.0a.json'
    if args.check:
        require(path.read_bytes()==json_bytes(report),'candidate inventory changed')
    else:
        write_json(path,report)
    if args.extract:
        base=(ROOT/'toolchain/installed/aztec-5.0a').resolve()
        for qualified,data in files.items():
            volume,name=qualified.split(':',1)
            target=(base/volume/name).resolve()
            require(target.is_relative_to(base),'unsafe candidate extraction path')
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                require(target.read_bytes()==data, f'existing candidate file differs: {qualified}')
            else:
                target.write_bytes(data)
    print(f'{report["validated_disks"]} validated disks, {report["rejected_disks"]} rejected; '
          f'{report["validated_files"]} files, {len(report["executables"])} Amiga executables. No guest code executed.')
    return 0


if __name__=='__main__':
    try:
        sys.exit(main())
    except (FormatError,OSError,json.JSONDecodeError) as e:
        print(f'ERROR: {e}',file=sys.stderr)
        sys.exit(1)
