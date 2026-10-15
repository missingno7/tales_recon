"""Pin the local analysis-only Capstone copy used by DOS x86/16 probes."""
import hashlib
import os
from pathlib import Path
import sys


EXPECTED_TREE_SHA256 = '8f9e32e3a255708979a04a9e4a7faed31b5cbdf24d3680ff620a8129391f4632'
PACKAGE = Path(os.environ.get('TALES_CAPSTONE_ROOT',
                              'C:/tools/capstone-5.0.3/capstone'))


def package_hash(root):
    files = sorted(p for p in root.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.suffix != '.pyc')
    h = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix().encode()
        h.update(len(relative).to_bytes(4, 'little'))
        h.update(relative)
        h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


if not PACKAGE.is_dir() or package_hash(PACKAGE) != EXPECTED_TREE_SHA256:
    raise RuntimeError('pinned DOS Capstone package missing or hash differs: '+str(PACKAGE))
sys.path.insert(0, str(PACKAGE.parent))
import capstone  # noqa: E402
if Path(capstone.__file__).resolve().parent != PACKAGE.resolve() or capstone.__version__ != '5.0.3':
    raise RuntimeError('unexpected Capstone import')
