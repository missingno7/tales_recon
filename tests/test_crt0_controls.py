"""Producer/order evidence must survive independently rehashed bad claims."""
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
from crt0_controls import BASE, SDK, TOOLS, verify


class Crt0ControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name) / 'base'
        paths = {SDK, 'evidence/toolchain/aztec-3.6a.json'} | TOOLS
        paths.update(p.relative_to(ROOT).as_posix() for p in active_files(ROOT / BASE))
        for path in paths:
            target = cls.base / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def setUp(self):
        self.case = tempfile.TemporaryDirectory()
        self.addCleanup(self.case.cleanup)
        self.root = Path(self.case.name) / 'repo'
        shutil.copytree(self.base, self.root)

    def receipt(self, fn, scope='allocation'):
        path = self.root / BASE / scope / 'receipt.json'
        value = json.loads(path.read_bytes())
        fn(value)
        path.write_text(json.dumps(value))

    def change(self, name, fn, scope='allocation'):
        path = self.root / BASE / scope / name
        raw = fn(path.read_bytes())
        path.write_bytes(raw)
        def rehash(doc):
            for key in ('source_files', 'artifacts'):
                for item in doc[key]:
                    if item['path'] == name:
                        item.update(sha256=sha256(raw), size=len(raw))
        self.receipt(rehash, scope)

    def reject(self, message):
        with self.assertRaisesRegex(FormatError, message):
            verify(self.root)

    def test_all_controls_and_no_acceptance(self):
        result = verify(self.root)
        self.assertFalse(result['acceptance'])
        self.assertFalse(result['accounting_promoted'])
        self.assertEqual(result['object_code_bytes'], 122)
        self.assertEqual(result['ordinary_bytes'], 108)
        self.assertEqual(len(result['controls']), 3)
        self.assertEqual(result['original_object_order'], 'UNKNOWN')

    def test_changed_provider_rehashed(self):
        self.change('provider.c', lambda b: b.replace(b'[2]', b'[3]'))
        self.reject('source does not rederive')

    def test_changed_sdk_source_rehashed(self):
        self.change('crt0-source.asm', lambda b: b + b'\n')
        self.reject('source does not rederive')

    def test_omitted_tool(self):
        self.receipt(lambda d: d['tool_inputs'].pop())
        self.reject('tool inventory incomplete')

    def test_omitted_artifact(self):
        self.receipt(lambda d: d.update(artifacts=[x for x in d['artifacts'] if x['path'] != 'shifted-source.exe']))
        self.reject('required artifact missing')

    def test_duplicate_artifact(self):
        self.receipt(lambda d: d['artifacts'].append(d['artifacts'][0]))
        self.reject('duplicate artifact')

    def test_changed_link_order(self):
        self.receipt(lambda d: d['steps'][-1].update(command=d['steps'][-1]['command'].replace('_close.o crt0-source.o', 'crt0-source.o _close.o')), 'order')
        self.reject('producing recipe differs')

    def test_failed_step(self):
        self.receipt(lambda d: d['steps'][0].update(returncode=10))
        self.reject('producing recipe differs')

    def test_changed_library_member_rehashed(self):
        self.change('_close.o', lambda b: b[:-1] + bytes([b[-1] ^ 1]), 'order')
        self.reject('earlier DOS consumer differs')

    def test_changed_symbol_fields_in_both_maps(self):
        for kind in ('lib', 'source'):
            self.change('base-' + kind + '.sym', lambda b: b.replace(b'00000024 __savsp', b'00000028 __savsp'))
        self.reject('independently resolved fields differ')

    def test_changed_object_extent_rehashed(self):
        self.change('crt0-source.o', lambda b: b[:10] + (120).to_bytes(4, 'big') + b[14:])
        self.reject('complete object storage differs')

    def test_changed_source_executable_rehashed(self):
        self.change('base-source.exe', lambda b: b[:-1] + bytes([b[-1] ^ 1]))
        self.reject('whole source/library executables differ')


if __name__ == '__main__':
    unittest.main()
