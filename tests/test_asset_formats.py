"""Structural checks for the supplied DuckTales indexed asset containers."""

from __future__ import annotations

import hashlib

import pytest

from formats.decode import (
    BITMAP_DEPTH,
    DEFAULT_ASSETS,
    ENTRY_HEADER_SIZE,
    MAX_INDEX_ENTRIES,
    decode_adpcm,
    decode_bitmap_rle,
    decode_lzw,
    load_supplied_assets,
)


def _assets_available() -> bool:
    return DEFAULT_ASSETS.is_dir() and any(DEFAULT_ASSETS.glob("*.adf"))


def _pack_9bit_codes(codes: list[int]) -> bytes:
    bits = 0
    width = 0
    for code in codes:
        bits |= code << width
        width += 9
    return bits.to_bytes((width + 7) // 8, "little")


def test_lzw_clear_literal_end_code_order() -> None:
    stream = _pack_9bit_codes([0x100, ord("A"), 0x101])
    assert decode_lzw(stream, expected_size=1) == b"A"


@pytest.mark.skipif(not _assets_available(), reason="supplied assets/ disk images are absent")
def test_all_supplied_assets_decode_and_match_loader_structure() -> None:
    assets = load_supplied_assets()
    assert len(assets) == 17

    for asset in assets:
        assert len(asset.offsets) <= MAX_INDEX_ENTRIES
        assert len(asset.entries) == len(asset.offsets)
        assert len(asset.unique_records) <= len(asset.entries)
        assert sum(len(entry.decoded_payload) for entry in asset.entries) == asset.decoded_size

        decoded_hash = hashlib.sha256()
        for entry in asset.entries:
            assert entry.end > entry.offset
            assert entry.end - entry.offset == ENTRY_HEADER_SIZE + entry.stored_size
            assert len(entry.stored_payload) == entry.stored_size
            if entry.kind == 4:
                # Kind 4's first metadata word is the decompressed byte count.
                assert len(entry.decoded_payload) == entry.metadata[0]
            else:
                # Non-kind-4 bytes are retained as stored streams; kind-1/2 RLE needs bitmap context.
                assert entry.decoded_payload == entry.stored_payload
            decoded_hash.update(entry.decoded_payload)
        assert decoded_hash.hexdigest() == asset.decoded_sha256


def test_404a_rle_column_plane_row_order() -> None:
    emitted = bytes((0x80, 0x40, 0x20, 0x10, 0x08, 0, 0, 0, 0, 0))
    stream = b"".join(bytes((1, value)) for value in emitted)

    output, consumed = decode_bitmap_rle(
        stream, width=16, rows=1, row_bytes=2, depth=5
    )

    assert consumed == len(stream)
    assert output == bytes((0x80, 0, 0x40, 0, 0x20, 0, 0x10, 0, 0x08, 0))


def test_4184_two_zero_nibbles_produce_two_zero_samples() -> None:
    assert decode_adpcm(bytes((0,))) == bytes((0, 0))


@pytest.mark.skipif(
    not DEFAULT_ASSETS.is_dir() or not any(DEFAULT_ASSETS.glob("*.adf")),
    reason="supplied assets/ disk images are absent",
)
def test_supplied_record_outputs_follow_loader_header_fields() -> None:
    for asset in load_supplied_assets():
        output_hash = hashlib.sha256()
        for record in asset.entries:
            output_hash.update(record.record_output)

            if record.kind == 1:
                assert record.image_row_bytes == record.metadata[0] >> 3
                expected = record.image_row_bytes * record.metadata[1] * BITMAP_DEPTH
                assert len(record.record_output) == expected
            elif record.kind == 2:
                row_bytes = (record.metadata[0] >> 3) * record.metadata[2]
                assert record.image_row_bytes == row_bytes
                expected = row_bytes * record.metadata[1] * BITMAP_DEPTH
                assert len(record.record_output) == expected
            elif record.kind == 4:
                assert len(record.record_output) == record.metadata[0]
            elif record.kind == 5:
                assert len(record.record_output) == record.metadata[0]
                assert len(record.record_output) == 2 * record.stored_size
            elif record.kind == 6:
                # +14 is the allocated capacity; Read fills only +0 bytes.
                assert record.metadata[4] >= record.stored_size
                assert len(record.record_output) == record.stored_size
            elif record.kind == 3:
                assert len(record.record_output) == record.stored_size

        assert output_hash.hexdigest() == asset.record_output_sha256


@pytest.mark.skipif(
    not DEFAULT_ASSETS.is_dir() or not any(DEFAULT_ASSETS.glob("*.adf")),
    reason="supplied assets/ disk images are absent",
)
def test_title_screen_shape_and_runtime_palette() -> None:
    from formats.decode import palette_for_entry

    main = next(a for a in load_supplied_assets() if a.path == "DT1:main.arc")
    title = main.entries[2]
    # 291E/404A: kind 1, 320x200, five bitplanes of 40-byte rows.
    assert title.kind == 1
    assert title.metadata[0:2] == (320, 200)
    assert len(title.record_output) == 5 * 40 * 200
    # The palette is read from resident DATA at run time (32 UWORDs, 0x0RGB).
    palette = palette_for_entry(main.path, 2)
    assert palette is not None and len(palette) == 32
    assert all(c is None or 0 <= c <= 0x0FFF for c in palette)
    # No matched call ties entry 4 to a table: its palette stays unknown.
    assert palette_for_entry(main.path, 4) is None
