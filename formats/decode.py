"""Decode indexed DuckTales .arc/.as files stored on the supplied ADFs.

The strict OFS reader extracts each file. decoded_payload preserves the
container-level convention used by existing callers (only kind 4 is expanded
there); record_output models bytes produced by the exact record loader for
kinds 1, 2, 4, 5, and 6.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSETS = ROOT / "assets"
DEFAULT_INVENTORY = ROOT / "evidence" / "assets.json"
MAX_INDEX_ENTRIES = 104  # resident_F_2816's G_h01_A7EE[104] bound
ENTRY_HEADER_SIZE = 16
LZW_CLEAR = 0x100
LZW_END = 0x101
LZW_FIRST = 0x102
LZW_MAX_BITS = 12
BITMAP_DEPTH = 5  # resident DATA G_h01_0970 (+0x970), also read by 3A6E

# Signed 16-bit tables read by resident_F_4184 from resident DATA:
# G_h01_1E32[8] and G_h01_1E42[49].
ADPCM_INDEX_DELTA = (-1, -1, -1, -1, 2, 4, 6, 8)
ADPCM_STEP = (
    16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66,
    73, 80, 88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230, 253,
    279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876,
    963, 1060, 1166, 1282, 1411, 1552,
)


@dataclass(frozen=True)
class Record:
    """One unique record body referenced by an asset's offset table."""

    offset: int
    end: int
    stored_size: int
    kind: int
    metadata: tuple[int, int, int, int, int]
    stored_payload: bytes
    decoded_payload: bytes
    record_output: bytes
    codec_input_consumed: int
    image_width: int | None = None
    image_height: int | None = None
    image_row_bytes: int | None = None
    image_depth: int | None = None


@dataclass(frozen=True)
class DecodedAsset:
    """An indexed asset, with logical references kept in table order."""

    path: str
    disk_image: str
    source_size: int
    source_sha256: str
    offsets: tuple[int, ...]
    unique_records: tuple[Record, ...]
    entries: tuple[Record, ...]
    decoded_size: int
    decoded_sha256: str
    record_output_size: int
    record_output_sha256: str


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_lsb_code(data: bytes, bit_offset: int, width: int) -> int:
    """Read low-order-first code bits, as resident_F_3E9C does."""

    if bit_offset < 0 or width <= 0 or bit_offset + width > len(data) * 8:
        raise ValueError(
            f"truncated LZW code at bit {bit_offset} (width {width}, "
            f"input {len(data)} bytes)"
        )
    byte_offset, shift = divmod(bit_offset, 8)
    window = int.from_bytes(data[byte_offset : byte_offset + 3], "little")
    return (window >> shift) & ((1 << width) - 1)


def decode_lzw(data: bytes, expected_size: int | None = None) -> bytes:
    """Decode the game's clear/end-code LZW stream.

    resident_F_3C4C and resident_F_3E9C establish CLEAR=0x100, END=0x101,
    first dictionary code=0x102, 9-to-12-bit widths, and LSB-first packing.
    """

    bit_offset = 0
    width = 9
    next_code = LZW_FIRST
    table: dict[int, bytes] = {code: bytes((code,)) for code in range(256)}
    output = bytearray()
    previous: bytes | None = None
    saw_initial_clear = False

    while True:
        code = _read_lsb_code(data, bit_offset, width)
        bit_offset += width
        if code == LZW_CLEAR:
            if not saw_initial_clear and bit_offset != 9:
                raise ValueError("LZW stream does not begin with a clear code")
            width = 9
            next_code = LZW_FIRST
            table = {value: bytes((value,)) for value in range(256)}
            previous = None
            saw_initial_clear = True
            continue
        if not saw_initial_clear:
            raise ValueError("LZW stream does not begin with a clear code")
        if code == LZW_END:
            decoded = bytes(output)
            if expected_size is not None and len(decoded) != expected_size:
                raise ValueError(
                    f"LZW output size {len(decoded)} != header size {expected_size}"
                )
            return decoded

        if previous is None:
            if code not in table:
                raise ValueError(f"invalid first LZW data code 0x{code:x}")
            entry = table[code]
        elif code in table:
            entry = table[code]
        elif code == next_code:
            # KwKwK case; the game takes its code>=next dictionary path here.
            entry = previous + previous[:1]
        else:
            raise ValueError(
                f"invalid LZW code 0x{code:x}; next dictionary code is "
                f"0x{next_code:x}"
            )

        output.extend(entry)
        if expected_size is not None and len(output) > expected_size:
            raise ValueError("LZW output exceeds the record's declared size")
        if previous is not None and next_code < (1 << LZW_MAX_BITS):
            table[next_code] = previous + entry[:1]
            next_code += 1
            if next_code == (1 << width) and width < LZW_MAX_BITS:
                width += 1
        previous = entry




def _read_rle_byte(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError(f"truncated kind-1/2 RLE stream at input byte {offset}")
    return data[offset], offset + 1


def decode_bitmap_rle(
    data: bytes,
    *,
    width: int,
    rows: int,
    row_bytes: int,
    depth: int = BITMAP_DEPTH,
) -> tuple[bytes, int]:
    """Apply resident_F_404A to the bitmap descriptor constructed by 291E.

    The source loops through low-byte columns, then planes, then rows. Its
    remaining counter is unsigned 16-bit, matching the recovered C.
    """

    width &= 0xFFFF
    rows &= 0xFFFF
    row_bytes &= 0xFFFF
    depth &= 0xFF
    stride = row_bytes & 0xFF  # F404A casts bitmap->width to unsigned char
    if stride == 0:
        raise ValueError("404A bitmap row stride has a zero low byte")

    numerator = (rows * row_bytes) & 0xFFFF  # 16-bit unsigned C multiply
    row_count = numerator // stride
    plane_size = rows * row_bytes
    written_per_plane = row_count * stride
    if written_per_plane != plane_size:
        raise ValueError(
            "404A's 16-bit row calculation leaves bitmap allocation bytes "
            f"unwritten (width={width}, rows={rows}, row_bytes={row_bytes})"
        )

    output = bytearray(plane_size * depth)
    input_offset = 0
    remaining = 0
    literal = False
    repeated_value = 0

    for column in range(stride):
        for plane in range(depth):
            output_offset = plane * plane_size + column
            for _row in range(row_count):
                if remaining == 0:
                    token, input_offset = _read_rle_byte(data, input_offset)
                    remaining = token & 0x7F
                    if token & 0x80:
                        literal = True
                    else:
                        literal = False
                        repeated_value, input_offset = _read_rle_byte(data, input_offset)
                remaining = (remaining - 1) & 0xFFFF
                if literal:
                    value, input_offset = _read_rle_byte(data, input_offset)
                else:
                    value = repeated_value
                output[output_offset] = value
                output_offset += stride

    return bytes(output), input_offset


def _signed16(value: int) -> int:
    value &= 0xFFFF
    return value if value < 0x8000 else value - 0x10000


def decode_adpcm(data: bytes, *, length: int | None = None) -> bytes:
    """Port resident_F_4184, including its 16-bit C int arithmetic."""

    if length is None:
        length = len(data)
    if length < 0 or length > len(data):
        raise ValueError(f"kind-5 stored length {length} exceeds input {len(data)}")
    # F4184 uses a signed 16-bit int loop variable. A larger positive long
    # would not terminate after i wraps from 32767 to -32768.
    if length > 0x7FFF:
        raise ValueError(f"kind-5 length {length} exceeds the terminating 16-bit C loop")

    sample = 0
    index = 1
    output = bytearray()
    for packed in data[:length]:
        for nibble in ((packed >> 4) & 0x0F, packed & 0x0F):
            bit4 = nibble & 4
            bit2 = nibble & 2
            bit1 = nibble & 1
            magnitude = bit4 + bit2 + bit1

            step = ADPCM_STEP[index - 1]
            half = step >> 1
            quarter = half >> 1
            delta = quarter >> 1
            index += ADPCM_INDEX_DELTA[magnitude]
            if index < 1:
                index = 1
            elif index > 49:
                index = 49

            if bit1:
                delta += quarter
            if bit2:
                delta += half
            if bit4:
                delta += step
            sample = _signed16(sample - delta if nibble & 8 else sample + delta)
            output.append((sample >> 4) & 0xFF)
    return bytes(output)


def _record_output(
    kind: int,
    payload: bytes,
    stored_size: int,
    metadata: tuple[int, int, int, int, int],
    rle_input: bytes,
) -> tuple[bytes, int, tuple[int | None, int | None, int | None, int | None]]:
    """Return game-facing output, input bytes consumed, and image shape."""

    if kind == 1:
        width, rows = metadata[0], metadata[1]
        row_bytes = width >> 3  # F3B16 stores width >> 3 in BytesPerRow
        output, consumed = decode_bitmap_rle(
            rle_input, width=width, rows=rows, row_bytes=row_bytes
        )
        return output, consumed, (width, rows, row_bytes, BITMAP_DEPTH)
    if kind == 2:
        width, rows, multiplier = metadata[0], metadata[1], metadata[2]
        row_bytes = ((width >> 3) * multiplier) & 0xFFFF  # resident_F_291E
        output, consumed = decode_bitmap_rle(
            rle_input, width=width, rows=rows, row_bytes=row_bytes
        )
        return output, consumed, (width, rows, row_bytes, BITMAP_DEPTH)
    if kind == 4:
        output = decode_lzw(payload, expected_size=metadata[0])
        return output, len(payload), (None, None, None, None)
    if kind == 5:
        output = decode_adpcm(payload, length=stored_size)
        if len(output) != metadata[0]:
            raise ValueError(
                f"kind-5 output size {len(output)} != header +6 size {metadata[0]}"
            )
        return output, len(payload), (None, None, None, None)
    if kind == 6 and len(payload) > metadata[4]:
        raise ValueError(
            f"kind-6 read size {len(payload)} exceeds header +14 allocation {metadata[4]}"
        )
    # 291E allocates +14 bytes, then reads +0 stored bytes. The bytes beyond
    # the completed Read are not initialized by this loader and stay UNKNOWN.
    return payload, len(payload), (None, None, None, None)


def decode_indexed_asset(path: str, disk_image: str, data: bytes) -> DecodedAsset:
    """Parse an indexed asset and model each recognized loader output."""

    if len(data) < 2:
        raise ValueError(f"{path}: truncated entry count")
    count = struct.unpack_from("<H", data, 0)[0]
    if count > MAX_INDEX_ENTRIES:
        raise ValueError(f"{path}: {count} entries exceeds loader limit {MAX_INDEX_ENTRIES}")
    table_end = 2 + count * 4
    if table_end > len(data):
        raise ValueError(f"{path}: truncated offset table")
    offsets = struct.unpack_from(f"<{count}I", data, 2) if count else ()
    if any(offset < table_end or offset >= len(data) for offset in offsets):
        raise ValueError(f"{path}: offset lies outside the record area")

    starts = sorted(set(offsets))
    records: dict[int, Record] = {}
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(data)
        if end - start < ENTRY_HEADER_SIZE:
            raise ValueError(f"{path}: record at {start} is shorter than its header")
        stored_size, kind = struct.unpack_from("<IH", data, start)
        metadata = struct.unpack_from("<5H", data, start + 6)
        payload_start = start + ENTRY_HEADER_SIZE
        payload_end = payload_start + stored_size
        if payload_end != end:
            raise ValueError(
                f"{path}: record at {start} declares {stored_size} payload bytes, "
                f"but its indexed span has {end - payload_start}"
            )
        payload = data[payload_start:payload_end]
        # Keep the existing container-decoding field stable. The full game
        # record-loader result is independently exposed as record_output.
        decoded = (
            decode_lzw(payload, expected_size=metadata[0])
            if kind == 4
            else payload
        )
        # 404A has no stored-size argument. Its behavioral byte reader
        # refills from the archive handle in 1024-byte chunks, so supply the
        # remaining file stream for kinds 1/2; other codecs use payload only.
        output, consumed, image_shape = _record_output(
            kind, payload, stored_size, metadata, data[payload_start:]
        )
        records[start] = Record(
            offset=start,
            end=end,
            stored_size=stored_size,
            kind=kind,
            metadata=metadata,
            stored_payload=payload,
            decoded_payload=decoded,
            record_output=output,
            codec_input_consumed=consumed,
            image_width=image_shape[0],
            image_height=image_shape[1],
            image_row_bytes=image_shape[2],
            image_depth=image_shape[3],
        )

    entries = tuple(records[offset] for offset in offsets)
    decoded_size = sum(len(entry.decoded_payload) for entry in entries)
    decoded_hash = hashlib.sha256()
    output_hash = hashlib.sha256()
    for entry in entries:
        decoded_hash.update(entry.decoded_payload)
        output_hash.update(entry.record_output)
    return DecodedAsset(
        path=path,
        disk_image=disk_image,
        source_size=len(data),
        source_sha256=_sha256(data),
        offsets=tuple(offsets),
        unique_records=tuple(records[start] for start in starts),
        entries=entries,
        decoded_size=decoded_size,
        decoded_sha256=decoded_hash.hexdigest(),
        record_output_size=sum(len(entry.record_output) for entry in entries),
        record_output_sha256=output_hash.hexdigest(),
    )


def _ofs_disk_class():
    """Import the repository's strict OFS implementation without third parties."""

    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    from ofs import OFSDisk  # type: ignore[import-not-found]

    return OFSDisk


def load_supplied_assets(
    assets_dir: Path = DEFAULT_ASSETS,
    inventory_path: Path = DEFAULT_INVENTORY,
) -> list[DecodedAsset]:
    """Read every inventoried .arc/.as from the supplied OFS disk images."""

    disk_paths = sorted(Path(assets_dir).glob("*.adf"))
    if not disk_paths:
        raise ValueError(f"no .adf disk images found under {assets_dir}")
    inventory_doc = json.loads(Path(inventory_path).read_text(encoding="utf-8"))
    expected = {row["path"]: row for row in inventory_doc["files"]}
    seen: set[str] = set()
    results: list[DecodedAsset] = []
    OFSDisk = _ofs_disk_class()

    for disk_path in disk_paths:
        disk = OFSDisk(disk_path.read_bytes())
        summary = disk.parse()
        volume = summary["volume"]
        for relative_path, contents in disk.files.items():
            if Path(relative_path).suffix.lower() not in {".arc", ".as"}:
                continue
            asset_path = f"{volume}:{relative_path}"
            row = expected.get(asset_path)
            if row is None:
                raise ValueError(f"{asset_path}: not present in evidence/assets.json")
            if len(contents) != row["size"] or _sha256(contents) != row["sha256"]:
                raise ValueError(f"{asset_path}: supplied bytes disagree with inventory")
            seen.add(asset_path)
            results.append(decode_indexed_asset(asset_path, disk_path.name, contents))

    missing = sorted(set(expected) - seen)
    if missing:
        raise ValueError("inventoried asset(s) missing from supplied disks: " + ", ".join(missing))
    return sorted(results, key=lambda item: item.path)


def _format_asset(asset: DecodedAsset) -> str:
    kinds: dict[int, int] = {}
    for record in asset.unique_records:
        kinds[record.kind] = kinds.get(record.kind, 0) + 1
    kind_text = ",".join(f"{kind}:{kinds[kind]}" for kind in sorted(kinds)) or "none"
    return (
        f"{asset.path}: entries={len(asset.entries)} unique={len(asset.unique_records)} "
        f"kinds={kind_text} stored={asset.source_size} "
        f"container_decoded={asset.decoded_size} container_sha256={asset.decoded_sha256} "
        f"loader_output={asset.record_output_size} "
        f"loader_output_sha256={asset.record_output_sha256}"
    )


def _grayscale_png(record: Record) -> bytes:
    """Encode the visible planar extent with a grey ramp (palette unknown)."""

    if None in (
        record.image_width, record.image_height,
        record.image_row_bytes, record.image_depth,
    ):
        raise ValueError("PNG requested for a non-bitmap record")
    width = int(record.image_width)
    height = int(record.image_height)
    row_bytes = int(record.image_row_bytes)
    depth = int(record.image_depth)
    plane_size = row_bytes * height
    if width > row_bytes * 8:
        raise ValueError("bitmap pixel width exceeds decoded row storage")

    maximum = (1 << depth) - 1
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)  # PNG filter type 0
        for x in range(width):
            mask = 1 << (7 - (x & 7))
            color_index = 0
            byte_index = y * row_bytes + (x >> 3)
            for plane in range(depth):
                plane_byte = record.record_output[plane * plane_size + byte_index]
                if plane_byte & mask:
                    color_index |= 1 << plane
            scanlines.append(color_index * 255 // maximum)

    def chunk(tag: bytes, content: bytes) -> bytes:
        return (
            struct.pack(">I", len(content)) + tag + content
            + struct.pack(">I", zlib.crc32(tag + content) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
        + chunk(b"IEND", b"")
    )


def dump_bitmaps(assets: Iterable[DecodedAsset], output_dir: Path) -> int:
    """Write all kind-1/2 bitmap previews; return the number of PNG files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    dumped = 0
    for asset in assets:
        asset_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", asset.path)
        for index, record in enumerate(asset.entries):
            if record.kind not in (1, 2):
                continue
            name = (
                f"{asset_stem}_entry{index:03d}_offset{record.offset:08x}_"
                f"kind{record.kind}.png"
            )
            (output_dir / name).write_bytes(_grayscale_png(record))
            dumped += 1
    return dumped


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--verbose", action="store_true", help="print each indexed entry")
    parser.add_argument(
        "--dump", type=Path,
        help="write kind-1/2 bitmap previews as grey-ramp PNGs under DIR",
    )
    args = parser.parse_args(argv)
    try:
        assets = load_supplied_assets(args.assets_dir, args.inventory)
    except (OSError, ValueError, KeyError, struct.error) as exc:
        print(f"decode: {exc}", file=sys.stderr)
        return 2
    for asset in assets:
        print(_format_asset(asset))
        if args.verbose:
            for index, record in enumerate(asset.entries):
                print(
                    f"  [{index:03}] offset=0x{record.offset:x} kind={record.kind} "
                    f"stored={len(record.stored_payload)} "
                    f"container_decoded={len(record.decoded_payload)} "
                    f"loader_output={len(record.record_output)} "
                    f"output_sha256={_sha256(record.record_output)} "
                    f"metadata={record.metadata}"
                    + (
                        f" rle_input_consumed={record.codec_input_consumed} "
                        f"image={record.image_width}x{record.image_height} "
                        f"row_bytes={record.image_row_bytes} depth={record.image_depth}"
                        if record.kind in (1, 2) else ""
                    )
                )
    if args.dump:
        print(f"png_bitmaps={dump_bitmaps(assets, args.dump)} output_dir={args.dump}")
    print(f"decoded_files={len(assets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
