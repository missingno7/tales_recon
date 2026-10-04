import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import census
import evidence_snapshot as snapshots
from common import FormatError, write_json


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('assets', 'tools', 'evidence/functions', 'recovery', 'custom/parts'):
            (self.root / name).mkdir(parents=True)
        (self.root / 'assets/disk.adf').write_bytes(b'fixture')
        (self.root / 'tools/parser.py').write_text('parser = 1\n')
        write_json(self.root / 'evidence/fixture-lock.json', {'locked': True})
        write_json(self.root / 'evidence/functions/ledger.json', {'analysis_identity': {'parser.py': 'digest'}})
        write_json(self.root / 'recovery/ledger.json', {'functions': {}, 'attempts': {}, 'blockers': {}})
        self.loader = Mock(return_value=(b'game', {'hunks': [{'number': 0}]}, {'count': 0}))

    def read(self):
        return snapshots.game_read(self.root, self.loader)

    def canonical(self):
        (self.root / 'custom/source.c').write_text('recovered() {}\n')
        write_json(self.root / 'custom/proof.json', {'comparison': {'complete_unit_receipt': 'custom/unit.json'}})
        write_json(self.root / 'custom/unit.json', {'object_groups': [['A', 'B']],
                                                  'ordered_members': [{'id': 'A'}, {'id': 'B'}]})
        (self.root / 'custom/unit.c').write_text('unit\n')
        for name in ('A', 'B'):(self.root / 'custom/parts' / (name + '.c')).write_text(name)
        write_json(self.root / 'recovery/ledger.json', {'functions': {'A': {'source': 'custom/source.c',
                                                                          'proof': 'custom/proof.json'}}})

    def test_reuses_only_within_scope_and_returns_independent_values(self):
        self.read();self.read()
        self.assertEqual(self.loader.call_count, 2)
        with snapshots.snapshot() as state:
            first = self.read()
            first[1]['hunks'][0]['number'] = 99
            first[2]['count'] = 99
            second = self.read()
            self.assertEqual(second[1]['hunks'][0]['number'], 0)
            self.assertEqual(second[2]['count'], 0)
            self.assertEqual((state.misses, state.hits), (1, 1))
        self.assertFalse(state.entries)
        self.assertFalse(state.parsed)
        self.read()
        self.assertEqual(self.loader.call_count, 4)

    def test_content_edit_with_preserved_file_metadata_invalidates(self):
        import os
        path = self.root / 'assets/disk.adf'
        with snapshots.snapshot() as state:
            self.read()
            old = path.stat()
            path.write_bytes(b'changed')  # Same length; mtime deliberately restored.
            os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns))
            self.read()
            self.assertEqual((state.misses, state.invalidations), (2, 1))

    def test_tool_inventory_addition_deletion_and_lock_edit_invalidate(self):
        with snapshots.snapshot() as state:
            self.read()
            extra = self.root / 'tools/new.py'
            extra.write_text('new')
            self.read()
            extra.unlink()
            self.read()
            write_json(self.root / 'evidence/fixture-lock.json', {'locked': False})
            self.read()
            self.assertEqual((state.misses, state.invalidations), (4, 3))

    def test_canonical_paths_units_parts_and_deletions_invalidate(self):
        self.canonical()
        paths = ['custom/source.c', 'custom/proof.json', 'custom/unit.json', 'custom/unit.c', 'custom/parts/B.c']
        for name in paths:
            with self.subTest(name=name), snapshots.snapshot() as state:
                self.read()
                path = self.root / name
                original = path.read_bytes()
                path.unlink()
                self.read()
                path.write_bytes(original)
                self.read()
                self.assertEqual((state.misses, state.invalidations), (3, 2))

    def test_new_canonical_member_invalidates_but_attempts_do_not(self):
        with snapshots.snapshot() as state:
            self.read()
            path = self.root / 'recovery/ledger.json'
            ledger = json.loads(path.read_text())
            ledger['attempts']['A'] = [{'verdict': 'DIFFER'}]
            ledger['blockers']['B'] = {'state': 'BLOCKED'}
            write_json(path, ledger)
            self.read()
            self.assertEqual((state.misses, state.hits), (1, 1))
            self.canonical()
            self.read()
            self.assertEqual(state.invalidations, 1)

    def test_analysis_and_optional_runtime_evidence_are_bound(self):
        with snapshots.snapshot() as state:
            self.read()
            write_json(self.root / 'evidence/functions/ledger.json', {'analysis_identity': {}, 'changed': True})
            self.read()
            write_json(self.root / 'evidence/experiments/runtime-matches.json', {'changed': True})
            self.read()
            write_json(self.root / 'evidence/experiments/overlay-topology.json', {'changed': True})
            self.read()
            self.assertEqual(state.invalidations, 3)

    def test_strict_and_advisory_entries_never_mix(self):
        with snapshots.snapshot() as state:
            strict = self.read()
            with census.advisory_image():
                self.loader.return_value = (b'game', {'hunks': []}, None)
                advisory = self.read()
                self.assertIsNone(advisory[2])
            self.assertEqual(self.read(), strict)
            self.assertEqual((state.misses, state.hits), (2, 1))

    def test_change_during_creation_and_loader_failure_never_cache(self):
        def changed():
            (self.root / 'assets/disk.adf').write_bytes(b'edited')
            return b'game', {}, {}
        with snapshots.snapshot() as state:
            self.loader.side_effect = changed
            with self.assertRaisesRegex(FormatError, 'inputs changed'):
                self.read()
            self.assertFalse(state.entries)
            self.loader.side_effect = FormatError('fixture mismatch')
            with self.assertRaisesRegex(FormatError, 'fixture mismatch'):
                self.read()
            self.assertFalse(state.entries)

    def test_nested_decorators_share_scope_and_disabled_mode_is_respected(self):
        @snapshots.scoped
        def pair():
            self.read();self.read()
        with snapshots.snapshot() as state:
            pair();pair()
            self.assertEqual((state.misses, state.hits), (1, 3))
        with snapshots.snapshot(enabled=False):pair()
        self.assertEqual(self.loader.call_count, 3)

    def test_exception_discards_scope_and_other_threads_do_not_inherit_it(self):
        with self.assertRaisesRegex(ValueError, 'stop'):
            with snapshots.snapshot() as state:
                self.read()
                thread = threading.Thread(target=self.read)
                thread.start();thread.join()
                self.assertEqual(self.loader.call_count, 2)
                raise ValueError('stop')
        self.assertFalse(state.entries)
        self.assertIsNone(snapshots._ACTIVE.get())

    def test_workspace_and_advisory_asset_scope(self):
        with snapshots.snapshot() as state, census.advisory_image():
            self.read()
            write_json(self.root / 'recovery/ledger.json', {'functions': {'broken': {}}})
            (self.root / 'assets/dos').mkdir()
            (self.root / 'assets/dos/ignored.img').write_bytes(b'comparison media')
            self.read()
            self.assertEqual(state.hits, 1)
            second = self.root / 'second'
            (second / 'assets').mkdir(parents=True)
            (second / 'assets/disk.adf').write_bytes(b'other')
            snapshots.game_read(second, self.loader)
            self.assertEqual(state.misses, 2)

    def test_canonical_paths_cannot_escape_root(self):
        write_json(self.root / 'recovery/ledger.json', {'functions': {'A': {'source': '../outside.c', 'proof': 'proof.json'}}})
        with snapshots.snapshot(), self.assertRaisesRegex(FormatError, 'escapes workspace'):
            self.read()
        self.loader.assert_not_called()


class RealSnapshotTests(unittest.TestCase):
    def test_cached_advisory_image_does_not_bypass_strict_proof_loader(self):
        from analysis_support import game
        with snapshots.snapshot(), patch.object(census, 'load_promotions', side_effect=FormatError('proof rejected')):
            with census.advisory_image():
                blob, model, outputs = game()
                self.assertIsNone(outputs)
                self.assertEqual(game(), (blob, model, None))
            with self.assertRaisesRegex(FormatError, 'proof rejected'):game()

    def test_cached_strict_read_rejects_changed_real_fixture_or_proof(self):
        from analysis_support import game, ROOT
        original_read = Path.read_bytes
        ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
        proof = ROOT / next(iter(ledger['functions'].values()))['proof']
        fixture = next((ROOT / 'assets').glob('*.adf'))
        for changed, error in ((fixture, 'fixture lock mismatch'), (proof, 'promotion receipt changed')):
            with self.subTest(path=changed), snapshots.snapshot() as state:
                game()
                def edited(path):
                    raw = original_read(path)
                    return raw + b' ' if path == changed else raw
                with patch.object(Path, 'read_bytes', edited):
                    with self.assertRaisesRegex(FormatError, error):game()
                self.assertEqual(state.invalidations, 1)
                self.assertFalse(state.entries)
                game()
                self.assertEqual(state.misses, 3)


if __name__ == '__main__':unittest.main()
