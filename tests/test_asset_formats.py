"""Structural checks for the supplied DuckTales indexed asset containers."""

from __future__ import annotations

import hashlib

import pytest

from formats.decode import (
    DEFAULT_ASSETS,
    ENTRY_HEADER_SIZE,
    MAX_INDEX_ENTRIES,
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
