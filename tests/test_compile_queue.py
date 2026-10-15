"""Compile-queue coalescing, file locks and shape-search hypothesis reservations."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from common import FormatError
import compile_queue
import file_lock
import shape_search


def dead_pid():
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid


def write_owner(path, pid):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(pid=pid, host=file_lock.HOST, token="other", started="t")), encoding="utf-8")


class FileLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.lock = Path(self.temp.name) / "x.lock"

    def tearDown(self):
        self.temp.cleanup()

    def test_waiter_acquires_after_release(self):
        owner = file_lock.acquire(self.lock, "first", 1)
        threading.Timer(0.3, file_lock.release, (self.lock, owner)).start()
        started = time.monotonic()
        second = file_lock.acquire(self.lock, "second", 5, poll=0.05)
        self.assertGreaterEqual(time.monotonic() - started, 0.2)
        self.assertEqual(json.loads(self.lock.read_text())["token"], second["token"])
        file_lock.release(self.lock, second)
        self.assertFalse(self.lock.exists())

    def test_timeout_and_dead_owner_are_reported_not_stolen(self):
        write_owner(self.lock, os.getpid())
        with self.assertRaisesRegex(FormatError, "lock is held"):
            file_lock.acquire(self.lock, "t", 0.2, "demo", 0.05)
        write_owner(self.lock, dead_pid())
        with self.assertRaisesRegex(FormatError, "stale"):
            file_lock.acquire(self.lock, "t", 5, "demo", 0.05)
        self.assertTrue(self.lock.exists())  # never removed automatically

    def test_release_keeps_foreign_lock(self):
        write_owner(self.lock, os.getpid())
        file_lock.release(self.lock, dict(token="mine"))
        self.assertTrue(self.lock.exists())


class CompileQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cache, self.calls, self.guard = set(), [], threading.Lock()
        self.patches = [patch.object(compile_queue, "QUEUE", Path(self.temp.name) / "queue"),
                        patch.object(compile_queue, "INNER_LOCK", Path(self.temp.name) / "oracle.lock"),
                        patch.object(compile_queue, "trial_key", lambda t: "k-" + t["source"]),
                        patch.object(compile_queue, "is_cached", lambda k: k in self.cache),
                        patch.object(compile_queue, "load", lambda k: dict(cache_key=k, cache_hit=True, status="COMPILED")
                                     if k in self.cache else None),
                        patch.object(compile_queue, "_original_compile_many", self.fake_compile)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.temp.cleanup()

    def fake_compile(self, trials):
        with self.guard:
            self.calls.append(sorted(t["source"] for t in trials))
        time.sleep(0.2)
        with self.guard:
            self.cache.update("k-" + t["source"] for t in trials)

    def test_cache_hit_never_waits_for_a_held_leader(self):
        self.cache.add("k-a")
        write_owner(compile_queue.QUEUE / "leader.lock", os.getpid())
        started = time.monotonic()
        result = compile_queue.compile_many([dict(source="a")], timeout=5)
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertEqual(result[0]["cache_hit"], True)
        self.assertEqual(self.calls, [])

    def test_waiting_requests_coalesce_into_one_batch(self):
        leader = compile_queue.QUEUE / "leader.lock"
        write_owner(leader, os.getpid())  # another live leader is busy
        results = {}

        def request(name):
            results[name] = compile_queue.compile_many([dict(source=name)], timeout=10, poll=0.05)
        threads = [threading.Thread(target=request, args=(n,)) for n in ("a", "b", "c")]
        for t in threads:
            t.start()
        time.sleep(0.5)  # all three are spooled and waiting
        leader.unlink()
        for t in threads:
            t.join(10)
        self.assertEqual(self.calls, [["a", "b", "c"]])
        for name in "abc":
            self.assertEqual(results[name][0]["cache_key"], "k-" + name)
            self.assertIs(results[name][0]["cache_hit"], False)
        self.assertEqual(list((compile_queue.QUEUE / "requests").glob("*.json")), [])

    def test_timeout_and_stale_leader_are_reported(self):
        leader = compile_queue.QUEUE / "leader.lock"
        write_owner(leader, os.getpid())
        with self.assertRaisesRegex(FormatError, "timed out"):
            compile_queue.compile_many([dict(source="x")], timeout=0.3, poll=0.05)
        write_owner(leader, dead_pid())
        with self.assertRaisesRegex(FormatError, "stale"):
            compile_queue.compile_many([dict(source="x")], timeout=5, poll=0.05)
        self.assertTrue(leader.exists())
        self.assertEqual(self.calls, [])

    def test_large_request_drains_capped_batches_and_preserves_result_order(self):
        trials = [dict(source=str(i)) for i in range(7)]
        trials.append(trials[0])  # duplicate requests retain their result slots
        with patch.object(compile_queue, "MAX_BATCH_TRIALS", 2):
            result = compile_queue.compile_many(trials, timeout=10)
        self.assertEqual([r["cache_key"] for r in result], ["k-" + t["source"] for t in trials])
        self.assertEqual([len(c) for c in self.calls], [2, 2, 2, 1])
        self.assertFalse(any(r["cache_hit"] for r in result))

    def test_command_budget_and_oversized_unit_make_progress(self):
        trials = [dict(source="a"), dict(source="b"), dict(source="c")]
        with patch.object(compile_queue, "MAX_BATCH_COMMANDS", 6), \
             patch.object(compile_queue, "command_count", side_effect=lambda t: 10 if t["source"] == "a" else 4):
            compile_queue.compile_many(trials, timeout=10)
        self.assertEqual(self.calls, [["a"], ["b"], ["c"]])

    def test_ordinary_and_mixed_waiters_share_one_backend_batch(self):
        leader = compile_queue.QUEUE / "leader.lock"
        write_owner(leader, os.getpid())
        results, failures = {}, []
        def request(name, mixed):
            try:
                trial = dict(source=name)
                if mixed: trial["object_profiles"] = ["aztec36", "aztec36-large-data"]
                results[name] = compile_queue.compile_many([trial], timeout=10, poll=0.02)
            except Exception as exc:
                failures.append(exc)
        with patch("queued_oracle.compile_many", side_effect=self.fake_compile) as combined:
            threads = [threading.Thread(target=request, args=("a", False)),
                       threading.Thread(target=request, args=("b", True))]
            for thread in threads: thread.start()
            deadline = time.monotonic() + 5
            while compile_queue.status()["pending_requests"] < 2 and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertEqual(compile_queue.status()["pending_requests"], 2)
            leader.unlink()
            for thread in threads: thread.join(10)
        self.assertEqual(failures, [])
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(combined.call_count, 1)
        self.assertEqual(self.calls, [["a", "b"]])
        self.assertEqual(set(results), {"a", "b"})

    def test_round_robin_gives_other_requests_a_slot(self):
        first = compile_queue._write_spool([dict(source=x) for x in "abcd"], ["k-" + x for x in "abcd"])
        second = compile_queue._write_spool([dict(source="e")], ["k-e"])
        # Specify arrival order independently of filesystem timestamp resolution.
        os.utime(first, (1000, 1000))
        os.utime(second, (1001, 1001))
        with patch.object(compile_queue, "MAX_BATCH_TRIALS", 2):
            batch = compile_queue._batch([("k-a", dict(source="a"))])
        self.assertEqual([t["source"] for t in batch], ["a", "e"])

    def test_invalid_collection_window_rejected_before_spooling(self):
        for value in ("-1", "1001", "nan", "inf"):
            with self.subTest(value=value), patch.dict(os.environ, TALES_COMPILE_COALESCE_MS=value), \
                 self.assertRaisesRegex(FormatError, "COALESCE_MS"):
                compile_queue.compile_many([dict(source="a")])
        self.assertFalse((compile_queue.QUEUE / "requests").exists())


class HypothesisReservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "build").mkdir()
        self.variant = dict(id="v", normalized_sha256="n" * 64, profile="aztec36")

    def tearDown(self):
        self.temp.cleanup()

    def test_in_flight_twin_is_waited_for_then_rejected_as_duplicate(self):
        with patch.object(shape_search, "ROOT", self.root):
            path = shape_search.ledger_path("build/h.jsonl")
            marker = shape_search._reservation_path(path, "f", self.variant)
            marker.parent.mkdir(parents=True)
            marker.write_text(json.dumps(dict(pid=os.getpid(), host=file_lock.HOST)), encoding="utf-8")

            def finish():
                shape_search.append_ledger(path, [dict(ledger_schema=1, record_type="trial", function_id="f",
                                                       normalized_sha256="n" * 64, profile="aztec36")])
                marker.unlink()
            threading.Timer(0.3, finish).start()
            _, duplicates, reserved, stale = shape_search.reserve_hypotheses(path, "f", [self.variant], 5, 0.05)
        self.assertEqual(list(duplicates), ["v"])
        self.assertEqual((reserved, stale), ([], []))

    def test_dead_reservation_is_replaced_and_reported(self):
        with patch.object(shape_search, "ROOT", self.root):
            path = shape_search.ledger_path("build/h.jsonl")
            marker = shape_search._reservation_path(path, "f", self.variant)
            marker.parent.mkdir(parents=True)
            marker.write_text(json.dumps(dict(pid=dead_pid(), host=file_lock.HOST)), encoding="utf-8")
            _, duplicates, reserved, stale = shape_search.reserve_hypotheses(path, "f", [self.variant], 1, 0.05)
            self.assertEqual((duplicates, reserved, len(stale)), ({}, [marker], 1))
            shape_search.release_reservations(reserved)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
