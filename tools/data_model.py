"""Curated resident data interpretation; no initializer, ownership or proof credit.

The readable view uses Manx sizes: int/short 16, long/pointer 32, alignment 2.
Sparse records and UNKNOWN extents remain explicit, never filled with byte arrays.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from common import FormatError, require

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'recovery/data_model.json'
IDENT = re.compile(r'[A-Za-z_]\w*\Z', re.ASCII)
GLOBAL = re.compile(r'G_h01_([0-9A-F]{4})\Z')
KEYWORDS = set(('auto break case char const continue default do double else enum extern float for goto if int '
                'long register return short signed sizeof static struct switch typedef union unsigned void '
                'volatile while').split())
TYPE = re.compile(r'(?P<base>(?:(?:const|volatile)\s+)*(?:(?:(?:unsigned|signed)\s+)?'
                  r'(?:char|short(?:\s+int)?|int|long(?:\s+int)?)|unsigned|signed|float|void|struct\s+[A-Za-z_]\w*))'
                  r'\s*(?P<ptr>(?:\*\s*(?:(?:const|volatile)\s*)*)*)'
                  r'(?P<dims>(?:\[\s*[1-9]\d*\s*\]\s*)*)\Z', re.ASCII)


def identifier(name):
    return isinstance(name, str) and IDENT.fullmatch(name) and name not in KEYWORDS


def parse_type(text):
    require(isinstance(text, str), 'type must be C type text')
    if text == 'UNKNOWN':
        return None
    m = TYPE.fullmatch(text.strip())
    require(m is not None, 'unsupported or unbounded C type: ' + text)
    base = ' '.join(m['base'].split())
    if 'struct' in base.split():
        require(identifier(base.split()[-1]), 'invalid struct type: ' + text)
    return base, m['ptr'].strip(), [int(d) for d in re.findall(r'\d+', m['dims'])]


def struct_tag(text):
    parsed = parse_type(text)
    return parsed[0].split()[-1] if parsed and 'struct' in parsed[0].split() else None


def type_layout(text, structs, stack=()):
    """(size or None, alignment); pointers may name incomplete record types."""
    parsed = parse_type(text)
    if parsed is None:
        return None, 1
    base, ptr, dims = parsed
    words = [w for w in base.split() if w not in ('const', 'volatile')]
    if ptr:
        size, align = 4, 2
    elif words[0] == 'struct':
        tag = words[1]
        require(tag in structs, 'unknown struct ' + tag)
        require(tag not in stack, 'recursive by-value struct ' + tag)
        struct_layout(tag, structs, stack)
        size, align = structs[tag]['size'], 2
    else:
        require(words != ['void'], 'void object has no size')
        size = 1 if 'char' in words else 4 if 'long' in words or 'float' in words else 2
        align = min(size, 2)
    for count in dims:
        if size is not None:
            size *= count
    return size, align


def struct_layout(tag, structs, stack=()):
    row = structs[tag]
    require(isinstance(row, dict) and set(row) == {'size', 'fields'}, tag + ': struct keys')
    size = row['size']
    require(size is None or type(size) is int and size > 0 and size % 2 == 0,
            tag + ': size must be positive even bytes or null (UNKNOWN)')
    require(isinstance(row['fields'], list) and row['fields'], tag + ': fields required')
    end, seen, complete, last_offset = 0, set(), True, -1
    for field in row['fields']:
        require(isinstance(field, dict) and set(field) == {'offset', 'name', 'type', 'evidence'}, tag + ': field keys')
        label = tag + '.' + str(field['name'])
        require(identifier(field['name']) and field['name'] not in seen, label + ': invalid/duplicate field name')
        seen.add(field['name'])
        require(isinstance(field['evidence'], str) and field['evidence'].strip(), label + ': evidence required')
        offset = field['offset']
        require(type(offset) is int and offset >= end and offset > last_offset, label + ': overlapping or unordered offset')
        last_offset = offset
        width, align = type_layout(field['type'], structs, stack + (tag,))
        require(offset % align == 0, label + ': misaligned field')
        require(size is None or offset < size, label + ': outside struct')
        if width is None:
            complete = False
            end = offset
        else:
            complete &= offset == (end + align - 1) // align * align
            end = offset + width
            require(size is None or end <= size, label + ': field exceeds struct size')
    complete &= size is not None and (end + 1) // 2 * 2 == size
    return dict(complete=bool(complete), minimum_size=end)


def validate(model, names=None, regions=None, mechanical_facts=None, root=ROOT):
    """Validate synthetic or repository maps without reading initializer values."""
    require(isinstance(model, dict) and set(model) == {'schema_version', 'globals', 'structs'}, 'data model keys')
    require(type(model['schema_version']) is int and model['schema_version'] == 1, 'data model schema_version')
    require(isinstance(model['globals'], dict) and isinstance(model['structs'], dict), 'globals/structs must be maps')
    structs = model['structs']
    for tag in structs:
        require(identifier(tag), 'invalid struct name: ' + str(tag))
        struct_layout(tag, structs)
    names = {'globals': {}, 'functions': {}} if names is None else names
    require(isinstance(names, dict), 'reviewed names must be a map')
    emitted = {}
    for kind in ('globals', 'functions'):
        require(isinstance(names.get(kind, {}), dict), 'reviewed ' + kind + ' must be a map')
        for key, row in names.get(kind, {}).items():
            require(isinstance(row, dict), 'reviewed name entry must be a map: ' + str(key))
            name = row.get('name')
            require(identifier(name) and name not in emitted, 'invalid/duplicate reviewed name: ' + str(name))
            emitted[name] = key
    intervals = []
    for key, row in model['globals'].items():
        require(isinstance(key, str) and GLOBAL.fullmatch(key), 'invalid resident global: ' + str(key))
        require(isinstance(row, dict) and {'type', 'extent', 'evidence', 'basis'} <= set(row)
                and set(row) <= {'type', 'extent', 'evidence', 'basis', 'struct'}, key + ': global keys')
        require(row['basis'] in ('CURATED', 'MECHANICAL_CONSISTENT_VIEWS'), key + ': invalid basis')
        require(isinstance(row['evidence'], str) and row['evidence'].strip(), key + ': evidence required')
        name = names.get('globals', {}).get(key, {}).get('name', key)
        require(name not in emitted or emitted[name] == key, 'duplicate emitted global name: ' + name)
        emitted[name] = key
        width, align = type_layout(row['type'], structs)
        extent = row['extent']
        require(extent is None or type(extent) is int and extent > 0, key + ': extent must be positive bytes or null')
        require(row['type'] == 'UNKNOWN' or width is not None and width == extent, key + ': type/extent mismatch')
        if 'struct' in row:
            require(row['struct'] in structs and parse_type(row['type']) is not None
                    and re.search(r'\bstruct\s+' + re.escape(row['struct']) + r'\b', row['type']),
                    key + ': struct annotation disagrees with type')
        start = int(GLOBAL.fullmatch(key)[1], 16)
        require(start % align == 0, key + ': misaligned global')
        if regions is not None:
            require(any(lo <= start < hi for _, lo, hi in regions), key + ': address outside resident DATA/BSS region')
        if extent is not None:
            if regions is not None:
                require(any(lo <= start and start + extent <= hi for _, lo, hi in regions),
                        key + ': extent outside resident DATA/BSS region')
            intervals.append((start, start + extent, key))
    previous = None
    for current in sorted(intervals):
        require(previous is None or current[0] >= previous[1],
                'overlapping global extents: %s / %s' % (previous[2] if previous else '', current[2]))
        previous = current
    mechanical = {k: r for k, r in model['globals'].items() if r['basis'] == 'MECHANICAL_CONSISTENT_VIEWS'}
    if mechanical:
        facts = load_scalar_facts(root) if mechanical_facts is None else mechanical_facts
        derived = derive_scalars(model, facts, regions)
        for key, row in mechanical.items():
            require(derived.get(key) == row, key + ': stale MECHANICAL_CONSISTENT_VIEWS entry; re-derive or curate')
    return model


def type_key(text):
    """Manx compatible spelling, preserving signedness, pointers and array shape."""
    parsed = parse_type(text)
    if parsed is None:
        return None
    base, ptr, dims = parsed
    base = {'short': 'int', 'short int': 'int', 'signed': 'int',
            'signed int': 'int', 'signed short': 'int', 'signed short int': 'int',
            'unsigned': 'unsigned int', 'unsigned short': 'unsigned int',
            'unsigned short int': 'unsigned int', 'long int': 'long',
            'signed long': 'long', 'signed long int': 'long',
            'unsigned long int': 'unsigned long', 'signed char': 'char'}.get(base, base)
    return base, ''.join(ptr.split()), tuple(dims)


def load_scalar_facts(root=ROOT):
    """Read current canonical views and freshness-checked instruction-width facts."""
    from declaration_views import corpus
    from type_evidence import evidence_staleness
    root = Path(root)
    document = json.loads((root / 'evidence/types.json').read_text())
    stale = evidence_staleness(document, root)
    require(not stale, '; '.join(stale))
    return dict(parsed=corpus(root), widths={g['data_hunk_offset']: g for g in document['globals']})


def derive_scalars(model, facts, regions=None):
    """Reproducible consistency tier, not historical declaration/boundary provenance.

    Require positive original accesses exactly as wide as the declared element.
    No by-value structs, unbounded arrays, address-only anchors or majority vote.
    All candidate/candidate overlaps are excluded symmetrically, so selection is
    independent of map order or which proposals have already been merged.
    Curated UNKNOWN aliases reserve their identity, but claim no unknown bytes.
    """
    parsed, widths = facts['parsed'], facts['widths']
    curated = {k: r for k, r in model['globals'].items() if r['basis'] == 'CURATED'}
    occupied = [(int(k[-4:], 16), int(k[-4:], 16) + r['extent'])
                for k, r in curated.items() if r['extent'] is not None]
    candidates = {}
    unparsed = {key for row in parsed.get('unparsed', [])
                for key in re.findall(r'\bG_h01_[0-9A-F]{4}\b', row['statement'])}
    for key, views in sorted(parsed['symbols'].items()):
        if not GLOBAL.fullmatch(key) or key in curated or key in unparsed or parsed['kinds'].get(key) != 'data':
            continue
        try:
            keys = {type_key(v) for v in views}
            if len(keys) != 1 or None in keys:
                continue
            base, ptr, dims = next(iter(keys))
            if not ptr and ('struct' in base.split() or base == 'void'):
                continue
            text = base + (' ' + ptr if ptr else '') + ''.join('[%d]' % n for n in dims)
            extent, align = type_layout(text, {})
            element = type_layout(base + (' ' + ptr if ptr else ''), {})[0]
        except FormatError:
            continue
        start = int(key[-4:], 16)
        stop = start + extent
        if start % align or regions is not None and not any(lo <= start and stop <= hi for _, lo, hi in regions):
            continue
        if any(start < hi and lo < stop for lo, hi in occupied):
            continue
        observed = widths.get(start, {})
        access_widths = sorted({a['width_bytes'] for a in observed.get('accesses', []) if a['width_bytes']})
        if access_widths != [element] or observed.get('observed_widths_bytes') != access_widths:
            continue
        # Include accesses starting outside but straddling this span. Checking
        # just base identities would incorrectly accept a word inside a long.
        interior = {offset: row for offset, row in widths.items()
                    if start <= offset < stop or any(a['width_bytes'] and offset < stop
                        and start < offset + a['width_bytes'] for a in row.get('accesses', []))}
        if any(w != element or offset < start or (offset - start) % element or offset + w > stop
               for offset, row in interior.items() for a in row.get('accesses', [])
               if (w := a['width_bytes'])):
            continue
        sources = sorted({src for consumers in views.values() for src in consumers})
        tag = struct_tag(text)
        # Fingerprint only recovered facts, never instruction/initializer bytes.
        snapshot = dict(views={v: sorted(set(ss)) for v, ss in sorted(views.items())},
                        accesses={str(o): dict(accesses=[{k: a.get(k) for k in
                            ('function', 'hunk', 'offset', 'mnemonic', 'operands', 'width_bytes', 'direction')}
                            for a in r.get('accesses', [])], address_taken=[{k: a.get(k) for k in
                            ('function', 'hunk', 'offset', 'mnemonic', 'operands', 'width_bytes', 'direction')}
                            for a in r.get('address_taken', [])],
                            widths=r.get('observed_widths_bytes')) for o, r in sorted(interior.items())},
                        pointee_views={src: parsed.get('source_structs', {}).get(src, {}).get(tag)
                                       for src in sources} if tag else {})
        digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        evidence = ('Canonical declaration_views: %s; consumers=%d; original access widths=%s bytes; '
                    'accesses=%d; address-takings=%d (evidence/types.json); facts sha256=%s. '
                    'Declared extent; mechanical consistency only, not historical type or object-boundary provenance.' %
                    (', '.join('%s (%d)' % (v, len(set(ss))) for v, ss in sorted(views.items())), len(sources),
                     access_widths, len(observed.get('accesses', [])), len(observed.get('address_taken', [])), digest))
        candidates[key] = dict(type=text, extent=extent, evidence=evidence, basis='MECHANICAL_CONSISTENT_VIEWS')
    intervals = sorted((int(k[-4:], 16), int(k[-4:], 16) + r['extent'], k) for k, r in candidates.items())
    blocked = set()
    for i, (lo, hi, key) in enumerate(intervals):
        for other_lo, other_hi, other_key in intervals[i+1:]:
            if other_lo >= hi:
                break
            blocked.update((key, other_key))
    return {k: r for k, r in candidates.items() if k not in blocked}


def refresh_scalar_evidence(model, facts, regions=None):
    """Refresh diagnostics only; refuse lost support or any semantic change."""
    derived = derive_scalars(model, facts, regions)
    rows = dict(model['globals'])
    for key, row in rows.items():
        if row['basis'] != 'MECHANICAL_CONSISTENT_VIEWS':
            continue
        current = derived.get(key)
        require(current is not None and
                {k: v for k, v in current.items() if k != 'evidence'} ==
                {k: v for k, v in row.items() if k != 'evidence'},
                key + ': mechanical facts changed; evidence-only refresh refused')
        rows[key] = current
    return dict(model, globals=rows)


def propose_scalars(model, facts, regions=None):
    """Only new rows; derivation also considers existing mechanical rows."""
    return {k: r for k, r in derive_scalars(model, facts, regions).items() if k not in model['globals']}


def resident_regions(root=ROOT):
    """Measured initialized DATA and zero tail, not guessed suffix bounds."""
    rows = json.loads((Path(root) / 'docs/data-layout.json').read_text())['ranges']
    bss = [r for r in rows if r['hunk'] == 1 and r['classification'] == 'BSS']
    require(len(bss) == 1, 'one resident DATA zero-tail region required')
    return [('DATA', 0, bss[0]['start']), ('BSS', bss[0]['start'], bss[0]['end'])]


def _unique_object(pairs):
    row = {}
    for key, value in pairs:
        require(key not in row, 'duplicate JSON key: ' + key)
        row[key] = value
    return row


def load_model(root=ROOT, names=None):
    root = Path(root)
    if names is None:
        names = json.loads((root / 'recovery/names.json').read_text())
    model = json.loads((root / MODEL).read_text(), object_pairs_hook=_unique_object)
    return validate(model, names, resident_regions(root), root=root)


def typed_bytes(text, structs):
    """Known field bytes only: exclude holes, UNKNOWN fields and ABI padding."""
    parsed = parse_type(text)
    if parsed is None:
        return 0
    base, ptr, dims = parsed
    tag = struct_tag(text)
    if not ptr and tag:
        size = sum(typed_bytes(f['type'], structs) for f in structs[tag]['fields'])
        for count in dims:
            size *= count
        return size
    return type_layout(text, structs)[0] or 0


def coverage(model, regions, symbols=()):
    totals = {kind: dict(total=hi-lo, typed=0, modeled_extent=0) for kind, lo, hi in regions}
    counts = dict(fully_typed_globals=0, partial_globals=0, unknown_globals=0)
    by_basis = {basis: dict(globals=0, typed_bytes={kind: 0 for kind, _, _ in regions})
                for basis in ('CURATED', 'MECHANICAL_CONSISTENT_VIEWS')}
    for key, row in model['globals'].items():
        known = typed_bytes(row['type'], model['structs'])
        by_basis[row['basis']]['globals'] += 1
        counts['unknown_globals' if row['type'] == 'UNKNOWN' else
               'fully_typed_globals' if known == row['extent'] else 'partial_globals'] += 1
        if row['extent'] is None:
            continue
        start = int(key[-4:], 16)
        for kind, lo, hi in regions:
            if lo <= start and start + row['extent'] <= hi:
                totals[kind]['typed'] += known
                by_basis[row['basis']]['typed_bytes'][kind] += known
                totals[kind]['modeled_extent'] += row['extent']
    return dict(**counts, modeled_globals=len(model['globals']), structs=len(model['structs']),
                canonical_declared_globals=len(set(symbols)),
                canonical_globals_in_model=len(set(symbols) & model['globals'].keys()), bytes=totals, by_basis=by_basis,
                policy='Readable interpretation only; no ownership/proof credit. Typed bytes exclude UNKNOWN spans and ABI padding. '
                       'BSS is the resident DATA zero tail; the separate four-byte BSS sentinel is not modeled.')


def declaration(name, text):
    base, ptr, dims = parse_type(text)
    return '%s %s%s%s;' % (base, (ptr + ' ') if ptr and not ptr.endswith('*') else ptr,
                           name, ''.join('[%d]' % d for d in dims))


def comment(text):
    return ' '.join(text.replace('*/', '* /').split())


def render_header(model, names):
    structs = model['structs']
    lines = ['/* Generated from recovery/data_model.json; reconstructed interpretation only.',
             ' * Manx ABI: int/short 16, long/pointer 32, word alignment 2.',
             ' * No initializers or ownership/proof credit. Sparse layouts stay UNKNOWN.',
             ' * MECHANICAL rows assert agreeing canonical views and access widths only;',
             ' * their declared extents do not establish historical object boundaries.',
             ' * Readable view only: private consumer expressions have not been rewritten.',
             ' * This is not a host-port header; native sizeof is not the historical layout. */',
             '#ifndef TALES_GAME_DATA_H', '#define TALES_GAME_DATA_H', '']
    for tag in sorted(structs):
        lines.append('struct %s;' % tag)
    lines.append('')
    done = set()

    def emit(tag):
        if tag in done:
            return
        row = structs[tag]
        for f in row['fields']:
            p = parse_type(f['type'])
            tag_used = struct_tag(f['type'])
            if p and not p[1] and tag_used:
                emit(tag_used)
        done.add(tag)
        complete = struct_layout(tag, structs)['complete']
        size = row['size'] if row['size'] is not None else 'UNKNOWN'
        if not complete:
            lines.append('/* struct %s: size %s; incomplete layout, no fabricated C definition.' % (tag, size))
            for f in row['fields']:
                lines.append(' * +%d: %s %s (evidence: data_model.json/structs/%s)' % (f['offset'], f['type'], f['name'], tag))
            lines.extend([' */', ''])
            return
        lines.append('struct %s { /* modeled size %s */' % (tag, size))
        for f in row['fields']:
            lines.append('    %s /* +%d; evidence: data_model.json/structs/%s */' % (declaration(f['name'], f['type']), f['offset'], tag))
        lines.extend(['};', ''])

    for tag in sorted(structs):
        emit(tag)
    for key, row in sorted(model['globals'].items()):
        name = names.get('globals', {}).get(key, {}).get('name', key)
        lines.append('/* %s: %s bytes; basis: %s; evidence: recovery/data_model.json/globals/%s */' % (key, row['extent'] if row['extent'] is not None else 'UNKNOWN', row['basis'], key))
        parsed = parse_type(row['type'])
        if parsed is None:
            lines.append('/* %s: UNKNOWN; no extern or storage claim. */' % name)
        elif not parsed[1] and struct_tag(row['type']) and not struct_layout(struct_tag(row['type']), structs)['complete']:
            lines.append('/* Incomplete layout; reviewed declaration only: extern %s */' % declaration(name, row['type']))
        else:
            lines.append('extern ' + declaration(name, row['type']))
        lines.append('')
    return '\n'.join(lines + ['#endif', ''])


def validate_storage_plan(document, root=ROOT, facts=None):
    """Re-derive storage partition and all aliases; no provider/proof credit."""
    from storage_plan import collect, validate as validate_storage
    return validate_storage(document, collect(root, document.get('curation')) if facts is None else facts)


def derive_storage_plan(curation, root=ROOT, facts=None):
    """Read-only proposal; curated inputs are retained and measurements re-derived."""
    from storage_plan import POLICY, collect, derive
    current = collect(root, curation) if facts is None else facts
    return dict(schema_version=1, policy=POLICY, curation=curation,
                derived=derive(curation, current))


def load_storage_plan(root=ROOT):
    from storage_plan import load
    return load(root)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--refresh-scalar-evidence', action='store_true',
                      help='re-derive existing mechanical evidence text; refuse type/extent changes or lost support')
    mode.add_argument('--propose-scalars', action='store_true', help='JSON global entries; read-only, reproducible consistency proposals')
    mode.add_argument('--check-storage-plan', action='store_true', help='re-derive resident storage partition and every view/alias')
    mode.add_argument('--propose-storage-plan', action='store_true', help='write the derived plan to build/storage-plan.json; no canonical writes')
    args = ap.parse_args(argv)
    try:
        if args.propose_storage_plan:
            from storage_plan import OUTPUT, write
            document = write(ROOT)
            print('wrote ' + OUTPUT)
            print(json.dumps(document['derived']['summary'], indent=2))
            return 0
        if args.check_storage_plan:
            document = load_storage_plan()
            print(json.dumps(document['derived']['summary'], indent=2))
            return 0
        if args.refresh_scalar_evidence:
            model = json.loads((ROOT / MODEL).read_text(), object_pairs_hook=_unique_object)
            facts, regions = load_scalar_facts(), resident_regions()
            updated = refresh_scalar_evidence(model, facts, regions)
            names = json.loads((ROOT / 'recovery/names.json').read_text())
            validate(updated, names, regions, mechanical_facts=facts)
            changed = sum(row != model['globals'][key] for key, row in updated['globals'].items())
            (ROOT / MODEL).write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8", newline="\n")
            print('refreshed %d mechanical evidence entries; types/extents unchanged' % changed)
            return 0
        model = load_model()
        if args.propose_scalars:
            print(json.dumps(propose_scalars(model, load_scalar_facts(), resident_regions()), indent=2))
        elif args.check:
            print('data_model.json valid (readable interpretation; no proof credit)')
        else:
            from declaration_views import corpus
            parsed = corpus(ROOT)
            symbols = [key for key in parsed['symbols'] if GLOBAL.fullmatch(key)]
            print(json.dumps(coverage(model, resident_regions(), symbols), indent=2))
    except (FormatError, OSError, ValueError, KeyError, TypeError) as exc:
        print('INVALID: ' + str(exc))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
