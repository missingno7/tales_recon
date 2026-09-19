"""Strict census of classic load-file records, preserving offsets and ordering.

Unknown record/extension variants fail with their first byte offset. This is
not a generic linker or a serializer; see docs/formats.md for supported scope.
"""
import struct
from collections import Counter
from common import require, sha256, FormatError

TYPES = {999:'UNIT',1000:'NAME',1001:'CODE',1002:'DATA',1003:'BSS',1004:'RELOC32',
         1005:'RELOC16',1006:'RELOC8',1007:'EXT',1008:'SYMBOL',1009:'DEBUG',1010:'END',
         1011:'HEADER',1013:'OVERLAY',1014:'BREAK',1015:'DREL32',1016:'DREL16',
         1017:'DREL8',1018:'LIB',1019:'INDEX',1020:'RELOC32SHORT',1021:'RELRELOC32',1022:'ABSRELOC16'}


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, n):
        require(0 <= n <= len(self.data) - self.pos, f'truncated input at 0x{self.pos:x}, need {n} bytes')
        p = self.pos
        self.pos += n
        return self.data[p:self.pos]

    def u32(self):
        return int.from_bytes(self.take(4), 'big')

    def u16(self):
        return int.from_bytes(self.take(2), 'big')

    def string(self, n):
        return self.take(n * 4).rstrip(b'\0').decode('latin-1')


def parse(data):
    r = Reader(data)
    records, hunks, nodes, relocations = [], [], [], []
    active = node = None
    next_hunk = None
    overlay = None
    while r.pos < len(data):
        start = r.pos
        tag = r.u32()
        kind = TYPES.get(tag & 0x3fffffff)
        require(kind is not None and tag >> 30 == 0, f'unsupported record 0x{tag:08x} at 0x{start:x}')
        rec = dict(file_offset=start, type='HUNK_' + kind, logical_hunk=active['number'] if active else None,
                   node=node['id'] if node else None)
        if kind == 'HEADER':
            require(active is None, f'unterminated hunk at 0x{start:x}')
            require(node is None or next_hunk == node['last_hunk'] + 1, 'incomplete preceding node')
            if nodes:
                require(overlay is not None and records[-1]['type'] in ('HUNK_OVERLAY','HUNK_BREAK'),
                        'overlay HEADER without OVERLAY/BREAK boundary')
            names = []
            while (n := r.u32()):
                names.append(r.string(n))
            table, first, last = r.u32(), r.u32(), r.u32()
            require(first <= last and last - first < 4096, 'invalid hunk header range')
            allocations = []
            for h in range(first, last + 1):
                raw = r.u32()
                flags = raw >> 30
                extra = r.u32() if flags == 3 else None
                allocations.append(dict(hunk=h, size=(raw & 0x3fffffff) * 4,
                                        memory_flags_raw=flags, memory_requirements=extra))
            node = dict(id='resident' if not nodes else f'ov{first:02d}', header_offset=start,
                        table_size_raw=table, first_hunk=first, last_hunk=last,
                        resident_names=names, allocations=allocations, hunks=[])
            nodes.append(node)
            next_hunk = first
            rec.update(node=node['id'], header=node)
        elif kind in ('CODE','DATA','BSS'):
            require(node is not None and active is None and next_hunk <= node['last_hunk'],
                    f'unexpected segment at 0x{start:x}')
            size = r.u32() * 4
            alloc = node['allocations'][next_hunk - node['first_hunk']]
            require(size <= alloc['size'], f'hunk {next_hunk}: content exceeds allocation')
            payload_offset = r.pos if kind != 'BSS' else None
            payload = r.take(size) if kind != 'BSS' else b''
            active = dict(number=next_hunk, node=node['id'], type=kind, record_offset=start,
                          content_offset=payload_offset, allocated_size=alloc['size'],
                          declared_size=size, initialized_size=len(payload),
                          zero_fill_size=alloc['size'] - len(payload), sha256=sha256(payload) if payload else None,
                          memory_flags_raw=alloc['memory_flags_raw'])
            hunks.append(active)
            node['hunks'].append(next_hunk)
            next_hunk += 1
            rec.update(logical_hunk=active['number'], segment=active)
        elif kind in ('RELOC32','RELOC16','RELOC8','DREL16','DREL8','RELRELOC32','ABSRELOC16','RELOC32SHORT','DREL32'):
            require(active is not None and active['type'] != 'BSS', 'relocation without initialized segment')
            short = kind in ('RELOC32SHORT','DREL32')
            read = r.u16 if short else r.u32
            width = 1 if kind.endswith('8') else 2 if kind.endswith('16') else 4
            groups = []
            while (count := read()):
                target = read()
                offsets = []
                for _ in range(count):
                    entry_offset = r.pos
                    off = read()
                    require(off + width <= active['initialized_size'], 'relocation site outside content')
                    require(width == 1 or off % 2 == 0, 'unaligned relocation site')
                    offsets.append(off)
                    pos = active['content_offset'] + off
                    relocations.append(dict(source_hunk=active['number'], source_offset=off,
                                            target_hunk=target, type='HUNK_' + kind, width=width,
                                            record_offset=start, entry_offset=entry_offset,
                                            addend_raw=int.from_bytes(data[pos:pos + width], 'big')))
                groups.append(dict(target_hunk=target, offsets=offsets))
            if short and r.pos % 4:
                require(r.u16() == 0, 'nonzero short-relocation alignment')
            rec['groups'] = groups
        elif kind == 'END':
            require(active is not None, f'END without hunk at 0x{start:x}')
            active = None
        elif kind == 'OVERLAY':
            require(overlay is None and active is None and len(nodes) == 1
                    and next_hunk == node['last_hunk'] + 1, 'invalid overlay position')
            upper_bound = r.u32()
            offset = r.pos
            payload = r.take((upper_bound + 1) * 4)
            overlay = dict(record_offset=start, content_offset=offset, upper_bound_longs=upper_bound,
                           payload_size=len(payload), words=list(struct.unpack('>' + 'I' * (upper_bound + 1), payload)))
            rec['overlay'] = overlay
        elif kind == 'BREAK':
            require(node is not None and active is None and next_hunk == node['last_hunk'] + 1,
                    'BREAK in incomplete node')
        elif kind in ('NAME','UNIT'):
            rec['name'] = r.string(r.u32())
        elif kind == 'SYMBOL':
            require(active is not None, 'SYMBOL outside segment')
            symbols = []
            while (n := r.u32()):
                symbols.append(dict(name=r.string(n), value=r.u32()))
            rec['symbols'] = symbols
        elif kind == 'DEBUG':
            require(active is not None, 'DEBUG outside segment')
            n = r.u32() * 4
            rec.update(payload_offset=r.pos, payload_size=n, sha256=sha256(r.take(n)))
        elif kind == 'EXT':
            require(active is not None, 'EXT outside segment')
            entries = []
            while (raw := r.u32()):
                etype, n = raw >> 24, raw & 0xffffff
                e = dict(type_raw=etype, name=r.string(n))
                if etype in (0,1,2,3):
                    e['value'] = r.u32()
                elif etype in (129,131,132,133,134,135,136,138,139):
                    e['references'] = [r.u32() for _ in range(r.u32())]
                elif etype in (130,137):
                    e['common_size'] = r.u32()
                    e['references'] = [r.u32() for _ in range(r.u32())]
                else:
                    raise FormatError(f'unsupported EXT {etype} at 0x{start:x}')
                entries.append(e)
            rec['entries'] = entries
        else:
            raise FormatError(f'unsupported HUNK_{kind} at 0x{start:x}')
        rec['end_offset'] = r.pos
        rec['file_size'] = r.pos - start
        records.append(rec)
    require(nodes and records[0]['type'] == 'HUNK_HEADER' and active is None
            and next_hunk == node['last_hunk'] + 1, 'incomplete load file')
    if overlay is not None:
        require(len(nodes) > 1 and records[-1]['type'] == 'HUNK_BREAK', 'incomplete overlay file: final BREAK missing')
    numbers = [h['number'] for h in hunks]
    require(len(set(numbers)) == len(numbers), 'reused logical hunk numbers unsupported')
    for rel in relocations:
        require(rel['target_hunk'] in numbers, f'unknown relocation target {rel["target_hunk"]}')
    counts = dict(sorted(Counter(x['type'] for x in records).items()))
    return dict(schema_version=1, size=len(data), sha256=sha256(data), records=records,
                hunks=hunks, nodes=nodes, record_counts=counts, relocations=relocations,
                absent_records=['HUNK_' + k for k in TYPES.values() if 'HUNK_' + k not in counts],
                overlay=overlay, accounted_file_bytes=sum(x['file_size'] for x in records), unparsed_bytes=0)


def manx_overlay(model, data):
    """Cross-check the *observed* Manx dialect, including empty slots.

    This fixture counts 14 eight-byte slots, one empty. Do not substitute the
    manual's inconsistent od-1 array dimension for measurements on this file.
    """
    ov = model['overlay']
    require(ov is not None, 'no overlay table')
    base, end = ov['content_offset'], ov['content_offset'] + ov['payload_size']
    slots = int.from_bytes(data[base:base + 4], 'big')
    require(0 < slots <= 256 and base + 4 + slots * 8 <= end, 'invalid Manx slot count')
    nodes = {n['header_offset']: n for n in model['nodes'][1:]}
    segments = {h['number']: h for h in model['hunks']}
    dh = segments[1]
    require(dh['type'] == 'DATA', 'expected resident DATA at hunk 1')
    entries, targets, manager_targets = [], set(), set()
    for i in range(slots):
        file_offset, trampoline, symoff = struct.unpack_from('>IHH', data, base + 4 + i * 8)
        e = dict(slot=i, descriptor_offset=base + 4 + i * 8,
                 header_offset=file_offset, trampoline_offset=trampoline, symbol_table_offset=symoff)
        if file_offset == 0:
            require(trampoline == symoff == 0, 'partially empty overlay slot')
            e.update(status='EMPTY', node=None, symbols=[])
        else:
            require(file_offset in nodes and file_offset not in targets, 'overlay offset does not uniquely identify a node')
            targets.add(file_offset)
            n = nodes[file_offset]
            e.update(status='OBSERVED', node=n['id'], symbols=[])
            p = base + 4 + symoff
            require(p >= base + 4 + slots * 8 and p % 4 == 0, 'invalid overlay symbol-table offset')
            t = trampoline
            while True:
                require(p + 4 <= end, 'unterminated overlay symbol table')
                h, count = struct.unpack_from('>HH', data, p)
                p += 4
                if h == 0:
                    require(count == 0, 'nonzero overlay terminator')
                    break
                require(h in n['hunks'] and count > 0, 'overlay symbol targets wrong node')
                for _ in range(count):
                    require(t + 8 <= dh['initialized_size'], 'trampoline exceeds DATA hunk')
                    tp = dh['content_offset'] + t
                    opcode, displacement, encoded = struct.unpack_from('>HhI', data, tp)
                    target = encoded & 0xffffff
                    require(opcode == 0x6100 and encoded >> 24 == i + 1, 'invalid Manx trampoline (fixture uses one-based node IDs)')
                    require(target % 2 == 0 and target < segments[h]['initialized_size'], 'invalid overlay entry offset')
                    bridge = t + 2 + displacement
                    require(0 <= bridge and bridge + 6 <= dh['initialized_size'], 'trampoline bridge outside DATA')
                    bp = dh['content_offset'] + bridge
                    require(data[bp:bp + 2] == b'\x4e\xf9', 'expected JMP absolute bridge')
                    rr = [x for x in model['relocations'] if x['source_hunk'] == 1 and x['source_offset'] == bridge + 2
                          and x['type'] == 'HUNK_RELOC32']
                    require(len(rr) == 1 and rr[0]['target_hunk'] == 0, 'bridge must relocate to resident CODE')
                    manager_targets.add(rr[0]['addend_raw'])
                    e['symbols'].append(dict(target_hunk=h, target_offset=target,
                                              trampoline_hunk=1, trampoline_offset=t, bridge_offset=bridge, encoded_node_id=i + 1,
                                              manager_hunk=0, manager_offset=rr[0]['addend_raw'],
                                              name_origin='RECONSTRUCTED_ADDRESS', confidence='OBSERVED'))
                    t += 8
        entries.append(e)
    require(targets == set(nodes), 'overlay table does not account for all physical nodes')
    return dict(schema_version=1, topology='MANX_FLAT', interpretation='table and trampolines cross-validated; compiler version unresolved',
                root='resident', table_record_offset=ov['record_offset'], slot_count=slots,
                physical_overlay_count=len(nodes), node_id_base=1, slots=entries, manager_entry_offsets=sorted(manager_targets),
                breaks=[r['file_offset'] for r in model['records'] if r['type'] == 'HUNK_BREAK'])
