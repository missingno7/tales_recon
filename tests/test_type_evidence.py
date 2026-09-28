import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import type_evidence as te


class DeclarationConflictTests(unittest.TestCase):
    def test_instruction_facts_do_not_collapse_to_store_or_signed_type(self):
        self.assertEqual(te.access_direction('add.w', 1, 2), 'READ_WRITE')
        self.assertEqual(te.access_direction('addq.l', 1, 2), 'READ_WRITE')
        self.assertEqual(te.access_direction('move.w', 0, 2), 'READ')
        self.assertEqual(te.access_direction('move.w', 1, 2), 'WRITE')
        self.assertEqual(te.access_direction('cmp.w', 0, 2), 'UNKNOWN')
        self.assertEqual(te.address_taking_kind('lea.l'), 'LEA')
        self.assertEqual(te.address_taking_kind('pea'), 'PEA')
        self.assertIsNone(te.address_taking_kind('move.l'))

    def test_extension_context_requires_same_loaded_register(self):
        mem = SimpleNamespace(type=te.K.M68K_OP_MEM,
                              mem=SimpleNamespace(base_reg=te.K.M68K_REG_A4))
        d0 = SimpleNamespace(type=te.K.M68K_OP_REG, reg=te.K.M68K_REG_D0)
        d1 = SimpleNamespace(type=te.K.M68K_OP_REG, reg=te.K.M68K_REG_D1)
        load = SimpleNamespace(mnemonic='move.w', operands=[mem, d0])
        self.assertTrue(te.extension_matches_load(load, SimpleNamespace(mnemonic='ext.l', operands=[d0])))
        self.assertFalse(te.extension_matches_load(load, SimpleNamespace(mnemonic='ext.l', operands=[d1])))
        frame_mem = SimpleNamespace(type=te.K.M68K_OP_MEM,
                                    mem=SimpleNamespace(base_reg=te.K.M68K_REG_A5))
        frame_load = SimpleNamespace(mnemonic='move.b', operands=[frame_mem, d0])
        self.assertTrue(te.extension_matches_load(
            frame_load, SimpleNamespace(mnemonic='ext.w', operands=[d0]), te.K.M68K_REG_A5))

    def test_distinguishes_abi_alias_from_real_shape_conflicts(self):
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern int value;')},
            {'shape': te._type_shape('extern short value;')}),
            'ABI_COMPATIBLE_INT_SHORT_VIEW')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern unsigned int value;')},
            {'shape': te._type_shape('extern unsigned short value;')}),
            'ABI_COMPATIBLE_INT_SHORT_VIEW')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern unsigned int value;')},
            {'shape': te._type_shape('extern int value;')}),
            'SIGNEDNESS_VIEW_CONFLICT')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern char value;')},
            {'shape': te._type_shape('extern int value;')}),
            'STORAGE_WIDTH_CONFLICT')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern long value;')},
            {'shape': te._type_shape('extern int value;')}),
            'STORAGE_WIDTH_CONFLICT')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern int *value;')},
            {'shape': te._type_shape('extern int value;')}),
            'POINTER_SCALAR_VIEW_CONFLICT')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern int value[2];')},
            {'shape': te._type_shape('extern int value[3];')}),
            'ARRAY_EXTENT_CONFLICT')
        self.assertEqual(te._relation(
            {'shape': te._type_shape('extern struct A value;')},
            {'shape': te._type_shape('extern struct B value;')}),
            'STRUCT_VIEW_DIFFERENCE_REVIEW')

    def test_reports_order_sensitive_declaration_pairs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src = root / 'src/recovered'
            src.mkdir(parents=True)
            (src / 'a.c').write_text('extern int score;\nextern int items[2];\n', encoding='ascii')
            (src / 'b.c').write_text('extern short score;\nextern int items[3];\n', encoding='ascii')
            report = te.declaration_conflicts(root)
        self.assertEqual(report['declarations_scanned'], 4)
        relations = {x['symbol']: x['relation'] for x in report['conflicts']}
        self.assertEqual(relations, {'items': 'ARRAY_EXTENT_CONFLICT',
                                     'score': 'ABI_COMPATIBLE_INT_SHORT_VIEW'})
        self.assertTrue(next(x for x in report['conflicts'] if x['symbol'] == 'items')['order_sensitive_harness'])

    def test_declaration_inventory_detects_added_and_removed_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src = root / 'src/recovered'
            src.mkdir(parents=True)
            first = src / 'a.c'
            first.write_text('extern int score;\n', encoding='ascii')
            initial = te.declaration_source_hashes(root)
            self.assertEqual(set(initial), {'src/recovered/a.c'})
            (src / 'b.c').write_text('extern long other;\n', encoding='ascii')
            added = te.declaration_source_hashes(root)
            self.assertEqual(set(added), {'src/recovered/a.c', 'src/recovered/b.c'})
            first.unlink()
            removed = te.declaration_source_hashes(root)
            self.assertEqual(set(removed), {'src/recovered/b.c'})

    def test_function_slice_rejects_stale_oracle_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'evidence').mkdir()
            (root / 'evidence/types.json').write_text('{}', encoding='utf-8')
            (root / 'evidence/functions').mkdir()
            (root / 'evidence/functions/ledger.json').write_text('{}', encoding='utf-8')
            (root / 'evidence/executable').mkdir()
            (root / 'evidence/executable/instructions.json').write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'stale'):
                te.function_evidence('missing_F_0000', root)

    def test_worker_reads_serve_stale_evidence_only_with_an_explicit_flag(self):
        fresh = te.function_evidence('ov09_F_298E', ROOT)
        self.assertEqual((fresh['stale'], fresh['stale_reasons']), (False, []))
        reason = 'type evidence is stale; run tools/type_evidence.py --write'
        with patch.object(te, 'evidence_staleness', return_value=[reason]):
            with self.assertRaisesRegex(ValueError, 'stale'):
                te.function_evidence('ov09_F_298E', ROOT)  # strict by default
            stale = te.function_evidence('ov09_F_298E', ROOT, allow_stale=True)
        self.assertTrue(stale['stale'])
        self.assertEqual(stale['stale_reasons'], [reason])
        self.assertIn('last generated', stale['stale_note'])
        self.assertEqual(stale['globals'], fresh['globals'])

    def test_function_slice_is_bounded_and_keeps_program_widths(self):
        evidence = te.function_evidence('ov09_F_298E', ROOT)
        self.assertLessEqual(len(evidence['globals']), 12)
        self.assertLessEqual(len(evidence['frame_accesses']), 8)
        self.assertLessEqual(len(evidence['declaration_conflict_summary']['examples']), 8)
        self.assertTrue(all(len(row['sites']) <= 2 for row in evidence['globals']))
        self.assertTrue(all('observed_widths_bytes' in row for row in evidence['globals']))


if __name__ == '__main__':
    unittest.main()
