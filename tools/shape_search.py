"""Evaluate a small, explicitly authored set of independent C variants.

This utility is a bounded diagnostic front end to ``check_function``. It never
generates source text, updates recovery state, or promotes an exact comparison.
"""
import argparse
import json
from pathlib import Path
import sys

from analysis_support import ROOT
from common import FormatError, require, sha256
from check_function import check_many
from recovery_state import evidence
from compiler_oracle import identity


MAX_VARIANTS = 32
MAX_UNIQUE_COMPILES = 32
MANIFEST_KEYS = {"schema_version", "function_id", "budget", "variants"}
BUDGET_KEYS = {"max_variants", "max_unique_compiles"}
VARIANT_KEYS = {"id", "causal_family", "diagnostic_scope", "source", "profile"}
DIAGNOSTIC_SCOPES = {"operand_width", "register_assignment", "frame_or_stack_reference",
                     "a4_global_layout", "pc_relative_layout", "memory_reference_or_layout",
                     "call_target_or_encoding", "immediate_constant", "unknown_codegen",
                     "instruction_layout", "branch_condition_or_kind", "control_flow_target_or_edge",
                     "control_flow_unresolved", "control_flow_shape", "data_ownership_review"}


def _object(value, where, keys):
    require(isinstance(value, dict), where + " must be an object")
    require(set(value) == keys,
            where + " keys must be exactly " + ", ".join(sorted(keys)))


def _text(value, where, limit=120):
    require(isinstance(value, str) and value.strip(), where + " must be non-empty text")
    require(len(value) <= limit and value == value.strip(), where + " is too long or has surrounding whitespace")
    return value


def _source_path(value):
    require(isinstance(value, str) and value and "\\" not in value,
            "variant source must be a repository-relative POSIX path")
    rel = Path(value)
    require(not rel.is_absolute() and ".." not in rel.parts,
            "variant source may not escape the repository")
    path = (ROOT / rel).resolve()
    experiments = (ROOT / "experiments").resolve()
    candidates = (ROOT / "recovery" / "candidates").resolve()
    require(path.is_relative_to(experiments) or path.is_relative_to(candidates),
            "variant source must live under experiments/ or recovery/candidates/")
    require(path.is_file() and path.suffix.lower() == ".c", "variant source must be an existing .c file")
    return path


def load_manifest(path):
    """Parse and validate the deliberately narrow JSON manifest format."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FormatError("cannot read manifest: " + str(exc)) from exc
    _object(manifest, "manifest", MANIFEST_KEYS)
    require(manifest["schema_version"] == 1, "unsupported manifest schema_version")
    function_id = _text(manifest["function_id"], "function_id", 80)
    _object(manifest["budget"], "budget", BUDGET_KEYS)
    max_variants = manifest["budget"]["max_variants"]
    max_unique = manifest["budget"]["max_unique_compiles"]
    require(type(max_variants) is int and 1 <= max_variants <= MAX_VARIANTS,
            "budget.max_variants must be an integer from 1 to " + str(MAX_VARIANTS))
    require(type(max_unique) is int and 1 <= max_unique <= MAX_UNIQUE_COMPILES,
            "budget.max_unique_compiles must be an integer from 1 to " + str(MAX_UNIQUE_COMPILES))
    variants = manifest["variants"]
    require(isinstance(variants, list) and 1 <= len(variants) <= max_variants,
            "variants must contain 1..budget.max_variants entries")
    ids = set()
    normalized = []
    for index, variant in enumerate(variants):
        where = "variants[" + str(index) + "]"
        _object(variant, where, VARIANT_KEYS)
        variant_id = _text(variant["id"], where + ".id", 80)
        require(variant_id not in ids, "variant ids must be unique")
        ids.add(variant_id)
        causal_family = _text(variant["causal_family"], where + ".causal_family", 80)
        diagnostic_scope = _text(variant["diagnostic_scope"], where + ".diagnostic_scope", 80)
        require(diagnostic_scope in DIAGNOSTIC_SCOPES,
                where + ".diagnostic_scope is unsupported")
        profile = _text(variant["profile"], where + ".profile", 80)
        source = _source_path(variant["source"])
        normalized.append(dict(id=variant_id, causal_family=causal_family,
                              diagnostic_scope=diagnostic_scope, profile=profile,
                              source_path=source, source=source.read_text(encoding="ascii"),
                              manifest_source=variant["source"]))

    # Every entry is one independent hypothesis over the same target and one
    # profile. Count conservative compile attempts by distinct source/profile;
    # no hidden Cartesian profile expansion is part of this format.
    unique_sources = {(sha256(v["source"].encode("ascii")), v["profile"]) for v in normalized}
    require(len(unique_sources) <= max_unique,
            "unique source/profile compile count exceeds budget.max_unique_compiles")
    return function_id, manifest["budget"], normalized


def _diagnostic(function_id, report, scope):
    """Attach the shared structural diagnostic, preserving its uncertainty."""
    try:
        from diag import diagnose
    except ImportError:
        return dict(status="UNSUPPORTED", requested_scope=scope,
                    reason="diag module unavailable")
    try:
        result = diagnose(function_id, report["cache_key"])
    except Exception as exc:
        # Exact comparison has already completed. A diagnostic parser failure
        # must leave its verdict intact and surface as unsupported evidence.
        return dict(status="UNSUPPORTED", requested_scope=scope, reason=str(exc))
    if not isinstance(result, dict) or result.get("status") not in ("DIAGNOSTIC_ONLY", "UNSUPPORTED"):
        return dict(status="UNSUPPORTED", requested_scope=scope,
                    reason="classifier returned an unsupported result shape")
    result = dict(result)
    result["requested_scope"] = scope
    if result["status"] == "DIAGNOSTIC_ONLY":
        hypotheses = result.get("hypotheses")
        alignment = result.get("alignment")
        if not isinstance(hypotheses, list) or not isinstance(alignment, dict) or not isinstance(alignment.get("pairs"), list):
            return dict(status="UNSUPPORTED", requested_scope=scope,
                        reason="diagnostic result lacks supported hypotheses or alignment")
        scoped = [h for h in hypotheses if isinstance(h, dict) and h.get("category") == scope]
        # Keep raw evidence and expose a scope-specific ranking signal. This
        # is only a sorting aid; no source-level conclusion is inferred.
        pairs = alignment["pairs"]
        result["scope_hypotheses"] = scoped
        expected_only = alignment.get("expected_only")
        actual_only = alignment.get("actual_only")
        blocks = result.get("blocks")
        if not isinstance(expected_only, list) or not isinstance(actual_only, list) or not isinstance(blocks, dict):
            return dict(status="UNSUPPORTED", requested_scope=scope,
                        reason="diagnostic result lacks bounded alignment counts")
        similarity = alignment.get("instruction_similarity")
        if type(similarity) not in (int, float) or not 0 <= similarity <= 1:
            return dict(status="UNSUPPORTED", requested_scope=scope,
                        reason="diagnostic instruction similarity is malformed")
        paired = len(pairs)
        aligned_total = paired + len(expected_only) + len(actual_only)
        coverage = paired / aligned_total if aligned_total else 0
        paired_blocks = blocks.get("paired")
        unpaired_blocks = blocks.get("unpaired")
        if not isinstance(paired_blocks, list) or not isinstance(unpaired_blocks, dict):
            return dict(status="UNSUPPORTED", requested_scope=scope,
                        reason="diagnostic CFG summary is malformed")
        target_checks = [b.get("target_check") for b in paired_blocks if isinstance(b, dict)
                         and b.get("target_check") in ("consistent", "different_or_unresolved")]
        cfg_coverage = (sum(x == "consistent" for x in target_checks) / len(target_checks)
                        if target_checks else 1)
        if any((blocks.get("unresolved_edges") or {}).values()):
            cfg_coverage = 0
        cfg_penalty = min(1, (len(unpaired_blocks.get("expected", [])) +
                              len(unpaired_blocks.get("actual", [])) +
                              sum(x == "different_or_unresolved" for x in target_checks)) / 8)
        # Deterministic ordering aid only: code-shape similarity, matched
        # instruction coverage, then conservative CFG consistency. Confidence
        # labels from hypotheses are deliberately excluded; they are not a
        # measure of how close a candidate is.
        result["structural_rank"] = int(round(60 * similarity + 25 * coverage +
                                               15 * cfg_coverage - 10 * cfg_penalty))
        result["alignment_pair_count"] = paired
    else:
        result["structural_rank"] = 0
    return result


def _rank_key(item):
    """Order by proven exact verdict first, then diagnostic structural rank."""
    report = item["report"]
    diag = item["diagnostic"]
    rank = diag.get("structural_rank") if diag.get("status") == "DIAGNOSTIC_ONLY" else None
    require(rank is None or (type(rank) is int and -10 <= rank <= 100),
            "diagnostic rank must be an integer in -10..100")
    return (0 if report.get("verdict") == "EQUAL" else 1,
            item["causal_family"], item["diagnostic_scope"], rank is None, -(rank or 0),
            -(report.get("mnemonic_similarity") or 0), report.get("actual_length") or 0)


def evaluate(function_id, variants, cached_only=False, output_dir=None):
    """Run exact isolated comparisons; never retain, rank-promote, or canonicalize."""
    require(1 <= len(variants) <= MAX_VARIANTS, "variant count exceeds the hard limit")
    ledger = evidence()
    function = next((f for f in ledger["functions"] if f["id"] == function_id), None)
    require(function is not None, "unknown function " + function_id)
    if cached_only and any(c.get("basis") == "PC_RELATIVE" and c.get("hunk") == function["hunk"] and c.get("id") != function_id
                           for c in function.get("direct_callees", [])):
        raise FormatError("same-overlay PC-relative calls require prepared-unit cache identity; bounded shape search currently rejects them")
    node = function["hunk"] - 2 if function.get("node") != "resident" and function.get("hunk", 0) >= 3 else 1
    requests = []
    expected_keys = []
    for variant in variants:
        try:
            key, _, _ = identity(variant["source"], variant["profile"], node)
        except (KeyError, FormatError) as exc:
            raise FormatError("variant " + variant["id"] + " is not accepted by the compiler oracle: " + str(exc)) from exc
        expected_keys.append(key)
        requests.append(dict(id=function_id, source=str(variant["source_path"]), profiles=[variant["profile"]]))
    unique_keys = set(expected_keys)
    require(len(unique_keys) <= MAX_UNIQUE_COMPILES,
            "compiler identity count exceeds the hard unique compile limit")
    if cached_only:
        from compiler_oracle import cached
        misses = [key for key in unique_keys if cached(key) is None]
        require(not misses, "cached-only mode refused: " + str(len(misses)) + " compiler identities would require a compile")
    reports = check_many(requests, promote_equal=False, isolated=True, output_dir=output_dir)
    require(len(reports) == len(variants), "verifier returned an unexpected report count")
    evaluated = []
    for variant, report in zip(variants, reports):
        diagnostic = _diagnostic(function_id, report, variant["diagnostic_scope"])
        evaluated.append(dict(id=variant["id"], causal_family=variant["causal_family"],
                              diagnostic_scope=variant["diagnostic_scope"],
                              source=variant["manifest_source"], source_sha256=report["source_sha256"],
                              compiler=variant["profile"], exact_verdict=report["verdict"],
                              diagnostic=diagnostic,
                              structure=dict(expected_length=report.get("expected_length"),
                                             actual_length=report.get("actual_length"),
                                             mnemonic_similarity=report.get("mnemonic_similarity"),
                                             first_structural_instruction_difference=report.get("first_structural_instruction_difference"),
                                             normalized_first_difference=report.get("normalized_first_difference")),
                              report=report))
    # Comparisons are ranked only within each explicitly named causal family
    # and diagnostic scope. A classifier's unsupported response stays visible.
    evaluated.sort(key=_rank_key)
    return dict(schema_version=1, function_id=function_id,
                exact_verdict_authority="check_function.check_many isolated comparison",
                promotion="NONE", evaluated=evaluated,
                ranking=[item["id"] for item in evaluated])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--cached-only", action="store_true",
                        help="refuse before verification if any unique compiler identity misses cache")
    parser.add_argument("--output-dir", type=Path,
                        help="save isolated exact reports under experiments/ or build/")
    parser.add_argument("--json", action="store_true", help="emit the complete JSON evaluation")
    args = parser.parse_args(argv)
    try:
        function_id, _budget, variants = load_manifest(args.manifest)
        output_dir = args.output_dir
        if output_dir is not None:
            output_dir = output_dir.resolve()
            allowed = ((ROOT / "experiments").resolve(), (ROOT / "build").resolve())
            require(any(output_dir.is_relative_to(root) for root in allowed),
                    "output directory must be under experiments/ or build/")
        result = evaluate(function_id, variants, args.cached_only, output_dir)
        print(json.dumps(result, indent=2 if args.json else None, sort_keys=True))
        return 0
    except (FormatError, OSError, UnicodeError, ValueError) as exc:
        print(json.dumps(dict(status="REJECTED", reason=str(exc))), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
