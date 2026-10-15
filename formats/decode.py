"""Decode indexed DuckTales .arc/.as files stored on the supplied ADFs.

The repository's strict OFS reader extracts files. Kind-4 LZW records are
expanded. Kind-1/2 RLE is established in formats/arc.md but remains stored
byte-for-byte here; other record payloads are also preserved unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
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


def decode_indexed_asset(path: str, disk_image: str, data: bytes) -> DecodedAsset:
    """Parse a count/offset indexed asset and expand its known LZW records."""

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
        decoded = (
            decode_lzw(payload, expected_size=metadata[0])
            if kind == 4
            else payload
        )
        records[start] = Record(
            offset=start,
            end=end,
            stored_size=stored_size,
            kind=kind,
            metadata=metadata,
            stored_payload=payload,
            decoded_payload=decoded,
        )

    entries = tuple(records[offset] for offset in offsets)
    decoded_size = sum(len(entry.decoded_payload) for entry in entries)
    decoded_hash = hashlib.sha256()
    for entry in entries:
        decoded_hash.update(entry.decoded_payload)
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
        f"kinds={kind_text} stored={asset.source_size} decoded={asset.decoded_size} "
        f"decoded_sha256={asset.decoded_sha256}"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--verbose", action="store_true", help="print each indexed entry")
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
                    f"decoded={len(record.decoded_payload)} "
                    f"decoded_sha256={_sha256(record.decoded_payload)}"
                )
    print(f"decoded_files={len(assets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
