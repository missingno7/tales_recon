"""Consistently rehashed negative controls for the staged mixed-source recipe."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import FormatError, sha256
from analysis_support import game
from recovery_state import evidence
from recovery_evidence import load_promotions
from resident_mixed import FACT, verify
from compiler_oracle import validate_source


class ResidentMixedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob, cls.model, _ = game(); cls.analysis = evidence()
        cls.ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
        cls.promotions = load_promotions(ROOT, cls.blob, cls.model, cls.analysis)
        cls.fact = json.loads((ROOT / FACT).read_text())
        cls.temp = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name) / 'base'; cls.base.mkdir()
        paths = [FACT, 'evidence/toolchain/aztec-3.6a.json', cls.fact['sdk_source'],
                 'evidence/contributions/library-a4.json']
        doc = json.loads((ROOT / paths[-1]).read_text())
        paths += [doc['library']['path'], doc['basis']['path']]
        paths += [a['path'] for a in doc['archives']]
        for g in doc['groups']:
            paths += [o['source'] for o in g['objects']]
            paths += [o[k]['path'] for o in g['objects'] for k in ('library', 'assembled')]
            paths += [c[k]['path'] for c in g['controls'] for k in ('executable', 'symbols', 'root_object')]
            paths += [c['root_source'] for c in g['controls']]
        for claim in doc['receipts']:
            paths.append(claim['path'])
            paths += [t['path'] for t in json.loads((ROOT / claim['path']).read_text())['tool_inputs']]
        for fid in ('resident_F_8534', 'resident_F_8640', 'ov04_F_1E36'):
            paths += [cls.ledger['functions'][fid][k] for k in ('source', 'proof')]
        for key in ('mechanical_directory', 'partition_directory', 'leaf_directory'):
            directory = cls.fact[key]
            paths += [p.relative_to(ROOT).as_posix() for p in (ROOT / directory).iterdir() if p.is_file()]
            receipt = json.loads((ROOT / directory / 'receipt.json').read_text())
            paths += [t['path'] for t in receipt['tool_inputs']]
        for path in set(paths):
            target = cls.base / path; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory(); self.addCleanup(self.temp_case.cleanup)
        self.root = Path(self.temp_case.name) / 'repo'; shutil.copytree(self.base, self.root)
        self.document = copy.deepcopy(self.fact)

    def check(self, **kwargs):
        return verify(self.root, kwargs.get('blob', self.blob), self.model, self.analysis,
                      kwargs.get('promotions', self.promotions), kwargs.get('ledger', self.ledger), fact=self.document)

    def rehash(self, directory, filename):
        path = self.root / directory / filename
        receipt_path = self.root / directory / 'receipt.json'
        receipt = json.loads(receipt_path.read_text())
        for field in ('source_files', 'artifacts'):
            for item in receipt[field]:
                if item['path'] == filename:
                    item['sha256'] = sha256(path.read_bytes())
        receipt_path.write_text(json.dumps(receipt))

    def change(self, directory, name, transform):
        path = self.root / directory / name; path.write_bytes(transform(path.read_bytes()))
        self.rehash(directory, name)

    def test_complete_staged_object_has_no_acceptance(self):
        report = self.check()
        self.assertFalse(report['acceptance'])
        self.assertEqual((report['code_bytes'], report['c_compiler_bytes'], report['sdk_asm_bytes']), (238, 196, 42))
        self.assertEqual(len(report['field_identities']), 29)

    def test_normal_c_guard_remains_closed(self):
        source = (self.root / self.document['mechanical_directory'] / 'candidate.c').read_text()
        with self.assertRaisesRegex(FormatError, 'inline assembly'):
            validate_source(source)

    def test_source_edit_with_rehashed_receipt_rejects(self):
        self.change(self.document['mechanical_directory'], 'candidate.c', lambda b: b.replace(b'fd = 0', b'fd = 1'))
        with self.assertRaisesRegex(FormatError, 'source does not rederive'):
            self.check()

    def test_asm_edit_with_rehashed_receipt_rejects(self):
        self.change(self.document['mechanical_directory'], 'candidate.c', lambda b: b.replace(b'\t\trts', b'\t\tnop'))
        with self.assertRaisesRegex(FormatError, 'source does not rederive'):
            self.check()

    def test_harness_edit_with_rehashed_receipt_rejects(self):
        self.change(self.document['mechanical_directory'], 'root.c', lambda b: b.replace(b'return 0', b'return 1'))
        with self.assertRaisesRegex(FormatError, 'harness does not rederive'):
            self.check()

    def test_source_extent_cannot_be_shortened_to_cfg(self):
        self.document['original']['end'] -= 6
        with self.assertRaisesRegex(FormatError, 'source extent differs'):
            self.check()

    def test_language_partition_cannot_absorb_asm(self):
        self.document['partitions'][0][2] = 154
        with self.assertRaisesRegex(FormatError, 'curated partition differs'):
            self.check()

    def test_whole_object_size_cannot_be_clipped(self):
        def shorten(raw):
            b = bytearray(raw); b[10:14] = (232).to_bytes(4, 'big'); return b
        self.change(self.document['mechanical_directory'], 'candidate.o', shorten)
        with self.assertRaisesRegex(FormatError, 'whole-object bounds differ'):
            self.check()

    def test_unexplained_object_storage_with_rehashed_receipt_rejects(self):
        def storage(raw):
            b = bytearray(raw); b[14:18] = (2).to_bytes(4, 'big'); return b
        self.change(self.document['mechanical_directory'], 'candidate.o', storage)
        with self.assertRaisesRegex(FormatError, 'unexplained storage'):
            self.check()

    def test_global_symbol_retarget_with_rehashed_map_rejects(self):
        import re
        for key in ('mechanical_directory', 'partition_directory'):
            directory = self.document[key]; path = self.root / directory / 'candidate.sym'
            text, count = re.subn(r'([0-9a-fA-F]{8})( _G_h01_B39E)', lambda m: '%08x%s' % (int(m[1], 16) + 2, m[2]), path.read_text())
            self.assertEqual(count, 1); path.write_bytes(text.encode('ascii')); self.rehash(directory, 'candidate.sym')
        with self.assertRaisesRegex(FormatError, 'global identity differs'):
            self.check()

    def test_marker_shift_with_rehashed_map_rejects(self):
        directory = self.document['partition_directory']; path = self.root / directory / 'candidate.sym'
        text = path.read_text(); import re
        text, count = re.subn(r'([0-9a-fA-F]{8})( _runtime_asm_begin0)', lambda m: '%08x%s' % (int(m[1], 16) + 2, m[2]), text)
        self.assertEqual(count, 1); path.write_bytes(text.encode('ascii')); self.rehash(directory, 'candidate.sym')
        with self.assertRaisesRegex(FormatError, 'source-language markers differ'):
            self.check()

    def test_link_recipe_edit_rejects(self):
        path = self.root / self.document['mechanical_directory'] / 'receipt.json'
        r = json.loads(path.read_text()); r['steps'][-1]['command'] += ' +ccd'; path.write_text(json.dumps(r))
        with self.assertRaisesRegex(FormatError, 'producing recipe differs'):
            self.check()

    def test_canonical_anchor_staleness_rejects(self):
        path = self.root / self.ledger['functions']['resident_F_8534']['source']; path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(FormatError, 'canonical anchor stale'):
            self.check()

    def test_changed_oracle_identity_rejects(self):
        b = bytearray(self.blob); b[-1] ^= 1
        with self.assertRaisesRegex(FormatError, 'game identity differs'):
            self.check(blob=bytes(b))

    def test_quarantine_is_never_a_recipe_input(self):
        self.document['mechanical_directory'] = 'to_delete/untrusted'
        with self.assertRaises(FormatError):
            self.check()

    def test_leaf_source_edit_with_rehashed_receipt_rejects(self):
        self.change(self.document['leaf_directory'], '_replyms.asm', lambda b: b.replace(b'-378', b'-374'))
        with self.assertRaisesRegex(FormatError, 'leaf SDK source differs'):
            self.check()
