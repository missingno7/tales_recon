from __future__ import annotations
import importlib.util, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))


def load(name):
    spec = importlib.util.spec_from_file_location(name + '_under_test', TOOLS / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_lfsr_steps_are_not_reseeds_but_other_changes_are():
    boot = load('game_boot')
    x = 0x8000
    chain = [x]
    for _ in range(5):
        chain.append(boot.lfsr_step(chain[-1]))
    assert not any(boot.is_reseed(a, b) for a, b in zip(chain, chain[1:]))
    assert not boot.is_reseed(chain[0], chain[5])            # several steps within one frame
    assert not boot.is_reseed(None, 0x1234) and not boot.is_reseed(7, 7)
    unreachable = next(v for v in range(0x10000) if v not in {chain[0]} and boot.is_reseed(chain[0], v))
    assert boot.is_reseed(chain[0], unreachable)


def test_sequences_ignore_timing_and_report_the_first_differing_state():
    compare = load('game_compare')
    original = {0: b'\x00', 25: b'\x01', 50: b'\x02', 75: b'\x02'}
    later = {0: b'\x00', 25: b'\x00', 50: b'\x01', 75: b'\x02'}       # same states, later
    other = {0: b'\x00', 25: b'\x03', 50: b'\x02', 75: b'\x02'}       # a different state
    globals_at = [('G_h01_0000', 0, 0, 1, 'char')]
    assert compare.sequence_differences(original, later, globals_at) == []
    (row,) = compare.sequence_differences(original, other, globals_at)
    assert (row['step'], row['frame'], row['original'], row['build']) == (1, 25, '01', '03')
