"""Render a readable view of the accepted sources with reviewed semantic names.

Matched sources keep their mechanical names (`recovered`, `F_hNN_XXXX`,
`G_h01_XXXX`); the compiler oracle and every proof depend on them. Semantic
names are curated separately in `recovery/names.json`, each with an evidence
note, and applied only to this generated view under ignored `build/readable/`.
A name is a reconstructed interpretation, never original-source provenance.

    python tools/readable.py            # write build/readable/
    python tools/readable.py --check    # validate recovery/names.json only
"""
import argparse
import json
from pathlib import Path
import re
import sys

from common import FormatError, require

ROOT = Path(__file__).resolve().parents[1]
NAMES = 'recovery/names.json'
OUT = 'build/readable'
IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')
MECHANICAL = re.compile(r'\b(F_h(\d\d)_([0-9A-F]{4})|G_h(\d\d)_([0-9A-F]{4}))\b')
C_KEYWORDS = set('auto break case char const continue default do double else enum extern float for goto if int '
                 'long register return short signed sizeof static struct switch typedef union unsigned void '
                 'volatile while main'.split())
OWNERSHIP_MAPS = ('functions', 'behavioral_functions', 'dead_code_functions')


def function_id(hunk, offset):
    hunk = int(hunk)
    return ('resident_F_%04X' if hunk == 0 else 'ov%02d_F_%%04X' % hunk) % offset


def load_names(root=ROOT):
    path = root / NAMES
    if not path.exists():
        return dict(schema_version=1, functions={}, globals={})
    names = json.loads(path.read_text())
    validate(names)
    return names


def validate(names):
    require(set(names) == {'schema_version', 'functions', 'globals'}, 'names.json keys')
    seen = {}
    for kind, pattern in (('functions', r'(resident|ov\d\d)_F_[0-9A-F]{4}\Z'), ('globals', r'G_h01_[0-9A-F]{4}\Z')):
        for key, row in names[kind].items():
            require(re.match(pattern, key), 'bad %s key %s' % (kind, key))
            require(set(row) == {'name', 'evidence'} and row['evidence'].strip(), key + ' needs a name and evidence')
            name = row['name']
            require(IDENT.match(name) and name not in C_KEYWORDS and not MECHANICAL.fullmatch(name)
                    and name != 'recovered', 'invalid name for %s: %s' % (key, name))
            require(name not in seen, 'duplicate name %s (%s, %s)' % (name, seen.get(name), key))
            seen[name] = key


def rename(text, fid, names):
    funcs, globs = names['functions'], names['globals']

    def sub(m):
        if m.group(2):
            target = function_id(m.group(2), int(m.group(3), 16))
            return funcs.get(target, {}).get('name', m.group(0))
        return globs.get(m.group(0), {}).get('name', m.group(0))
    text = MECHANICAL.sub(sub, text)
    own = funcs.get(fid, {}).get('name', fid)
    return re.sub(r'\brecovered\b', own, text)


def render(root=ROOT, out=None):
    names = load_names(root)
    ledger = json.loads((root / 'recovery/ledger.json').read_text())
    out = Path(out or root / OUT)
    rows = []
    for kind in OWNERSHIP_MAPS:
        for fid, item in sorted(ledger.get(kind, {}).items()):
            source = (root / item['source']).read_text()
            node = fid.split('_F_')[0]
            name = names['functions'].get(fid, {}).get('name')
            header = '/* %s (%s, %s)%s */\n' % (fid, kind, item['state'],
                                               '' if not name else ': ' + names['functions'][fid]['evidence'])
            dest = out / node / ((name or fid) + '.c')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((header + rename(source, fid, names)).encode('ascii', 'replace'))
            rows.append((node, fid, name or '', kind))
    index = ['# Readable view (generated; names are reconstructed interpretations)', '',
             '| Node | Mechanical id | Name | Proof class |', '| --- | --- | --- | --- |']
    index += ['| %s | %s | %s | %s |' % r for r in rows]
    named = sum(1 for r in rows if r[2])
    index += ['', '%d of %d accepted functions named; %d globals named.' % (named, len(rows), len(names['globals']))]
    (out / 'index.md').write_text('\n'.join(index) + '\n')
    return dict(functions=len(rows), named_functions=named, named_globals=len(names['globals']), output=str(out))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    try:
        if args.check:
            load_names()
            print('names.json valid')
        else:
            print(json.dumps(render(), indent=2))
    except FormatError as exc:
        print('INVALID: ' + str(exc))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
