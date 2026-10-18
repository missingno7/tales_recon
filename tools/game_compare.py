"""Compare game state between two runs: the original or a from-source build in WinUAE
(tools/game_boot.py), or the SDL3 port (port/main.c --dump).

Every run dumps the program's DATA hunk (initialized data and its BSS tail) at
checkpoints. Each typed global of recovery/data_model.json is located in both runs:
in the original and the port at the offset its mechanical name encodes (G_h01_XXXX;
the port keeps the original layout), in a build through its link map. A global is
compared field by field through its data-model type: numbers by value (the port
keeps them in host byte order), pointers never (their values are addresses, which
differ between layouts by design), UNKNOWN fields and padding only between two
Amiga runs (their byte order in the port is unknown). The report counts what was
compared and what was not.

Usage: python tools/game_compare.py ORIGINAL_RUN OTHER_RUN [--port] [--sequences]
Diagnostic evidence only: a match is not a proof, a difference is a lead.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / 'build' / 'trace'
SCALARS = {'char': 1, 'unsigned char': 1, 'short': 2, 'unsigned short': 2, 'int': 2,
           'unsigned int': 2, 'long': 4, 'unsigned long': 4}


def map_offsets(map_path, data_initialized):
    """DATA-hunk offsets of every symbol in an ln map. The map lists the
    zero-fill part of the DATA hunk as its own segment ("Hunk 002", starting
    at __H2_org = the initialized size); its offsets already count from the
    start of the DATA hunk."""
    offsets, current = {}, None
    for line in Path(map_path).read_text(encoding='utf-8', errors='replace').splitlines():
        heading = re.match(r'Segment\s+\d+:\s+Hunk\s+(\d+)', line)
        if heading:
            current = int(heading.group(1)); continue
        m = re.match(r'\s*([0-9a-fA-F]{8})\s+(\S+)', line)
        if m and current == 1:
            offsets[m.group(2)] = int(m.group(1), 16)
        elif m and current == 2:
            offsets.setdefault(m.group(2), int(m.group(1), 16))
    return offsets


def type_size(kind, structs):
    kind = kind.strip()
    array = re.match(r'^(.*?)\s*\[(\d+)\](.*)$', kind)
    if array:
        element = type_size((array[1] + array[3]).strip(), structs)
        return None if element is None else element * int(array[2])
    if kind.endswith('*'):
        return 4
    if kind in SCALARS:
        return SCALARS[kind]
    record = structs.get(kind[7:].strip()) if kind.startswith('struct ') else None
    if not record:
        return None
    if record.get('size'):
        return record['size']
    last = max(record['fields'], key=lambda f: f['offset'])
    size = type_size(last['type'], structs) if last['type'] != 'UNKNOWN' else None
    return None if size is None else last['offset'] + size


def layout(kind, structs, at=0):
    """(offset, size, part) for every scalar of a data-model type; part is 'value',
    'pointer' or 'unknown'. None when the type has no layout."""
    kind = kind.strip()
    array = re.match(r'^(.*?)\s*\[(\d+)\](.*)$', kind)
    if array:
        element = (array[1] + array[3]).strip()
        size, inner = type_size(element, structs), layout(element, structs)
        if size is None or inner is None:
            return None
        return [(at + i * size + o, s, p) for i in range(int(array[2])) for o, s, p in inner]
    if kind.endswith('*'):
        return [(at, 4, 'pointer')]
    if kind in SCALARS:
        return [(at, SCALARS[kind], 'value')]
    record = structs.get(kind[7:].strip()) if kind.startswith('struct ') else None
    size = type_size(kind, structs)
    if not record or size is None:
        return None
    rows, ordered = [], sorted(record['fields'], key=lambda f: f['offset'])
    for index, field in enumerate(ordered):
        end = ordered[index + 1]['offset'] if index + 1 < len(ordered) else size
        inner = None if field['type'] == 'UNKNOWN' else layout(field['type'], structs, at + field['offset'])
        rows += inner if inner is not None else [(at + field['offset'], end - field['offset'], 'unknown')]
    covered = {o for row in rows for o in range(row[0], row[0] + row[1])}
    rows += [(o, 1, 'unknown') for o in range(at, at + size) if o not in covered]   # padding
    return sorted(rows)


def comparable(dump, at, parts, host_order, unknown):
    """The comparable bytes of one global: numbers big-endian, pointers left out, UNKNOWN
    bytes kept only when `unknown`."""
    out = bytearray()
    for offset, size, part in parts:
        if part == 'pointer' or (part == 'unknown' and not unknown):
            continue
        raw = dump[at + offset:at + offset + size]
        out += raw[::-1] if host_order and part == 'value' else raw
    return bytes(out)


def frames(run):
    index = [json.loads(l) for l in (TRACE / run / 'state-index.jsonl').read_text().splitlines() if l.strip()]
    data = (TRACE / run / 'state.bin').read_bytes()
    return {row['frame']: data[row['offset']:row['offset'] + row['size']] for row in index}


def value_sequence(frames_by_number, read):
    """[(first frame, value)] for each distinct consecutive value of one global."""
    out = []
    for frame in sorted(frames_by_number):
        value = read(frames_by_number[frame])
        if not out or out[-1][1] != value:
            out.append((frame, value))
    return out


def sequence_differences(original, other, globals_at):
    """Timing-free comparison: the ORDER of distinct values each global takes.
    A run that reaches the same states later (load times, input timing) agrees;
    a different state sequence is a lead. Fast-changing state (animation frames,
    interrupt counters) sampled at a different phase also differs - judge those
    by structure, not by this list. globals_at rows: (name, original offset, other
    offset, size, type[, read_original, read_other])."""
    rows = []
    for row in globals_at:
        name, orig, ours, size, kind = row[:5]
        read_a = row[5] if len(row) > 5 else (lambda d, o=orig, n=size: d[o:o + n])
        read_b = row[6] if len(row) > 6 else (lambda d, o=ours, n=size: d[o:o + n])
        a = value_sequence(original, read_a); b = value_sequence(other, read_b)
        av = [v for _, v in a]; bv = [v for _, v in b]
        if av == bv:
            continue
        k = next((i for i, (x, y) in enumerate(zip(av, bv)) if x != y), min(len(av), len(bv)))
        rows.append(dict(name=name, type=kind, step=k, original_steps=len(av), build_steps=len(bv),
                         frame=a[k][0] if k < len(a) else None, other_frame=b[k][0] if k < len(b) else None,
                         original=av[k].hex() if k < len(av) else None, build=bv[k].hex() if k < len(bv) else None))
    return sorted(rows, key=lambda r: (r['frame'] is None, r['frame'] or 0, r['name']))


def located_globals(model, structs, ours_at, port):
    """(name, original offset, other offset, extent, type, parts) for every global both runs
    hold, and the byte counts of what is compared and what is not."""
    rows, counts = [], dict(globals=0, value_bytes=0, pointer_bytes=0, unknown_bytes=0, unlocated=[])
    for name, info in sorted(model.items()):
        m = re.fullmatch(r'G_h01_([0-9A-F]{4})', name)
        size = info.get('extent') or 0
        if not m or not size:
            continue
        orig = int(m.group(1), 16)
        ours = orig if port else ours_at.get('_' + name)
        if ours is None:
            counts['unlocated'].append(name); continue
        parts = layout(str(info.get('type', 'UNKNOWN')), structs)
        if parts is None or sum(s for _, s, _ in parts) != size:
            parts = [(0, size, 'unknown')]
        for _, s, part in parts:
            counts[part + '_bytes'] += s
        counts['globals'] += 1
        rows.append((name, orig, ours, size, info.get('type'), parts))
    return rows, counts


GAME_CLOCK = 0xB1EC  # G_h01_B1EC game_frame_tick: the VBlank count since the game started it


def by_clock(dumps, host_order):
    """Checkpoints keyed by the game clock instead of the frame or tick they were taken at."""
    order = 'little' if host_order else 'big'
    return {int.from_bytes(d[GAME_CLOCK:GAME_CLOCK + 4], order): d for d in dumps.values()}


def best_lag(original, other, read_a, read_b, lags):
    """(lag, share): the shift (original key = other key + lag) at which one global agrees
    on the largest share of the checkpoints both runs have. A global whose values agree at
    some lag takes the same values in the same order, earlier or later; one that agrees at
    no lag is a different state."""
    best = (0, 0.0)
    for lag in lags:
        pairs = [(k + lag, k) for k in other if k + lag in original]
        if pairs:
            share = sum(read_a(original[a]) == read_b(other[b]) for a, b in pairs) / len(pairs)
            if share > best[1]:
                best = (lag, share)
    return best


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('original_run'); ap.add_argument('build_run')
    ap.add_argument('--port', action='store_true',
                    help='the second run is the SDL3 port (port/main.c --dump): original layout, host '
                         'byte order; checkpoints are matched by the game clock (the port spends no '
                         'frames on disk loads)')
    ap.add_argument('--map', default=str(ROOT / 'build' / 'game' / 'DuckTales.sym'))
    ap.add_argument('--top', type=int, default=25)
    ap.add_argument('--shift', type=int, default=0,
                    help='build frame = original frame + SHIFT (Amiga runs, aligned by emulated frame)')
    ap.add_argument('--max-lag', type=int, default=1500,
                    help='largest shift tried when explaining a difference as the same values earlier or later')
    ap.add_argument('--sequences', action='store_true',
                    help='timing-free: compare the order of distinct values instead of aligned checkpoints')
    args = ap.parse_args(argv)
    import sys
    sys.path.insert(0, str(ROOT / 'tools'))
    ours_at = {}
    if not args.port:
        from hunk import parse
        build_model = parse((ROOT / 'build' / 'game' / 'DuckTales').read_bytes())
        ours_at = map_offsets(args.map, build_model['hunks'][1]['initialized_size'])
    data_model = json.loads((ROOT / 'recovery' / 'data_model.json').read_text())
    located, counts = located_globals(data_model['globals'], data_model['structs'], ours_at, args.port)
    unknown = not args.port
    reads = [(name, orig, ours, size, kind,
              lambda d, o=orig, p=parts: comparable(d, o, p, False, unknown),
              lambda d, o=ours, p=parts: comparable(d, o, p, args.port, unknown))
             for name, orig, ours, size, kind, parts in located
             if any(part == 'value' or (unknown and part == 'unknown') for _, _, part in parts)]
    original, built = frames(args.original_run), frames(args.build_run)
    print('globals located: %d (%d not located); bytes compared: %d values%s; not compared: %d pointer%s'
          % (counts['globals'], len(counts['unlocated']), counts['value_bytes'],
             '' if args.port else ' + %d UNKNOWN' % counts['unknown_bytes'], counts['pointer_bytes'],
             ', %d UNKNOWN/padding' % counts['unknown_bytes'] if args.port else ''))
    if args.sequences:
        rows = sequence_differences(original, built, reads)
        print('globals compared: %d; value sequences differing: %d' % (len(reads), len(rows)))
        for r in rows[:args.top]:
            print('  frame %5s/%-5s %-12s %-26s step %3d (%d/%d steps)  original %s  other %s' % (
                r['frame'], r['other_frame'], r['name'], r['type'], r['step'], r['original_steps'],
                r['build_steps'], (r['original'] or '-')[:24], (r['build'] or '-')[:24]))
        out = TRACE / ('sequences-%s-%s.json' % (args.original_run, args.build_run))
        out.write_text(json.dumps(dict(counts=counts, compared=len(reads), differences=rows), indent=1) + '\n',
                       encoding='utf-8')
        print('report:', out)
        return rows
    if args.port:
        original, built, unit = by_clock(original, False), by_clock(built, True), 'clock'
        original.pop(0, None); built.pop(0, None)            # before the game started its clock
    else:
        built, unit = {frame - args.shift: data for frame, data in built.items()}, 'frame'
    common = sorted(set(original) & set(built))
    step = min((b - a for a, b in zip(common, common[1:])), default=1) or 1
    lags = range(-args.max_lag // step * step, args.max_lag + 1, step)
    rows = []
    for name, orig, ours, size, kind, read_a, read_b in reads:
        differing = [k for k in common if read_a(original[k]) != read_b(built[k])]
        if not differing:
            continue
        k = differing[0]
        lag, share = best_lag(original, built, read_a, read_b, lags)
        rows.append(dict(name=name, type=kind, first=k, differing=len(differing), lag=lag, agree_at_lag=round(share, 3),
                         original=read_a(original[k]).hex(), other=read_b(built[k]).hex()))
    rows.sort(key=lambda r: (r['first'], r['name']))
    print('checkpoints compared: %d (%s %s..%s); globals compared: %d; equal at every checkpoint: %d; differing: %d'
          % (len(common), unit, common[0] if common else None, common[-1] if common else None,
             len(reads), len(reads) - len(rows), len(rows)))
    print('  (lag: the same values later in the original (+) or earlier (-); agree: share of checkpoints at that lag)')
    for r in rows[:args.top]:
        print('  %s %5d  %3d/%d differ  lag %+5d agree %5.1f%%  %-12s %-26s original %s  other %s' % (
            unit, r['first'], r['differing'], len(common), r['lag'], 100 * r['agree_at_lag'], r['name'],
            str(r['type'])[:26], r['original'][:16], r['other'][:16]))
    report = dict(unit=unit, checkpoints=common, counts=counts, compared=len(reads), differences=rows)
    out = TRACE / ('compare-%s-%s.json' % (args.original_run, args.build_run))
    out.write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('report:', out)
    return rows


if __name__ == '__main__':
    main()
