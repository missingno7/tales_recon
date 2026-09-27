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


if __name__ == "__main__":
    unittest.main()
