"""Read-only DOS MZ/overlay and observed 16-byte RB EXEPACK census.

This is a secondary oracle. No output from this tool is a reconstruction input.
The unpacked root image is written only on explicit request to ignored build/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'assets/dos/DUCKTALE.EXE'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def mz(data, start=0):
    require(start + 28 <= len(data) and data[start:start+2] == b'MZ',
            'missing MZ header')
    fields = struct.unpack_from('<14H', data, start)
    (_, last, pages, count, paragraphs, minimum, maximum, ss, sp,
     checksum, ip, cs, table, overlay_number) = fields
    size = (pages - 1) * 512 + (last or 512)
    header = paragraphs * 16
    require(pages and last <= 511 and 28 <= header <= size <= len(data)-start,
            'invalid MZ bounds')
    require(28 <= table and table + count * 4 <= header,
            'MZ relocation table outside header')
    raw_sites = []
    for i in range(count):
        offset, segment = struct.unpack_from('<HH', data, start+table+4*i)
        raw_sites.append((segment, offset))
    # Microsoft overlay headers use a shared overlay load window. The minimum
    # segment is the observed window base in each of these ten records; retain
    # the raw coordinates as well as the normalized, bounds-checked sites.
    base = min((segment for segment, _ in raw_sites), default=0) if overlay_number else 0
    sites = []
    for segment, offset in raw_sites:
        linear = (segment-base)*16 + offset
        require(linear+2 <= size-header, 'MZ relocation outside normalized load image')
        sites.append(dict(segment=segment, offset=offset, load_offset=linear))
    return dict(file_start=start, file_end=start+size, size=size, header_bytes=header,
                load_bytes=size-header, relocation_count=count, relocations=sites,
                relocation_coordinate_base_segment=base,
                minalloc=minimum, maxalloc=maximum, ss=ss, sp=sp, cs=cs, ip=ip,
                checksum=checksum, overlay_number=overlay_number,
                sha256=digest(data[start:start+size]))


def overlay_chain(data):
    root = mz(data)
    require(root['overlay_number'] == 0, 'root has nonzero overlay number')
    cursor = root['file_end']
    overlays = []
    while cursor < len(data):
        at = (cursor+511) & ~511
        require(at < len(data) and data[cursor:at] == bytes(at-cursor),
                'nonzero or truncated overlay alignment')
        item = mz(data, at)
        require(item['overlay_number'] == len(overlays)+1,
                'nonsequential overlay number')
        item['alignment_before_bytes'] = at-cursor
        overlays.append(item)
        cursor = item['file_end']
    require(cursor == len(data), 'trailing bytes outside overlay chain')
    return root, overlays


def decompress_reverse(data, size):
    """EXEPACK backward fill/copy stream; require full destination coverage."""
    require(0 < size <= 0x100000, 'unreasonable EXEPACK destination')
    out = bytearray(data + bytes(max(0, size-len(data))))
    src, dst = len(data), size
    # Observed EXEPACK stream ends in up to 15 FF alignment bytes.
    for _ in range(15):
        if src and out[src-1] == 0xff:
            src -= 1
        else:
            break
    commands = []
    while True:
        require(src >= 3, 'truncated EXEPACK command')
        op = out[src-1]
        count = struct.unpack_from('<H', out, src-3)[0]
        src -= 3
        require(count and dst >= count, 'EXEPACK destination underflow')
        dst -= count
        if op & 0xfe == 0xb0:
            require(src >= 1, 'truncated EXEPACK fill')
            src -= 1
            out[dst:dst+count] = bytes([out[src]])*count
            kind = 'fill'
        elif op & 0xfe == 0xb2:
            require(src >= count, 'truncated EXEPACK copy')
            src -= count
            for i in range(count-1, -1, -1):
                out[dst+i] = out[src+i]
            kind = 'copy'
        else:
            raise ValueError('unknown EXEPACK command %02x' % op)
        commands.append(dict(kind=kind, packed_start=src,
                             unpacked_start=dst, size=count))
        if op & 1:
            break
    require(dst <= len(data), 'EXEPACK leaves unknown destination prefix')
    return bytes(out[:size]), commands, dst


def unpack_root(data, root):
    require(root['relocation_count'] == 0 and root['ip'] == 16,
            'not the observed EXEPACK outer MZ profile')
    body = data[root['header_bytes']:root['file_end']]
    at = root['cs']*16
    require(at+16 <= len(body), 'EXEPACK header outside root image')
    ip, cs, scratch, block_size, sp, ss, dest, signature = struct.unpack_from('<8H', body, at)
    require(signature == 0x4252 and at+block_size == len(body),
            'not the observed 16-byte RB EXEPACK block')
    block = body[at:]
    suffix = b'\xcd\x21\xb8\xff\x4c\xcd\x21Packed file is corrupt'
    require(block.count(suffix) == 1, 'unknown EXEPACK stub suffix')
    pointer = block.index(suffix)+len(suffix)
    relocations = []
    for bank in range(16):
        require(pointer+2 <= len(block), 'truncated EXEPACK relocation bank')
        count = struct.unpack_from('<H', block, pointer)[0]
        pointer += 2
        require(pointer+count*2 <= len(block), 'truncated EXEPACK relocation sites')
        for i in range(count):
            offset = struct.unpack_from('<H', block, pointer+i*2)[0]
            linear = bank*65536+offset
            require(linear+2 <= dest*16, 'EXEPACK relocation outside root image')
            relocations.append(dict(segment=bank*4096, offset=offset,
                                    load_offset=linear))
        pointer += count*2
    require(pointer == len(block), 'unparsed EXEPACK relocation bytes')
    require(len({x['load_offset'] for x in relocations}) == len(relocations),
            'duplicate EXEPACK relocation')
    image, commands, prefix = decompress_reverse(body[:at], dest*16)
    return image, dict(format='RB_EXEPACK_16', packed_header_load_offset=at,
                       original_cs=cs, original_ip=ip, original_ss=ss,
                       original_sp=sp, scratch=scratch, block_size=block_size,
                       destination_paragraphs=dest, stub_sha256=digest(block[16:block.index(suffix)]),
                       relocation_count=len(relocations), relocations=relocations,
                       command_count=len(commands), unchanged_prefix_bytes=prefix,
                       unpacked_bytes=len(image), unpacked_sha256=digest(image))


def analyze(data):
    root, overlays = overlay_chain(data)
    image, packed = unpack_root(data, root)
    return image, dict(schema_version=1, role='SECONDARY_DOS_ORACLE',
                       executable_sha256=digest(data), file_bytes=len(data),
                       root=root, root_exepack=packed, overlays=overlays,
                       unparsed_file_bytes=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=EXE)
    parser.add_argument('--write-root-image', type=Path,
                        help='explicitly write derived image, normally build/dos/root-image.bin')
    parser.add_argument('--write', type=Path, help='write measured JSON census')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()
    image, result = analyze(args.exe.read_bytes())
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(result, indent=2)+'\n')
    if args.write_root_image:
        args.write_root_image.parent.mkdir(parents=True, exist_ok=True)
        args.write_root_image.write_bytes(image)
    if args.summary:
        print('DOS EXE: %d bytes; packed root %d bytes; unpacked root %d bytes; '
              '%d overlay MZs; %d root relocations after unpacking' %
              (result['file_bytes'], result['root']['size'], len(image),
               len(result['overlays']), result['root_exepack']['relocation_count']))
        for row in result['overlays']:
            print('  ov%02d file %05x..%05x load %d relocations %d' %
                  (row['overlay_number'], row['file_start'], row['file_end'],
                   row['load_bytes'], row['relocation_count']))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
