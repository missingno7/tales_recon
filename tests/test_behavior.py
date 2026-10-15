"""The behavior report is a pure view of the accounting and ownership ledgers."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import behavior


class BehaviorReportTests(unittest.TestCase):
    def setUp(self):
        self.report = behavior.report(ROOT)
        self.accounting = json.loads((ROOT / 'evidence/hybrid/accounting.json').read_text())

    def test_code_classes_partition_the_accounted_code_hunks(self):
        totals = self.accounting['totals']
        code = {}
        for row in self.report['code'].values():
            for k, v in row.items():
                code[k] = code.get(k, 0) + v
        self.assertEqual(code.get('exact_c', 0), totals['RECOVERED_C'])
        self.assertEqual(code.get('asm', 0), totals['RECOVERED_ASM'] + totals['RECONSTRUCTED_ASM'])
        data = self.report['data_hunk']
        self.assertEqual(code.get('runtime', 0) + data.get('runtime', 0), totals['PINNED_RUNTIME'])
        self.assertEqual(code.get('unresolved', 0) + data.get('raw', 0), totals['RAW_ORACLE_DEBT'])
        self.assertEqual(data.get('typed', 0), totals['RECOVERED_DATA'])

    def test_unresolved_functions_are_never_canonical(self):
        ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
        owned = set(ledger['functions']) | set(ledger['mixed_source_objects']) | set(ledger['dead_code_functions'])
        self.assertFalse(owned & {u['id'] for u in self.report['unresolved']})

    def test_platform_services_name_only_pinned_runtime_members(self):
        ids = {r.get('id') for r in self.accounting['ranges'] if r['category'] == 'PINNED_RUNTIME'}
        self.assertTrue(self.report['platform_services'])
        self.assertLessEqual(set(self.report['platform_services']), ids)


if __name__ == '__main__':
    unittest.main()
