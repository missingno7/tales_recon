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


AMIGA = dict(data_base=0x20000, data_size=0x1000, regions=[(0x400, 0x80000), (0xC00000, 0xC80000)])
PORT = dict(data_base=0x500000, data_size=0x1000, regions=[(0x500000, 0x501000), (0x600000, 0x700000)])


def test_host_order_values_and_pointers_by_what_they_point_at():
    compare = load('game_compare')
    parts = compare.layout('struct Rec', STRUCTS)
    amiga = bytes.fromhex('00020010' '1234' 'aaaa' '07' '00')     # pointer into the DATA hunk, +0x10
    port = bytes.fromhex('10005000' '3412' 'bbbb' '07' '00')      # little-endian: 0x500010, also +0x10
    a = compare.comparable(amiga, 0, parts, False, False, AMIGA)
    assert a == compare.comparable(port, 0, parts, True, False, PORT)
    elsewhere = bytes.fromhex('14005000') + port[4:]               # +0x14: a different target
    assert a != compare.comparable(elsewhere, 0, parts, True, False, PORT)
    changed = port[:4] + bytes.fromhex('3512') + port[6:]          # a different number
    assert a != compare.comparable(changed, 0, parts, True, False, PORT)
    # heap addresses on both machines: no common identity - equal, but reported as incomparable
    heap_a = compare.comparable(bytes.fromhex('00c01000') + amiga[4:], 0, parts, False, False, AMIGA)
    heap_b = compare.comparable(bytes.fromhex('00106000') + port[4:], 0, parts, True, False, PORT)
    assert heap_a == heap_b and compare.opaque(heap_a, heap_b)
    # a number is never an address: 1000 on one side, an arena address on the other
    number = compare.comparable(bytes.fromhex('000003e8') + amiga[4:], 0, parts, False, False, AMIGA)
    assert number != heap_b
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


def test_winuae_inputs_become_a_port_log_in_poll_frames():
    boot = load('game_boot')
    assert [boot.joy1dat(h) for h in ({'right'}, {'left'}, {'down'}, {'up'}, set())] == [0x3, 0x300, 0x1, 0x100, 0]
    injected = [(50, dict(frame=100, event='JOY2_FIRE_BUTTON', value=1)),
                (52, dict(frame=105, event='JOY2_FIRE_BUTTON', value=0)),
                (100, dict(frame=200, event='JOY2_RIGHT', value=1)),
                (120, dict(frame=240, event='JOY2_RIGHT', value=0))]
    lines = boot.port_replay_log(injected, [0x8000, 0x8AA6]).splitlines()[1:]
    assert lines == ['50 fire 0001', '52 fire 0000', '100 joy 0003', '120 joy 0000', '0 seed 8000', '0 seed 8aa6']


class FakeEmulator:
    """A WinUAE debugger that stops at a scripted sequence of entries (poll, VBlank server,
    seed_random), each in a given frame, and reports a cycle counter for that frame."""
    def __init__(self, stops):
        self.stops, self.frame, self.commands, self.armed = list(stops), 0, [], set()

    def snap(self):
        return None

    def reconnect_console(self):
        pass

    def wait_prompt(self, before=None, timeout=None):
        while True:                                      # entries not armed are run through
            pc, self.frame = self.stops.pop(0)
            if pc in self.armed:
                return 'VPOS: 100 HPOS: 0\n%08x 4e55 fff2   link.w a5,#$fff2\n>' % pc

    def cmd(self, text, wait=True, timeout=10):
        self.commands.append(text)
        if text.startswith('f '):
            self.armed.add(int(text[2:], 16))
        if text == 'fd':
            self.armed.clear()
        if text == 'c':
            return 'CYC=%X' % ((1000 + self.frame * 71051 + 500) * 512)
        return '>'


POLL, VBLANK, SEED, DELAY = 0x1919E, 0x1AF2C, 0x1949E, 0x1D4D0


def test_the_original_is_driven_by_its_input_polls():
    boot = load('game_boot')
    polls, dumps, records = boot.PollFrames(2), [], []
    polls.address, polls.vblank, polls.waits = POLL, VBLANK, (DELAY,)
    # frame 3: two polls (a busy loop): one poll frame; 4: polled again the next frame: a new one;
    # 5-8: drawing and loading (no polls, no wait); 9: a poll right after - the same poll frame;
    # 10: Delay; 11: a poll after the wait - a new poll frame; 12: past the end
    emu = FakeEmulator([(POLL, 3), (POLL, 3), (VBLANK, 4), (POLL, 4), (VBLANK, 5), (VBLANK, 6),
                        (VBLANK, 9), (POLL, 9), (DELAY, 10), (VBLANK, 11), (POLL, 11), (VBLANK, 12)])
    pending = [dict(frame=4, event='JOY2_FIRE_BUTTON', value=1), dict(frame=6, event='JOY2_FIRE_BUTTON', value=0)]
    boot.poll_driven(emu, polls, 1000, 12, pending, None, lambda f, n: dumps.append((f, n)), records)
    assert [(r['frame'], r['poll']) for r in records] == [(3, 1), (4, 2), (11, 3)]
    # inputs change only where a poll frame starts: the release, due during the drawing, waits
    # for the poll frame after the Delay (as the port applies it)
    assert [(at, e['frame']) for at, e in polls.injected] == [(2, 4), (3, 6)]
    assert dumps == [(4, 2)]


def test_busy_waits_on_interrupt_state_wait_one_frame_per_pass():
    gen = load('port_gen')
    text = ('    while (G_h01_2A16 != 0)\n        ;\n'
            '    while (G_h01_2A16) {\n        poll();\n    }\n'
            '    while (G_h01_B396 == G_h01_B1EC)\n        ;\n'
            '    do { x++; } while (G_h01_2A16);\n'
            '    while (other != 0)\n        ;\n')
    out, count = gen.spin_waits(text)
    assert count == 3
    assert 'while (G_h01_2A16 != 0) platform_spin_frame();' in out
    assert 'while (G_h01_2A16) { platform_spin_frame();' in out
    assert 'while (G_h01_B396 == G_h01_B1EC) platform_spin_frame();' in out
    assert '} while (G_h01_2A16);' in out and 'while (other != 0)\n        ;' in out
    # a loop that already waits for time keeps its own pace
    waiting = '    while (G_h01_2A16 != 0) {\n        key = poll();\n        Delay(5L);\n    }\n'
    assert gen.spin_waits(waiting) == (waiting, 0)


def test_link_stub_cells_move_into_the_data_hunk():
    gen = load('port_gen')
    text = '#include "aztec.h"\nint16_t G_h01_2B4A[2] = {0};\nint16_t GfxBase[2];\n'
    out, cells = gen.hunk_cells(text)
    assert cells == [('G_h01_2B4A', 0x2B4A)]
    assert 'G_h01_2B4A' not in out and 'GfxBase' in out


def test_sound_commands_compare_in_order_and_poll_frame(tmp_path):
    compare = load('game_compare')
    a, b = tmp_path / 'a.log', tmp_path / 'b.log'
    a.write_text('# log\n0 seed 8000\n12 sound 0001\n40 fire 0001\n41 sound 0024\n90 end\n')
    b.write_text('12 sound 0001\n41 sound 0024\n')
    assert compare.compare_events(compare.events(a, 'sound'), compare.events(b, 'sound')) is None
    b.write_text('12 sound 0001\n42 sound 0024\n')                 # one poll frame later
    assert compare.compare_events(compare.events(a, 'sound'), compare.events(b, 'sound'))[0] == 1
