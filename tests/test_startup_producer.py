"""Actual retained producer inputs, with consistently rehashed negative controls."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import FormatError, sha256
from repo_paths import active_files
from startup_producer import BASE, FACT, SDK, verify


class StartupProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name) / 'base'
        paths = {FACT, SDK, 'evidence/toolchain/aztec-3.6a.json'}
        for scope in ('abi', 'partition'):
            directory = BASE + '/' + scope
            paths.update(p.relative_to(ROOT).as_posix() for p in active_files(ROOT / directory))
            receipt = json.loads((ROOT / directory / 'receipt.json').read_bytes())
            paths.update(t['path'] for t in receipt['tool_inputs'])
        for path in paths:
            target = cls.base / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def setUp(self):
        self.case = tempfile.TemporaryDirectory()
        self.addCleanup(self.case.cleanup)
        self.root = Path(self.case.name) / 'repo'
        shutil.copytree(self.base, self.root)

    def receipt(self, mutate, scope='abi'):
        path = self.root / BASE / scope / 'receipt.json'
        doc = json.loads(path.read_bytes())
        mutate(doc)
        path.write_text(json.dumps(doc))

    def change(self, filename, mutate, scope='abi'):
        path = self.root / BASE / scope / filename
        raw = mutate(path.read_bytes())
        path.write_bytes(raw)
        def rehash(doc):
            for key in ('source_files', 'artifacts'):
                for item in doc[key]:
                    if item['path'] == filename:
                        item['sha256'] = sha256(raw)
                        if 'size' in item:
                            item['size'] = len(raw)
        self.receipt(rehash, scope)

    def reject(self, message):
        with self.assertRaisesRegex(FormatError, message):
            verify(self.root)

    def test_producer_only_never_accepts_source(self):
        report = verify(self.root)
        self.assertFalse(report['acceptance'])
        self.assertEqual(report['status'], 'VERIFIED_STARTUP_PRODUCER_ONLY')
        self.assertEqual((report['c_compiler_bytes'], report['sdk_asm_bytes'], report['compiler_literal_bytes']),
                         (304, 6, 2))

    def test_omitted_header_is_not_a_valid_shorter_inventory(self):
        self.receipt(lambda d: d['tool_inputs'].pop(5))
        self.reject('inventory incomplete')

    def test_omitted_artifact_cannot_escape_hash_check(self):
        self.receipt(lambda d: d.update(artifacts=[x for x in d['artifacts'] if x['path'] != 'x3.o']))
        self.reject('required artifact missing')

    def test_duplicate_artifact_rejected(self):
        self.receipt(lambda d: d['artifacts'].append(d['artifacts'][0]))
        self.reject('duplicate artifact')

    def test_rehashed_source_edit_rejected(self):
        self.change('candidate.c', lambda b: b.replace(b'20000', b'20001') if b'20000' in b else b + b'\n')
        self.reject('source does not rederive')

    def test_rehashed_harness_edit_rejected(self):
        self.change('root.c', lambda b: b.replace(b'return 0;', b'return 1;', 1))
        self.reject('source does not rederive')

    def test_rehashed_assembly_control_edit_rejected(self):
        self.change('marked.c', lambda b: b.replace(b'_startup_asm_begin:', b'_wrong_begin:'), 'partition')
        self.reject('source does not rederive')

    def test_missing_x3_flag_rejected(self):
        def mutate(d):
            for step in d['steps']:
                step['command'] = step['command'].replace('+X3 ', '')
        self.receipt(mutate)
        self.reject('producing recipe differs')

    def test_failed_guest_step_rejected(self):
        self.receipt(lambda d: d['steps'][0].update(returncode=1))
        self.reject('producing recipe differs')

    def test_rehashed_object_storage_rejected(self):
        self.change('x3.o', lambda b: b[:14] + (2).to_bytes(4, 'big') + b[18:])
        self.reject('object storage differs')

    def test_fact_cannot_claim_literal_as_c(self):
        path = self.root / FACT
        fact = json.loads(path.read_bytes())
        fact['partitions'][-1][0] = 'C_COMPILER'
        path.write_text(json.dumps(fact))
        self.reject('staged fact differs')

    def test_rehashed_header_not_inventory_pin(self):
        receipt = json.loads((self.root / BASE / 'abi/receipt.json').read_bytes())
        item = next(t for t in receipt['tool_inputs'] if '/include/' in t['path'])
        path = self.root / item['path']
        path.write_bytes(path.read_bytes() + b'\n')
        self.receipt(lambda d: next(t for t in d['tool_inputs'] if t['path'] == item['path']).update(
            sha256=sha256(path.read_bytes())))
        self.reject('tool/header pin differs')

    def test_quarantine_artifact_rejected(self):
        self.receipt(lambda d: d['artifacts'].append(dict(path='../../to_delete/fixture', size=0, sha256='')))
        self.reject('artifact path differs')


if __name__ == '__main__':
    unittest.main()
