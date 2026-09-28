import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import shape_search
from common import FormatError


class ShapeSearchManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "experiments").mkdir()
        (self.root / "experiments" / "a.c").write_text("recovered() { return 1; }\n", encoding="ascii")
        (self.root / "experiments" / "b.c").write_text("recovered() { return 2; }\n", encoding="ascii")
        self.manifest_path = self.root / "manifest.json"
        self.base = {
            "schema_version": 1,
            "function_id": "ov03_F_0000",
            "budget": {"max_variants": 2, "max_unique_compiles": 2},
            "variants": [
                {"id": "a", "causal_family": "value-form", "diagnostic_scope": "register_assignment",
                 "source": "experiments/a.c", "profile": "aztec36"},
                {"id": "b", "causal_family": "value-form", "diagnostic_scope": "register_assignment",
                 "source": "experiments/b.c", "profile": "aztec36"},
            ],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_manifest_parses_explicit_independent_variants(self):
        self.manifest_path.write_text(json.dumps(self.base), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            function_id, budget, variants = shape_search.load_manifest(self.manifest_path)
        self.assertEqual(function_id, "ov03_F_0000")
        self.assertEqual(budget["max_unique_compiles"], 2)
        self.assertEqual([v["id"] for v in variants], ["a", "b"])

    def test_rejects_unknown_schema_fields_and_escaping_source_paths(self):
        extra = dict(self.base, surprise=True)
        self.manifest_path.write_text(json.dumps(extra), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            with self.assertRaises(FormatError):
                shape_search.load_manifest(self.manifest_path)
        invalid = json.loads(json.dumps(self.base))
        invalid["variants"][0]["source"] = "../assets/immutable.c"
        self.manifest_path.write_text(json.dumps(invalid), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            with self.assertRaises(FormatError):
                shape_search.load_manifest(self.manifest_path)

    def test_rejects_unique_compile_budget_overrun_and_duplicate_ids(self):
        invalid = json.loads(json.dumps(self.base))
        invalid["budget"]["max_unique_compiles"] = 1
        self.manifest_path.write_text(json.dumps(invalid), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            with self.assertRaises(FormatError):
                shape_search.load_manifest(self.manifest_path)

    def test_rejects_unsupported_diagnostic_scope(self):
        invalid = json.loads(json.dumps(self.base))
        invalid["variants"][0]["diagnostic_scope"] = "handwavy"
        self.manifest_path.write_text(json.dumps(invalid), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            with self.assertRaises(FormatError):
                shape_search.load_manifest(self.manifest_path)
        invalid = json.loads(json.dumps(self.base))
        invalid["variants"][1]["id"] = "a"
        self.manifest_path.write_text(json.dumps(invalid), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            with self.assertRaises(FormatError):
                shape_search.load_manifest(self.manifest_path)


class ShapeSearchEvaluationTests(unittest.TestCase):
    def test_runs_isolated_verifier_and_keeps_exact_verdicts_ahead_of_diagnostic_rank(self):
        variants = [
            dict(id="different", causal_family="shape", diagnostic_scope="register_assignment",
                 manifest_source="experiments/a.c", source_path=Path("experiments/a.c"), source="int x;", profile="aztec36"),
            dict(id="equal", causal_family="shape", diagnostic_scope="register_assignment",
                 manifest_source="experiments/b.c", source_path=Path("experiments/b.c"), source="int y;", profile="aztec36"),
        ]
        def report(verdict, cache_key, similarity):
            return dict(verdict=verdict, source_sha256=cache_key, cache_key=cache_key,
                        expected_length=20, actual_length=20, mnemonic_similarity=similarity,
                        first_structural_instruction_difference=None, normalized_first_difference=None)
        reports = [report("DIFFER", "a" * 64, 0.99), report("EQUAL", "b" * 64, 0.5)]
        with patch.object(shape_search, "evidence", return_value={"functions": [dict(id="f", hunk=3, node="ov03")]}), \
             patch.object(shape_search, "identity", side_effect=lambda source, profile, node: (source, {}, "")), \
             patch.object(shape_search, "check_many", return_value=reports) as verifier, \
             patch.object(shape_search, "_diagnostic", side_effect=lambda fid, report, scope: {"status": "DIAGNOSTIC_ONLY", "structural_rank": 1}):
            result = shape_search.evaluate("f", variants)
        self.assertEqual(result["promotion"], "NONE")
        self.assertEqual(result["ranking"], ["equal", "different"])
        self.assertEqual([x["exact_verdict"] for x in result["evaluated"]], ["EQUAL", "DIFFER"])
        self.assertTrue(verifier.call_args.kwargs["isolated"])
        self.assertFalse(verifier.call_args.kwargs["promote_equal"])

    def test_unsupported_diagnosis_remains_visible_without_changing_verdict(self):
        report = dict(verdict="DIFFER", source_sha256="a" * 64, cache_key="b" * 64,
                      expected_length=10, actual_length=11)
        variants = [dict(id="v", causal_family="x", diagnostic_scope="control_flow_unresolved",
                         manifest_source="x.c", source="int x;", source_path=Path("x.c"), profile="aztec36")]
        with patch.object(shape_search, "evidence", return_value={"functions": [dict(id="f", hunk=1, node="resident")]}), \
             patch.object(shape_search, "identity", return_value=("key", {}, "")), \
             patch.object(shape_search, "check_many", return_value=[report]), \
             patch.object(shape_search, "_diagnostic", return_value={"status": "UNSUPPORTED", "reason": "outside scope"}):
            result = shape_search.evaluate("f", variants)
        self.assertEqual(result["evaluated"][0]["exact_verdict"], "DIFFER")
        self.assertEqual(result["evaluated"][0]["diagnostic"]["status"], "UNSUPPORTED")

    def test_cached_only_refuses_prepared_same_overlay_unit_before_verifier(self):
        variants = [dict(id="v", causal_family="x", diagnostic_scope="control_flow_shape",
                         manifest_source="x.c", source="recovered() { return 0; }\n",
                         source_path=Path("x.c"), profile="aztec36")]
        target = dict(id="f", hunk=3, node="ov03", direct_callees=[
            dict(basis="PC_RELATIVE", hunk=3, id="other")])
        with patch.object(shape_search, "evidence", return_value={"functions": [target]}), \
             patch.object(shape_search, "check_many") as verifier:
            with self.assertRaises(FormatError):
                shape_search.evaluate("f", variants, cached_only=True)
        verifier.assert_not_called()


def _prediction(**overrides):
    value = {"length_delta": None, "removed_candidate_only": None, "register_role_diffs": "fewer", "note": "n"}
    value.update(overrides)
    return value


class ShapeSearchSchemaV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "experiments").mkdir()
        (self.root / "experiments" / "base.c").write_text("recovered() { return 1; }\n", encoding="ascii")
        (self.root / "experiments" / "a.c").write_text("recovered() { return 2; }\n", encoding="ascii")
        (self.root / "experiments" / "b.c").write_text("recovered() { return 3; }\n", encoding="ascii")
        (self.root / "experiments" / "a_comment.c").write_text(
            "/* same */ recovered()  {\n\n  return 2; // trailing\n}\n", encoding="ascii")
        self.manifest_path = self.root / "manifest.json"
        self.base = {
            "schema_version": 2,
            "function_id": "f",
            "budget": {"max_variants": 3, "max_unique_compiles": 3},
            "variants": [
                {"id": "a", "causal_family": "value-form", "diagnostic_scope": "register_assignment",
                 "source": "experiments/a.c", "profile": "aztec36", "parent": "experiments/base.c",
                 "suspected_cause": "temporary lifetime", "controlled_change": "return constant changed",
                 "predicted_effect": _prediction(length_delta=0)},
                {"id": "b", "causal_family": "value-form", "diagnostic_scope": "register_assignment",
                 "source": "experiments/b.c", "profile": "aztec36", "parent": "a",
                 "suspected_cause": "temporary lifetime", "controlled_change": "second change",
                 "predicted_effect": _prediction()},
            ],
        }

    def tearDown(self):
        self.temp.cleanup()

    def load(self, manifest):
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with patch.object(shape_search, "ROOT", self.root):
            return shape_search.load_manifest(self.manifest_path)

    def test_v2_manifest_parses_hypothesis_fields(self):
        _, _, variants = self.load(self.base)
        self.assertEqual(variants[0]["parent"]["kind"], "source")
        self.assertEqual(variants[1]["parent"], dict(kind="variant", value="a"))
        self.assertEqual(variants[0]["predicted_effect"]["length_delta"], 0)
        self.assertEqual(len(variants[0]["normalized_sha256"]), 64)

    def test_v1_manifest_still_rejects_v2_fields_and_v2_requires_them(self):
        v1 = json.loads(json.dumps(self.base))
        v1["schema_version"] = 1
        with self.assertRaises(FormatError):
            self.load(v1)
        for key in ("parent", "suspected_cause", "controlled_change", "predicted_effect"):
            missing = json.loads(json.dumps(self.base))
            del missing["variants"][0][key]
            with self.assertRaises(FormatError):
                self.load(missing)

    def test_v2_rejects_malformed_predictions_and_parents(self):
        cases = [
            ("predicted_effect", _prediction(register_role_diffs="better")),
            ("predicted_effect", _prediction(register_role_diffs=None)),  # nothing machine-checkable
            ("predicted_effect", _prediction(length_delta=1.5)),
            ("predicted_effect", dict(_prediction(), extra=1)),
            ("parent", "b"),  # forward reference: parents must be earlier variants
            ("parent", "experiments/missing.c"),
            ("parent", "experiments/a.c"),  # identical to itself: no controlled change
        ]
        for key, value in cases:
            invalid = json.loads(json.dumps(self.base))
            invalid["variants"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(FormatError):
                self.load(invalid)

    def test_duplicate_after_normalization_is_rejected_within_manifest(self):
        invalid = json.loads(json.dumps(self.base))
        invalid["variants"][1]["source"] = "experiments/a_comment.c"
        with self.assertRaises(FormatError):
            self.load(invalid)
        other_profile = json.loads(json.dumps(invalid))
        other_profile["variants"][1]["profile"] = "aztec50"
        _, _, variants = self.load(other_profile)
        self.assertEqual(len(variants), 2)

    def test_normalization_is_comments_and_whitespace_only(self):
        norm = shape_search.normalize_source
        self.assertEqual(norm("/* c */ int  x;\n\n\t// d\nint y; \n"), "int x; int y;")
        self.assertEqual(norm("#define A \\\n  1\nint\n x;\n"), "#define A \\\n1\nint x;")
        self.assertEqual(norm('char *s = "/* kept */  x";'), 'char *s = "/* kept */  x";')
        self.assertEqual(norm("#define A /*\n*/ 1\n"), "#define A 1")
        self.assertNotEqual(norm("a+b;"), norm("a + b;"))
        self.assertEqual(shape_search.normalized_sha256("recovered() { return 2; }\n"),
                         shape_search.normalized_sha256(
                             (self.root / "experiments" / "a_comment.c").read_text(encoding="ascii")))


class PredictionScoringTests(unittest.TestCase):
    parent = dict(status="DIAGNOSTIC_ONLY", candidate_bytes=672, candidate_only=6, expected_only=0,
                  register_role_diffs=10)

    def test_confirmed_refuted_and_partial(self):
        child = dict(self.parent, candidate_bytes=668, candidate_only=4, register_role_diffs=7)
        score = shape_search.score_prediction(
            _prediction(length_delta=-4, removed_candidate_only=2), child, self.parent)
        self.assertEqual(score["outcome"], "confirmed")
        self.assertEqual(score["observed_delta"],
                         dict(length_delta=-4, removed_candidate_only=2, register_role_diffs="fewer"))
        score = shape_search.score_prediction(
            _prediction(length_delta=-2, register_role_diffs="more"), child, self.parent)
        self.assertEqual(score["outcome"], "refuted")
        score = shape_search.score_prediction(_prediction(length_delta=-2), child, self.parent)
        self.assertEqual(score["outcome"], "partial")
        self.assertEqual(score["fields"]["removed_candidate_only"], "not_predicted")

    def test_unsupported_or_missing_parent_is_unmeasurable(self):
        unsupported = dict(status="UNSUPPORTED", reason="x")
        for child, parent in ((unsupported, self.parent), (self.parent, unsupported), (self.parent, None)):
            score = shape_search.score_prediction(_prediction(length_delta=0), child, parent)
            self.assertEqual(score["outcome"], "unmeasurable")
            self.assertIsNone(score["observed_delta"])

    def test_metrics_come_only_from_supported_diagnostics(self):
        self.assertEqual(shape_search.diagnostic_metrics(dict(status="UNSUPPORTED", reason="r"))["status"],
                         "UNSUPPORTED")
        metrics = shape_search.diagnostic_metrics(dict(
            status="DIAGNOSTIC_ONLY", candidate_extent=dict(bytes=10),
            alignment=dict(actual_only=[{}, {}], expected_only=[]),
            hypotheses=[dict(category="register_assignment", count=3), dict(category="operand_width", count=1)]))
        self.assertEqual(metrics, dict(status="DIAGNOSTIC_ONLY", candidate_bytes=10, candidate_only=2,
                                       expected_only=0, register_role_diffs=3))


class HypothesisLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "build").mkdir()
        self.ledger = "build/hyp.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def variant(vid, text, parent):
        return dict(id=vid, causal_family="shape", diagnostic_scope="register_assignment",
                    manifest_source="experiments/" + vid + ".c", source_path=Path(vid + ".c"), source=text,
                    profile="aztec36", parent=parent, suspected_cause="cause", controlled_change="change",
                    predicted_effect=_prediction(removed_candidate_only=1),
                    normalized_sha256=shape_search.normalized_sha256(text))

    @staticmethod
    def diagnostic(size, only, roles):
        return dict(status="DIAGNOSTIC_ONLY", candidate_extent=dict(bytes=size),
                    alignment=dict(actual_only=[{}] * only, expected_only=[]),
                    hypotheses=[dict(category="register_assignment", count=roles)])

    def run_eval(self, variants, diagnostics, cache_hits):
        def fake_evaluate(function_id, run, cached_only=False, output_dir=None):
            evaluated = [dict(id=v["id"], diagnostic=diagnostics[v["id"]],
                              report=dict(cache_key=v["id"] * 8, cache_hit=cache_hits[v["id"]],
                                          verdict="EQUAL" if v["id"] == "win" else "DIFFER"))
                         for v in run]
            return dict(evaluated=evaluated, ranking=[v["id"] for v in run])
        with patch.object(shape_search, "ROOT", self.root), \
             patch.object(shape_search, "evidence", return_value={"functions": [dict(id="f", hunk=3, node="ov01")]}), \
             patch.object(shape_search, "evaluate", side_effect=fake_evaluate) as evaluator:
            result = shape_search.evaluate_hypotheses("f", variants, cached_only=True, ledger=self.ledger,
                                                      now="2026-01-01T00:00:00+00:00")
        return result, evaluator

    def test_ledger_appends_scores_and_rejects_prior_duplicates(self):
        none = dict(kind="none", value="none")
        base = self.variant("base", "recovered() { return 1; }", none)
        child = self.variant("win", "recovered() { return 2; }", dict(kind="variant", value="base"))
        result, _ = self.run_eval([base, child],
                                  dict(base=self.diagnostic(20, 3, 2), win=self.diagnostic(18, 2, 1)),
                                  dict(base=False, win=False))
        self.assertEqual(result["ledger"]["lines"], [1, 2])
        win = next(e for e in result["evaluated"] if e["id"] == "win")
        self.assertEqual(win["hypothesis"]["prediction"]["outcome"], "confirmed")
        self.assertEqual(win["hypothesis"]["prediction"]["observed_delta"]["length_delta"], -2)
        path = self.root / self.ledger
        first = path.read_bytes()

        # Same normalized source/profile again: not re-run; pointer to prior record.
        again = self.variant("win", "/* c */ recovered()  { return 2; }", dict(kind="variant", value="base"))
        third = self.variant("third", "recovered() { return 3; }", dict(kind="variant", value="win"))
        result, evaluator = self.run_eval([again, third], dict(third=self.diagnostic(18, 2, 1)),
                                          dict(third=True))
        self.assertEqual([v["id"] for v in evaluator.call_args.args[1]], ["third"])
        self.assertEqual(result["duplicates_rejected"][0]["prior_record"]["ledger_line"], 2)
        self.assertEqual(result["duplicates_rejected"][0]["prior_record"]["exact_verdict"], "EQUAL")
        third_eval = result["evaluated"][0]
        # Parent is the skipped duplicate: its prior observation is the baseline.
        self.assertEqual(third_eval["hypothesis"]["prediction"]["fields"]["removed_candidate_only"], "refuted")
        self.assertTrue(path.read_bytes().startswith(first))  # append-only
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r["record_type"] for r in records], ["trial", "trial", "duplicate_rejected", "trial"])
        for key in ("timestamp", "function_id", "variant", "normalized_sha256", "source_sha256", "profile",
                    "cache_key", "parent", "suspected_cause", "controlled_change", "predicted_effect",
                    "exact_verdict", "observed_delta", "prediction"):
            self.assertIn(key, records[1])

        with patch.object(shape_search, "ROOT", self.root):
            summary = shape_search.ledger_summary(shape_search.ledger_path(self.ledger), "f")
        self.assertEqual(summary["compiler_trials"], 2)
        self.assertEqual(summary["cache_hits"], 1)
        self.assertEqual(summary["exact_matches"], 1)
        self.assertEqual(summary["exact_matches_per_compiler_trial"], 0.5)
        self.assertEqual(summary["duplicates_rejected"], 1)
        self.assertEqual(summary["predictions"], dict(confirmed=1, partial=0, refuted=1, unmeasurable=1))

    def test_malformed_ledger_and_outside_path_are_refused(self):
        with patch.object(shape_search, "ROOT", self.root):
            with self.assertRaises(FormatError):
                shape_search.ledger_path("assets/ledger.jsonl")
            path = shape_search.ledger_path(self.ledger)
            path.write_text('{"ledger_schema": 1, "record_type": "trial"}\n{broken\n', encoding="utf-8")
            with self.assertRaises(FormatError):
                shape_search.read_ledger(path)
            path.write_text('{"ledger_schema": 1, "record_type": "trial"}', encoding="utf-8")
            with self.assertRaises(FormatError):
                shape_search.append_ledger(path, [dict(ledger_schema=1, record_type="trial")])

    def test_ledger_lock_is_respected(self):
        with patch.object(shape_search, "ROOT", self.root):
            path = shape_search.ledger_path(self.ledger)
            path.with_name(path.name + ".lock").write_text("", encoding="ascii")
            with self.assertRaises(FormatError):
                shape_search.append_ledger(path, [dict(ledger_schema=1, record_type="trial")], timeout=0)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
