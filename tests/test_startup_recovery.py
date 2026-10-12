"""Whole startup, independent leaf bindings and canonical literal accounting."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from analysis_support import game
from common import FormatError, sha256, write_json
from recovery_state import evidence
from recovery_evidence import load_promotions
from startup_recovery import ID, SOURCE, PROOF, ANCHORS, inputs, load, proof, contributions
from startup_callees import leaf_groups, dosbase
from startup_producer import source_views
from compiler_oracle import validate_source


class StartupRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob, cls.model, _ = game(); cls.analysis = evidence()
        cls.ledger = json.loads((ROOT / 'recovery/ledger.json').read_bytes())
        cls.ledger.get('mixed_source_objects', {}).pop(ID, None)
        cls.promotions = load_promotions(ROOT, cls.blob, cls.model, cls.analysis)
        cls.temp = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name) / 'repo'
        paths = set(inputs(ROOT))
        for fid in set(ANCHORS) | {'resident_F_8640'}:
            paths.update(cls.ledger['functions'][fid][k] for k in ('source', 'proof'))
        for p in paths:
            dest = cls.base / p; dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / p, dest)

    def setUp(self):
        self.case = tempfile.TemporaryDirectory(); self.addCleanup(self.case.cleanup)
        self.root = Path(self.case.name) / 'repo'; shutil.copytree(self.base, self.root)

    def check(self, **kw):
        return load(self.root, kw.get('blob', self.blob), self.model, kw.get('analysis', self.analysis),
                    kw.get('promotions', self.promotions), kw.get('ledger', self.ledger))

    def change(self, directory, name, transform):
        path = self.root / directory / name; raw = transform(path.read_bytes()); path.write_bytes(raw)
        receipt_path = self.root / directory / 'receipt.json'
        receipt = json.loads(receipt_path.read_bytes())
        for key in ('source_files', 'artifacts'):
            for item in receipt[key]:
                if item['path'] == name:
                    item['sha256'] = sha256(raw)
                    if 'size' in item: item['size'] = len(raw)
        write_json(receipt_path, receipt)

    def leaves(self, bases=None):
        return leaf_groups(self.root, self.blob, self.model, bases or {'_SysBase':45986, '_DOSBase':43406}, 32766)

    def test_staged_complete_extent_has_no_acceptance(self):
        row, = self.check()
        self.assertFalse(row['acceptance'])
        self.assertEqual((row['size'], row['cfg_extent']['size']), (312, 310))
        self.assertEqual(len(row['field_identities']), 38)
        self.assertEqual((row['c_compiler_bytes'], row['sdk_asm_bytes'], row['compiler_literal_bytes']), (304, 6, 2))

    def test_canonical_reload_and_language_accounting(self):
        row, = self.check(); ledger = copy.deepcopy(self.ledger)
        source = source_views(self.root)['candidate'].encode('ascii')
        path = self.root / SOURCE; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(source)
        write_json(self.root / PROOF, proof(self.root, self.blob, self.model, ledger, row))
        ledger.setdefault('mixed_source_objects', {})[ID] = dict(state='FUNCTION_WITH_DATA_MATCH', source=SOURCE,
            source_sha256=sha256(source), proof=PROOF, proof_sha256=sha256((self.root / PROOF).read_bytes()))
        accepted, = self.check(ledger=ledger)
        self.assertTrue(accepted['acceptance'])
        parts = contributions(self.root, self.blob, self.model, accepted)
        totals = {k: sum(len(p['bytes']) for p in parts if p['category'] == k)
                  for k in ('RECOVERED_C', 'RECOVERED_ASM', 'COMPILER_OWNED_DATA')}
        self.assertEqual(totals, {'RECOVERED_C':304, 'RECOVERED_ASM':6, 'COMPILER_OWNED_DATA':2})
        self.assertEqual(parts[-1]['bytes'], b'*\0')
        result = json.loads((self.root / PROOF).read_bytes()); result['compiler_literal_bytes'] = 0
        write_json(self.root / PROOF, result)
        ledger['mixed_source_objects'][ID]['proof_sha256'] = sha256((self.root / PROOF).read_bytes())
        with self.assertRaisesRegex(FormatError, 'proof does not rederive'): self.check(ledger=ledger)

    def test_normal_c_still_rejects_sdk_assembly(self):
        with self.assertRaisesRegex(FormatError, 'inline assembly'):
            validate_source(source_views(self.root)['candidate'])

    def test_rehashed_sdk_leaf_edit_rejected(self):
        self.change('evidence/rules/startup-callees/exec', 'alert.asm', lambda b: b.replace(b'-108', b'-110'))
        with self.assertRaisesRegex(FormatError, 'SDK source differs'): self.leaves()

    def test_rehashed_library_object_edit_rejected(self):
        self.change('evidence/rules/startup-callees/exec', 'alert.o', lambda b: b[:-1] + bytes([b[-1] ^ 1]))
        with self.assertRaisesRegex(FormatError, 'whole library object differs'): self.leaves()

    def test_wrong_independent_dos_base_rejected(self):
        with self.assertRaisesRegex(FormatError, 'identity not unique'):
            self.leaves({'_SysBase':45986, '_DOSBase':43408})

    def test_rehashed_leaf_data_constructor_rejected(self):
        self.change('evidence/rules/startup-callees/exec', 'root2.asm', lambda b: b.replace(b'1,2,3', b'3,2,1'))
        with self.assertRaisesRegex(FormatError, 'DATA source differs'): self.leaves()

    def test_dos_initializer_vector_mutation_rejected(self):
        blob = bytearray(self.blob); h = next(h for h in self.model['hunks'] if h['number'] == 0)
        blob[h['content_offset'] + 30269] ^= 2
        with self.assertRaisesRegex(FormatError, 'call/store differs'):
            dosbase(self.root, bytes(blob), self.model, 45986, 32766)

    def test_canonical_parser_anchor_required(self):
        with self.assertRaisesRegex(FormatError, 'canonical callee missing'):
            self.check(promotions=[p for p in self.promotions if p['id'] != 'resident_F_7B24'])

    def test_conflicting_cfg_extent_rejected(self):
        a = copy.deepcopy(self.analysis); f = next(f for f in a['functions'] if f['id'] == ID); f['end'] += 2
        with self.assertRaisesRegex(FormatError, 'descent extent conflicts'): self.check(analysis=a)

    def test_nested_entry_rejected(self):
        a = copy.deepcopy(self.analysis); a['functions'].append(dict(id='nested', hunk=0, start=30626))
        with self.assertRaisesRegex(FormatError, 'contains another entry'): self.check(analysis=a)

    def test_accepted_overlap_rejected(self):
        with self.assertRaisesRegex(FormatError, 'overlaps accepted source'):
            self.check(promotions=self.promotions + [dict(id='overlap', hunk=0, start=30626, end=30628)])

    def test_fresh_source_mutation_rejected_even_after_rehash(self):
        self.change('evidence/rules/startup-refresh/abi', 'candidate.c', lambda b: b + b'\n')
        with self.assertRaisesRegex(FormatError, 'source does not rederive'): self.check()


if __name__ == '__main__':
    unittest.main()
