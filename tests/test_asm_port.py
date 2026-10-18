from __future__ import annotations
import importlib.util
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'asm_port.py'
spec = importlib.util.spec_from_file_location('asm_port_under_test', SOURCE)
asm_port = importlib.util.module_from_spec(spec)
spec.loader.exec_module(asm_port)

# tst.b d16(a0) 4, beq short 2, lea d16(a4) 4 (a public declared outside dseg),
# lea abs.L 6 (declared in dseg), move.w #,abs.L 8 -> 0x1018; bsr short 2, jsr d16(pc) 4.
MODULE = '''; staged from accepted source: src/x.asm; proof class: RECONSTRUCTED_ASM
\tfar data
\tpublic _G_h01_0100
\tdseg
\tpublic _G_h01_0200
\tcseg
\tpublic _recon_h00_1000
_recon_h00_1000
\ttst.b $1e(a0)
\tbeq _recon_h00_1018
\tlea _G_h01_0100,a1
\tlea _G_h01_0200,a2
\tmove.w #$80,$dff09c
_recon_h00_1018
\tbsr _end_x
\tjsr _recon_h00_1000
_end_x
\tdseg
\tend
'''


def test_layout_follows_the_assemblers_sizes():
    mod = asm_port.Module('src/x.asm', MODULE, 'obj_x')
    assert mod.where['_recon_h00_1018'] == 0x1018 and mod.where['_end_x'] == mod.end == 0x101E


def test_a_label_that_disagrees_with_the_layout_is_an_error():
    with pytest.raises(asm_port.AsmError):
        asm_port.Module('src/x.asm', MODULE.replace('_recon_h00_1018', '_recon_h00_1016'), 'obj_x')


def test_tables_are_big_endian_with_alignment_and_references():
    text = 'T_LOOP macro\n\tdc.b $81\n\tds 0\n\tdc.w \\1\n\tendm\n\tcseg\n' \
           '_t_begin:\n\tdc.b 1\n\tT_LOOP $1234\n\tdc.l _other+2\n_t_end:\n'
    statements, equates, publics, ends = asm_port.parse(text, 'obj_t')
    table = asm_port.Table('obj_t', 'x', 'cseg', statements, equates)
    assert bytes(table.bytes) == bytes([1, 0x81, 0x12, 0x34, 0, 0, 0, 0])
    assert table.refs == [(4, '_other', 2)]


def test_generated_code_branches_calls_and_reaches_the_custom_chips():
    mod = asm_port.Module('src/x.asm', MODULE, 'obj_x')
    c = asm_port.Generator([mod], {}).module(mod)
    assert 'case 0x1000: goto L_1000;' in c and 'goto L_1018;' in c
    assert 'eb = 0xDFF09Cu;' in c and 'm68k_wr16(eb, v);' in c
    assert 'm68k_run(0x1000);' in c and 'm68k_run(0x101E);' in c


def test_the_build_symbol_file_checks_offsets_between_labels(tmp_path):
    sym = tmp_path / 'x.sym'
    sym.write_text('Segment 00:  Hunk 000\n\t00000100 _a\n\t00000108 _b\n')
    built = asm_port.read_symbols(sym)
    assert asm_port.check_against_build('u', {'_a': 0, '_b': 8}, built) == 2
    with pytest.raises(asm_port.AsmError):
        asm_port.check_against_build('u', {'_a': 0, '_b': 6}, built)
