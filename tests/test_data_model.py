"""Curated type/extent invariants and readable-only application, mostly synthetic."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import FormatError
import data_model as dm
import readable


def field(offset, name, type_):
    return dict(offset=offset, name=name, type=type_, evidence='independent access')


def global_(type_='int', extent=2):
    return dict(type=type_, extent=extent, evidence='consumer and bound', basis='CURATED')


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


def scalar_facts(entries):
    """Synthetic canonical declarations plus original direct-access facts."""
    symbols, widths, kinds = {}, {}, {}
    for key, views, observed in entries:
        symbols[key] = {v: list(ss) for v, ss in views.items()}
        kinds[key] = 'data'
        if observed is not None:
            widths[int(key[-4:], 16)] = dict(observed_widths_bytes=sorted(set(observed)),
                accesses=[dict(width_bytes=w, function='original', hunk=0, offset=i*2,
                               mnemonic='move', operands='(a4),d0', direction='READ')
                          for i, w in enumerate(observed)], address_taken=[])
    return dict(parsed=dict(symbols=symbols, kinds=kinds, source_structs={}), widths=widths)


class MechanicalTests(unittest.TestCase):
    def test_scalar_pointer_and_array_proposals_and_merge_idempotence(self):
        facts = scalar_facts([
            ('G_h01_0100', {'int':['a.c'], 'short':['b.c']}, [2]),
            ('G_h01_0102', {'unsigned char':['a.c']}, [1]),
            ('G_h01_0104', {'struct Opaque *':['c.c']}, [4]),
            ('G_h01_0108', {'long [2][3]':['a.c','b.c']}, [4]),
            ('G_h01_0120', {'char **':['c.c']}, [4])])
        m = model()
        proposals = dm.propose_scalars(m, facts)
        self.assertEqual({k:r['type'] for k,r in proposals.items()},
            dict(G_h01_0100='int', G_h01_0102='unsigned char', G_h01_0104='struct Opaque *',
                 G_h01_0108='long[2][3]', G_h01_0120='char **'))
        self.assertEqual(proposals['G_h01_0108']['extent'], 24)
        self.assertIn('consumers=2', proposals['G_h01_0100']['evidence'])
        self.assertIn('original access widths=[2]', proposals['G_h01_0100']['evidence'])
        m['globals'].update(proposals)
        dm.validate(m, mechanical_facts=facts)
        self.assertEqual(dm.propose_scalars(m, facts), {})
        self.assertEqual(dm.derive_scalars(m, facts), proposals)
        self.assertTrue(all(r['basis']=='MECHANICAL_CONSISTENT_VIEWS' for r in proposals.values()))

    def test_no_majority_vote_no_address_only_or_partial_width_evidence(self):
        views = [{'int':['a','b'], 'unsigned int':['c']},
                 {'long':['a'], 'char *':['b']}, {'char':['a'], 'char [1]':['b']},
                 {'int []':['a']}, {'struct R':['a']}, {'int':['a']}]
        for v in views:
            with self.subTest(views=v):
                facts = scalar_facts([('G_h01_0100', v, [] if v==views[-1] else [2])])
                self.assertEqual(dm.propose_scalars(model(), facts), {})
        for width in (None, [], [1], [1,2], [4]):
            with self.subTest(width=width):
                facts=scalar_facts([('G_h01_0100', {'int':['a']}, width)])
                self.assertEqual(dm.propose_scalars(model(), facts), {})
        facts=scalar_facts([('G_h01_0100', {'int':['a']}, [2])])
        facts['widths'][256]['observed_widths_bytes']=[1]
        self.assertEqual(dm.propose_scalars(model(), facts), {})

    def test_interior_accesses_alignment_and_region_bounds(self):
        facts=scalar_facts([('G_h01_0100', {'int [2]':['a']}, [2])])
        for offset,width in [(257,2),(258,1),(259,2)]:
            with self.subTest(offset=offset,width=width):
                changed=deepcopy(facts)
                changed['widths'][offset]=dict(observed_widths_bytes=[width],accesses=[dict(width_bytes=width)])
                self.assertEqual(dm.propose_scalars(model(),changed),{})
        self.assertEqual(dm.propose_scalars(model(),facts, [('DATA',0,258)]),{})
        odd=scalar_facts([('G_h01_0101', {'int':['a']}, [2])])
        self.assertEqual(dm.propose_scalars(model(),odd),{})
        # A long straddling the array's start is an overlap even when its base
        # lies outside the candidate. Both eligible candidate rows are rejected.
        crossed=scalar_facts([('G_h01_00FE', {'long':['a']}, [4]),
                             ('G_h01_0100', {'int [2]':['b']}, [2])])
        self.assertEqual(dm.propose_scalars(model(),crossed),{})

    def test_overlaps_are_symmetric_and_curated_extents_take_precedence(self):
        facts=scalar_facts([('G_h01_0100', {'int [2]':['a']}, [2]),
                            ('G_h01_0102', {'int':['b']}, [2]),
                            ('G_h01_0104', {'int':['c']}, [2])])
        result=dm.propose_scalars(model(),facts)
        self.assertEqual(list(result),['G_h01_0104'])
        reversed_facts=deepcopy(facts)
        reversed_facts['parsed']['symbols']=dict(reversed(list(facts['parsed']['symbols'].items())))
        self.assertEqual(dm.propose_scalars(model(),reversed_facts),result)
        reserved=model({'G_h01_0100':global_('UNKNOWN',4)})
        self.assertEqual(dm.propose_scalars(reserved,facts),result)
        reserved['globals']['G_h01_0104']=global_('UNKNOWN',None)
        self.assertEqual(dm.propose_scalars(reserved,facts),{})

    def test_every_mechanical_row_is_rederived_including_evidence_and_consumers(self):
        facts=scalar_facts([('G_h01_0100', {'int':['a','b']}, [2])])
        m=model(dm.propose_scalars(model(),facts))
        for change in (dict(type='unsigned int'),dict(type='short'),dict(extent=4),
                       dict(evidence='same width but invented facts'),dict(struct='Invented')):
            changed=deepcopy(m);changed['globals']['G_h01_0100'].update(change)
            with self.subTest(change=change),self.assertRaises(FormatError):
                dm.validate(changed,mechanical_facts=facts)
        variants=[]
        for view in ({'int':['a']},{'int':['a','c']},{'short':['a','b']},
                     {'int':['a','b'],'char':['c']}):
            changed=deepcopy(facts);changed['parsed']['symbols']['G_h01_0100']=view;variants.append(changed)
        for key,value in [('width_bytes',1),('offset',99),('function','other')]:
            changed=deepcopy(facts);changed['widths'][256]['accesses'][0][key]=value;variants.append(changed)
        changed=deepcopy(facts);changed['parsed']['symbols']={};variants.append(changed)
        for changed in variants:
            with self.subTest(facts=changed),self.assertRaises(FormatError):
                dm.validate(m,mechanical_facts=changed)
        # A newly discovered unanimous array overlaps the existing scalar.
        overlap=deepcopy(facts)
        overlap['parsed']['symbols']['G_h01_00FE']={'int [2]':['new']}
        overlap['parsed']['kinds']['G_h01_00FE']='data'
        overlap['widths'][254]=deepcopy(facts['widths'][256])
        with self.assertRaises(FormatError):dm.validate(m,mechanical_facts=overlap)

    def test_evidence_refresh_preserves_semantics_and_refuses_lost_support(self):
        facts = scalar_facts([('G_h01_0100', {'int':['a']}, [2])])
        m = model(dm.derive_scalars(model(), facts))
        m['globals']['G_h01_0200'] = global_()
        before = deepcopy(m)
        regrouped = deepcopy(facts)
        regrouped['parsed']['symbols']['G_h01_0100'] = {'int':['a','b']}
        fresh = dm.refresh_scalar_evidence(m, regrouped)
        self.assertEqual(m, before)
        self.assertNotEqual(fresh['globals']['G_h01_0100']['evidence'], m['globals']['G_h01_0100']['evidence'])
        self.assertEqual(fresh['globals']['G_h01_0200'], m['globals']['G_h01_0200'])
        dm.validate(fresh, mechanical_facts=regrouped)
        for view, widths in [({'unsigned int':['a']}, [2]), ({'int [2]':['a']}, [2]),
                             ({'int':['a']}, [1]), ({}, [2])]:
            changed = scalar_facts([('G_h01_0100', view, widths)])
            with self.subTest(view=view, widths=widths), self.assertRaisesRegex(FormatError, 'refresh refused'):
                dm.refresh_scalar_evidence(m, changed)
        self.assertEqual(m, before)

    def test_unparsed_declarations_prevent_false_unanimity(self):
        facts=scalar_facts([('G_h01_0100', {'long':['a']}, [4])])
        m=model(dm.propose_scalars(model(),facts))
        facts['parsed']['unparsed']=[dict(source='b',statement='float G_h01_0100')]
        self.assertEqual(dm.propose_scalars(model(),facts),{})
        with self.assertRaises(FormatError):dm.validate(m,mechanical_facts=facts)

    def test_opaque_pointee_views_are_fingerprinted_without_claiming_layout(self):
        facts=scalar_facts([('G_h01_0100',{'struct Local *':['a']},[4])])
        facts['parsed']['source_structs']={'a':{'Local':'int x;'}}
        m=model(dm.propose_scalars(model(),facts))
        dm.validate(m,mechanical_facts=facts)
        changed=deepcopy(facts);changed['parsed']['source_structs']['a']['Local']='long x;'
        with self.assertRaises(FormatError):dm.validate(m,mechanical_facts=changed)
        self.assertNotIn('struct Local {',dm.render_header(m,{}))
        self.assertTrue(readable.compatible_view('struct Local *','struct Local *',{}, {'Local':'int x;'}))

    def test_required_basis_and_fresh_type_evidence(self):
        for basis in ('GUESS', None):
            row=global_();row['basis']=basis
            with self.subTest(basis=basis),self.assertRaises(FormatError):dm.validate(model({'G_h01_0100':row}))
        row=global_();del row['basis']
        with self.assertRaises(FormatError):dm.validate(model({'G_h01_0100':row}))
        with TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'evidence').mkdir();(root/'evidence/types.json').write_text('{"globals":[]}')
            with patch('type_evidence.evidence_staleness',return_value=['stale widths']), patch('declaration_views.corpus') as corpus:
                with self.assertRaisesRegex(FormatError,'stale widths'):dm.load_scalar_facts(root)
                corpus.assert_not_called()


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
            self.assertEqual(result['sources_without_private_data_externs'], 1)
            self.assertEqual(result['sources_without_private_data_views'], 1)
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
