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
import fleet
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


def task(tid, kind="function", targets=None, priority=50, deps=()):
    return dict(id=tid, kind=kind, targets=targets or ["t_" + tid], priority=priority, title=tid,
                dependencies=list(deps), origin={}, verifier="check_function",
                budget=dict(fleet.BUDGETS[kind]), notes=[])


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp.name)
        self.ledger = "build/test-fleet-" + uuid.uuid4().hex + ".jsonl"
        self.fleet = fleet.Fleet(self.dir / "fleet", self.ledger, self.dir / "packets")
        self.canonical = patch.object(fleet, "canonical_ids", return_value={"t_done"})
        self.canonical.start()

    def tearDown(self):
        self.canonical.stop()
        for suffix in ("", ".lock"):
            path = ROOT / (self.ledger + suffix)
            if path.exists():
                path.unlink()
        self.temp.cleanup()

    def write_tasks(self, tasks):
        self.fleet.dir.mkdir(parents=True, exist_ok=True)
        self.fleet.tasks.write_text(json.dumps(dict(schema_version=1, tasks=tasks)), encoding="utf-8")

    def test_parallel_processes_never_share_a_task(self):
        self.write_tasks([task("t%d" % i, priority=i) for i in range(5)])
        cmd = [sys.executable, str(ROOT / "tools/fleet.py"), "--fleet-dir", str(self.fleet.dir),
               "--ledger", self.ledger, "claim", "--worker"]
        procs = [subprocess.Popen(cmd + ["w%d" % i], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for i in range(8)]
        outputs = [json.loads(p.communicate(timeout=120)[0]) for p in procs]
        leased = [o["task"]["id"] for o in outputs if o["status"] == "LEASED"]
        self.assertEqual(sorted(leased), ["t%d" % i for i in range(5)])
        self.assertEqual(sum(o["status"] == "NONE" for o in outputs), 3)
        state = json.loads(self.fleet.state.read_text())
        self.assertEqual(len(state["leases"]), 5)

    def test_priority_dependencies_obsolete_and_idempotence(self):
        self.write_tasks([task("dep", priority=1), task("caller", priority=0, deps=["dep"]),
                          task("gone", targets=["t_done"], priority=0), task("other", priority=5)])
        first, lease = fleet.claim(self.fleet, "w1")
        self.assertEqual(first["id"], "dep")  # caller waits; canonical-target task is obsolete
        again, lease2 = fleet.claim(self.fleet, "w1")
        self.assertEqual((again["id"], lease2["lease_id"]), ("dep", lease["lease_id"]))
        second, _ = fleet.claim(self.fleet, "w2", kinds=["function"])
        self.assertEqual(second["id"], "other")
        none, reason = fleet.claim(self.fleet, "w3")
        self.assertIsNone(none)
        with self.assertRaises(FormatError):
            fleet.release(self.fleet, "dep", "w2")
        fleet.release(self.fleet, "dep", "w1")
        fleet.complete(self.fleet, "dep", "NEAR_RECORDED", "w1")
        with patch.object(fleet, "canonical_ids", return_value={"t_done", "t_dep"}):
            self.assertEqual(fleet.claim(self.fleet, "w3")[0]["id"], "caller")
        status = fleet.status(self.fleet)
        self.assertIn("function:completed", status["counts"])

    def test_expired_lease_is_reclaimable(self):
        self.write_tasks([task("a")])
        fleet.claim(self.fleet, "w1", lease_hours=0.1 / 3600)
        time.sleep(0.2)
        claimed, lease = fleet.claim(self.fleet, "w2")
        self.assertEqual((claimed["id"], lease["worker"]), ("a", "w2"))
        history = json.loads(self.fleet.state.read_text())["history"]
        self.assertEqual(history[-1]["replaced_expired_lease"], "w1")

    def test_build_tasks_skips_canonical_and_keeps_targets_unique(self):
        def item(fid, **kw):
            base = dict(id=fid, node="ov01", size=40, extent="CLOSED_CFG", confidence="HIGH", indirect=0,
                        unknown_calls=0, data_references=0, pending_local_dependencies=[], pc_relative_data=0,
                        same_node_unit_ready=True, state="DISCOVERED")
            base.update(kw)
            return base
        functions = [dict(id=x, hunk=3, start=i * 64, end=i * 64 + 40) for i, x in enumerate("ABCDEF")]
        items = [item("A"), item("B", state="CODEGEN_SIMILAR"), item("C", pending_local_dependencies=["A"]),
                 item("D", extent="UNCERTAIN"), item("E"), item("F")]
        ledger = dict(functions={"E": dict(state="FUNCTION_CODE_MATCH")}, attempts={"B": [dict(mnemonic_similarity=0.9)]},
                      blockers={"F": dict(reason="PERSISTENT_CODEGEN_MISMATCH: x")})
        tasks, _ = fleet.build_tasks(functions, items, ledger, [])
        by_target = {t["targets"][0]: t for t in tasks}
        self.assertNotIn("E", by_target)
        self.assertEqual(by_target["F"]["kind"], "blocker-probe")
        self.assertEqual(by_target["B"]["priority"], 15)
        self.assertEqual(by_target["C"]["dependencies"], ["fn-A"])
        self.assertEqual(by_target["D"]["kind"], "review")
        targets = [t for x in tasks for t in x["targets"]]
        self.assertEqual(len(targets), len(set(targets)))


class PacketAndIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp.name)
        self.ledger = "build/test-fleet-" + uuid.uuid4().hex + ".jsonl"
        self.fleet = fleet.Fleet(self.dir / "fleet", self.ledger, ROOT / "build" / ("test-packets-" + uuid.uuid4().hex))

    def tearDown(self):
        import shutil
        for suffix in ("", ".lock"):
            path = ROOT / (self.ledger + suffix)
            if path.exists():
                path.unlink()
        shutil.rmtree(self.fleet.packets, ignore_errors=True)
        self.temp.cleanup()

    def test_packet_is_small_and_self_contained(self):
        from recovery_state import recovery
        attempts = recovery()["attempts"]
        fid = next(f for f in attempts if f not in recovery()["functions"]) if any(
            f not in recovery()["functions"] for f in attempts) else next(iter(attempts))
        prior = dict(ledger_schema=1, record_type="trial", function_id=fid, variant="v-prior",
                     controlled_change="swap the loop test", exact_verdict="DIFFER",
                     prediction=dict(outcome="refuted"), observed_delta=dict(length_delta=2))
        shape_search.append_ledger(self.fleet.ledger(), [prior])
        t = task("fn-x", targets=[fid])
        text = fleet.render_packet(self.fleet, t, dict(worker="luna-fn-x", expires="2026-01-01T00:00:00+00:00"))
        self.assertLessEqual(len(text.encode()), fleet.PACKET_MAX_BYTES)
        for needle in ("assets/` is immutable", "Never promote", fid, "result.json", "schema v2 manifest",
                       "swap the loop test", "--isolated", "luna-fn-x", "NEEDS_EVIDENCE", "BEFORE compiling"):
            self.assertIn(needle, text)

    def result(self, tid, target, **kw):
        directory = self.fleet.task_dir(tid)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "c.c").write_text("recovered() { return 1; }\n", encoding="ascii")
        source = fleet.rel(directory / "c.c")
        best = dict(source=source, profile="aztec36", cache_key="a" * 64, verdict="EQUAL", verifier="check_function",
                    entry=target, options=[], expected_length=4, actual_length=4)
        value = dict(schema_version=1, task_id=tid, worker="w", status="EQUAL_CANDIDATE", target=target, best=best,
                     hypotheses=[dict(id="h1", statement="s", outcome="confirmed", evidence="e")], compile_trials=1,
                     ledger_lines=[], explanation="because", proposed_blocker=None)
        value.update(kw)
        (directory / "result.json").write_text(json.dumps(value), encoding="utf-8")
        return value

    def setup_task(self, tid, target):
        self.fleet.dir.mkdir(parents=True, exist_ok=True)
        self.fleet.tasks.write_text(json.dumps(dict(schema_version=1, tasks=[task(tid, targets=[target])])))

    def test_equal_claim_is_reverified_and_never_promoted(self):
        self.setup_task("t1", "tgt")
        self.result("t1", "tgt")
        rejected = lambda f, t, b: dict(verdict="DIFFER", cache_key="b" * 64)
        with patch.object(fleet, "canonical_ids", return_value=set()):
            out = fleet.intake(self.fleet, "t1", verifier=rejected)
        self.assertEqual(out["intake_status"], "EQUAL_CLAIM_REJECTED")
        self.assertIsNone(out["promote_command"])
        fleet.reopen(self.fleet, "t1")
        confirmed = lambda f, t, b: dict(verdict="EQUAL", cache_key="a" * 64)
        with patch.object(fleet, "canonical_ids", return_value=set()), \
             patch("recovery_state.recovery", return_value=dict(functions={})):
            out = fleet.intake(self.fleet, "t1", verifier=confirmed)
        self.assertEqual(out["intake_status"], "CONFIRMED_EQUAL")
        self.assertTrue(out["promote_command"].startswith("python tools/check_function.py tgt "))
        self.assertNotIn("--isolated", out["promote_command"])
        records = [r for _, r in shape_search.read_ledger(self.fleet.ledger())]
        self.assertEqual([r["intake_status"] for r in records], ["EQUAL_CLAIM_REJECTED", "CONFIRMED_EQUAL"])
        self.assertEqual(records[-1]["promotion"], "NONE_SUPERVISOR_REVIEW_REQUIRED")

    def test_blocked_result_is_summarized_not_written(self):
        self.setup_task("t2", "tgt")
        self.result("t2", "tgt", status="BLOCKED", best=None,
                    proposed_blocker=dict(mechanism="LAYOUT_GAP", text="needs interval"))
        with patch.object(fleet, "canonical_ids", return_value=set()):
            out = fleet.intake(self.fleet, "t2", verifier=lambda *a: self.fail("no verification"))
        self.assertEqual(out["intake_status"], "BLOCKED_FOR_CURATION")
        self.assertEqual(out["blocker_curation"]["written"], False)
        self.assertEqual(out["blocker_curation"]["mechanism"], "LAYOUT_GAP")

    def test_invalid_results_are_rejected(self):
        self.setup_task("t3", "tgt")
        cases = [dict(extra=1), dict(status="WIN"), dict(target="other"),
                 dict(best=dict(self.result("t3", "tgt")["best"], cache_key="xyz")),
                 dict(best=dict(self.result("t3", "tgt")["best"], source="tools/fleet.py")),
                 dict(status="BLOCKED", proposed_blocker=None), dict(status="NEAR", best=None)]
        for change in cases:
            value = self.result("t3", "tgt")
            value.update(change)
            with self.subTest(change=change), self.assertRaises(FormatError):
                fleet.validate_result(self.fleet, task("t3", targets=["tgt"]), value)


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
