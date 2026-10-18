"""Invariants of the replay and comparison pieces: data-model layouts, host-order reads,
lag explanation, WinUAE inputs as a port replay log, busy-wait and stub-cell rewrites."""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))


def load(name):
    spec = importlib.util.spec_from_file_location(name + '_under_test', TOOLS / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


STRUCTS = {'Rec': {'size': 10, 'fields': [
    dict(name='p', offset=0, type='char *'), dict(name='n', offset=4, type='int'),
    dict(name='u', offset=6, type='UNKNOWN'), dict(name='c', offset=8, type='char')]}}


def test_layout_splits_values_pointers_unknown_and_padding():
    compare = load('game_compare')
    assert compare.layout('struct Rec [2]', STRUCTS) == [
        (0, 4, 'pointer'), (4, 2, 'value'), (6, 2, 'unknown'), (8, 1, 'value'), (9, 1, 'unknown'),
        (10, 4, 'pointer'), (14, 2, 'value'), (16, 2, 'unknown'), (18, 1, 'value'), (19, 1, 'unknown')]
    assert compare.layout('unsigned char [2][3]', {}) == [(i, 1, 'value') for i in range(6)]
    assert compare.layout('struct Missing', {}) is None


def test_host_order_values_compare_equal_and_pointers_never_count():
    compare = load('game_compare')
    parts = compare.layout('struct Rec', STRUCTS)
    amiga = bytes.fromhex('00c0ffee' '1234' 'aaaa' '07' '00')
    port = bytes.fromhex('11223344' '3412' 'bbbb' '07' '00')     # other pointer, little-endian int
    assert compare.comparable(amiga, 0, parts, False, False) == compare.comparable(port, 0, parts, True, False)
    changed = port[:4] + bytes.fromhex('3512') + port[6:]
    assert compare.comparable(amiga, 0, parts, False, False) != compare.comparable(changed, 0, parts, True, False)
    # between two Amiga runs UNKNOWN bytes are compared too
    assert compare.comparable(amiga, 0, parts, False, True) != compare.comparable(amiga[:6] + b'\0\0' + amiga[8:], 0, parts, False, True)


def test_best_lag_explains_a_delay_but_not_a_different_value():
    compare = load('game_compare')
    read = lambda d: d
    original = {k: (b'a' if k < 100 else b'b') for k in range(0, 300, 25)}
    later = {k: (b'a' if k < 50 else b'b') for k in range(0, 300, 25)}          # same change, 50 earlier
    other = {k: (b'a' if k < 50 else b'c') for k in range(0, 300, 25)}
    assert compare.best_lag(original, later, read, read, range(-100, 101, 25)) == (50, 1.0)
    assert compare.best_lag(original, other, read, read, range(-100, 101, 25))[1] < 0.5


def test_winuae_inputs_become_a_port_log_in_the_game_clock():
    boot = load('game_boot')
    assert [boot.joy1dat(h) for h in ({'right'}, {'left'}, {'down'}, {'up'}, set())] == [0x3, 0x300, 0x1, 0x100, 0]
    events = [dict(frame=100, event='JOY2_FIRE_BUTTON', value=1), dict(frame=105, event='JOY2_FIRE_BUTTON', value=0),
              dict(frame=200, event='JOY2_RIGHT', value=1), dict(frame=240, event='JOY2_RIGHT', value=0)]
    clock_at = lambda frame: max(0, frame - 50)
    lines = boot.port_replay_log(events, clock_at, [0x8000, 0x8AA6]).splitlines()[1:]
    assert lines == ['49 fire 0001', '54 fire 0000', '149 joy 0003', '189 joy 0000', '0 seed 8000', '0 seed 8aa6']


def test_busy_waits_on_interrupt_state_wait_one_frame_per_pass():
    gen = load('port_gen')
    text = ('    while (G_h01_2A16 != 0)\n        ;\n'
            '    while (G_h01_2A16) {\n        poll();\n    }\n'
            '    while (G_h01_B396 == G_h01_B1EC)\n        ;\n'
            '    do { x++; } while (G_h01_2A16);\n'
            '    while (other != 0)\n        ;\n')
    out, count = gen.spin_waits(text)
    assert count == 3
    assert 'while (G_h01_2A16 != 0) platform_wait_ticks(1);' in out
    assert 'while (G_h01_2A16) { platform_wait_ticks(1);' in out
    assert 'while (G_h01_B396 == G_h01_B1EC) platform_wait_ticks(1);' in out
    assert '} while (G_h01_2A16);' in out and 'while (other != 0)\n        ;' in out


def test_link_stub_cells_move_into_the_data_hunk():
    gen = load('port_gen')
    text = '#include "aztec.h"\nint16_t G_h01_2B4A[2] = {0};\nint16_t GfxBase[2];\n'
    out, cells = gen.hunk_cells(text)
    assert cells == [('G_h01_2B4A', 0x2B4A)]
    assert 'G_h01_2B4A' not in out and 'GfxBase' in out
