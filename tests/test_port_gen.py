from __future__ import annotations
import importlib.util
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'port_gen.py'
spec = importlib.util.spec_from_file_location('port_gen_under_test', SOURCE)
port_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(port_gen)


def test_aztec_integer_types_become_fixed_width_outside_strings_and_comments():
    text = 'unsigned int a; long b; unsigned long c; short d; unsigned e; int f; unsigned char g;\n' \
           '/* int long */ char *s = "unsigned int";\n'
    out = port_gen.translate_types(text)
    assert out.startswith('uint16_t a; int32_t b; uint32_t c; int16_t d; uint16_t e; int16_t f; unsigned char g;')
    assert '/* int long */' in out and '"unsigned int"' in out


def test_implicit_int_definitions_return_16_bits_and_are_declared_first():
    text = 'extern int16_t helper();\nrecovered(a)\nint16_t a;\n{\n    return helper(a);\n}\n' \
           'char\nkept()\n{\n    return 0;\n}\n'
    out, names = port_gen.explicit_returns(text)
    assert names == ['recovered']
    assert 'int16_t recovered(a)' in out and 'char\nkept()' in out
    full = port_gen.translate(text)
    assert full.index('int16_t recovered();') < full.index('int16_t recovered(a)')


def test_reserved_runtime_names_are_renamed_as_whole_tokens_only():
    out = port_gen.rename_runtime('int errno; x = my_errno + errno; main(); domain();')
    assert out == 'int aztec_errno; x = my_errno + aztec_errno; game_main(); domain();'


def test_units_needing_a_port_version_are_reported():
    assert port_gen.needs_override('#asm\n move.l d0,d1\n#endasm\n') == ['inline #asm']
    assert port_gen.needs_override('x = *(unsigned short *)0xdff004;') == ['custom chip / CIA address']
    assert port_gen.needs_override('/* 0xdff004 */ x = 1;') == []


def test_materialization_carries_only_the_symbol_aliases(tmp_path):
    (tmp_path / 'LINK_MATERIALIZATION').mkdir()
    (tmp_path / 'LINK_MATERIALIZATION/data_aliases.asm').write_text('\tpublic __cln\n__cln equ _G_h01_0012\n')
    out = port_gen.translate_materialization(tmp_path)
    assert '\t.set __cln, _G_h01_0012' in out and '.space' not in out


def test_data_hunk_places_providers_and_reservations_at_their_offsets(tmp_path):
    root = tmp_path / 'repo'
    guest = tmp_path / 'guest'
    (root / 'recovery').mkdir(parents=True)
    (root / 'facts').mkdir()
    (guest / 'tu').mkdir(parents=True)
    (guest / 'LINK_ONLY_STUBS').mkdir()
    fact = dict(original=dict(start=0x10, size=6), definitions=[
        dict(symbol='G_h01_0010', offset=0), dict(symbol='G_h01_0012', offset=2)])
    (root / 'facts/p.json').write_text(json.dumps(fact))
    (root / 'recovery/ledger.json').write_text(json.dumps(
        {'data_providers': {'resident_data_0010': {'fact': 'facts/p.json'}}}))
    (guest / 'tu/data_resident_data_0010.c').write_text(
        '/* staged accepted DATA provider: resident_data_0010; proof class: DATA_LAYOUT_MATCH */\n'
        'struct T { short a; };\nextern short G_h01_0020;\n'
        'struct T G_h01_0010 = {7};\nshort *G_h01_0012 = &G_h01_0020;\n')
    (guest / 'LINK_ONLY_STUBS/measured_reservations.asm').write_text('\tpublic _G_h01_0020\n\tbss _G_h01_0020,4\n')
    plan = [dict(kind='c', object='obj_data_resident_data_0010.o', source='tu/data_resident_data_0010.c')]
    out = port_gen.generate_data_hunk(plan, guest, root)
    assert 'gap_0000[16]' in out and 'gap_0016[10]' in out and 'uint8_t m_0020[4];' in out
    assert 'struct T_resident_data_0010 v;' in out and '.m_0012 = { .v = HUNK(0x0020) }' in out
    assert '.set _G_h01_0012, _amiga_data_hunk+0x12' in out
    assert '_Static_assert(offsetof(struct amiga_data_hunk, m_0012) == 0x12' in out


def test_narrow_views_inside_big_endian_scalars_move_to_the_host_byte(monkeypatch):
    monkeypatch.setitem(port_gen.PROVIDER_TYPES, 'G_h01_0970', 'int16_t')
    monkeypatch.setitem(port_gen.PROVIDER_TYPES, 'G_h01_0A00', 'int32_t')
    monkeypatch.setitem(port_gen.PROVIDER_TYPES, 'G_h01_12B4', 'struct Entry')
    low_byte = '#define G_h01_0971 (*(char *)((char *)&G_h01_0970 + 1))'
    assert port_gen.byte_order_aliases(low_byte).startswith('#define G_h01_0971 (*(char *)((char *)&G_h01_0970 + 0))')
    low_word = '#define G_h01_0A02 (*(int16_t *)((char *)&G_h01_0A00 + 2))'
    assert '&G_h01_0A00 + 0))' in port_gen.byte_order_aliases(low_word)
    field = '#define G_h01_12B5 (*(char *)((char *)&G_h01_12B4 + 1))'
    assert port_gen.byte_order_aliases(field) == field              # a struct field: same bytes on any host


def test_narrow_views_of_scalars_go_through_be_view_and_offset_views_stay():
    text = 'c = ((char *)&i)[1]; v = ((unsigned char *)&e->value12)[1]; ' \
           'w = ((int16_t *)&rows[n])[2]; p = ((char *)&G_h01_5014 + 4)[j];'
    notes = []
    out = port_gen.scalar_views(text, notes)
    assert 'c = BE_VIEW(char, i, 1);' in out and 'BE_VIEW(unsigned char, e->value12, 1)' in out
    assert 'BE_VIEW(int16_t, rows[n], 2)' in out
    assert '((char *)&G_h01_5014 + 4)[j]' in out and len(notes) == 3


def test_reviewed_byte_of_a_word_is_swapped_into_the_host_low_byte():
    text = 'struct Cell {\n    char pad;\n    unsigned char bits;\n};\nstruct Other { char pad; char bits; };\n'
    out = port_gen.swap_word_bytes(text)
    assert out.index('unsigned char bits;') < out.index('char pad;')
    assert 'struct Other { char pad; char bits; };' in out


def test_names_inside_wider_scalars_move_to_the_host_position_of_their_bits():
    units = ['extern int16_t G_h01_A9C2;\nf() { G_h01_A9C2 = g(); }\n',
             'extern unsigned char G_h01_A9C3;\nextern int32_t G_h01_A7D6;\nextern int16_t G_h01_A7D8;\n'
             'extern int16_t G_h01_1000;\nextern char G_h01_1001;\n'
             'h() { x = G_h01_A9C3 + G_h01_A7D6 + G_h01_A7D8 + G_h01_1000; y = &G_h01_1001; }\n']
    widths = port_gen.access_widths(units)
    assert 'G_h01_1001' not in widths                 # only its address is taken
    assert port_gen.interior_aliases(widths) == {'G_h01_A9C3': 0xA9C2, 'G_h01_A7D8': 0xA7D6}


def test_port_output_spells_readable_names_in_code_and_asm_strings(tmp_path, monkeypatch):
    import sys
    sys.path.insert(0, str(SOURCE.parent))
    import names
    forward = {'G_h01_0010': 'tick', '_G_h01_0010': '_tick'}
    monkeypatch.setattr(names, '_maps', lambda root=None: (forward, {v: k for k, v in forward.items()}))
    (tmp_path / 'a.c').write_text('extern long G_h01_0010;\n__asm__(".globl _G_h01_0010\\n.set _G_h01_0010, x\\n");\n'
                                  'long G_h01_00100;\n')
    assert port_gen.readable_names(tmp_path) == 1
    out = (tmp_path / 'a.c').read_text()
    assert 'extern long tick;' in out and '.globl _tick\\n.set _tick, x' in out and 'G_h01_00100' in out


def test_le_readers_and_hardware_units_have_port_versions():
    overrides = Path(__file__).resolve().parents[1] / 'port' / 'override'
    for name in ('resident_F_2D66', 'resident_F_2DBA', 'resident_F_33E6'):
        assert (overrides / (name + '.c')).is_file(), name
    # the input poll and seed_random run as recovered: their hardware reads are translated
    poll = ('    p0 = 0xdff00c;\n    p1 = 0xbfe0fe;\n'
            '    s = ((*(uint16_t *)p1 & 0x80) ^ 0x80) >> 3;\n    s |= (*(uint16_t *)p0 & 0x2) << 2;\n')
    out, count = port_gen.hardware_reads(poll)
    assert count == 2 and 'amiga_read16(p1)' in out and 'amiga_read16(p0)' in out
    assert port_gen.needs_override(out) == []
    seed = 'G_h01_3AB8 = *(uint16_t *)0xdff004 + G_h01_B1EC;'
    assert port_gen.hardware_reads(seed) == ('G_h01_3AB8 = amiga_read16(0xdff004) + G_h01_B1EC;', 1)
    # a write to a hardware address is not translated: it still needs a port version
    assert port_gen.needs_override('*(uint16_t *)0xdff096 = 0x8200;') == ['custom chip / CIA address']
    one = '/* staged from accepted source: src/recovered/resident/resident_F_2D66.c; x */'
    two = '/* staged from accepted source: a/x.c; */ /* staged from accepted source: a/y.c; */'
    assert port_gen.unit_override(one, overrides)
    assert port_gen.unit_override(two, overrides) is None
