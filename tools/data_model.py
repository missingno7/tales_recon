"""Curated resident data interpretation; no initializer, ownership or proof credit.

The readable view uses Manx sizes: int/short 16, long/pointer 32, alignment 2.
Sparse records and UNKNOWN extents remain explicit, never filled with byte arrays.
"""
import argparse
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


def validate(model, names=None, regions=None):
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
        require(isinstance(row, dict) and {'type', 'extent', 'evidence'} <= set(row)
                and set(row) <= {'type', 'extent', 'evidence', 'struct'}, key + ': global keys')
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
    return model


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
    return validate(model, names, resident_regions(root))


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
    for key, row in model['globals'].items():
        known = typed_bytes(row['type'], model['structs'])
        counts['unknown_globals' if row['type'] == 'UNKNOWN' else
               'fully_typed_globals' if known == row['extent'] else 'partial_globals'] += 1
        if row['extent'] is None:
            continue
        start = int(key[-4:], 16)
        for kind, lo, hi in regions:
            if lo <= start and start + row['extent'] <= hi:
                totals[kind]['typed'] += known
                totals[kind]['modeled_extent'] += row['extent']
    return dict(**counts, modeled_globals=len(model['globals']), structs=len(model['structs']),
                canonical_declared_globals=len(set(symbols)),
                canonical_globals_in_model=len(set(symbols) & model['globals'].keys()), bytes=totals,
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
        lines.append('/* %s: %s bytes; evidence: recovery/data_model.json/globals/%s */' % (key, row['extent'] if row['extent'] is not None else 'UNKNOWN', key))
        parsed = parse_type(row['type'])
        if parsed is None:
            lines.append('/* %s: UNKNOWN; no extern or storage claim. */' % name)
        elif not parsed[1] and struct_tag(row['type']) and not struct_layout(struct_tag(row['type']), structs)['complete']:
            lines.append('/* Incomplete layout; reviewed declaration only: extern %s */' % declaration(name, row['type']))
        else:
            lines.append('extern ' + declaration(name, row['type']))
        lines.append('')
    return '\n'.join(lines + ['#endif', ''])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    try:
        model = load_model()
        if args.check:
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
