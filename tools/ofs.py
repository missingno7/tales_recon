"""Read-only DD AmigaDOS DOS\0 census. Fail closed on damaged file topology.

On-disk field reference: https://adflib.github.io/FAQ/adf_info.html
Boot checksum and bitmap validity are observations, not repaired disk contents.
"""
import struct
from datetime import datetime, timedelta
from common import require, sha256


def words(data):
    return struct.unpack('>' + 'I' * (len(data) // 4), data)


def bstr(data, offset, maximum):
    n = data[offset]
    require(n <= maximum, f'oversized BSTR at {offset}')
    return data[offset + 1:offset + 1 + n].decode('latin-1')


def stamp(w, offset):
    days, minutes, ticks = w[offset:offset + 3]
    valid = minutes < 1440 and ticks < 3000
    return dict(days=days, minutes=minutes, ticks=ticks, timezone='unspecified',
                iso_local=(datetime(1978, 1, 1) + timedelta(days=days, minutes=minutes,
                           seconds=ticks / 50)).isoformat() if valid and days < 1000000 else None)


def name_hash(name):
    value = len(name)
    for c in name.encode('latin-1'):
        value = (value * 13 + (c - 32 if 97 <= c <= 122 else c)) & 0x7ff
    return value % 72


class OFSDisk:
    def __init__(self, data):
        require(len(data) == 901120, 'only 1760-sector DD images are supported')
        require(data[:4] == b'DOS\0', 'expected non-international OFS DOS\0')
        self.data = data
        self.owners = {0: 'boot', 1: 'boot'}
        self.entries = []
        self.files = {}

    def block(self, number, owner):
        require(2 <= number < 1760, f'{owner}: invalid block {number}')
        require(number not in self.owners, f'block {number}: duplicate use by {owner}')
        self.owners[number] = owner
        raw = self.data[number * 512:(number + 1) * 512]
        w = words(raw)
        require(sum(w) & 0xffffffff == 0, f'block {number}: bad checksum')
        return raw, w

    def file(self, header, w, path):
        pointers, extensions = [], []
        current = w
        while True:
            count = current[2]
            require(count <= 72, f'{path}: too many data pointers')
            pointers.extend(reversed(current[78 - count:78]))
            require(not any(current[6:78 - count]), f'{path}: unused data pointers are nonzero')
            nxt = current[126]
            if not nxt:
                break
            _, current = self.block(nxt, f'{path}:extension')
            require(current[0] == 16 and current[1] == nxt and current[125] == header
                    and current[127] == 0xfffffffd, f'{path}: invalid extension {nxt}')
            extensions.append(nxt)
        chain, chunks, blocks = [], [], []
        nxt = w[4]
        while nxt:
            raw, dw = self.block(nxt, f'{path}:data')
            require(dw[0] == 8 and dw[1] == header and dw[2] == len(chain) + 1,
                    f'{path}: invalid data block {nxt}')
            require(0 < dw[3] <= 488, f'{path}: invalid data size at {nxt}')
            chain.append(nxt)
            chunks.append(raw[24:24 + dw[3]])
            blocks.append(dict(block=nxt, sequence=dw[2], payload_size=dw[3],
                               next_block=dw[4], checksum=dw[5]))
            nxt = dw[4]
        require(chain == pointers, f'{path}: chain and header/extension pointers disagree')
        content = b''.join(chunks)
        require(len(content) == w[81], f'{path}: file size and payload disagree')
        self.files[path] = content
        return dict(size=len(content), sha256=sha256(content), data_blocks=blocks,
                    extension_blocks=extensions, pointer_table_chain=pointers,
                    chain_crosscheck='MATCH', transformation='concatenate OFS payloads; omit 24-byte block headers and unused tails; no content conversion')

    def directory(self, number, w, prefix):
        seen_names = set()
        for bucket, head in enumerate(w[6:78]):
            nxt = head
            while nxt:
                raw, ew = self.block(nxt, f'{prefix}:entry')
                name = bstr(raw, 432, 30)
                require(name and name not in ('.', '..') and not any(c in name for c in '/:\\\0'),
                        f'unsafe/unsupported filename {name!r}')
                key = name.upper()
                require(key not in seen_names, f'duplicate filename {name}')
                seen_names.add(key)
                require(name_hash(name) == bucket, f'{name}: hash bucket mismatch')
                require(ew[0] == 2 and ew[1] == nxt and ew[125] == number,
                        f'{name}: invalid entry header or parent')
                path = prefix + name
                kind = {2: 'directory', 0xfffffffd: 'file'}.get(ew[127])
                require(kind, f'{path}: unsupported secondary type {ew[127]:08x}')
                entry = dict(path=path, kind=kind, header_block=nxt, parent_block=number,
                             hash_bucket=bucket, next_hash=ew[124], protection_raw=ew[80],
                             comment=bstr(raw, 328, 79), date=stamp(ew, 105),
                             uid=ew[79] >> 16, gid=ew[79] & 65535, checksum=ew[5])
                self.entries.append(entry)
                if kind == 'file':
                    entry.update(self.file(nxt, ew, path))
                else:
                    self.directory(nxt, ew, path + '/')
                nxt = ew[124]

    def parse(self):
        raw, root = self.block(880, 'root')
        require(root[0] == 2 and root[3] == 72 and root[127] == 1, 'invalid root block')
        label = bstr(raw, 432, 30)
        self.directory(880, root, '')
        require(root[104] == 0, 'DD bitmap extensions are unsupported')
        maps = [n for n in root[79:104] if n]
        require(len(maps) == 1, 'expected one DD bitmap page')
        _, bitmap = self.block(maps[0], 'bitmap')
        free = [n for n in range(2, 1760) if bitmap[1 + (n - 2) // 32] & (1 << ((n - 2) % 32))]
        allocated = set(range(2, 1760)) - set(free)
        contradictions = sorted(set(self.owners) & set(free))
        require(not contradictions, f'referenced blocks marked free: {contradictions}')
        total = 0
        for v in words(self.data[:1024]):
            total += v
            total = (total & 0xffffffff) + (total >> 32)
        boot = words(self.data[:12])
        return dict(schema_version=1, filesystem='OFS', volume=label, size=len(self.data),
                    sha256=sha256(self.data), block_size=512, block_count=1760, root_block=880,
                    boot=dict(signature_hex=self.data[:4].hex(), checksum=boot[1],
                              checksum_valid=total == 0xffffffff, root_pointer_raw=boot[2],
                              sha256=sha256(self.data[:1024])),
                    root=dict(checksum=root[5], modified=stamp(root, 105),
                              volume_modified=stamp(root, 118), created=stamp(root, 121)),
                    bitmap=dict(blocks=maps, validity_flag_raw=root[78], free_blocks=free,
                                allocated_unreferenced_blocks=sorted(allocated - set(self.owners))),
                    entries=sorted(self.entries, key=lambda e: e['path']),
                    startup_sequences=[dict(path=p, text=b.decode('latin-1'), sha256=sha256(b))
                                       for p, b in sorted(self.files.items()) if p.lower() == 's/startup-sequence'],
                    blocks=[dict(block=n, owner=o) for n, o in sorted(self.owners.items())])
