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


class PlannerUnlockTests(unittest.TestCase):
    @staticmethod
    def item(fid, **kw):
        base = dict(id=fid, node="ov11", size=130, extent="CLOSED_CFG", confidence="HIGH", indirect=0,
                    unknown_calls=0, data_references=0, pending_local_dependencies=[], pc_relative_data=0,
                    same_node_unit_ready=True, state="DISCOVERED")
        base.update(kw)
        return base

    def test_intake_mentions_and_dependencies_boost_the_blocking_unit(self):
        functions = [dict(id=x, hunk=11, start=s, end=s + 40) for x, s in
                     (("ov11_F_5962", 0x5962), ("ov11_F_5C42", 0x5C42), ("ov11_F_54F8", 0x54F8),
                      ("ov11_F_583A", 0x583A), ("ov11_F_1000", 0x1000))]
        items = [self.item("ov11_F_5962", pending_local_dependencies=["ov11_F_5C42"]),
                 self.item("ov11_F_5C42", pending_local_dependencies=["ov11_F_5962"]),
                 self.item("ov11_F_54F8"), self.item("ov11_F_583A", pending_local_dependencies=["ov11_F_5962"]),
                 self.item("ov11_F_1000")]
        ledger = dict(functions={}, attempts={"ov11_F_54F8": [dict(mnemonic_similarity=0.9)],
                                              "ov11_F_583A": [dict(mnemonic_similarity=0.9)]}, blockers={})
        packages = [dict(kind="DEPENDENCY_SCC_REVIEW", members_complete=True,
                         members=["ov11_F_5962", "ov11_F_5C42"], metadata={})]
        # 54F8 has no pending dependency in the frontier; only its NEEDS_EVIDENCE intake names F_h11_5962.
        intakes = [dict(record_type="fleet_intake", task_id="fn-ov11_F_54F8", targets=["ov11_F_54F8"],
                        intake_status="NEEDS_EVIDENCE_FOR_CURATION",
                        explanation="Missing evidence is an independently recovered F_h11_5962.", proposed_blocker=None)]
        tasks, extra = fleet.build_tasks(functions, items, ledger, packages, intakes=intakes)
        by_id = {t["id"]: t for t in tasks}
        # The mutual pending dependency is a region; it supersedes the package unit.
        self.assertNotIn("unit-ov11_F_5962-5C42", by_id)
        region = by_id["reg-ov11_5962-5C6A"]
        self.assertEqual((region["kind"], region["targets"]), ("region", ["ov11_F_5962", "ov11_F_5C42"]))
        self.assertEqual(region["unlocks_targets"], ["ov11_F_54F8", "ov11_F_583A"])
        self.assertEqual((region["base_priority"], region["priority"]), (10, 1))
        self.assertEqual(by_id["fn-ov11_F_583A"]["blocked_by"], ["ov11_F_5962"])
        self.assertEqual(by_id["fn-ov11_F_54F8"]["blocked_by"], ["ov11_F_5962"])
        self.assertLess(region["priority"], by_id["fn-ov11_F_1000"]["priority"])
        self.assertEqual(by_id["fn-ov11_F_583A"]["priority"], 15)  # blocked tasks are not boosted
        self.assertEqual(extra["untasked_blocking_leaves"], [])
        without, _ = fleet.build_tasks(functions, items, ledger, packages)
        self.assertEqual({t["id"]: t for t in without}["reg-ov11_5962-5C6A"]["unlocks"], 1)
        # With region planning disabled the package unit path still works.
        units, _ = fleet.build_tasks(functions, items, ledger, packages, intakes=intakes, regions=[])
        unit = {t["id"]: t for t in units}["unit-ov11_F_5962-5C42"]
        self.assertEqual((unit["base_priority"], unit["priority"]), (30, 30 - 2 * fleet.UNLOCK_BOOST))

    def test_blocked_task_is_not_boosted_and_waiting_tasks_count(self):
        tasks = [task("leaf", targets=["L"], priority=40), task("mid", targets=["M"], priority=44),
                 task("top", targets=["T"], priority=55, deps=["mid"]), task("rev", "review", ["R"], 80)]
        graph = {"L": {"M", "R"}, "M": {"T"}}
        fleet.apply_unlocks(tasks, graph)
        by_id = {t["id"]: t for t in tasks}
        self.assertEqual((by_id["leaf"]["unlocks"], by_id["leaf"]["priority"]), (1, 40 - fleet.UNLOCK_BOOST))
        # Review targets never count; a task that itself waits keeps its priority.
        self.assertEqual((by_id["mid"]["unlocks"], by_id["mid"]["priority"], by_id["mid"]["blocked_by"]),
                         (1, 44, ["L"]))
        self.assertEqual(by_id["top"]["unlocks"], 0)

    def test_blocked_leaf_without_task_is_reported(self):
        functions = [dict(id=x, hunk=14, start=s, end=s + 40) for x, s in (("ov14_F_0000", 0), ("ov14_F_0412", 0x412))]
        items = [self.item("ov14_F_0000", node="ov14", pending_local_dependencies=["ov14_F_0412"]),
                 self.item("ov14_F_0412", node="ov14")]
        ledger = dict(functions={}, attempts={}, blockers={"ov14_F_0412": dict(reason="CHAR_RETURN_EXTENSION: x")})
        with patch.object(fleet, "_blocker_class", return_value="ABI_OR_CODEGEN_PROFILE"):
            tasks, extra = fleet.build_tasks(functions, items, ledger, [])
        self.assertNotIn("fn-ov14_F_0412", {t["id"] for t in tasks})
        self.assertEqual(extra["untasked_blocking_leaves"][0]["id"], "ov14_F_0412")
        self.assertEqual(extra["untasked_blocking_leaves"][0]["blocker_class"], "ABI_OR_CODEGEN_PROFILE")


class RegionTests(unittest.TestCase):
    """Synthetic hunk-11 layout: A B G C D [gap] F E (A, C, F canonical)."""

    CYCLE = ("CYCLIC_INTER_OBJECT_PC_CALL: exact displacement requires the full physical 0x0100..0x01C0 "
             "interval; recover it in order.")

    @staticmethod
    def fn(fid, start, end, calls=(), instructions=()):
        return dict(id="ov11_F_" + fid, hunk=11, node="ov11", start=start, end=end, size=end - start,
                    direct_callees=[dict(basis="PC_RELATIVE", hunk=11, id="ov11_F_" + c, offset=o, site=s)
                                    for c, o, s in calls],
                    instructions=list(instructions))

    def setUp(self):
        fn = self.fn
        self.functions = [fn("0100", 0x100, 0x120), fn("0120", 0x120, 0x160, [("01C0", 0x1C0, 0x130)]),
                          fn("0160", 0x160, 0x180), fn("0180", 0x180, 0x1C0),
                          fn("01C0", 0x1C0, 0x200, [("0240", 0x240, 0x1D0)]), fn("0210", 0x210, 0x240),
                          fn("0240", 0x240, 0x280, [("01C0", 0x1C0, 0x250)])]
        self.items = [PlannerUnlockTests.item("ov11_F_" + x, size=0x40) for x in ("0120", "0160", "01C0", "0240")]
        self.canonical = {"ov11_F_0100", "ov11_F_0180", "ov11_F_0210"}
        self.ledger = dict(functions={c: dict(state="FUNCTION_CODE_MATCH") for c in self.canonical}, attempts={
            "ov11_F_0120": [dict(source_sha256="ab" * 32, verdict="DIFFER", mnemonic_similarity=0.9,
                                 cache_key="c" * 64, expected_length=64, actual_length=66)]},
            blockers={"ov11_F_0240": dict(reason=self.CYCLE, state="BLOCKED")})

    def test_layout_interval_widens_cycle_into_one_region(self):
        import fleet_regions
        regions = fleet_regions.build_regions(self.functions, self.items, self.canonical, self.ledger["blockers"],
                                              self.ledger["attempts"], source_exists=lambda p: True,
                                              existing_dirs=["fn-ov11_F_0120", "fn-other"])
        self.assertEqual(len(regions), 1)
        r = regions[0]
        self.assertEqual((r["id"], r["interval"]), ("reg-ov11_0100-0280", [0x100, 0x280]))
        self.assertEqual(r["new_members"], ["ov11_F_0120", "ov11_F_0160", "ov11_F_01C0", "ov11_F_0240"])
        self.assertEqual(r["scc_members"], ["ov11_F_0120", "ov11_F_01C0", "ov11_F_0240"])
        self.assertEqual(r["independent_members"], ["ov11_F_0160"])  # inside the interval, no prerequisites
        self.assertEqual(r["gaps"], [dict(start=0x200, end=0x210, size=16, ownership="UNKNOWN_NOT_ASSIGNED")])
        self.assertEqual(r["options"], ["separate_objects", "allow_original_gaps"])
        self.assertEqual(r["bridges_not_linked"], ["ov11_F_0100", "ov11_F_0180", "ov11_F_0210"])
        self.assertEqual(r["edge_kinds"]["layout_interval"], 2)  # 0240 needs 0120 and 0160
        cand = r["candidates"]["ov11_F_0120"]
        self.assertEqual(cand["candidates"][0]["source"], "recovery/candidates/ov11_F_0120/" + "ab" * 32 + ".c")
        self.assertEqual(cand["experiment_dirs"], ["experiments/fleet/fn-ov11_F_0120"])
        commands = fleet_regions.region_commands(r, "experiments/fleet/" + r["id"])
        self.assertIn("verify-unit ov11_F_0120 experiments/fleet/reg-ov11_0100-0280/vNN/ov11_F_0120.c "
                      "--member ov11_F_0160=", commands["verify"])
        self.assertTrue(commands["verify"].endswith("--separate-objects --allow-original-gaps "
                                                    "--output-dir experiments/fleet/reg-ov11_0100-0280/runs"))
        self.assertEqual(commands["promote_shape"].count("--member"), 3)

    def test_member_tasks_are_blocked_by_region_and_independent_ones_stay_open(self):
        tasks, _ = fleet.build_tasks(self.functions, self.items, self.ledger, [])
        by_id = {t["id"]: t for t in tasks}
        region = by_id["reg-ov11_0100-0280"]
        self.assertEqual((region["kind"], region["verifier"], region["budget"]["max_compile_trials"]),
                         ("region", "check_unit", 40))
        self.assertEqual(by_id["fn-ov11_F_0120"]["blocked_by_region"], region["id"])
        self.assertEqual(by_id["blk-ov11_F_0240"]["blocked_by_region"], region["id"])
        self.assertNotIn("blocked_by_region", by_id["fn-ov11_F_0160"])
        self.assertEqual(region["member_tasks_blocked"], 3)  # fn-0120, fn-01C0, blk-0240
        self.assertFalse(any(t["kind"] == "review" and set(t["targets"]) & set(region["targets"]) for t in tasks))
        state = dict(leases={}, completed={}, reopened={}, history=[])
        self.assertEqual(fleet.task_state(by_id["fn-ov11_F_0120"], state, {}, set(), by_id, 0), "blocked_by_region")
        with tempfile.TemporaryDirectory() as temp:
            f = fleet.Fleet(Path(temp) / "fleet", "build/test-fleet-" + uuid.uuid4().hex + ".jsonl", Path(temp) / "p")
            f.dir.mkdir(parents=True)
            f.tasks.write_text(json.dumps(dict(schema_version=1, tasks=tasks)), encoding="utf-8")
            with patch.object(fleet, "canonical_ids", return_value=set()):
                claimed = [fleet.claim(f, "w%d" % i)[0] for i in range(4)]
        self.assertEqual({t["id"] for t in claimed if t}, {region["id"], "fn-ov11_F_0160"})

    def test_short_form_call_depends_on_unrecovered_bytes_between(self):
        import fleet_regions
        call = dict(offset=0x10, raw="4eba00fc", size=4, mnemonic="jsr", operands="")
        functions = [self.fn("0000", 0, 0x20, [("0100", 0x100, 0x10)], [call]), self.fn("0020", 0x20, 0xF0),
                     self.fn("00F0", 0xF0, 0x100), self.fn("0100", 0x100, 0x120)]
        by_id = {f["id"]: f for f in functions}
        unrecovered = set(by_id) - {"ov11_F_00F0"}
        edges = fleet_regions.region_edges(by_id, {}, unrecovered, [])
        self.assertEqual(edges[("ov11_F_0000", "ov11_F_0020")], {"short_form_if_compacted"})
        self.assertEqual(edges[("ov11_F_0000", "ov11_F_0100")], {"call"})
        # With the 0xD0 bytes between recovered, the compact distance stays long.
        edges = fleet_regions.region_edges(by_id, {}, {"ov11_F_0000", "ov11_F_0100"}, [])
        self.assertEqual(set(edges), {("ov11_F_0000", "ov11_F_0100")})

    def test_region_packet_and_verify_argv(self):
        tasks, _ = fleet.build_tasks(self.functions, self.items, self.ledger, [])
        region = next(t for t in tasks if t["kind"] == "region")
        packets = ROOT / "build" / ("test-packets-" + uuid.uuid4().hex)
        ledger = "build/test-fleet-" + uuid.uuid4().hex + ".jsonl"
        try:
            with tempfile.TemporaryDirectory() as temp:
                f = fleet.Fleet(Path(temp) / "fleet", ledger, packets)
                f.dir.mkdir(parents=True)
                f.tasks.write_text(json.dumps(dict(schema_version=1, tasks=tasks)), encoding="utf-8")
                text = fleet.render_packet(f, region, dict(worker="luna-reg", expires="2026-01-01T00:00:00+00:00"))
                self.assertLessEqual(len(text.encode()), fleet.PACKET_MAX_BYTES)
                for needle in ("Region protocol", "verify-region reg-ov11_0100-0280", "GAP UNKNOWN_NOT_ASSIGNED",
                               "NEW ov11_F_0120 scc", "independent", "canonical (reused)", "best.members",
                               "at most 40 compiler trials", '"member"', "entry `ov11_F_0120`"):
                    self.assertIn(needle, text)
                variant = f.task_dir(region["id"]) / "v01"
                variant.mkdir(parents=True)
                with patch.object(fleet, "canonical_ids", return_value=set()):
                    with self.assertRaisesRegex(FormatError, "missing member source"):
                        fleet.region_verify_argv(f, region["id"], variant)
                    for m in region["targets"]:
                        (variant / (m + ".c")).write_text("recovered() { return 0; }\n", encoding="ascii")
                    argv = fleet.region_verify_argv(f, region["id"], variant)
                    with self.assertRaisesRegex(FormatError, "inside the task directory"):
                        fleet.region_verify_argv(f, region["id"], packets)
                src = fleet.rel(variant)
                self.assertEqual(argv[:2], ["ov11_F_0120", src + "/ov11_F_0120.c"])
                self.assertEqual(argv.count("--member"), 3)
                self.assertIn("--allow-original-gaps", argv)
                self.assertNotIn("--isolated", argv)  # _run_wrapped adds it
        finally:
            import shutil
            shutil.rmtree(packets, ignore_errors=True)


CX_PS = """f2-author-1   01a0  gpt-6-luna/xhigh   up   4h25m  idle   0m08s  cmds-failed 0/8  simantw_recon  | thinking
luna-fn-x     01a1  gpt-6-luna/xhigh   up  49m19s  idle   0m02s  cmds-failed 0/20  tales_recon  | $ python tools/x.py
luna-fn-y     01a2  gpt-6-luna/xhigh   up   8m12s  idle   0m20s  cmds-failed 1/9  tales_recon  | thinking
"""


class HostGuardTests(unittest.TestCase):
    def test_parse_cx_ps(self):
        self.assertEqual(fleet.parse_cx_ps(CX_PS, "tales_recon"), (3, 2))
        self.assertEqual(fleet.parse_cx_ps("no running codex exec workers\n", "tales_recon"), (0, 0))

    def test_caps_and_reasons(self):
        counted = dict(status="COUNTED", total=18, here=2, detail=None)
        self.assertEqual(fleet.host_cap(8, counted, env={})[0], 2)  # host room 20-18
        n, reasons = fleet.host_cap(8, counted, env={"TALES_FLEET_HOST_MAX": "40"})
        self.assertEqual(n, 4)  # repository room 6-2
        self.assertIn("TALES_FLEET_MAX=6", reasons[-1])
        self.assertEqual(fleet.host_cap(3, dict(counted, total=30), env={})[0], 0)
        n, reasons = fleet.host_cap(8, dict(status="CX_MISSING", total=None, here=None, detail="cx not found"),
                                    leased_here=5, env={})
        self.assertEqual(n, 1)
        self.assertIn("cx not found", reasons[0])
        n, reasons = fleet.host_cap(2, dict(status="CX_PS_FAILED", total=None, here=None, detail="timeout"), env={})
        self.assertEqual(n, 0)
        self.assertIn("launching nothing", reasons[0])

    def test_running_workers_handles_missing_cx_and_failures(self):
        self.assertEqual(fleet.running_workers("~/definitely-missing-cx.py")["status"], "CX_MISSING")

        class Proc:
            returncode, stdout, stderr = 0, CX_PS, ""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as handle:
            path = handle.name
        try:
            counted = fleet.running_workers(path, runner=lambda *a, **k: Proc())
            self.assertEqual((counted["status"], counted["total"]), ("COUNTED", 3))

            def hang(*a, **k):
                raise subprocess.TimeoutExpired("cx", 1)
            self.assertEqual(fleet.running_workers(path, runner=hang)["status"], "CX_PS_FAILED")
        finally:
            os.unlink(path)


class LaunchPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp.name)
        self.fleet = fleet.Fleet(self.dir / "fleet", "build/test-fleet-" + uuid.uuid4().hex + ".jsonl",
                                 ROOT / "build" / ("test-packets-" + uuid.uuid4().hex))
        self.fleet.dir.mkdir(parents=True)
        self.fleet.tasks.write_text(json.dumps(dict(schema_version=1, tasks=[task("a"), task("b"), task("c")])))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.fleet.packets, ignore_errors=True)
        self.temp.cleanup()

    def test_launch_plan_caps_and_prints_both_shells(self):
        workers = dict(status="COUNTED", total=19, here=0, detail=None)
        with patch.object(fleet, "canonical_ids", return_value=set()), \
             patch.object(fleet, "write_packet", side_effect=lambda f, tid: (f.task_dir(tid) / "PROMPT.md", 100)):
            lines, claimed = fleet.launch_plan(self.fleet, 3, workers=workers, env={})
        self.assertEqual(claimed, ["a"])
        self.assertTrue(any("TALES_FLEET_HOST_MAX=20 -> at most 1" in l for l in lines))
        bash = [l for l in lines if l.startswith("python ~/.codex-dashboard/cx.py run -n luna-a ")]
        self.assertEqual(len(bash), 1)
        self.assertIn(" < ", bash[0])
        self.assertIn(fleet.PS_UTF8, lines)
        ps = [l for l in lines if l.startswith("Get-Content -Raw -Encoding UTF8 ")]
        self.assertEqual(len(ps), 1)
        self.assertIn("| python $HOME/.codex-dashboard/cx.py run -n luna-a ", ps[0])
        with patch.object(fleet, "canonical_ids", return_value=set()):
            lines, claimed = fleet.launch_plan(self.fleet, 3, workers=dict(workers, total=25), env={})
        self.assertEqual(claimed, [])


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
                       "swap the loop test", "--isolated", "luna-fn-x", "NEEDS_EVIDENCE", "BEFORE compiling",
                       "BLOCKED HOST_TOOLS_UNRESPONSIVE", "python tools/fleet.py renew fn-x --worker luna-fn-x"):
            self.assertIn(needle, text)
        # The liveness check is the first instruction after the header.
        self.assertLess(text.index("First step (host liveness)"), text.index("## Rules"))

    def test_intake_all_summarizes_and_skips_already_intaken(self):
        self.fleet.dir.mkdir(parents=True, exist_ok=True)
        tasks = [task("eq", targets=["t_eq"]), task("bad", targets=["t_bad"]), task("ne", targets=["t_ne"]),
                 task("old", targets=["t_old"]), task("none", targets=["t_none"])]
        self.fleet.tasks.write_text(json.dumps(dict(schema_version=1, tasks=tasks)))
        self.result("eq", "t_eq")
        self.result("bad", "t_bad", status="WIN")
        self.result("ne", "t_ne", status="NEEDS_EVIDENCE", best=None, explanation="needs ov11_F_5962")
        self.result("old", "t_old", status="NEAR")
        self.fleet.task_dir("none").mkdir(parents=True, exist_ok=True)  # no result.json yet
        confirmed = lambda f, t, b: dict(verdict="EQUAL", cache_key="a" * 64)
        with patch.object(fleet, "canonical_ids", return_value=set()), \
             patch("recovery_state.recovery", return_value=dict(functions={})):
            fleet.intake(self.fleet, "old")
            out = fleet.intake_all(self.fleet, verifier=confirmed)
            again = fleet.intake_all(self.fleet, verifier=confirmed)
        self.assertEqual(out["counts"]["confirmed_equal"], 1)
        self.assertTrue(out["confirmed_equal"][0]["promote_command"].startswith("python tools/check_function.py t_eq"))
        self.assertEqual([r["task"] for r in out["rejected"]], ["bad"])
        self.assertIn("status must be", out["rejected"][0]["reason"])
        self.assertEqual([r["task"] for r in out["needs_evidence"]], ["ne"])
        self.assertEqual([r["task"] for r in out["already_intaken"]], ["old"])
        self.assertEqual(out["promotion"], "NONE_SUPERVISOR_REVIEW_REQUIRED")
        self.assertEqual(again["counts"]["already_intaken"], 3)  # eq, ne, old; bad stays rejected
        self.assertEqual([r["task"] for r in again["rejected"]], ["bad"])

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

    def test_unit_result_names_every_new_member_source(self):
        unit = task("u1", kind="unit", targets=["a", "b"])
        self.setup_task("u1", "a")
        value = self.result("u1", "a,b")
        member = self.fleet.task_dir("u1") / "b.c"
        member.write_text("recovered() { return 2; }\n", encoding="ascii")
        best = dict(value["best"], verifier="check_unit", entry="a", options=["separate_objects"],
                    members={"b": fleet.rel(member)})
        value["best"] = best
        self.assertEqual(fleet.validate_result(self.fleet, unit, value)["best"]["members"], {"b": fleet.rel(member)})
        command = fleet.promote_command(best)
        self.assertTrue(command.startswith("python tools/check_unit.py a "))
        self.assertIn("--separate-objects --member b=" + fleet.rel(member), command)
        for members in ({"a": fleet.rel(member)}, {"x": fleet.rel(member)}, {"b": "tools/fleet.py"}, {}):
            with self.subTest(members=members), self.assertRaises(FormatError):
                fleet.validate_result(self.fleet, unit, dict(value, best=dict(best, members=members)))
        with self.assertRaises(FormatError):
            fleet.validate_result(self.fleet, unit, dict(value, best=dict(best, verifier="check_function")))
        seen = {}
        with patch("compile_queue.install"), patch("check_unit.check",
                   side_effect=lambda *a, **k: seen.update(k) or [dict(verdict="EQUAL", cache_key="a" * 64)]):
            self.assertEqual(fleet.reverify(self.fleet, unit, best)["verdict"], "EQUAL")
        self.assertEqual(seen["member_sources"], {"b": ROOT / fleet.rel(member)})
        self.assertTrue(seen["isolated"])

    def test_unit_packet_explains_multi_member_authoring(self):
        unit = task("u2", kind="unit", targets=["ov11_F_5962", "ov11_F_5C42"])
        unit["verifier"] = "check_unit"
        text = fleet.render_packet(self.fleet, unit, None)
        self.assertIn("--member ID=", text)
        self.assertIn('"members"', text)


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
