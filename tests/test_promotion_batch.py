"""Shared regression gates, canonical commit boundaries and interrupted recovery."""
import copy
import json
import shutil
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_function
import promote_batch
import recovery_transaction as transaction
from common import FormatError, json_bytes, sha256, write_json


class PromotionBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = self.root / 'recovery/ledger.json'
        write_json(self.ledger, dict(schema_version=1, functions={}, attempts={}, blockers={}))
        (self.root / 'tools').mkdir()
        for name in ('check_function.py', 'function_compare.py', 'compiler_oracle.py', 'runtime_arithmetic.py'):
            shutil.copyfile(ROOT / 'tools' / name, self.root / 'tools' / name)
        self.entries, self.requests = [], []
        cache = self.root / 'build/cache'
        cache.mkdir(parents=True)
        (cache / 'receipt.json').write_text('{}')
        for i in range(2):
            fid = 'ov03_F_%04X' % (i * 4)
            source = 'recovered() { return %d; }\n' % i
            path = self.root / ('candidate%d.c' % i)
            path.write_text(source)
            f = dict(id=fid, node='ov03', hunk=3, start=i * 4, end=i * 4 + 4, size=4,
                     sha256='0' * 64, extent_status='CLOSED_CFG', direct_callees=[])
            report = dict(verdict='EQUAL', proof_level='FUNCTION_CODE_MATCH',
                          source_sha256=sha256(source.encode()), relocation_proof=[])
            compiled = dict(status='COMPILED', directory=str(cache), artifacts=[], cache_key='k%d' % i,
                            identity=dict(profile='aztec36', library='c.lib', flags=[]),
                            contribution=dict(object_sha256='0' * 64))
            self.entries.append(dict(id=fid, source=source, function=f, report=report, compiled=compiled, evidence={}))
            self.requests.append(dict(id=fid, source=str(path), profiles=['aztec36']))
        self.regression = dict(passed=True, command='synthetic regression control', output_sha256='a' * 64)
        self.patches = [patch.object(check_function, 'ROOT', self.root),
                        patch.object(check_function, 'LEDGER', self.ledger),
                        patch.object(check_function, 'recovery', lambda: json.loads(self.ledger.read_text()))]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def publish(self, entries=None, regression=None, requests=None):
        with patch.object(check_function, 'regression_receipt',
                          side_effect=regression or (lambda: self.regression)) as gate:
            result = promote_batch.publish_verified(requests or self.requests, entries or self.entries)
        return result, gate.call_count

    def test_two_promotions_share_one_bound_regression_receipt(self):
        result, calls = self.publish()
        self.assertEqual(calls, 1)
        ledger = json.loads(self.ledger.read_text())
        self.assertEqual(set(ledger['functions']), {e['id'] for e in self.entries})
        proofs = [json.loads((self.root / item['proof']).read_text()) for item in ledger['functions'].values()]
        self.assertEqual(proofs[0]['regression'], proofs[1]['regression'])
        self.assertEqual(proofs[0]['regression']['batch_members'], result['functions'])
        self.assertEqual(len(proofs[0]['regression']['batch_inputs_sha256']), 64)
        for item in ledger['functions'].values():
            self.assertEqual(sha256((self.root / item['proof']).read_bytes()), item['proof_sha256'])
            self.assertEqual(sha256((self.root / item['source']).read_bytes()), item['source_sha256'])
        journal = json.loads((transaction.journals(self.ledger) / result['transaction'] / 'journal.json').read_text())
        self.assertEqual(journal['status'], 'COMMITTED')
        self.assertEqual(journal['files'][-1]['path'], 'recovery/ledger.json')

    def test_failed_member_and_overlapping_members_block_before_regression(self):
        for kind in ('mismatch', 'overlap', 'duplicate'):
            entries = copy.deepcopy(self.entries)
            if kind == 'mismatch': entries[1]['report']['verdict'] = 'DIFFER'
            if kind == 'overlap': entries[1]['function']['start'] = 2
            if kind == 'duplicate': entries[1]['id'] = entries[0]['id']
            with self.subTest(kind=kind), patch.object(check_function, 'regression_receipt') as gate, \
                 self.assertRaises(FormatError):
                promote_batch.publish_verified(self.requests, entries)
            gate.assert_not_called()
        self.assertFalse((self.root / 'src').exists())
        self.assertEqual(json.loads(self.ledger.read_text())['functions'], {})

    def test_owned_literal_span_cannot_overlap_another_member(self):
        entries = copy.deepcopy(self.entries)
        entries[0]['report'].update(proof_level='FUNCTION_WITH_DATA_MATCH', owned_code_data=dict(end=6))
        with patch.object(check_function, 'owned_code_data_boundary'), \
             self.assertRaisesRegex(FormatError, 'overlaps'):
            self.publish(entries)

    def test_regression_failure_and_changed_inputs_publish_nothing(self):
        def failed(): raise FormatError('regression failed')
        with self.assertRaisesRegex(FormatError, 'regression failed'):
            self.publish(regression=failed)
        def mutate():
            Path(self.requests[0]['source']).write_text('changed candidate')
            return self.regression
        with self.assertRaisesRegex(FormatError, 'inputs changed'):
            self.publish(regression=mutate)
        self.assertEqual(json.loads(self.ledger.read_text())['functions'], {})
        self.assertFalse(transaction.journals(self.ledger).exists())

    def test_verification_snapshot_rejects_dependency_edit_before_gate(self):
        before = promote_batch.verification_snapshot(self.root, self.ledger, self.requests)
        (self.root / 'tools/check_function.py').write_text('changed verifier')
        with patch.object(check_function, 'regression_receipt') as gate, \
             self.assertRaisesRegex(FormatError, 'verification inputs changed'):
            promote_batch.publish_verified(self.requests, self.entries, before)
        gate.assert_not_called()

    def test_existing_source_conflict_cannot_be_silently_replaced(self):
        item = dict(state='FUNCTION_CODE_MATCH', source_sha256='f' * 64,
                    evidence_extent=dict(hunk=3, start=0, end=4))
        write_json(self.ledger, dict(functions={self.entries[0]['id']: item}, blockers={}, attempts={}))
        with self.assertRaisesRegex(FormatError, 'preserve canonical source'):
            self.publish()

    def test_write_failure_restores_every_canonical_file(self):
        real = transaction.replace_bytes
        first = self.root / 'src/recovered/ov03' / (self.entries[0]['id'] + '.c')
        first.parent.mkdir(parents=True)
        first.write_bytes(b'previous source')
        original_ledger = self.ledger.read_bytes()
        fail = self.root / 'recovery/proofs' / (self.entries[1]['id'] + '.json')
        def failing(path, data):
            if path == fail: raise OSError('injected publish failure')
            return real(path, data)
        with patch.object(transaction, 'replace_bytes', side_effect=failing), \
             self.assertRaisesRegex(OSError, 'injected publish failure'):
            self.publish()
        self.assertEqual(self.ledger.read_bytes(), original_ledger)
        self.assertEqual(first.read_bytes(), b'previous source')
        self.assertFalse(fail.exists())
        self.assertEqual(transaction.pending(self.ledger), [])

    def interrupt(self, after_commit=False):
        real = transaction.replace_bytes
        def interrupted(path, data):
            if path == self.ledger and not after_commit: raise KeyboardInterrupt()
            value = real(path, data)
            if path == self.ledger and after_commit: raise KeyboardInterrupt()
            return value
        with patch.object(transaction, 'replace_bytes', side_effect=interrupted), self.assertRaises(KeyboardInterrupt):
            self.publish()
        return transaction.pending(self.ledger)[0]

    def test_interruption_before_commit_blocks_writers_and_recovers(self):
        old = self.ledger.read_bytes()
        tid = self.interrupt()
        self.assertEqual(self.ledger.read_bytes(), old)
        with self.assertRaisesRegex(FormatError, 'unfinished promotion'):
            with transaction.ledger_lock(self.ledger): pass
        self.assertEqual(transaction.recover(self.ledger, tid), 'ROLLED_BACK')
        self.assertFalse(any((self.root / 'src').rglob('*.c')))
        self.assertEqual(self.ledger.read_bytes(), old)

    def test_interruption_after_commit_recognizes_complete_batch(self):
        tid = self.interrupt(after_commit=True)
        self.assertEqual(len(json.loads(self.ledger.read_text())['functions']), 2)
        self.assertEqual(transaction.recover(self.ledger, tid), 'COMMITTED')

    def test_recovery_preserves_conflicting_foreign_edit(self):
        tid = self.interrupt()
        source = self.root / 'src/recovered/ov03' / (self.entries[0]['id'] + '.c')
        source.write_bytes(b'later human edit')
        with self.assertRaisesRegex(FormatError, 'later edit'):
            transaction.recover(self.ledger, tid)
        self.assertEqual(source.read_bytes(), b'later human edit')
        self.assertEqual(transaction.pending(self.ledger), [tid])

    def test_real_cached_comparisons_publish_and_independently_reload(self):
        import compiler_oracle
        from analysis_support import game
        from recovery_state import evidence
        from recovery_evidence import load_promotions
        ids = ['ov14_F_03AE', 'ov03_F_154E']
        requests = [dict(id=fid, source=str(ROOT / 'src/recovered' / fid.split('_F_')[0] / (fid + '.c')),
                         profiles=['aztec36']) for fid in ids]
        if not all(Path(r['source']).is_file() for r in requests):
            self.skipTest('cached source controls absent')
        def cache_only(trials):
            values = []
            for t in trials:
                key = compiler_oracle.identity(t['source'], t['profile'], t.get('target_node', 1),
                                               local_functions=t.get('local_functions', ()))[0]
                value = compiler_oracle.cached(key)
                if value is None: self.skipTest('control compiler cache absent')
                values.append(value)
            return values
        with patch.object(check_function, 'ROOT', ROOT), \
             patch.object(check_function, 'compile_many', side_effect=cache_only):
            reports = check_function.check_many(requests, isolated=True)
            functions = [check_function.validated_function(fid) for fid in ids]
        entries = []
        for request, report, (f, ev) in zip(requests, reports, functions):
            text = Path(request['source']).read_text()
            entries.append(dict(id=request['id'], source=text, report=report, function=f, evidence=ev,
                                compiled=compiler_oracle.cached(report['cache_key'])))
        result, calls = self.publish(entries, requests=requests)
        self.assertEqual(calls, 1)
        blob, model, _ = game()
        accepted = load_promotions(self.root, blob, model, evidence())
        self.assertEqual(len(accepted), 2)
        self.assertEqual(result['functions'], ids)

    def test_competing_ledger_writer_waits_and_preserves_batch_commit(self):
        started, finished = threading.Event(), threading.Event()
        failures = []
        def writer():
            started.set()
            try:
                with transaction.ledger_lock(self.ledger):
                    current = json.loads(self.ledger.read_text())
                    current['blockers']['later'] = dict(reason='retained concurrent update')
                    write_json(self.ledger, current)
            except Exception as exc:
                failures.append(exc)
            finally:
                finished.set()
        thread = threading.Thread(target=writer)
        def gate():
            thread.start()
            self.assertTrue(started.wait(2))
            self.assertFalse(finished.wait(0.1))
            return self.regression
        try:
            self.publish(regression=gate)
        finally:
            thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failures, [])
        ledger = json.loads(self.ledger.read_text())
        self.assertEqual(len(ledger['functions']), 2)
        self.assertIn('later', ledger['blockers'])

    def test_regression_gate_rejects_suite_source_changed_mid_run(self):
        path = self.root / 'tests/control.py'
        path.parent.mkdir()
        path.write_text('before')
        def run(*args, **kwargs):
            path.write_text('after')
            return SimpleNamespace(returncode=0, stdout='OK', stderr='')
        with patch.object(check_function.subprocess, 'run', side_effect=run), \
             self.assertRaisesRegex(FormatError, 'suite inputs changed'):
            check_function.regression_receipt()


if __name__ == '__main__':
    unittest.main()
