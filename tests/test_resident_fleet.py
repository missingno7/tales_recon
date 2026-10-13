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
        # A4 helper routes are supplied by the helper export control, not deferred.
        self.assertIsNone(resident_deferral(caller, self.floor, {(0, 0x7F9C)}))

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


class CanonicalReplacementTests(unittest.TestCase):
    """Replacing a canonical source re-proves every receipt that pinned it, or changes nothing."""

    def setUp(self):
        import canonical_replacement
        self.cr = canonical_replacement
        self.tmp = Path(tempfile.mkdtemp())
        for rel, text in (("src/a.c", "old a"), ("src/b.c", "b"), ("proofs/a.json", "{\"comparison\": {}}")):
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / rel).write_text(text)
        unit = dict(id="B", dependency_sources={"A": "hA"}, verdict="EQUAL")
        (self.tmp / "units").mkdir()
        (self.tmp / "units/b.json").write_text(json.dumps(unit))
        (self.tmp / "proofs/b.json").write_text(json.dumps(dict(
            compiler=dict(profile="aztec36"), comparison=dict(complete_unit_receipt="units/b.json"))))
        self.ledger = dict(functions=dict(
            A=dict(source="src/a.c", source_sha256="hA", proof="proofs/a.json", state="FUNCTION_CODE_MATCH"),
            B=dict(source="src/b.c", source_sha256="hB", proof="proofs/b.json", state="FUNCTION_WITH_DATA_MATCH")))
        (self.tmp / "ledger.json").write_text(json.dumps(self.ledger))

    def patched(self, check_many):
        import check_function
        return (patch.object(self.cr, "ROOT", self.tmp), patch.object(check_function, "LEDGER", self.tmp / "ledger.json"),
                patch.object(check_function, "recovery", side_effect=lambda: json.loads(json.dumps(self.ledger))),
                patch.object(check_function, "regression_receipt", return_value=dict(passed=True)),
                patch.object(check_function, "check_many", side_effect=check_many),
                patch("canonical_replacement.canonical_path", side_effect=lambda root, rel: self.tmp / rel))

    def run_replace(self, check_many):
        patches = self.patched(check_many)
        for item in patches:
            item.start()
        self.addCleanup(lambda: [item.stop() for item in patches])

        def write(gate):
            self.assertEqual(gate, dict(passed=True))
            (self.tmp / "src/a.c").write_text("new a")
            (self.tmp / "ledger.json").write_text("replaced")
        return self.cr.replace("A", write)

    def test_dependent_is_reproved_from_its_own_canonical_source(self):
        seen = []
        reports = self.run_replace(lambda requests, regression: seen.extend(requests) or
                                   [dict(id="B", verdict="EQUAL", promotion=dict(state="FUNCTION_WITH_DATA_MATCH"))])
        self.assertEqual(seen, [dict(id="B", source="src/b.c", profiles=["aztec36"], owned_code_data=True)])
        self.assertEqual([r["id"] for r in reports], ["B"])
        self.assertEqual((self.tmp / "src/a.c").read_text(), "new a")
        # B is withdrawn while it is re-proved against the replacement.
        self.assertNotIn("B", json.loads((self.tmp / "ledger.json").read_text())["functions"])

    def test_failed_dependent_restores_prior_canonical_state(self):
        with self.assertRaisesRegex(FormatError, "dependent re-proof failed"):
            self.run_replace(lambda requests, regression: [dict(id="B", verdict="DIFFER")])
        self.assertEqual((self.tmp / "src/a.c").read_text(), "old a")
        self.assertEqual(json.loads((self.tmp / "ledger.json").read_text()), self.ledger)

    def test_grouped_dependent_refuses_replacement(self):
        unit = dict(id="B", dependency_sources={"A": "hA"}, object_partition=[["A", "B"]])
        (self.tmp / "units/b.json").write_text(json.dumps(unit))
        with self.assertRaisesRegex(FormatError, "grouped or multi-member"):
            self.run_replace(lambda requests, regression: [])
        self.assertEqual((self.tmp / "src/a.c").read_text(), "old a")


class HelperExportControlTests(unittest.TestCase):
    """Resident A4 helper routes come from evidence; unregistered harnesses are unchanged."""

    ENTRIES = {0x7F9C: ".divs", 0x7FC4: ".mods", 0x7B00: ".mulu"}

    def test_original_helpers_come_from_a4_stub_calls_into_pinned_entries(self):
        import helper_exports
        f = dict(node="resident", direct_callees=[
            dict(basis="A4_RELOCATED_JMP_STUB", hunk=0, offset=0x7FC4, id="resident_F_7FC4"),
            dict(basis="PC_RELATIVE", hunk=0, offset=0x7F9C, id="resident_F_7F9C"),
            dict(basis="A4_RELOCATED_JMP_STUB", hunk=0, offset=0x35DC, id="resident_F_35DC")])
        overlay = dict(f, node="ov03")
        self.assertEqual(helper_exports.original_helpers([f], self.ENTRIES), (".mods",))
        self.assertEqual(helper_exports.original_helpers([overlay], self.ENTRIES), ())

    def test_pinned_runtime_evidence_names_the_divide_family(self):
        import helper_exports
        entries = helper_exports.helper_entries()
        self.assertEqual(entries[0x7FC4], ".mods")
        self.assertEqual(entries[0x7F9C], ".divs")
        self.assertEqual(entries[0x7B00], ".mulu")

    def test_control_source_uses_only_the_requested_helpers(self):
        import helper_exports
        text = helper_exports.control_source((".mods", ".divs"))
        self.assertIn("a = a % b;", text)
        self.assertIn("a = a / b;", text)
        self.assertNotIn("c = c", text)
        with self.assertRaises(FormatError):
            helper_exports.control_source((".bogus",))

    def test_only_registered_resident_sources_get_the_control(self):
        import compiler_oracle
        import helper_exports
        routed = "/* routed probe */\nrecovered(a,b) long a,b; { return a % b; }\n"
        plain = "/* plain probe */\nrecovered(a,b) long a,b; { return a % b; }\n"
        helper_exports.register(routed, (".mods",))
        self.assertIn(helper_exports.CONTROL, compiler_oracle.harness(routed, 0))
        self.assertEqual([p["name"] for p in compiler_oracle.overlay_proxies(routed, 0)], [helper_exports.CONTROL])
        self.assertNotIn(helper_exports.CONTROL, compiler_oracle.harness(plain, 0))
        self.assertNotIn(helper_exports.CONTROL, compiler_oracle.harness(routed, 1))
        self.assertEqual(compiler_oracle.overlay_proxies(plain, 0), [])
        with self.assertRaisesRegex(FormatError, "different helper routes"):
            helper_exports.register(routed, (".divs",))


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


class RuntimeTailCallTests(unittest.TestCase):
    def test_only_resident_game_calls_into_the_tail_qualify(self):
        from recovery_state import runtime_tail_call
        caller = dict(hunk=0, start=0x2D66)
        stub = dict(hunk=0, offset=0x86F6, basis="PC_RELATIVE", id="resident_F_86F6")
        self.assertTrue(runtime_tail_call(caller, stub, 0x75D8))
        self.assertFalse(runtime_tail_call(caller, dict(stub, offset=0x30F0), 0x75D8))   # game callee
        self.assertFalse(runtime_tail_call(caller, dict(stub, basis="A4_RELOCATED_JMP_STUB"), 0x75D8))
        self.assertFalse(runtime_tail_call(dict(hunk=0, start=0x8000), stub, 0x75D8))    # tail caller
        self.assertFalse(runtime_tail_call(dict(hunk=11, start=0x100), dict(stub, hunk=11), 0x75D8))
        self.assertFalse(runtime_tail_call(caller, stub, None))


class BlockerCategoryTests(unittest.TestCase):
    def test_named_mechanism_wins_over_incidental_words(self):
        from recovery_state import blocker_category
        self.assertEqual(blocker_category("CHAR_RETURN_EXTENSION: under aztec36-large-data ..."), "TOOLCHAIN")
        self.assertEqual(blocker_category("XOR_RESULT_REGISTER_ORIENTATION: large-data profile"), "SOURCE_SHAPE")
        # Without a recognised mechanism token the full text still decides.
        self.assertEqual(blocker_category("NON_CONVERGENCE: data table differs"), "DATA_OWNERSHIP")
        self.assertEqual(blocker_category("plain text about a CFG boundary"), "CFG/BOUNDARY")


class TailProofJumpTableTests(unittest.TestCase):
    """The owned-literal proof decodes around census-proven switch tables."""

    def test_table_span_between_code_and_tail(self):
        from owned_code_data import pc_relative_tail_proof
        # lea tail(pc),a0; nop; <undecodable 4-byte table>; nop | tail at +12
        raw = "41fa000a" + "4e71" + "ffffffff" + "4e71"
        f = dict(start=0, end=12, size=12, hunk=5, raw_bytes=raw,
                 referenced_data=[dict(kind="PC_RELATIVE_DATA", hunk=5, offset=12, instruction_offset=0)],
                 jump_tables=[dict(table_start=6, table_end=10)])
        proof = pc_relative_tail_proof(f, bytes.fromhex(raw), 12)
        self.assertEqual([(p["original_offset"], p["candidate_offset"]) for p in proof], [(12, 12)])
        with self.assertRaisesRegex(FormatError, "cannot decode"):
            pc_relative_tail_proof(dict(f, jump_tables=[]), bytes.fromhex(raw), 12)
        # A candidate addressing anything but the owned tail is still refused.
        with self.assertRaisesRegex(FormatError, "does not address owned tail"):
            pc_relative_tail_proof(f, bytes.fromhex("41fa000c" + raw[8:]), 12)


class EvidencedObjectGroupTests(unittest.TestCase):
    """A standalone-proved canonical member joins a group only on BSR evidence."""

    @staticmethod
    def member(fid, start, end, calls=(), bsr_sites=()):
        instructions = [dict(offset=s, mnemonic="bsr.b") for s in bsr_sites]
        return dict(id=fid, start=start, end=end, instructions=instructions,
                    direct_callees=[dict(id=c, site=s, basis="PC_RELATIVE") for c, s in calls])

    def test_bsr_evidence_admits_standalone_canonical(self):
        import check_unit
        caller = self.member("ov07_F_1F6E", 0x1F6E, 0x2026, calls=[("ov07_F_2050", 0x1FE4)], bsr_sites=[0x1FE4])
        callee = self.member("ov07_F_2050", 0x2050, 0x20A0)
        ledger = dict(functions={"ov07_F_2050": dict(state="FUNCTION_CODE_MATCH")})
        groups = check_unit.validate_object_groups([caller, callee], [["ov07_F_1F6E", "ov07_F_2050"]],
                                                   {"ov07_F_1F6E"}, (), {"ov07_F_1F6E": 0x2A}, ledger)
        self.assertEqual(groups, [["ov07_F_1F6E", "ov07_F_2050"]])
        # Without an original BSR between them the grouping stays refused.
        jsr_caller = self.member("ov07_F_1F6E", 0x1F6E, 0x2026, calls=[("ov07_F_2050", 0x1FE4)])
        with self.assertRaisesRegex(FormatError, "without agreeing proven grouping"):
            check_unit.validate_object_groups([jsr_caller, callee], [["ov07_F_1F6E", "ov07_F_2050"]],
                                              {"ov07_F_1F6E"}, (), {"ov07_F_1F6E": 0x2A}, ledger)
        # A member of a recorded multi-member object never joins a new group.
        with patch.object(check_unit, "proven_object_members", return_value=["ov07_F_20A0"]):
            with self.assertRaisesRegex(FormatError, "without agreeing proven grouping"):
                check_unit.validate_object_groups([caller, callee], [["ov07_F_1F6E", "ov07_F_2050"]],
                                                  {"ov07_F_1F6E"}, (), {"ov07_F_1F6E": 0x2A}, ledger)
        # Original bytes between the members still refuse the group.
        with self.assertRaisesRegex(FormatError, "does not own"):
            check_unit.validate_object_groups([caller, callee], [["ov07_F_1F6E", "ov07_F_2050"]],
                                              {"ov07_F_1F6E"}, (), {}, ledger)


class EvidencedShortCallConsumerTests(unittest.TestCase):
    def test_consumer_rederives_bsr_from_function_evidence(self):
        import recovery_evidence
        fake = {"ov07_F_1F6E": dict(id="ov07_F_1F6E", instructions=[dict(offset=0x1FE4, mnemonic="bsr.b")],
                                    direct_callees=[dict(id="ov07_F_2050", site=0x1FE4, basis="PC_RELATIVE")]),
                "ov07_F_0E06": dict(id="ov07_F_0E06", instructions=[dict(offset=0x0E10, mnemonic="jsr")],
                                    direct_callees=[dict(id="ov07_F_2050", site=0x0E10, basis="PC_RELATIVE")]),
                "ov07_F_2050": dict(id="ov07_F_2050", hunk=7, start=0x2050, instructions=[], direct_callees=[])}
        with patch.dict(recovery_evidence._FUNCTION_EVIDENCE, fake, clear=True):
            self.assertTrue(recovery_evidence.evidenced_short_call("ov07_F_1F6E", "ov07_F_2050"))
            self.assertFalse(recovery_evidence.evidenced_short_call("ov07_F_0E06", "ov07_F_2050"))
            self.assertFalse(recovery_evidence.evidenced_short_call("ov07_F_2050", "ov07_F_1F6E"))


class SymbolMapHunkNumberTests(unittest.TestCase):
    def test_manx_hunk_numbers_are_decimal(self):
        from overlay_experiment import symbols
        text = ("Segment 00:  Hunk 009\n\t00000000 _F_h13_02BE\n"
                "Segment 12:  Hunk 010\n\t00000000 _F_h14_0000\n\t0000000a _F_h14_03AE\n"
                "Segment 13:  Hunk 011\n\t00000000 _F_h15_0000\n")
        parsed = symbols(text)
        self.assertEqual(parsed[(10, "_F_h14_0000")], 0)
        self.assertEqual(parsed[(10, "_F_h14_03AE")], 10)
        self.assertEqual(parsed[(11, "_F_h15_0000")], 0)
        self.assertNotIn((16, "_F_h14_0000"), parsed)


class ExportedCallEvidenceTests(unittest.TestCase):
    """A PC-relative JSR to an overlay export is same-object evidence; spans admit members between."""

    def test_exported_jsr_and_span(self):
        from recovery_evidence import same_object_call, evidenced_span_member
        caller = dict(id="ov03_F_001C", hunk=3, start=0x1C,
                      instructions=[dict(offset=0x136, mnemonic="jsr"), dict(offset=0x18C, mnemonic="jsr")],
                      direct_callees=[dict(id="ov03_F_154E", site=0x136, basis="PC_RELATIVE"),
                                      dict(id="ov03_F_1500", site=0x18C, basis="PC_RELATIVE")])
        middle = dict(id="ov03_F_1500", hunk=3, start=0x1500, instructions=[], direct_callees=[])
        exported = dict(id="ov03_F_154E", hunk=3, start=0x154E, instructions=[], direct_callees=[])
        exports = {(3, 0x154E)}
        self.assertTrue(same_object_call(caller, exported, exports))
        self.assertFalse(same_object_call(caller, middle, exports))      # plain JSR to a non-export
        self.assertFalse(same_object_call(caller, exported, set()))      # not exported: no evidence
        by = {x["id"]: x for x in (caller, middle, exported)}
        group = ["ov03_F_001C", "ov03_F_1500", "ov03_F_154E"]
        with patch("recovery_evidence.overlay_exports", return_value=exports):
            self.assertTrue(evidenced_span_member("ov03_F_1500", group, by))
            self.assertFalse(evidenced_span_member("ov03_F_1500", ["ov03_F_001C", "ov03_F_1500"], by))
