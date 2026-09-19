"""Revalidate acquired 3.6a archives and extract only complete valid OFS volumes."""
import json
import zipfile
from pathlib import Path
from common import sha256, write_json, require, FormatError
from ofs import OFSDisk

ROOT=Path(__file__).resolve().parents[1]

def inventory():
    receipt=json.loads((ROOT/'toolchain/aztec36-acquisition.json').read_text())
    reports=[]
    base=ROOT/'toolchain/installed/aztec-3.6a'
    for archive in receipt['archives']:
        p=ROOT/archive['path']
        require(sha256(p.read_bytes())==archive['sha256'],'archive changed')
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                data=z.read(name)
                report=dict(archive=archive,member=name,member_sha256=sha256(data))
                try:
                    disk=OFSDisk(data);manifest=disk.parse()
                except FormatError as exc:
                    report.update(status='REJECTED',error=str(exc))
                else:
                    report.update(status='VALIDATED',manifest=manifest)
                    for path,content in disk.files.items():
                        dest=base/manifest['volume']/path
                        require(dest.resolve().is_relative_to(base.resolve()),'unsafe candidate path')
                        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
                reports.append(report)
    return dict(disks=reports,historical_selection_proven=False)

if __name__=='__main__':
    result=inventory()
    write_json(ROOT/'evidence/toolchain/aztec-3.6a.json',result)
    print([d['status'] for d in result['disks']])
