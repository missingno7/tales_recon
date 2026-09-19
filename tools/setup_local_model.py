"""Download hash-pinned public runtime/weights; never upload project data."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
from common import require, write_json

ROOT=Path(__file__).resolve().parents[1]


def file_hash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def install():
    lock=json.loads((ROOT/'toolchain/local-model.lock.json').read_text())
    downloads=ROOT/'toolchain/downloads/local-model';downloads.mkdir(parents=True,exist_ok=True)
    dest=ROOT/'toolchain/installed/local-model';dest.mkdir(parents=True,exist_ok=True)
    installed=[]
    for item in lock['files']:
        path=(dest if item['kind']=='model' else downloads)/item['name']
        if not path.exists():
            partial=path.with_suffix(path.suffix+'.part')
            print('Downloading '+item['name'],flush=True)
            with urllib.request.urlopen(item['url'],timeout=60) as response,partial.open('wb') as out:
                while True:
                    block=response.read(8*1024*1024)
                    if not block:break
                    out.write(block)
            require(partial.stat().st_size==item['size'] and file_hash(partial)==item['sha256'],'download hash/size mismatch')
            partial.replace(path)
        require(path.stat().st_size==item['size'] and file_hash(path)==item['sha256'],'installed input changed')
        if item['kind']=='runtime':
            with zipfile.ZipFile(path) as z:
                for member in z.infolist():
                    target=(dest/member.filename).resolve()
                    require(target.is_relative_to(dest.resolve()),'archive path escapes install directory')
                    require(not ((member.external_attr>>16)&0o170000)==0o120000,'archive symlink unsupported')
                z.extractall(dest)
        installed.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=item['sha256']))
        print('Verified '+item['name'],flush=True)
    executables=[p for p in dest.rglob('*') if p.suffix.lower() in ('.exe','.dll')]
    write_json(dest/'installed.json',dict(inputs=installed,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=file_hash(p)) for p in sorted(executables)]))


if __name__=='__main__':install()
