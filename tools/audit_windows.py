"""Record bounded local host-tool checks; never start an emulator or install tools."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

from common import sha256, write_json
from inventory_candidate import file_kind

ROOT = Path(__file__).resolve().parents[1]


def main():
    specs = [('gcc', shutil.which('gcc'), ['--version']),
             ('make', str(Path('C:/msys64/mingw64/bin/mingw32-make.exe')), ['--version']),
             ('objdump', shutil.which('objdump'), ['-i']),
             ('java', shutil.which('java'), ['-version']),
             ('WinUAE', str(Path('C:/Program Files/WinUAE/winuae64.exe')), None)]
    results = []
    for name, location, arguments in specs:
        entry = dict(name=name, path=location, present=bool(location and Path(location).is_file()))
        if entry['present']:
            data = Path(location).read_bytes()
            entry.update(sha256=sha256(data), format=file_kind(data), size=len(data))
            if arguments is not None:
                p = subprocess.run([location] + arguments, capture_output=True, timeout=20)
                output = (p.stdout+p.stderr).decode('utf-8',errors='replace')
                entry.update(command=[location]+arguments, returncode=p.returncode, output=output)
            else:
                entry.update(execution='NOT_RUN', reason='Full-system emulator is inventory-only for this audit.')
        results.append(entry)
    report = dict(schema_version=1, scope='PATH plus explicitly listed MSYS2 and WinUAE installation paths; not a complete machine search',
        python=dict(path=sys.executable, version=sys.version, sha256=sha256(Path(sys.executable).read_bytes())),
        tools=results,
        python_modules={name: bool(importlib.util.find_spec(name)) for name in ('capstone','amitools','machine68k','unicorn')},
        native_cross_tools_on_path={name:shutil.which(name) for name in ('vasmm68k_mot','vlink','vc','vbccm68k','m68k-amigaos-gcc')})
    write_json(ROOT/'evidence/toolchain/windows-host.json', report)
    print('Wrote bounded native-host audit; no emulator started and no packages installed.')


if __name__ == '__main__':
    main()
