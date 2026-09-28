"""Declaration views already used by canonical recovered sources.

For a target function (or a set of targets) this reports, per referenced
global and callee, the ``extern`` declarations that canonical sources under
``recovery/ledger.json`` compiled with: counts per distinct view, the
majority view, alternatives, observed original access widths, and the struct
definitions those views name.  It also renders a paste-ready extern block.

These are candidate source views that already reached exact acceptance in
other routines.  They are NOT historical type provenance: a view that
compiled exactly elsewhere says nothing about the original declaration, and
access widths do not determine a C type uniquely.  Nothing here edits a
source; the conflict-cluster report is for supervisor review only.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from analysis_support import ROOT

POLICY = ('candidate source views used by canonical recovered sources; not historical type provenance. '
          'Access widths are original-instruction facts and do not determine a C type uniquely.')
BASE = r'(?:(?:unsigned|signed)\s+)?(?:char|short|int|long|void)|unsigned|signed|struct\s+\w+'
EXTERN_RE = re.compile(r'\bextern\s+([^;{}]+?)\s*;')
TYPE_RE = re.compile(r'^(?P<base>' + BASE + r')\s*(?P<rest>.+)$', re.S)
DECLARATOR_RE = re.compile(r'^(?P<ptr>(?:\*\s*)*)(?P<name>[A-Za-z_]\w*)\s*(?P<dims>(?:\[\s*\d*\s*\]\s*)*)$')
FUNC_DECLARATOR_RE = re.compile(r'^(?P<ptr>(?:\*\s*)*)(?P<name>[A-Za-z_]\w*)\s*\(\s*\)$')
STRUCT_RE = re.compile(r'\bstruct\s+(\w+)\s*\{([^{}]*)\}\s*;')
MECHANICAL_DATA_RE = re.compile(r'^G_h(\d\d)_([0-9A-F]{4})$')
SCALAR_SIZES = {'char': 1, 'short': 2, 'int': 2, 'long': 4}


def _strip_comments(text):
    return re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)


def _norm(text):
    return ' '.join(text.split())


def _view(base, ptr, dims, function=False):
    """Name-free normalized view such as ``struct Record [36]`` or ``int ()``."""
    base = _norm(base)
    stars = '*' * ptr.count('*')
    dims = ''.join('[%s]' % d.strip() for d in re.findall(r'\[([^\]]*)\]', dims or ''))
    view = base + (' ' + stars if stars else '')
    if function:
        return view + ' ()'
    return view + (' ' + dims if dims else '')


def render_declaration(name, view):
    """``extern`` text for one symbol under a normalized view."""
    if view.endswith(' ()'):
        head = view[:-3]
        stars = head.count('*')
        return 'extern %s %s%s();' % (head.replace('*', '').strip(), '*' * stars, name)
    m = re.match(r'^(?P<base>[^*\[]+?)\s*(?P<ptr>\**)\s*(?P<dims>(?:\[[^\]]*\])*)$', view)
    return 'extern %s %s%s%s;' % (m['base'], m['ptr'], name, m['dims'])


def parse_source(text):
    """Return ``(externs, structs)`` from one source; unparsed externs are listed separately."""
    text = _strip_comments(text)
    externs, unparsed = [], []
    for m in EXTERN_RE.finditer(text):
        statement = _norm(m[1])
        t = TYPE_RE.match(statement)
        if not t:
            unparsed.append(statement)
            continue
        base, parts = t['base'], [p.strip() for p in t['rest'].split(',')]
        for part in parts:
            f = FUNC_DECLARATOR_RE.match(part)
            d = DECLARATOR_RE.match(part) if f is None else None
            if f:
                externs.append(dict(name=f['name'], kind='function', view=_view(base, f['ptr'], '', True)))
            elif d:
                externs.append(dict(name=d['name'], kind='data', view=_view(base, d['ptr'], d['dims'])))
            else:
                unparsed.append(statement)
    structs = {}
    for m in STRUCT_RE.finditer(text):
        structs.setdefault(m[1], _norm(m[2]))
    return externs, structs, unparsed


def canonical_sources(root=ROOT):
    """Canonical source paths (relative) named by the recovery ledger."""
    root = Path(root)
    path = root / 'recovery/ledger.json'
    if not path.is_file():
        return []
    ledger = json.loads(path.read_text(encoding='utf-8'))
    return sorted({item['source'] for item in ledger.get('functions', {}).values() if item.get('source')})


def corpus(root=ROOT):
    """Parse every canonical source once: symbol views, struct bodies, unparsed statements."""
    root = Path(root)
    symbols = defaultdict(lambda: defaultdict(list))   # name -> view -> [source]
    kinds = {}
    structs = defaultdict(lambda: defaultdict(list))   # tag -> body -> [source]
    source_structs = {}
    unparsed = []
    for relative in canonical_sources(root):
        path = root / relative
        try:
            text = path.read_text(encoding='ascii')
        except (OSError, UnicodeDecodeError):
            continue
        externs, defs, bad = parse_source(text)
        seen = set()
        for e in externs:
            key = (e['name'], e['view'])
            if key in seen:
                continue
            seen.add(key)
            symbols[e['name']][e['view']].append(relative)
            kinds[e['name']] = e['kind']
        for tag, body in defs.items():
            structs[tag][body].append(relative)
        source_structs[relative] = defs
        unparsed.extend(dict(source=relative, statement=s) for s in bad)
    return dict(symbols=symbols, kinds=kinds, structs=structs, source_structs=source_structs,
                unparsed=unparsed, sources=len(source_structs))


def _dims(view):
    return [d for d in re.findall(r'\[([^\]]*)\]', view)]


def _struct_tag(view):
    m = re.match(r'^struct\s+(\w+)', view)
    return m[1] if m else None


def struct_size(tag, defs, depth=0):
    """Estimated sizeof under the Manx 68k 16-bit int model (even-aligned words), or None."""
    body = defs.get(tag)
    if body is None or depth > 8:
        return None
    offset = 0
    for member in [m for m in body.split(';') if m.strip()]:
        member = _norm(member)
        t = TYPE_RE.match(member)
        if not t:
            return None
        base = _norm(t['base'])
        for part in [p.strip() for p in t['rest'].split(',')]:
            d = DECLARATOR_RE.match(part)
            if not d or '(' in part or ':' in part:
                return None
            if d['ptr'].strip():
                size, align = 4, 2
            elif base.startswith('struct '):
                size, align = struct_size(base.split()[1], defs, depth + 1), 2
                if size is None:
                    return None
            else:
                word = base.split()[-1]
                size = SCALAR_SIZES.get(word, 2 if word in ('unsigned', 'signed') else None)
                if size is None:
                    return None
                align = 1 if size == 1 else 2
            count = 1
            for dim in _dims(d['dims']):
                if not dim.strip():
                    return None
                count *= int(dim)
            offset = -(-offset // align) * align + size * count
    return offset + (offset & 1)


def view_extent(view, defs):
    """Declared byte extent of a data view, or None when it is not computable."""
    tag = _struct_tag(view)
    if '*' in view:
        element = 4
    elif tag:
        element = struct_size(tag, defs)
    else:
        word = view.split('[')[0].split()[-1]
        element = SCALAR_SIZES.get(word, 2 if word in ('unsigned', 'signed') else None)
    dims = _dims(view)
    if element is None or any(not d for d in dims):
        return None
    return element * _prod(dims)


def _prod(dims):
    n = 1
    for d in dims:
        n *= int(d)
    return n


def _majority(views):
    """(view, sources) pairs ordered by count, then first source, then view text."""
    return sorted(views.items(), key=lambda kv: (-len(kv[1]), min(kv[1]), kv[0]))


def target_symbols(targets, functions):
    """Mechanical names referenced by the targets: A4 data identities and direct callees."""
    data, calls = set(), set()
    for fid in targets:
        f = functions.get(fid)
        if not f:
            continue
        # An A4 reference at a direct-call site is the jump-stub slot of the
        # callee (A4_RELOCATED_JMP_STUB), not a data global.
        call_sites = {c.get('site') for c in f.get('direct_callees', [])}
        for ref in f.get('referenced_data', []):
            if ref.get('kind') == 'A4_RELATIVE' and ref.get('instruction_offset') not in call_sites:
                data.add('G_h%02d_%04X' % (ref['hunk'], ref['offset']))
        for c in f.get('direct_callees', []):
            calls.add('F_h%02d_%04X' % (c['hunk'], c['offset']))
    return sorted(data), sorted(calls)


def _widths(root, targets):
    path = Path(root) / 'evidence/types.json'
    try:
        document = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}, None
    out = {}
    for g in document.get('globals', []):
        mine = sorted({a['width_bytes'] for a in g['accesses'] if a['function'] in targets and a['width_bytes']})
        out[g['data_hunk_offset']] = dict(program=g['observed_widths_bytes'], target=mine,
                                          program_accesses=len(g['accesses']),
                                          address_taken=len(g['address_taken']))
    return out, 'evidence/types.json'


def views_for(targets, root=ROOT, functions=None, data=None, calls=None, parsed=None):
    """Canonical declaration views for the symbols the targets reference."""
    root = Path(root)
    targets = list(targets)
    if functions is None and (data is None or calls is None):
        from recovery_state import evidence
        functions = {f['id']: f for f in evidence()['functions']}
    if data is None or calls is None:
        data, calls = target_symbols(targets, functions)
    parsed = corpus(root) if parsed is None else parsed
    widths, width_source = _widths(root, set(targets))
    symbols, rows, missing = parsed['symbols'], [], []
    chosen_structs = defaultdict(Counter)   # tag -> body -> uses
    for name in list(data) + list(calls):
        views = symbols.get(name)
        m = MECHANICAL_DATA_RE.match(name)
        observed = widths.get(int(m[2], 16)) if m and int(m[1]) == 1 else None
        if not views:
            missing.append(dict(name=name, kind='data' if name in data else 'function', widths=observed))
            continue
        ordered = _majority(views)
        view, sources = ordered[0]
        tie = len(ordered) > 1 and len(ordered[1][1]) == len(sources)
        row = dict(name=name, kind=parsed['kinds'].get(name), view=view, declaration=render_declaration(name, view),
                   count=len(sources), sources=sorted(sources)[:4], canonical_sources=sum(len(s) for _, s in ordered),
                   alternatives=[dict(view=v, declaration=render_declaration(name, v), count=len(s),
                                      sources=sorted(s)[:3]) for v, s in ordered[1:]],
                   majority_tie=tie)
        if observed:
            row['widths'] = observed
        tag = _struct_tag(view)
        if tag:
            for src in sources:
                body = parsed['source_structs'].get(src, {}).get(tag)
                if body is not None:
                    chosen_structs[tag][body] += 1
        rows.append(row)
    # Containment by a declared canonical extent (only for data without an exact view).
    by_offset = {}
    for name in symbols:
        m = MECHANICAL_DATA_RE.match(name)
        if m and parsed['kinds'].get(name) == 'data':
            by_offset[(int(m[1]), int(m[2], 16))] = name
    for item in missing:
        m = MECHANICAL_DATA_RE.match(item['name'])
        if not m:
            continue
        hunk, off = int(m[1]), int(m[2], 16)
        for (h, base), name in sorted(by_offset.items(), key=lambda kv: -kv[0][1]):
            if h != hunk or base >= off or off - base > 0x1000:
                continue
            view, sources = _majority(symbols[name])[0]
            defs = parsed['source_structs'].get(sorted(sources)[0], {})
            extent = view_extent(view, defs)
            if extent is not None and off < base + extent:
                item['within_declared_view'] = dict(name=name, view=view, displacement=off - base, extent=extent,
                                                    basis='canonical majority view extent (Manx 68k size estimate); '
                                                          'containment is a candidate, not an object boundary')
                break
    structs = []
    emitted = set()

    def add_struct(tag, depth=0):
        if tag in emitted or depth > 8 or tag not in chosen_structs:
            return
        emitted.add(tag)
        bodies = chosen_structs[tag].most_common()
        body = bodies[0][0]
        for inner in re.findall(r'\bstruct\s+(\w+)\s+(?!\*)\w', body):
            if inner not in chosen_structs:
                for src_body, srcs in parsed['structs'].get(inner, {}).items():
                    chosen_structs[inner][src_body] += len(srcs)
            add_struct(inner, depth + 1)
        corpus_bodies = parsed['structs'].get(tag, {})
        structs.append(dict(tag=tag, definition='struct %s { %s };' % (tag, body), uses=bodies[0][1],
                            alternatives_among_chosen=[dict(definition='struct %s { %s };' % (tag, b), uses=n)
                                                       for b, n in bodies[1:]],
                            canonical_body_variants=len(corpus_bodies)))
    for tag in sorted(chosen_structs):
        add_struct(tag)
    conflicts = [r['name'] for r in rows if r['alternatives']]
    return dict(schema_version=1, policy=POLICY, targets=targets, canonical_sources=parsed['sources'],
                width_source=width_source, symbols=rows, structs=structs, without_canonical_view=missing,
                conflicting_symbols=conflicts,
                struct_conflicts=[s['tag'] for s in structs if s['alternatives_among_chosen']])


def extern_block(views):
    """Paste-ready text: chosen struct definitions, then one extern per symbol."""
    lines = ['/* Declarations already used by canonical sources: candidate views, not provenance.',
             '   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */']
    for s in views['structs']:
        note = ' /* %d other body/bodies among these views */' % len(s['alternatives_among_chosen']) \
            if s['alternatives_among_chosen'] else ''
        lines.append(s['definition'] + note)
    for r in views['symbols']:
        notes = ['%dx' % r['count']]
        if r['alternatives']:
            notes.append('alt ' + ', '.join('%s x%d' % (a['view'], a['count']) for a in r['alternatives'][:3]))
        if r.get('majority_tie'):
            notes.append('tie')
        w = r.get('widths')
        if w and w.get('target'):
            notes.append('w' + ','.join(map(str, w['target'])))
        lines.append('%s /* %s */' % (r['declaration'], '; '.join(notes)))
    for item in views['without_canonical_view']:
        inside = item.get('within_declared_view')
        w = (item.get('widths') or {}).get('target')
        detail = ('inside %s+%d (%s)' % (inside['name'], inside['displacement'], inside['view'])) if inside \
            else 'no canonical view'
        lines.append('/* %s: %s%s */' % (item['name'], detail, '; w' + ','.join(map(str, w)) if w else ''))
    return '\n'.join(lines) + '\n'


def conflict_clusters(root=ROOT, top=10):
    """Declaration conflicts grouped by 256-byte DATA page / name family, plus struct tag variants."""
    import type_evidence
    pairs = type_evidence.declaration_conflicts(root)['conflicts']
    clusters = defaultdict(lambda: dict(pairs=0, symbols=set(), relations=Counter(), sources=set()))

    def key(name):
        m = MECHANICAL_DATA_RE.match(name)
        return 'G_h%s_%sxx' % (m[1], m[2][:2]) if m else re.sub(r'_[0-9A-F]{4}$', '_*', name)
    for c in pairs:
        row = clusters[key(c['symbol'])]
        row['pairs'] += 1
        row['symbols'].add(c['symbol'])
        row['relations'][c['relation']] += 1
        row['sources'].update((c['left']['path'], c['right']['path']))
    parsed = corpus(root)
    multi = defaultdict(list)
    for name, views in parsed['symbols'].items():
        if len(views) > 1:
            multi[key(name)].append(name)
    ranked = sorted(clusters.items(), key=lambda kv: (-kv[1]['pairs'], kv[0]))
    table = [dict(cluster=k, pairwise_conflicts=v['pairs'], symbols=sorted(v['symbols'])[:8],
                  symbol_count=len(v['symbols']), relations=dict(sorted(v['relations'].items())),
                  sources=len(v['sources']),
                  multi_view_symbols_all_statements=len(multi.get(k, ())))
             for k, v in ranked[:top]]
    tags = sorted(((tag, bodies) for tag, bodies in parsed['structs'].items() if len(bodies) > 1),
                  key=lambda kv: (-len(kv[1]), kv[0]))
    return dict(schema_version=1, policy=POLICY + ' Diagnostic for supervisor review; no source is rewritten.',
                pairwise_total=len(pairs), clusters_total=len(clusters), top=table,
                cluster_basis='mechanical G_hNN_XXXX name grouped by 256-byte DATA page; pairs from '
                              'type_evidence.declaration_conflicts (single-line parser)',
                multi_view_symbols_all_statements=sum(map(len, multi.values())),
                struct_tag_variants=[dict(tag=t, distinct_bodies=len(b), sources=sum(map(len, b.values())))
                                     for t, b in tags[:top]],
                struct_tags_with_variants=len(tags), unparsed_extern_statements=len(parsed['unparsed']))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--function', action='append', help='target id (repeatable: union of targets)')
    mode.add_argument('--clusters', action='store_true', help='conflict breakdown by symbol cluster')
    ap.add_argument('--block', action='store_true', help='with --function: print only the paste-ready block')
    ap.add_argument('--top', type=int, default=10)
    args = ap.parse_args(argv)
    if args.clusters:
        print(json.dumps(conflict_clusters(top=args.top), indent=2))
        return
    views = views_for(args.function)
    print(extern_block(views) if args.block else json.dumps(views, indent=2))


if __name__ == '__main__':
    main()
