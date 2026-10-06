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
from resident_mixed import FACT, SOURCE, PROOF, verify, load_source_objects, source_object_proof, accepted_contributions
from compiler_oracle import validate_source


class ResidentMixedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob, cls.model, _ = game(); cls.analysis = evidence()
        cls.ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
        cls.ledger.pop('mixed_source_objects', None)
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

    def source_objects(self, analysis=None, promotions=None, ledger=None):
        return load_source_objects(self.root, self.blob, self.model, analysis or self.analysis,
                                   promotions or self.promotions, ledger or self.ledger)

    def test_generated_source_extent_keeps_cfg_and_language_separate(self):
        before = copy.deepcopy(self.analysis)
        row, = self.source_objects()
        self.assertEqual(self.analysis, before)
        self.assertFalse(row['acceptance'])
        self.assertEqual((row['cfg_extent']['size'], row['size']), (232, 238))
        self.assertEqual(row['original']['end'], 34368)
        self.assertEqual(sum(p['end'] - p['start'] for p in row['partitions']), 238)
        self.assertEqual(sum(p['end'] - p['start'] for p in row['partitions']
                             if p['language'] == 'ASM'), 42)
        self.assertEqual(row['original_tu'], 'UNKNOWN')

    def test_source_extent_rejects_conflicting_cfg(self):
        analysis = copy.deepcopy(self.analysis)
        entry = next(f for f in analysis['functions'] if f['id'] == self.document['id'])
        entry['end'] = self.document['original']['end'] + 2
        with self.assertRaisesRegex(FormatError, 'descent extent conflicts'):
            self.source_objects(analysis=analysis)

    def test_source_extent_rejects_nested_entry(self):
        analysis = copy.deepcopy(self.analysis)
        analysis['functions'].append(dict(id='nested', hunk=0, start=34362))
        with self.assertRaisesRegex(FormatError, 'contains another entry'):
            self.source_objects(analysis=analysis)

    def test_staged_extent_rejects_overlap_with_canonical_source(self):
        promotions = self.promotions + [dict(id='overlap', hunk=0, start=34362, end=34368)]
        with self.assertRaisesRegex(FormatError, 'overlaps accepted source'):
            self.source_objects(promotions=promotions)

    def test_staged_extent_cannot_replace_canonical_proof(self):
        ledger = copy.deepcopy(self.ledger)
        ledger['functions'][self.document['id']] = dict(state='FUNCTION_CODE_MATCH')
        with self.assertRaisesRegex(FormatError, 'already promoted'):
            self.source_objects(ledger=ledger)

    def test_scoped_census_binds_mixed_artifacts_and_fact_presence(self):
        from evidence_snapshot import Snapshot
        (self.root / 'assets').mkdir()
        (self.root / 'assets/fixture.adf').write_bytes(b'fixture')
        (self.root / 'tools').mkdir()
        snapshot = Snapshot()
        calls = []
        def loader():
            calls.append(True)
            return {'count': len(calls)}
        snapshot.load(self.root, True, loader)
        snapshot.load(self.root, True, loader)
        self.assertEqual(len(calls), 1)
        artifact = self.root / self.document['partition_directory'] / 'candidate.sym'
        artifact.write_bytes(artifact.read_bytes() + b'\n')
        snapshot.load(self.root, True, loader)
        self.assertEqual(len(calls), 2)
        sdk = self.root / self.document['sdk_source']
        sdk.write_bytes(sdk.read_bytes() + b'\n')
        snapshot.load(self.root, True, loader)
        self.assertEqual(len(calls), 3)
        (self.root / FACT).unlink()
        snapshot.load(self.root, True, loader)
        self.assertEqual(len(calls), 4)

    def admit(self):
        from common import write_json
        ledger = copy.deepcopy(self.ledger)
        row, = self.source_objects(ledger=ledger)
        source = (self.root / self.document['mechanical_directory'] / 'candidate.c').read_bytes()
        path = self.root / SOURCE; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(source)
        proof = source_object_proof(self.root, self.blob, self.model, self.analysis, ledger, row)
        path = self.root / PROOF; write_json(path, proof)
        ledger['mixed_source_objects'] = {row['id']: dict(state='FUNCTION_CODE_MATCH', source=SOURCE,
            source_sha256=sha256(source), proof=PROOF, proof_sha256=sha256(path.read_bytes()))}
        return ledger

    def test_canonical_mixed_admission_and_language_accounting(self):
        from recovery_state import canonical_state
        ledger = self.admit()
        row, = self.source_objects(ledger=ledger)
        self.assertTrue(row['acceptance'])
        self.assertEqual(row['status'], 'FUNCTION_CODE_MATCH')
        self.assertEqual(canonical_state(ledger)['mixed_source_objects'], ledger['mixed_source_objects'])
        parts = accepted_contributions(self.root, self.blob, self.model, self.analysis, self.promotions, ledger)
        self.assertEqual(sum(len(p['bytes']) for p in parts if p['category'] == 'RECOVERED_C'), 196)
        self.assertEqual(sum(len(p['bytes']) for p in parts if p['category'] == 'RECOVERED_ASM'), 42)
        self.assertEqual(b''.join(p['bytes'] for p in parts), self.blob[
            next(h['content_offset'] for h in self.model['hunks'] if h['number'] == 0) + 34130:
            next(h['content_offset'] for h in self.model['hunks'] if h['number'] == 0) + 34368])

    def test_rehashed_mixed_proof_cannot_absorb_asm_as_c(self):
        ledger = self.admit(); path = self.root / PROOF
        proof = json.loads(path.read_bytes()); proof['partitions'][1]['language'] = 'C_COMPILER'
        path.write_text(json.dumps(proof))
        ledger['mixed_source_objects'][self.document['id']]['proof_sha256'] = sha256(path.read_bytes())
        with self.assertRaisesRegex(FormatError, 'does not rederive'):
            self.source_objects(ledger=ledger)

    def test_mixed_canonical_source_is_rederived_after_rehash(self):
        ledger = self.admit(); path = self.root / SOURCE
        path.write_bytes(path.read_bytes().replace(b'fd = 0', b'fd = 1'))
        ledger['mixed_source_objects'][self.document['id']]['source_sha256'] = sha256(path.read_bytes())
        with self.assertRaisesRegex(FormatError, 'canonical source differs'):
            self.source_objects(ledger=ledger)

    def test_mixed_proof_binds_unchanged_canonical_dependencies(self):
        ledger = self.admit(); path = self.root / ledger['functions']['resident_F_8534']['source']
        path.write_bytes(path.read_bytes() + b'\n')
        ledger['functions']['resident_F_8534']['source_sha256'] = sha256(path.read_bytes())
        with self.assertRaisesRegex(FormatError, 'does not rederive'):
            self.source_objects(ledger=ledger)

    def test_canonical_mixed_object_requires_its_curated_fact(self):
        ledger = self.admit(); (self.root / FACT).unlink()
        with self.assertRaisesRegex(FormatError, 'fact missing'):
            self.source_objects(ledger=ledger)

    def test_original_relocation_cannot_be_silently_omitted(self):
        model = copy.deepcopy(self.model)
        model['relocations'].append(dict(source_hunk=0, source_offset=34132, width=4,
                                         target_hunk=1, type='RELOC32', addend_raw=0))
        with self.assertRaisesRegex(FormatError, 'original CODE relocation unsupported'):
            verify(self.root, self.blob, model, self.analysis, self.promotions, self.ledger, fact=self.document)

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
