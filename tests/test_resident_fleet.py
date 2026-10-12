"""Resident eligibility, measured data model, advisory routes and Claude waves."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from common import FormatError
import fleet
from grinder import deferral_reason, eligible
from recovery_plan import _constraints
from recovery_state import data_model, resident_deferral, resident_gate, runtime_floor


def evidence_function(fid, start, ownership="UNKNOWN", calls=(), data=(), relocations=()):
    return dict(id=fid, node="resident", hunk=0, start=start, end=start + 40, ownership=ownership,
                direct_callees=list(calls), referenced_data=list(data), relocations=list(relocations))


ABS = dict(target_hunk=1, addend_raw=0x3AB8, type="HUNK_RELOC32")
A4_DATA = dict(kind="A4_RELATIVE", hunk=1, offset=0x3AC0, instruction_offset=0x10)
A4_SLOT = dict(kind="A4_RELATIVE", hunk=1, offset=0x96, instruction_offset=0x20)
STUB_CALL = dict(basis="A4_RELOCATED_JMP_STUB", hunk=0, id="resident_F_3C0E", offset=0x3C0E, site=0x20)


class DataModelTests(unittest.TestCase):
    def test_jump_table_slots_are_not_data(self):
        f = evidence_function("resident_F_4EC6", 0x4EC6, calls=[STUB_CALL], data=[A4_SLOT], relocations=[ABS])
        self.assertEqual(data_model(f), "ABSOLUTE")
        self.assertEqual(data_model(dict(f, relocations=[])), "NONE")

    def test_small_large_and_mixed_models(self):
        self.assertEqual(data_model(evidence_function("a", 0, data=[A4_DATA])), "A4")
        self.assertEqual(data_model(evidence_function("b", 0, relocations=[ABS])), "ABSOLUTE")
        self.assertEqual(data_model(evidence_function("c", 0, data=[A4_DATA], relocations=[ABS])), "MIXED")
        # A code-hunk relocation is not a data reference.
        self.assertEqual(data_model(evidence_function("d", 0, relocations=[dict(ABS, target_hunk=0)])), "NONE")


class ResidentEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.functions = [evidence_function("resident_F_463E", 0x463E, relocations=[ABS]),
                          evidence_function("resident_F_75D8", 0x75D8, ownership="RUNTIME_CANDIDATE"),
                          evidence_function("resident_F_88A6", 0x88A6, data=[A4_DATA]),
                          evidence_function("resident_F_0100", 0x0100, data=[A4_DATA], relocations=[ABS])]
        self.floor = runtime_floor(self.functions)

    def test_runtime_floor_is_lowest_runtime_candidate(self):
        self.assertEqual(self.floor, 0x75D8)
        self.assertIsNone(runtime_floor([f for f in self.functions if f["ownership"] == "UNKNOWN"]))

    def test_game_code_is_eligible_and_runtime_tail_is_deferred(self):
        by_id = {f["id"]: f for f in self.functions}
        self.assertIsNone(resident_deferral(by_id["resident_F_463E"], self.floor))
        self.assertEqual(resident_deferral(by_id["resident_F_88A6"], self.floor), "RESIDENT_RUNTIME_TAIL")
        self.assertEqual(resident_deferral(by_id["resident_F_0100"], self.floor), "RESIDENT_MIXED_DATA_MODEL")
        self.assertEqual(resident_deferral(by_id["resident_F_463E"], None), "RESIDENT_RUNTIME_UNBOUNDED")
        self.assertIsNone(resident_deferral(dict(by_id["resident_F_463E"], node="ov04"), self.floor))
        helper_call = dict(basis="A4_RELOCATED_JMP_STUB", hunk=0, id="resident_F_7F9C", offset=0x7F9C, site=0x14)
        caller = dict(by_id["resident_F_463E"], direct_callees=[helper_call])
        self.assertEqual(resident_deferral(caller, self.floor, {(0, 0x7F9C)}), "RESIDENT_IMPLICIT_HELPER_A4_ROUTE")
        self.assertIsNone(resident_deferral(caller, self.floor, {(0, 0x7B00)}))

    def test_ranked_items_enter_queue_only_when_classified_safe(self):
        item = dict(id="resident_F_463E", node="resident", size=56, extent="CLOSED_CFG", confidence="HIGH",
                    indirect=0, unknown_calls=0, data_references=0, pending_local_dependencies=[],
                    pc_relative_data=0, same_node_unit_ready=True, resident_deferral=None)
        args = type("Args", (), dict(max_unknown_calls=1, max_data_references=40))()
        self.assertTrue(eligible(item, args, 256))
        self.assertIsNone(deferral_reason(item, args, 256))
        self.assertEqual(_constraints(item, 256), [])
        for reason in ("RESIDENT_RUNTIME_TAIL", "RESIDENT_MIXED_DATA_MODEL"):
            deferred = dict(item, resident_deferral=reason)
            self.assertFalse(eligible(deferred, args, 256))
            self.assertEqual(deferral_reason(deferred, args, 256), reason)
            self.assertIn(reason, _constraints(deferred, 256))
        # An unclassified resident item (no measured deferral field) stays deferred.
        legacy = {k: v for k, v in item.items() if k != "resident_deferral"}
        self.assertEqual(resident_gate(legacy), "RESIDENT_UNCLASSIFIED")
        self.assertFalse(eligible(legacy, args, 256))
        # Other safety limits still apply to eligible resident items.
        self.assertFalse(eligible(dict(item, indirect=2), args, 256))


def rank_item(fid, **kw):
    base = dict(id=fid, node="resident", size=56, extent="CLOSED_CFG", confidence="HIGH", indirect=0,
                unknown_calls=0, data_references=0, pending_local_dependencies=[], pc_relative_data=0,
                same_node_unit_ready=True, state="DISCOVERED", resident_deferral=None, unlock_value=0)
    base.update(kw)
    return base


class RouteAndWaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = "build/test-fleet-" + uuid.uuid4().hex + ".jsonl"
        self.fleet = fleet.Fleet(Path(self.temp.name) / "fleet", self.ledger,
                                 ROOT / "build" / ("test-packets-" + uuid.uuid4().hex))

    def tearDown(self):
        import shutil
        for suffix in ("", ".lock"):
            path = ROOT / (self.ledger + suffix)
            if path.exists():
                path.unlink()
        shutil.rmtree(self.fleet.packets, ignore_errors=True)
        self.temp.cleanup()

    def build(self, intakes=()):
        functions = [dict(id=x, hunk=0, start=s, end=s + 56) for x, s in
                     (("resident_F_463E", 0x463E), ("resident_F_4F62", 0x4F62), ("resident_F_435E", 0x435E),
                      ("resident_F_88A6", 0x88A6), ("resident_F_2EAC", 0x2EAC))]
        items = [rank_item("resident_F_463E", unlock_value=1800),
                 rank_item("resident_F_2EAC", unlock_value=400),
                 rank_item("resident_F_4F62", unlock_value=800),
                 rank_item("resident_F_435E", pending_local_dependencies=["resident_F_4F62"], unlock_value=2000),
                 rank_item("resident_F_88A6", resident_deferral="RESIDENT_RUNTIME_TAIL")]
        ledger = dict(functions={}, attempts={}, blockers={}, mixed_source_objects={"resident_F_766C": {}})
        tasks, _ = fleet.build_tasks(functions, items, ledger, [], regions=[], intakes=intakes)
        return {t["targets"][0]: t for t in tasks}, tasks

    def test_routes_and_leverage_order(self):
        by_target, tasks = self.build()
        self.assertEqual(by_target["resident_F_463E"]["route"], "READY_FOR_HAIKU")
        self.assertEqual(by_target["resident_F_88A6"]["route"], "NEEDS_STRUCTURAL_EVIDENCE")
        self.assertEqual(by_target["resident_F_435E"]["dependencies"], ["fn-resident_F_4F62"])
        # The dependency unlock outranks; equal priorities fall back to leverage.
        order = [t["targets"][0] for t in tasks if t["route"] == "READY_FOR_HAIKU"]
        self.assertEqual(order[:3], ["resident_F_4F62", "resident_F_463E", "resident_F_2EAC"])
        exhausted = [dict(intake_status="BLOCKED_FOR_CURATION", kind="function", targets=["resident_F_2EAC"])]
        by_target, _ = self.build(exhausted)
        self.assertEqual(by_target["resident_F_2EAC"]["route"], "ALREADY_EXHAUSTED")
        self.assertEqual(fleet.classify_route(dict(kind="blocker-probe", targets=["x"],
                                                   origin=dict(mechanism="ABI_OR_CODEGEN_PROFILE"))),
                         "BLOCKED_BY_SHARED_MECHANISM")

    def write_plan(self, tasks, ledger_hash):
        self.fleet.dir.mkdir(parents=True, exist_ok=True)
        self.fleet.tasks.write_text(json.dumps(dict(schema_version=1, tasks=tasks,
                                                    frontier=dict(recovery_ledger_sha256=ledger_hash))))

    def test_wave_leases_independent_tasks_and_writes_agent_specs(self):
        _, tasks = self.build()
        from common import sha256
        self.write_plan(tasks, sha256((ROOT / "recovery/ledger.json").read_bytes()))
        with patch.object(fleet, "canonical_ids", return_value=set()), \
             patch.object(fleet, "write_packet", side_effect=lambda f, tid: (f.task_dir(tid) / "PROMPT.md", 100)):
            preview = fleet.wave(self.fleet, 5, dry_run=True)
            doc = fleet.wave(self.fleet, 5)
        ids = [e["task_id"] for e in doc["entries"]]
        self.assertEqual([e["task_id"] for e in preview["entries"]], ids)
        # The dependent caller waits and the runtime-tail review is not a Haiku route.
        self.assertEqual(ids, ["fn-resident_F_4F62", "fn-resident_F_463E", "fn-resident_F_2EAC"])
        targets = [t for e in doc["entries"] for t in e["targets"]]
        self.assertEqual(len(targets), len(set(targets)))
        spec = doc["entries"][0]["agent"]
        self.assertEqual((spec["model"], spec["subagent_type"], spec["run_in_background"]),
                         ("haiku", "general-purpose", True))
        self.assertIn("PROMPT.md", spec["prompt"])
        self.assertIn("Never promote", spec["prompt"])
        self.assertTrue(doc["entries"][0]["worker"].startswith(fleet.WORKER_PREFIX))
        self.assertTrue((self.fleet.dir / "waves" / (doc["wave_id"] + ".json")).is_file())
        with patch.object(fleet, "canonical_ids", return_value=set()):
            self.assertEqual(fleet.wave(self.fleet, 5)["entries"], [])  # everything open is now leased

    def test_wave_refuses_a_stale_plan(self):
        _, tasks = self.build()
        self.write_plan(tasks, "0" * 64)
        with self.assertRaisesRegex(FormatError, "predates"):
            fleet.wave(self.fleet, 2)


if __name__ == "__main__":
    unittest.main()


class ProvenObjectClosureTests(unittest.TestCase):
    """Canonical members proved inside one natural object stay in that object."""

    def test_member_pulls_in_its_whole_proven_object(self):
        from check_unit import proven_object_members
        from recovery_state import recovery
        ledger = recovery()
        if "ov10_F_22E6" not in ledger["functions"]:
            self.skipTest("canonical ov10 object not present")
        self.assertEqual(proven_object_members("ov10_F_22E6", ledger), ["ov10_F_1FDE", "ov10_F_2160"])
        # A separately proved function has no co-members.
        self.assertEqual(proven_object_members("ov10_F_1FDE", ledger), [])
        # A changed co-member source invalidates the evidence instead of guessing.
        import copy
        changed = copy.deepcopy(ledger)
        changed["functions"]["ov10_F_1FDE"]["source_sha256"] = "0" * 64
        self.assertEqual(proven_object_members("ov10_F_22E6", changed), [])
