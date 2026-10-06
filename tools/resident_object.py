"""Object-bounded root CODE extraction; no oracle bytes or fixed placement."""
import re
from common import require


def code_size(path):
    obj = path.read_bytes()
    require(obj[:2] in (b'AJ', b'CJ') and len(obj) >= 22,
            'resident object dialect/header differs')
    size = int.from_bytes(obj[10:14], 'big')
    require(size > 0 and size % 2 == 0, 'resident object CODE extent differs')
    return size


def code_labels(path):
    # This boundary accepts compiler-produced C objects, not arbitrary ASM.
    # A named function must start their CODE. Anonymous leading CODE data is
    # deliberately unsupported rather than inferred from a convenient symbol.
    assembly = path.read_text(encoding='ascii')
    code = True
    labels = []
    for line in assembly.splitlines():
        text = line.split(';', 1)[0].strip()
        if not text:
            continue
        if text == 'dseg':
            code = False
            continue
        if text == 'cseg':
            code = True
            continue
        if not code:
            continue
        label = re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*):', text)
        if label:
            labels.append(label[1])
        elif not labels:
            require(text.split()[0] in ('public', 'entry', 'far', 'near', 'mc68881'),
                    'resident C object has anonymous leading CODE')
    require(labels, 'resident object has no leading C function label')
    return labels


def first_function(path):
    return code_labels(path)[0]


def bounds(directory, prefix, labels, model, symbols, entry_function):
    match = re.fullmatch(r't(\d{3,})', prefix)
    require(match is not None, 'resident producer prefix differs')
    harness = 'h' + match[1]
    require(first_function(directory / (harness + '.asm')) == '_main',
            'resident harness must start with its authored main')
    require((0, '_main') in symbols, 'resident harness main is not root CODE')
    root = next(h for h in model['hunks'] if h['number'] == 0)
    require(root['type'] == 'CODE' and root['node'] == 'resident',
            'resident contribution must be in root CODE')
    harness_start = symbols[(0, '_main')]
    harness_size = code_size(directory / (harness + '.o'))
    cursor = start = harness_start + harness_size
    objects = []; owned_symbols = set()
    for label in labels:
        name = prefix if label == 'candidate' else prefix + '_' + label
        size = code_size(directory / (name + '.o'))
        first = first_function(directory / (name + '.asm'))
        owned_symbols.update(code_labels(directory / (name + '.asm')))
        require(symbols.get((0, first)) == cursor,
                'resident object order/boundary does not re-derive')
        objects.append(dict(label=label, start=cursor, size=size, first_symbol=first))
        cursor += size
    require(0 <= harness_start < start < cursor <= root['initialized_size'],
            'resident object block outside initialized root CODE')
    entry = symbols.get((0, '_' + entry_function))
    require(entry is not None and start <= entry < start + objects[0]['size'],
            'resident entry must be in the first source object')
    require(all(name in owned_symbols for (hunk, name), offset in symbols.items()
                if hunk == 0 and start <= offset < cursor and not name.startswith('__H')),
            'resident object extent absorbs another linked contribution')
    for relocation in model['relocations']:
        if relocation['source_hunk'] != 0:
            continue
        lo = relocation['source_offset']
        hi = lo + relocation['width']
        require(not (lo < start < hi or lo < cursor < hi),
                'relocation straddles resident contribution boundary')
    return start, entry - start, dict(schema_version=1,
        harness_start=harness_start, harness_code_size=harness_size,
        start=start, end=cursor, objects=objects)
