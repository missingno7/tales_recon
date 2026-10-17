"""Compare game state between two game_boot.py runs (original vs a from-source build).

Both runs dump the program's DATA hunk (initialized data and its BSS tail) at
the same emulated frames (`--dump-from/--dump-every`). Each typed global of
recovery/data_model.json is located in both: the original at the offset its
mechanical name encodes (G_h01_XXXX), the build through its link map. Values
are compared byte for byte; pointer-typed globals are skipped (their values
are addresses, which differ between layouts by design).

Usage: python tools/game_compare.py ORIGINAL_RUN BUILD_RUN [--map build/game/DuckTales.sym]
Diagnostic evidence only: a match is not a proof, a difference is a lead.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / 'build' / 'trace'


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


def frames(run):
    index = [json.loads(l) for l in (TRACE / run / 'state-index.jsonl').read_text().splitlines() if l.strip()]
    data = (TRACE / run / 'state.bin').read_bytes()
    return {row['frame']: data[row['offset']:row['offset'] + row['size']] for row in index}


def value_sequence(frames_by_number, offset, size):
    """[(first frame, value)] for each distinct consecutive value of one global."""
    out = []
    for frame in sorted(frames_by_number):
        value = frames_by_number[frame][offset:offset + size]
        if not out or out[-1][1] != value:
            out.append((frame, value))
    return out


def sequence_differences(original, built, globals_at):
    """Timing-free comparison: the ORDER of distinct values each global takes.
    A run that reaches the same states later (load times, input timing) agrees;
    a different state sequence is a lead. Fast-changing state (animation frames,
    interrupt counters) sampled at a different phase also differs - judge those
    by structure, not by this list."""
    rows = []
    for name, orig, ours, size, kind in globals_at:
        a = value_sequence(original, orig, size); b = value_sequence(built, ours, size)
        av = [v for _, v in a]; bv = [v for _, v in b]
        if av == bv:
            continue
        k = next((i for i, (x, y) in enumerate(zip(av, bv)) if x != y), min(len(av), len(bv)))
        rows.append(dict(name=name, type=kind, step=k, original_steps=len(av), build_steps=len(bv),
                         frame=a[k][0] if k < len(a) else None,
                         original=av[k].hex() if k < len(av) else None, build=bv[k].hex() if k < len(bv) else None))
    return sorted(rows, key=lambda r: (r['frame'] is None, r['frame'] or 0, r['name']))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('original_run'); ap.add_argument('build_run')
    ap.add_argument('--map', default=str(ROOT / 'build' / 'game' / 'DuckTales.sym'))
    ap.add_argument('--top', type=int, default=25)
    ap.add_argument('--shift', type=int, default=0,
                    help='build frame = original frame + SHIFT (align by the game tick G_h01_B1EC)')
    ap.add_argument('--sequences', action='store_true',
                    help='timing-free: compare the order of distinct values instead of aligned frames')
    args = ap.parse_args(argv)
    import sys
    sys.path.insert(0, str(ROOT / 'tools'))
    from hunk import parse
    build_model = parse((ROOT / 'build' / 'game' / 'DuckTales').read_bytes())
    initialized = build_model['hunks'][1]['initialized_size']
    ours_at = map_offsets(args.map, initialized)
    model = json.loads((ROOT / 'recovery' / 'data_model.json').read_text())['globals']
    original = frames(args.original_run)
    built = {frame - args.shift: data for frame, data in frames(args.build_run).items()}
    if args.sequences:
        located = []
        for name, info in sorted(model.items()):
            m = re.fullmatch(r'G_h01_([0-9A-F]{4})', name)
            size = info.get('extent') or 0
            if m and size and '*' not in str(info.get('type', '')) and '_' + name in ours_at:
                located.append((name, int(m.group(1), 16), ours_at['_' + name], size, info.get('type')))
        rows = sequence_differences(original, built, located)
        print('globals compared: %d; value sequences differing: %d' % (len(located), len(rows)))
        for r in rows[:args.top]:
            print('  frame %5s  %-12s %-26s step %3d (%d/%d steps)  original %s  build %s' % (
                r['frame'], r['name'], r['type'], r['step'], r['original_steps'], r['build_steps'],
                (r['original'] or '-')[:24], (r['build'] or '-')[:24]))
        out = TRACE / ('sequences-%s-%s.json' % (args.original_run, args.build_run))
        out.write_text(json.dumps(dict(compared=len(located), differences=rows), indent=1) + '\n', encoding='utf-8')
        print('report:', out)
        return
    common = sorted(set(original) & set(built))
    checked, first_diff, unlocated = 0, {}, []
    for name, info in sorted(model.items()):
        m = re.fullmatch(r'G_h01_([0-9A-F]{4})', name)
        size = info.get('extent') or 0
        if not m or not size or '*' in str(info.get('type', '')):
            continue
        ours = ours_at.get('_' + name)
        if ours is None:
            unlocated.append(name); continue
        orig = int(m.group(1), 16)
        checked += 1
        for frame in common:
            a, b = original[frame][orig:orig + size], built[frame][ours:ours + size]
            if a != b:
                first_diff[name] = (frame, a.hex(), b.hex(), info.get('type')); break
    print('frames compared: %d (%s..%s); globals compared: %d; differing: %d; not located in build: %d'
          % (len(common), common[0] if common else None, common[-1] if common else None,
             checked, len(first_diff), len(unlocated)))
    for name, (frame, a, b, kind) in sorted(first_diff.items(), key=lambda kv: kv[1][0])[:args.top]:
        print('  frame %5d  %-12s %-28s original %s  build %s' % (frame, name, kind, a[:24], b[:24]))
    report = dict(frames=common, checked=checked, first_diff=first_diff, unlocated=unlocated)
    out = TRACE / ('compare-%s-%s.json' % (args.original_run, args.build_run))
    out.write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('report:', out)


if __name__ == '__main__':
    main()
