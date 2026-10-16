"""Curated type/extent invariants and readable-only application, mostly synthetic."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import FormatError
import data_model as dm
import readable


def field(offset, name, type_):
    return dict(offset=offset, name=name, type=type_, evidence='independent access')


def global_(type_='int', extent=2):
    return dict(type=type_, extent=extent, evidence='consumer and bound')


def model(globals_=None, structs=None):
    return dict(schema_version=1, globals=globals_ or {}, structs=structs or {})


class ValidationTests(unittest.TestCase):
    def test_manx_widths_and_multidimensional_pointer_arrays(self):
        for text, size in [('char', 1), ('int', 2), ('short int', 2),
                           ('unsigned', 2), ('long', 4), ('unsigned long int', 4),
                           ('float', 4), ('const char *', 4), ('int **[2][3]', 24)]:
            with self.subTest(text=text):
                self.assertEqual(dm.type_layout(text, {})[0], size)
                dm.validate(model({'G_h01_0100': global_(text, size)}))

    def test_struct_even_alignment_and_no_padding_credit(self):
        structs = {'Record': dict(size=8, fields=[field(0, 'flag', 'char'),
                   field(2, 'word', 'int'), field(4, 'pointer', 'char *')])}
        m = model({'G_h01_0100': global_('struct Record [3]', 24)}, structs)
        dm.validate(m)
        self.assertTrue(dm.struct_layout('Record', structs)['complete'])
        self.assertEqual(dm.typed_bytes('struct Record [3]', structs), 21)
        c = dm.coverage(m, [('DATA', 0, 256), ('BSS', 256, 512)])
        self.assertEqual(c['bytes']['BSS']['typed'], 21)
        self.assertEqual(c['bytes']['BSS']['modeled_extent'], 24)
        self.assertEqual(c['partial_globals'], 1)

    def test_sparse_records_and_unknown_boundary_remain_explicit(self):
        structs = {'Sparse': dict(size=8, fields=[field(0, 'word', 'int'),
                    field(2, 'unknown', 'UNKNOWN'), field(6, 'tail', 'int')]),
                   'Open': dict(size=None, fields=[field(4, 'cursor', 'char *')])}
        m = model({'G_h01_0100': global_('struct Sparse [2]', 16),
                   'G_h01_0120': global_('struct Open *[4]', 16),
                   'G_h01_0130': global_('UNKNOWN', None)}, structs)
        dm.validate(m)
        self.assertFalse(dm.struct_layout('Sparse', structs)['complete'])
        self.assertEqual(dm.typed_bytes('struct Sparse [2]', structs), 8)
        self.assertEqual(dm.typed_bytes('const struct Sparse [2]', structs), 8)
        header = dm.render_header(m, {})
        active = readable.NON_CODE.sub('', header)
        self.assertIn('struct Open *G_h01_0120[4];', active)
        self.assertNotIn('extern struct Sparse', active)
        self.assertNotIn('struct Sparse {', active)
        self.assertIn('UNKNOWN', header)
        self.assertNotIn('pad[', header)

    def test_nested_records_emit_dependencies_before_parent(self):
        structs = {'A': dict(size=4, fields=[field(0, 'b', 'const struct B [2]')]),
                   'B': dict(size=2, fields=[field(0, 'n', 'int')])}
        m = model({'G_h01_0100': global_('struct A', 4)}, structs)
        dm.validate(m)
        h = dm.render_header(m, {})
        self.assertLess(h.index('struct B {'), h.index('struct A {'))

    def test_bad_structs_rejected(self):
        bad = [dict(size=2, fields=[field(0, 'n', 'long')]),
               dict(size=6, fields=[field(0, 'n', 'long'), field(2, 'm', 'int')]),
               dict(size=4, fields=[field(1, 'n', 'int')]),
               dict(size=4, fields=[field(0, 'n', 'int'), field(2, 'n', 'int')]),
               dict(size=3, fields=[field(0, 'n', 'int')]),
               dict(size=4, fields=[field(0, 'n', 'struct R')]),
               dict(size=4, fields=[field(0, 'n', 'struct Missing')]),
               dict(size=4, fields=[field(0, 'n', 'int [0]')]),
               dict(size=2, fields=[dict(field(0, 'n', 'int'), evidence='')])]
        for row in bad:
            with self.subTest(row=row), self.assertRaises(FormatError):
                dm.validate(model(structs={'R': row}))

    def test_invalid_globals_and_overlaps_rejected(self):
        bad = [model({'G_h01_0100': global_('long', 2)}),
               model({'G_h01_0100': global_('int []', 2)}),
               model({'G_h01_0101': global_()}),
               model({'G_h01_0100': global_('void', 2)}),
               model({'G_h01_0100': global_('const struct int *', 4)}),
               model({'G_h01_0100': global_('int', None)}),
               model({'G_h01_0100': global_('int', True)}),
               model({'G_h01_0100': global_('int', -2)}),
               model({'G_h02_0100': global_()}),
               model({'G_h01_0100': dict(global_(), evidence=' ')}),
               model({'G_h01_0100': global_('long', 4), 'G_h01_0102': global_()}),
               model({'G_h01_0100': dict(global_(), value=123)}),
               model({'G_h01_0100': dict(global_(), struct='Missing')})]
        for m in bad:
            with self.subTest(m=m), self.assertRaises(FormatError):
                dm.validate(m)
        # UNKNOWN extents, if independently bounded, also reserve their span.
        with self.assertRaises(FormatError):
            dm.validate(model({'G_h01_0100': global_('UNKNOWN', 8), 'G_h01_0102': global_()}))

    def test_region_boundary_not_just_total_size(self):
        for key, row in [('G_h01_00FE', global_('long', 4)),
                         ('G_h01_0200', global_('UNKNOWN', None))]:
            with self.subTest(key=key), self.assertRaises(FormatError):
                dm.validate(model({key: row}), regions=[('DATA', 0, 256), ('BSS', 256, 512)])

    def test_reviewed_names_must_be_unique_including_mechanical_fallback(self):
        m = model({'G_h01_0100': global_(), 'G_h01_0102': global_()})
        for names in [dict(globals={'G_h01_0100': dict(name='same'), 'G_h01_0102': dict(name='same')}),
                      dict(globals={'G_h01_0100': dict(name='G_h01_0102')}),
                      dict(globals={'G_h01_0100': dict(name='int')}),
                      dict(globals={'G_h01_0100': None}),
                      dict(globals={'G_h01_0100': dict(name='same')}, functions={'resident_F_0000': dict(name='same')})]:
            with self.subTest(names=names), self.assertRaises(FormatError):
                dm.validate(m, names)
        dm.validate(m, dict(globals={'G_h01_0100': dict(name='money')}))
        self.assertIn('extern int money;', dm.render_header(m, dict(globals={'G_h01_0100': dict(name='money')})))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(FormatError):
            json.loads('{"globals": {}, "globals": {}}', object_pairs_hook=dm._unique_object)

    def test_repository_map_valid(self):
        # One cheap real-map test; no proof replay, corpus-count snapshot or oracle write.
        dm.load_model(ROOT)


class ReadableTests(unittest.TestCase):
    def setUp(self):
        self.m = model({'G_h01_0100': global_('int', 2),
                        'G_h01_0102': global_('unsigned int', 2),
                        'G_h01_0104': global_('long', 4),
                        'G_h01_0108': global_('UNKNOWN', None)})

    def test_scalar_compatibility_preserves_signedness_and_array_shape(self):
        self.assertTrue(readable.compatible_view('short', 'int', {}))
        self.assertTrue(readable.compatible_view('unsigned short', 'unsigned int', {}))
        for left, right in [('int', 'unsigned int'), ('long', 'char *'),
                            ('char', 'char [1]'), ('int [2]', 'int [3]'),
                            ('int *', 'char *'), ('const char *', 'char *')]:
            self.assertFalse(readable.compatible_view(left, right, {}), (left, right))

    def test_struct_tag_and_size_do_not_establish_compatibility(self):
        structs = {'R': dict(size=2, fields=[field(0, 'n', 'int')])}
        self.assertTrue(readable.compatible_view('struct R', 'struct R', structs, {'R': 'int n;'}))
        self.assertFalse(readable.compatible_view('struct R', 'struct R', structs, {'R': 'int other;'}))
        self.assertFalse(readable.compatible_view('struct Local *', 'struct R *', structs))
        partial = {'R': dict(size=4, fields=[field(0, 'unknown', 'UNKNOWN')])}
        self.assertFalse(readable.compatible_view('struct R *', 'struct R *', partial, {'R': 'int n;'}))

    def test_grouped_externs_keep_unmodeled_and_function_declarators(self):
        source = 'extern short G_h01_0100, G_h01_0102, untouched, callee();\nrecovered() { return G_h01_0100; }\n'
        output, stats = readable.apply_data_model(source, self.m)
        self.assertEqual(stats, dict(shared=1, differing=1, unknown=0))
        active = readable.NON_CODE.sub('', output)
        self.assertNotIn('extern short G_h01_0100', active)
        self.assertNotIn('extern short G_h01_0102', active)
        self.assertIn('extern short untouched;', active)
        self.assertIn('extern short callee();', active)
        self.assertIn('PRIVATE VIEW DIFFERS', output)
        self.assertIn('extern short G_h01_0102;', output)
        self.assertIn('recovered() { return G_h01_0100; }', output)

    def test_unknown_keeps_private_view_and_unsupported_declarators_are_untouched(self):
        source = 'extern char G_h01_0108;\nextern int G_h01_0100, (*fn)();\n'
        output, stats = readable.apply_data_model(source, self.m)
        self.assertEqual(stats, dict(shared=0, differing=0, unknown=1))
        self.assertIn('extern char G_h01_0108;', readable.NON_CODE.sub('', output))
        self.assertIn('extern int G_h01_0100, (*fn)();', output)

    def test_comments_strings_and_character_literals_are_not_declarations(self):
        source = ('/* extern int G_h01_0100; */\n// extern int G_h01_0100;\n'
                  'recovered() { char *s="extern int G_h01_0100;"; return \'x\'; }\n')
        output, stats = readable.apply_data_model(source, self.m)
        self.assertTrue(output.endswith(source))
        self.assertEqual(stats, dict(shared=0, differing=0, unknown=0))

    def test_render_writes_header_and_renames_without_touching_input(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'recovery').mkdir()
            (root/'docs').mkdir()
            (root/'src').mkdir()
            names = dict(schema_version=1, functions={}, globals={'G_h01_0100':dict(name='money',evidence='consumer')})
            (root/'recovery/names.json').write_text(json.dumps(names))
            (root/'recovery/data_model.json').write_text(json.dumps(self.m))
            (root/'docs/data-layout.json').write_text(json.dumps(dict(ranges=[dict(hunk=1,classification='BSS',start=256,end=512)])))
            source = 'extern short G_h01_0100;\nrecovered() { return G_h01_0100; }\n'
            p = root/'src/f.c'
            p.write_text(source)
            ledger = dict(functions={'resident_F_0000':dict(source='src/f.c',state='FUNCTION_CODE_MATCH')})
            (root/'recovery/ledger.json').write_text(json.dumps(ledger))
            result = readable.render(root)
            self.assertEqual(result['data_model']['shared'], 1)
            self.assertEqual(p.read_text(), source)
            rendered = (root/'build/readable/resident/resident_F_0000.c').read_text()
            self.assertIn('#include "../include/game_data.h"', rendered)
            self.assertIn('return money;', rendered)
            self.assertIn('extern int money;', (root/'build/readable/include/game_data.h').read_text())
            ledger['functions']['resident_F_0000']['source'] = 'to_delete/f.c'
            (root/'recovery/ledger.json').write_text(json.dumps(ledger))
            with self.assertRaises(FormatError):
                readable.render(root)
            self.assertEqual(p.read_text(), source)


if __name__ == '__main__':
    unittest.main()
