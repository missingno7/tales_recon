"""Byte-level diff of the from-source build against the original executable.

Every hunk of the original is mapped to the build through link-map symbols whose
names encode an original offset (F_hNN_XXXX, G_h01_XXXX, recon_h00_XXXX,
audio*_XXXX, ...) and through runtime aliases of the link inventory (the
original's F_h00_7AF0 is c.lib's _strcpy). Between two anchors the build is
assumed contiguous. Bytes are then compared:

  IDENTICAL         same byte
  RELOC_CONSISTENT  a relocated pointer whose target maps to the build's target
  A4_CONSISTENT     a small-data displacement d16(a4) naming the mapped DATA offset
  DIFFERENT         anything else: a lead, attributed to the hybrid accounting
                    category (RAW_ORACLE_DEBT, exact C, behavioral, ...) of the
                    original bytes

A DIFFERENT span is not a defect by itself: behavioral sources, link-only
placeholders and unmapped runtime differ by design. The report says which
proof category owns each difference, so a difference inside exact-matched code
or proven DATA points at the build materialization, not at the recovery.

Usage: python tools/game_diff.py [--top 40]  (writes build/game/diff.json)
Diagnostic evidence only; never a proof.
"""
import argparse
import bisect
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
A4_BIAS = 0x7FFE
INV_PATH = ROOT / 'build/workers/sol-link-inventory/inventory.json'

NAME_PATTERNS = (
    (re.compile(r'_(?:F|G|recon)_h(\d\d)_([0-9A-F]{4})$'), None),
    (re.compile(r'_audio\d*_[a-z]+_h(\d\d)_([0-9A-F]{4})$'), None),
    (re.compile(r'_(?:audio\d*_[a-z]+|resident_asm|recovered_exit)_([0-9A-F]{4})$'), 0),
)


def original_offset(name):
    """(hunk, offset) encoded in a symbol name, or None."""
    for pattern, hunk in NAME_PATTERNS:
        m = pattern.match(name)
        if m:
            if hunk is None:
                return int(m.group(1)), int(m.group(2), 16)
            return hunk, int(m.group(1), 16)
    return None


def map_symbols(map_path):
    """{name: (hunk, offset)} from an ln map; the UDATA segment ("Hunk 002"
    after the DATA hunk) already counts from the DATA hunk start."""
    out, current = {}, None
    for line in Path(map_path).read_text(encoding='utf-8', errors='replace').splitlines():
        heading = re.match(r'Segment\s+\d+:\s+Hunk\s+(\d+)', line)
        if heading:
            current = int(heading.group(1)); continue
        m = re.match(r'\s*([0-9a-fA-F]{8})\s+(\S+)', line)
        if m and current is not None:
            hunk = 1 if current == 2 else current  # root UDATA belongs to the DATA hunk
            out.setdefault(m.group(2), (hunk, int(m.group(1), 16)))
    return out


def provider_part_anchors(ledger, symbols, root=ROOT):
    """(hunk, original offset, build offset, label) for every part of every
    accepted CODE-data provider object. The original interleaves parts of
    several providers; each build object starts at its `_<name>_begin` label
    and a part's candidate offset is relative to it."""
    out = []
    for record in (ledger.get('code_data_providers') or {}).values():
        fact = json.loads((root / record['fact']).read_text())
        sections = {}
        for index, obj in enumerate(fact.get('objects', [])):
            if obj.get('id'):
                label = '_' + obj['id'].replace('resident_', '', 1) + '_begin'
            else:  # one source, one object per section, labelled by section index
                stem = Path(next(iter(record['sources']))).stem
                label = '_%s_%d_begin' % (stem, sections.setdefault(obj.get('section'), len(sections)))
            if label not in symbols:
                continue
            hunk, base = symbols[label]
            for part in obj.get('parts', []):
                out.append((hunk, part['original_start'], base + part['candidate_start'], label))
    return out


def anchors(symbols, inventory, extra=()):
    """{hunk: sorted [(original offset, build offset, name)]}."""
    rows = collections.defaultdict(dict)
    for hunk, orig, build, name in extra:
        rows[hunk][orig] = (build, name)
    for name, (hunk, offset) in symbols.items():
        orig = original_offset(name)
        if orig and orig[0] == hunk:
            rows[hunk].setdefault(orig[1], (offset, name))
    for obj in (inventory or {}).get('objects', []):
        for item in obj.get('link_reference_plan', []):
            source, target = item.get('source_symbol'), item.get('target_symbol')
            if int(item.get('addend') or 0) or not source or target not in symbols:
                continue
            orig = original_offset(source)
            if orig and symbols[target][0] == orig[0]:
                rows[orig[0]].setdefault(orig[1], (symbols[target][1], target))
    return {h: sorted((o, b, n) for o, (b, n) in r.items()) for h, r in rows.items()}


class Mapping:
    def __init__(self, table):
        self.table = table
        self.keys = {h: [row[0] for row in rows] for h, rows in table.items()}

    def point(self, hunk, offset):
        keys = self.keys.get(hunk)
        if not keys:
            return None
        i = bisect.bisect_right(keys, offset) - 1
        if i < 0:
            return None
        orig, build, _ = self.table[hunk][i]
        return build + offset - orig

    def owner(self, hunk, offset):
        keys = self.keys.get(hunk) or []
        i = bisect.bisect_right(keys, offset) - 1
        return self.table[hunk][i][2] if i >= 0 else None


def categories(accounting):
    rows = collections.defaultdict(list)
    for r in accounting.get('ranges', []):
        rows[r['hunk']].append((r['start'], r['end'], r.get('category', 'UNKNOWN'), r.get('id')))
    return {h: sorted(v) for h, v in rows.items()}


def category_at(cats, hunk, offset):
    rows = cats.get(hunk, [])
    i = bisect.bisect_right([r[0] for r in rows], offset) - 1
    if i >= 0 and rows[i][0] <= offset < rows[i][1]:
        return rows[i][2], rows[i][3]
    return 'UNACCOUNTED', None


def same_target_bytes(ocont, bcont, original, build, window=16):
    """Both pointers reach the same bytes: up to `window` bytes, or through the
    first NUL for a string. Used where no anchor names the target."""
    a = ocont.get(original[0], b'')[original[1]:original[1] + window]
    b = bcont.get(build[0], b'')[build[1]:build[1] + window]
    if b'\0' in a:
        a = a[:a.index(b'\0') + 1]; b = b[:len(a)]
    return len(a) >= 2 and a == b


def contents(blob, model):
    return {h['number']: blob[h['content_offset']:h['content_offset'] + h['initialized_size']]
            for h in model['hunks'] if h['type'] != 'BSS'}


def relocs(model):
    return {(r['source_hunk'], r['source_offset']): (r['target_hunk'], r['addend_raw'])
            for r in model['relocations'] if r['width'] == 4}


def slot_table_end(cont):
    """End of the ln jump-slot table (JMP abs.l entries) at the start of DATA."""
    end = 0
    while cont.get(1, b'')[end:end + 2] == b'\x4e\xf9':
        end += 6
    return end


def diff(original, build, build_map, inventory, accounting, ledger=None):
    from hunk import parse
    om, bm = parse(original), parse(build)
    ocont, bcont = contents(original, om), contents(build, bm)
    orel, brel = relocs(om), relocs(bm)
    symbols = map_symbols(build_map)
    mapping = Mapping(anchors(symbols, inventory, provider_part_anchors(ledger or {}, symbols)))
    oslots, bslots = slot_table_end(ocont), slot_table_end(bcont)

    def slot_target(rel, data_offset, end):
        if 0 <= data_offset < end and data_offset % 6 == 0:
            return rel.get((1, data_offset + 2))
        return None

    def mapped(target):
        return target and (target[0], mapping.point(*target))

    def a4_equivalent(ow, bw):
        """A small-data reference (d16(a4)) whose two targets are jump slots to
        corresponding code, or the same unnamed bytes (a moved literal)."""
        od, bd = ow + A4_BIAS, bw + A4_BIAS
        t, u = slot_target(orel, od, oslots), slot_target(brel, bd, bslots)
        if t and u:
            return 'A4_SLOT_CONSISTENT' if mapped(t) == u else None
        if (0 <= od < len(ocont.get(1, b'')) and 0 <= bd < len(bcont.get(1, b''))
                and same_target_bytes(ocont, bcont, (1, od), (1, bd))):
            return 'A4_CONTENT_CONSISTENT'
        return None

    def call_target(cont, rel, slots, hunk, at):
        """Callee of a JSR d16(pc) (0x4EBA) or JSR d16(a4) through a slot (0x4EAC)."""
        opcode = cont[hunk][at:at + 2]; disp = int.from_bytes(cont[hunk][at + 2:at + 4], 'big', signed=True)
        if opcode == b'\x4e\xba':
            return (hunk, at + 2 + disp)
        if opcode == b'\x4e\xac':
            return slot_target(rel, disp + A4_BIAS, slots)
        return None
    cats = categories(accounting)
    totals = collections.Counter()
    by_category = collections.defaultdict(collections.Counter)
    regions = []
    for hunk, data in sorted(ocont.items()):
        mine = bcont.get(hunk, b'')
        state, start, owner = None, None, None
        offset = 0
        while offset < len(data):
            category, ident = category_at(cats, hunk, offset)
            where = mapping.point(hunk, offset)
            width, verdict = 1, None
            if where is None or where >= len(mine):
                verdict = 'UNMAPPED'
            elif (hunk, offset) in orel:
                width = 4
                target_hunk, addend = orel[(hunk, offset)]
                expected = mapping.point(target_hunk, addend)
                mine_target = brel.get((hunk, where))
                if mine_target == (target_hunk, expected):
                    verdict = 'RELOC_CONSISTENT'
                elif mine_target and same_target_bytes(ocont, bcont, (target_hunk, addend), mine_target):
                    verdict = 'RELOC_CONTENT_CONSISTENT'  # unnamed target (literal pool) moved
                else:
                    verdict = 'DIFFERENT'
            elif offset % 2 == 0 and offset + 2 <= len(data) and where + 2 <= len(mine) and where % 2 == 0:
                width = 2
                ow = int.from_bytes(data[offset:offset + 2], 'big', signed=True)
                bw = int.from_bytes(mine[where:where + 2], 'big', signed=True)
                ocall = call_target(ocont, orel, oslots, hunk, offset) if offset + 4 <= len(data) else None
                bcall = call_target(bcont, brel, bslots, hunk, where) if ocall and where + 4 <= len(mine) else None
                if ow == bw:
                    verdict = 'IDENTICAL'
                elif ocall and bcall and mapped(ocall) == bcall:
                    width, verdict = 4, 'CALL_CONSISTENT'  # direct JSR vs JSR through a slot, same callee
                elif (mapping.point(1, ow + A4_BIAS) or 0) - A4_BIAS == bw:
                    verdict = 'A4_CONSISTENT'
                elif a4_equivalent(ow, bw):
                    verdict = a4_equivalent(ow, bw)
                elif mapping.point(hunk, offset + ow) == where + bw:
                    verdict = 'PCREL_CONSISTENT'  # 16-bit displacement from its extension word
                elif 0x60 <= data[offset] <= 0x6F and data[offset] == mine[where] and data[offset + 1] and mine[where + 1]:
                    # Bcc.s / BRA.s / BSR.s: an 8-bit displacement from the opcode word + 2.
                    ot = offset + 2 + int.from_bytes(data[offset + 1:offset + 2], 'big', signed=True)
                    bt = where + 2 + int.from_bytes(mine[where + 1:where + 2], 'big', signed=True)
                    verdict = 'PCREL_CONSISTENT' if mapping.point(hunk, ot) == bt else 'DIFFERENT'
                else:
                    verdict = 'DIFFERENT'
            elif data[offset] == mine[where]:
                verdict = 'IDENTICAL'
            else:
                verdict = 'DIFFERENT'
            totals[verdict] += width
            by_category[category][verdict] += width
            if verdict == 'DIFFERENT':
                if state is None or offset > state['end'] + 3 or state['category'] != category:
                    state = dict(hunk=hunk, start=offset, end=offset + width, category=category, id=ident,
                                 anchor=mapping.owner(hunk, offset), build_offset=where)
                    regions.append(state)
                else:
                    state['end'] = offset + width
            offset += width
    for r in regions:
        r['bytes'] = r['end'] - r['start']
        r['original'] = ocont[r['hunk']][r['start']:r['end']][:16].hex()
        b = r['build_offset']
        r['build'] = bcont.get(r['hunk'], b'')[b:b + r['bytes']][:16].hex() if b is not None else None
    return dict(totals=dict(totals), by_category={k: dict(v) for k, v in by_category.items()},
                regions=regions, anchors={h: len(v) for h, v in mapping.table.items()})


def original_executable():
    import game_trace as trace, game_boot
    cfg = trace.runtime_config()
    disk = Path(trace.resolve_path(cfg['disks'][0]['source'])).read_bytes()
    return game_boot.original_executable(disk)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--game-dir', type=Path, default=ROOT / 'build' / 'game')
    ap.add_argument('--top', type=int, default=40)
    ap.add_argument('--category', help='list only regions of this accounting category')
    args = ap.parse_args(argv)
    inventory = json.loads(INV_PATH.read_text()) if INV_PATH.is_file() else {}
    accounting = json.loads((ROOT / 'evidence/hybrid/accounting.json').read_text())
    ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
    report = diff(original_executable(), (args.game_dir / 'DuckTales').read_bytes(),
                  args.game_dir / 'DuckTales.sym', inventory, accounting, ledger)
    (args.game_dir / 'diff.json').write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('bytes:', report['totals'])
    for category, counts in sorted(report['by_category'].items(), key=lambda kv: -kv[1].get('DIFFERENT', 0)):
        print('  %-28s %s' % (category, dict(counts)))
    shown = [r for r in report['regions'] if not args.category or r['category'] == args.category]
    shown.sort(key=lambda r: -r['bytes'])
    for r in shown[:args.top]:
        print('  h%02d %05X+%-5d %-22s %-26s orig %s build %s' % (
            r['hunk'], r['start'], r['bytes'], r['category'], r['anchor'] or '-', r['original'][:16], (r['build'] or '')[:16]))
    print('report:', args.game_dir / 'diff.json')


if __name__ == '__main__':
    main()
