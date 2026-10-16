"""Render a readable view of the accepted sources with reviewed semantic names.

Matched sources keep their mechanical names (`recovered`, `F_hNN_XXXX`,
`G_h01_XXXX`); the compiler oracle and every proof depend on them. Semantic
names are curated separately in `recovery/names.json`, each with an evidence
note, and applied only to this generated view under ignored `build/readable/`.
A name is a reconstructed interpretation, never original-source provenance.

    python tools/readable.py            # write build/readable/
    python tools/readable.py --check    # validate names and curated data model
"""
import argparse
import json
from pathlib import Path
import re
import sys

from common import FormatError, require
from repo_paths import canonical_path
import data_model
from declaration_views import EXTERN_RE, parse_source, render_declaration

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


# Mask comments and literals without changing offsets. A string containing
# "extern int G_h01_XXXX;" is evidence/text, never a declaration to rewrite.
NON_CODE = re.compile(r"""/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'""", re.S)


_type_key = data_model.type_key


def compatible_view(view, reviewed, structs, local_structs=None):
    """A struct tag alone is never proof its private body agrees with the model."""
    try:
        left, right = _type_key(view), _type_key(reviewed)
    except FormatError:
        return False
    if left is None or left != right:
        return False
    base, ptr, _ = right
    if 'struct' in base.split():
        tag = base.split()[-1]
        if tag not in structs:
            return bool(ptr)  # same opaque tag; no shared pointee layout is asserted
        body = (local_structs or {}).get(tag)
        if body is not None and not data_model.struct_layout(tag, structs)['complete']:
            return False
        if body is not None:
            # Compare exact declarator text including field names: replacing a
            # merely layout-compatible struct could invalidate member accesses.
            expected = ' '.join(data_model.declaration(f['name'], f['type'])
                                for f in structs[tag]['fields'])
            if re.sub(r'\s+', '', body) != re.sub(r'\s+', '', expected):
                return False
        if not ptr and not data_model.struct_layout(tag, structs)['complete']:
            return False
    return True


def apply_data_model(source, model):
    """Remove compatible private externs; retain differing views as review comments.

    This renders an interpretation, not a compilable port: no struct member,
    scalar/array expression, alias, cast or function body is silently rewritten.
    UNKNOWN objects keep their active private declaration, explicitly marked.
    """
    masked = NON_CODE.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), source)
    _, local_structs, _ = parse_source(masked)
    stats = dict(shared=0, differing=0, unknown=0)
    edits = []
    for match in EXTERN_RE.finditer(masked):
        text = source[match.start():match.end()]
        externs, _, unparsed = parse_source(text)
        if unparsed:
            continue  # all-or-nothing: never split an unsupported declarator
        if not any(e['kind'] == 'data' and e['name'] in model['globals'] for e in externs):
            continue
        lines = []
        for e in externs:
            private = render_declaration(e['name'], e['view'])
            row = model['globals'].get(e['name']) if e['kind'] == 'data' else None
            if row is None:
                lines.append(private)
            elif row['type'] == 'UNKNOWN':
                stats['unknown'] += 1
                lines += ['/* Data model UNKNOWN / alias; private view retained: %s */' % data_model.comment(private), private]
            elif compatible_view(e['view'], row['type'], model['structs'], local_structs):
                stats['shared'] += 1
                lines.append('/* %s declared by game_data.h (%s). */' % (e['name'], row['type']))
            else:
                stats['differing'] += 1
                lines.append('/* PRIVATE VIEW DIFFERS from game_data.h (%s); consumer expressions require review: %s */' %
                             (row['type'], data_model.comment(private)))
        edits.append((match.start(), match.end(), '\n'.join(lines)))
    for lo, hi, text in reversed(edits):
        source = source[:lo] + text + source[hi:]
    return '#include "../include/game_data.h"\n' + source, stats


def render(root=ROOT, out=None):
    names = load_names(root)
    model = data_model.load_model(root, names)

    ledger = json.loads((root / 'recovery/ledger.json').read_text())
    out = Path(out or root / OUT)
    rows = []
    sources_without_private_data = 0
    sources_without_private_views = 0
    totals = dict(shared=0, differing=0, unknown=0)
    header_path = out / 'include/game_data.h'
    header_path.parent.mkdir(parents=True, exist_ok=True)
    header_path.write_bytes(data_model.render_header(model, names).encode('ascii'))
    for kind in OWNERSHIP_MAPS:
        for fid, item in sorted(ledger.get(kind, {}).items()):
            source = canonical_path(root, item['source']).read_text()
            source, decisions = apply_data_model(source, model)
            active = NON_CODE.sub('', source)
            externs, _, unparsed = parse_source(active)
            no_private_data = not unparsed and not any(e['kind'] == 'data' for e in externs)
            sources_without_private_data += no_private_data
            sources_without_private_views += no_private_data and decisions['differing'] == 0
            for key, count in decisions.items():
                totals[key] += count
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
    index += ['', 'Data model: [game_data.h](include/game_data.h). %d compatible private declarations use the shared header; %d differing views are retained as comments; %d UNKNOWN/alias views remain private.' % (totals['shared'], totals['differing'], totals['unknown']), '', 'This generated view is for review, not a compilable port. Differing struct/member and scalar/array consumer expressions are unchanged. Sparse layouts stay incomplete; no filler or initializer bytes are emitted.']
    index += ['', '%d of %d source views have no active private data externs; %d also have no differing-view comments. Function externs are excluded; unsupported extern statements conservatively count as private.' % (sources_without_private_data, len(rows), sources_without_private_views)]
    (out / 'index.md').write_bytes(('\n'.join(index) + '\n').encode('ascii'))
    return dict(functions=len(rows), named_functions=named, named_globals=len(names['globals']), data_model=totals, sources_without_private_data_externs=sources_without_private_data,
                sources_without_private_data_views=sources_without_private_views, output=str(out))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    try:
        if args.check:
            names = load_names()
            data_model.load_model(ROOT, names)
            print('names.json and data_model.json valid')
        else:
            print(json.dumps(render(), indent=2))
    except FormatError as exc:
        print('INVALID: ' + str(exc))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
