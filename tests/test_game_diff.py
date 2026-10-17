from __future__ import annotations
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'game_diff.py'
spec = importlib.util.spec_from_file_location('game_diff_under_test', SOURCE)
game_diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_diff)


def test_original_offsets_come_only_from_offset_encoding_names():
    assert game_diff.original_offset('_F_h05_467E') == (5, 0x467E)
    assert game_diff.original_offset('_G_h01_2042') == (1, 0x2042)
    assert game_diff.original_offset('_audio5_h_h01_19E8') == (1, 0x19E8)
    assert game_diff.original_offset('_audio4_h_6ECC') == (0, 0x6ECC)
    assert game_diff.original_offset('_strcpy') is None
    assert game_diff.original_offset('_audio3_00_begin') is None


def test_mapping_is_contiguous_from_the_nearest_anchor():
    m = game_diff.Mapping({0: [(0x100, 0x80, '_a'), (0x200, 0x190, '_b')]})
    assert m.point(0, 0x100) == 0x80 and m.point(0, 0x1FF) == 0x17F and m.point(0, 0x210) == 0x1A0
    assert m.point(0, 0x50) is None and m.owner(0, 0x150) == '_a'


def test_moved_targets_compare_by_content_through_the_string_end():
    ocont = {1: b'xxHELLO\0zz'}
    bcont = {1: b'HELLO\0qqqq'}
    assert game_diff.same_target_bytes(ocont, bcont, (1, 2), (1, 0))
    assert not game_diff.same_target_bytes(ocont, bcont, (1, 0), (1, 0))
    assert not game_diff.same_target_bytes({1: b'\0abc'}, {1: b'\0xyz'}, (1, 0), (1, 0))


def test_slot_table_end_counts_leading_jump_slots():
    assert game_diff.slot_table_end({1: b'\x4e\xf9\0\0\0\1' * 3 + b'\0\0'}) == 18
    assert game_diff.slot_table_end({1: b'\0\0'}) == 0
