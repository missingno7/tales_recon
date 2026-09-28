"""Evaluate a small, explicitly authored set of independent C variants.

This utility is a bounded diagnostic front end to ``check_function``. It never
generates source text, updates recovery state, or promotes an exact comparison.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time

from analysis_support import ROOT
from common import FormatError, require, sha256
from check_function import check_many
from recovery_state import evidence
from compiler_oracle import identity
import compile_queue
import file_lock


MAX_VARIANTS = 32
MAX_UNIQUE_COMPILES = 32
MANIFEST_KEYS = {"schema_version", "function_id", "budget", "variants"}
BUDGET_KEYS = {"max_variants", "max_unique_compiles"}
VARIANT_KEYS = {"id", "causal_family", "diagnostic_scope", "source", "profile"}
# Schema v2 adds a recorded, machine-checkable hypothesis to every variant.
HYPOTHESIS_KEYS = {"parent", "suspected_cause", "controlled_change", "predicted_effect"}
PREDICTION_KEYS = {"length_delta", "removed_candidate_only", "register_role_diffs", "note"}
PREDICTED_FIELDS = ("length_delta", "removed_candidate_only", "register_role_diffs")
ROLE_TRENDS = {"fewer", "same", "more"}
LEDGER_SCHEMA = 1
# ``fleet_intake`` records are appended by tools/fleet.py after supervisor
# intake of a worker result; they never count as compiler trials.
RECORD_TYPES = ("trial", "duplicate_rejected", "fleet_intake")
DEFAULT_LEDGER = Path("evidence/experiments/hypothesis-ledger.jsonl")
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


def normalize_source(text):
    """Deliberately shallow C text normalization for duplicate detection only.

    Comments are replaced by one space; string and character literals are
    copied verbatim. Outside literals, every whitespace run (including line
    breaks) collapses to one space, except that preprocessor directive lines
    (and their backslash continuations) stay on their own lines. No token,
    macro, or semantic normalization is applied: ``a+b`` and ``a + b`` remain
    different hypotheses.
    """
    segments, plain, i, n = [], [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            segments.append(re.sub(r"[ \t\f\v\r]+", " ", "".join(plain)))
            segments.append(text[i:j + 1])
            plain, i = [], j + 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            plain.append(" ")
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            plain.append(" ")
        else:
            plain.append(c)
            i += 1
    segments.append(re.sub(r"[ \t\f\v\r]+", " ", "".join(plain)))
    out, code, directive = [], [], False
    for line in (x.strip() for x in "".join(segments).split("\n")):
        if directive or line.startswith("#"):
            if code:
                out.append(" ".join(code))
                code = []
            if line:
                out.append(line)
            directive = line.endswith("\\")
        elif line:
            code.append(line)
    if code:
        out.append(" ".join(code))
    return "\n".join(out)


def normalized_sha256(text):
    return sha256(normalize_source(text).encode("utf-8"))


def _prediction(value, where):
    _object(value, where, PREDICTION_KEYS)
    length = value["length_delta"]
    removed = value["removed_candidate_only"]
    roles = value["register_role_diffs"]
    require(length is None or type(length) is int, where + ".length_delta must be an integer or null")
    require(removed is None or type(removed) is int, where + ".removed_candidate_only must be an integer or null")
    require(roles is None or roles in ROLE_TRENDS, where + ".register_role_diffs must be fewer, same, more or null")
    require(any(v is not None for v in (length, removed, roles)),
            where + " must make at least one machine-checkable prediction")
    _text(value["note"], where + ".note", 300)
    return dict(length_delta=length, removed_candidate_only=removed,
                register_role_diffs=roles, note=value["note"])


def _parent(value, where, earlier_ids):
    require(isinstance(value, str) and value, where + " must be text")
    if value == "none":
        return dict(kind="none", value=value)
    if value in earlier_ids:
        return dict(kind="variant", value=value)
    if re.fullmatch(r"ledger:[1-9][0-9]{0,8}", value):
        return dict(kind="ledger", value=value, line=int(value.split(":")[1]))
    if re.fullmatch(r"[0-9a-f]{64}", value):
        return dict(kind="cache_key", value=value)
    require(value.endswith(".c"), where + " must be an earlier variant id, a repository .c path, "
                                          "ledger:N, a 64-hex cache key, or none")
    path = _source_path(value)
    return dict(kind="source", value=value, source_path=path,
                source=path.read_text(encoding="ascii"))


def load_manifest(path):
    """Parse and validate the deliberately narrow JSON manifest format."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FormatError("cannot read manifest: " + str(exc)) from exc
    require(isinstance(manifest, dict) and manifest.get("schema_version") in (1, 2),
            "unsupported manifest schema_version")
    version = manifest["schema_version"]
    _object(manifest, "manifest", MANIFEST_KEYS)
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
        _object(variant, where, VARIANT_KEYS if version == 1 else VARIANT_KEYS | HYPOTHESIS_KEYS)
        variant_id = _text(variant["id"], where + ".id", 80)
        require(variant_id not in ids, "variant ids must be unique")
        causal_family = _text(variant["causal_family"], where + ".causal_family", 80)
        diagnostic_scope = _text(variant["diagnostic_scope"], where + ".diagnostic_scope", 80)
        require(diagnostic_scope in DIAGNOSTIC_SCOPES,
                where + ".diagnostic_scope is unsupported")
        profile = _text(variant["profile"], where + ".profile", 80)
        source = _source_path(variant["source"])
        item = dict(id=variant_id, causal_family=causal_family,
                    diagnostic_scope=diagnostic_scope, profile=profile,
                    source_path=source, source=source.read_text(encoding="ascii"),
                    manifest_source=variant["source"])
        if version == 2:
            # A variant may only name an earlier variant as parent, so the
            # hypothesis graph is acyclic by construction.
            item["parent"] = _parent(variant["parent"], where + ".parent", ids)
            item["suspected_cause"] = _text(variant["suspected_cause"], where + ".suspected_cause", 300)
            item["controlled_change"] = _text(variant["controlled_change"], where + ".controlled_change", 300)
            item["predicted_effect"] = _prediction(variant["predicted_effect"], where + ".predicted_effect")
            item["normalized_sha256"] = normalized_sha256(item["source"])
            twin = next((v for v in normalized if v["normalized_sha256"] == item["normalized_sha256"]
                         and v["profile"] == profile), None)
            require(twin is None, where + " duplicates variant " + (twin or {}).get("id", "") +
                    " after comment/whitespace normalization")
            parent = item["parent"]
            if parent["kind"] == "source":
                require(normalized_sha256(parent["source"]) != item["normalized_sha256"],
                        where + " is identical to its parent after normalization; no controlled change")
        ids.add(variant_id)
        normalized.append(item)

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


def _node(function):
    return function["hunk"] - 2 if function.get("node") != "resident" and function.get("hunk", 0) >= 3 else 1


def evaluate(function_id, variants, cached_only=False, output_dir=None):
    """Run exact isolated comparisons; never retain, rank-promote, or canonicalize."""
    require(1 <= len(variants) <= MAX_VARIANTS, "variant count exceeds the hard limit")
    ledger = evidence()
    function = next((f for f in ledger["functions"] if f["id"] == function_id), None)
    require(function is not None, "unknown function " + function_id)
    if cached_only and any(c.get("basis") == "PC_RELATIVE" and c.get("hunk") == function["hunk"] and c.get("id") != function_id
                           for c in function.get("direct_callees", [])):
        raise FormatError("same-overlay PC-relative calls require prepared-unit cache identity; bounded shape search currently rejects them")
    node = _node(function)
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
    # Cache misses wait in the coalescing compile queue instead of failing
    # while another process holds the oracle; cache hits never wait.
    compile_queue.install()
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


# ---------------------------------------------------------------------------
# Schema v2: recorded hypotheses, duplicate rejection and prediction scoring.
# Nothing below reads or alters an exact verdict; it only records it.


def ledger_path(path=None):
    """Resolve the append-only hypothesis ledger, confined to experiment areas."""
    rel = Path(path) if path is not None else DEFAULT_LEDGER
    full = (rel if rel.is_absolute() else ROOT / rel).resolve()
    allowed = [(ROOT / "evidence" / "experiments").resolve(), (ROOT / "experiments").resolve(),
               (ROOT / "build").resolve()]
    require(any(full.is_relative_to(a) for a in allowed) and full.suffix == ".jsonl",
            "hypothesis ledger must be a .jsonl file under evidence/experiments/, experiments/ or build/")
    return full


def read_ledger(path):
    """Return [(line_number, record)]; any malformed line refuses the ledger."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    require(not text or text.endswith("\n"), "hypothesis ledger has a truncated final line")
    records = []
    for number, line in enumerate(text.splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FormatError("hypothesis ledger line " + str(number) + " is not JSON") from exc
        require(isinstance(record, dict) and record.get("ledger_schema") == LEDGER_SCHEMA
                and record.get("record_type") in RECORD_TYPES,
                "hypothesis ledger line " + str(number) + " has an unsupported record shape")
        records.append((number, record))
    return records


def append_ledger(path, records, timeout=60):
    """Append records under an exclusive lock file; never rewrite prior lines."""
    if not records:
        return []
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock.locked(_ledger_lock(path), "hypothesis ledger append", timeout, "hypothesis ledger"):
        first = len(read_ledger(path)) + 1
        data = "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in records)
        with open(path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return list(range(first, first + len(records)))


def _ledger_lock(path):
    return path.with_name(path.name + ".lock")


def _reservation_dir(path):
    """Ephemeral in-flight markers live in ignored build/, never in evidence/."""
    return ROOT / "build" / "hypothesis-inflight" / sha256(str(path).encode("utf-8"))[:16]


def _reservation_path(path, function_id, variant):
    key = "|".join((function_id, variant["normalized_sha256"], variant["profile"]))
    return _reservation_dir(path) / (sha256(key.encode("utf-8"))[:32] + ".json")


def _prior_trials(prior):
    seen = {}
    for number, record in prior:
        if record["record_type"] == "trial":
            seen.setdefault((record.get("function_id"), record.get("normalized_sha256"), record.get("profile")),
                            (number, record))
    return seen


def reserve_hypotheses(path, function_id, variants, timeout=None, poll=0.5):
    """Race-safe duplicate check immediately before compiling.

    Under the ledger lock, the ledger is re-read and every variant that is
    neither recorded nor in flight elsewhere receives an in-flight
    reservation. A twin in flight in a live process is waited for, then
    re-checked, so it becomes an ordinary ``duplicate_rejected`` pointer. A
    reservation left by a dead process is replaced and reported.
    """
    timeout = compile_queue.wait_timeout() if timeout is None else timeout
    deadline = time.monotonic() + timeout
    lock = _ledger_lock(path)
    while True:
        with file_lock.locked(lock, "hypothesis ledger reservation", 60, "hypothesis ledger"):
            prior = read_ledger(path)
            seen = _prior_trials(prior)
            duplicates = {v["id"]: seen[(function_id, v["normalized_sha256"], v["profile"])] for v in variants
                          if (function_id, v["normalized_sha256"], v["profile"]) in seen}
            waiting, stale = [], []
            for v in variants:
                if v["id"] in duplicates:
                    continue
                marker = _reservation_path(path, function_id, v)
                try:
                    owner = json.loads(marker.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if owner.get("host") == file_lock.HOST and not file_lock.pid_alive(owner.get("pid")):
                    stale.append(dict(variant=v["id"], reservation=owner))
                else:
                    waiting.append(dict(variant=v["id"], reservation=owner))
            if not waiting:
                reserved = []
                for v in variants:
                    if v["id"] in duplicates:
                        continue
                    marker = _reservation_path(path, function_id, v)
                    marker.parent.mkdir(parents=True, exist_ok=True)
                    marker.write_text(json.dumps(dict(pid=os.getpid(), host=file_lock.HOST, function_id=function_id,
                                                      variant=v["id"], profile=v["profile"],
                                                      normalized_sha256=v["normalized_sha256"],
                                                      started=time.time()), sort_keys=True), encoding="utf-8")
                    reserved.append(marker)
                return prior, duplicates, reserved, stale
        require(time.monotonic() < deadline,
                "identical hypothesis is still in flight in another process: " + json.dumps(waiting, sort_keys=True))
        time.sleep(poll)


def release_reservations(markers):
    for marker in markers:
        try:
            owner = json.loads(marker.read_text(encoding="utf-8"))
            if owner.get("pid") == os.getpid():
                file_lock.unlink_retry(marker)
        except (OSError, ValueError):
            pass


def diagnostic_metrics(diagnostic):
    """Extract the few quantities predictions are scored against.

    An unsupported diagnostic keeps only ``candidate_bytes`` when the diagnostic
    itself measured the compiled single-object code payload (for example when
    the original has PC-relative data whose boundary cannot be aligned). That
    length is the same quantity a supported diagnostic reports; alignment and
    register-role counts stay unavailable.
    """
    if not isinstance(diagnostic, dict) or diagnostic.get("status") != "DIAGNOSTIC_ONLY":
        out = dict(status="UNSUPPORTED", reason=str((diagnostic or {}).get("reason", "UNSUPPORTED")))
        extent = diagnostic.get("candidate_extent") if isinstance(diagnostic, dict) else None
        if isinstance(extent, dict) and type(extent.get("bytes")) is int:
            out.update(candidate_bytes=extent["bytes"], candidate_bytes_basis="COMPILED_CODE_PAYLOAD")
        return out
    align = diagnostic.get("alignment") or {}
    extent = diagnostic.get("candidate_extent") or diagnostic.get("actual_extent") or {}
    size, actual_only, expected_only = extent.get("bytes"), align.get("actual_only"), align.get("expected_only")
    hypotheses = diagnostic.get("hypotheses")
    if type(size) is not int or not isinstance(actual_only, list) or not isinstance(expected_only, list) \
            or not isinstance(hypotheses, list):
        return dict(status="UNSUPPORTED", reason="diagnostic lacks extent, alignment or hypothesis counts")
    roles = sum(h.get("count", 0) for h in hypotheses
                if isinstance(h, dict) and h.get("category") == "register_assignment")
    return dict(status="DIAGNOSTIC_ONLY", candidate_bytes=size, candidate_only=len(actual_only),
                expected_only=len(expected_only), register_role_diffs=roles)


def score_prediction(predicted, child, parent):
    """Compare a structured prediction with the observed child-parent delta.

    A field is ``unmeasurable`` whenever no parent measurement exists or the
    quantity is unavailable on either side; it is never guessed from other
    signals. Alignment and register-role fields need supported diagnostics on
    both sides. ``length_delta`` needs only both compiled code-payload lengths,
    which an unsupported diagnostic still reports when it measured them.
    """
    full = (isinstance(child, dict) and child.get("status") == "DIAGNOSTIC_ONLY" and
            isinstance(parent, dict) and parent.get("status") == "DIAGNOSTIC_ONLY")
    sized = (isinstance(child, dict) and isinstance(parent, dict) and
             type(child.get("candidate_bytes")) is int and type(parent.get("candidate_bytes")) is int)
    observed = None
    measurable = {name: False for name in PREDICTED_FIELDS}
    if full:
        roles = child["register_role_diffs"] - parent["register_role_diffs"]
        observed = dict(length_delta=child["candidate_bytes"] - parent["candidate_bytes"],
                        removed_candidate_only=parent["candidate_only"] - child["candidate_only"],
                        register_role_diffs="fewer" if roles < 0 else "more" if roles > 0 else "same")
        measurable = {name: True for name in PREDICTED_FIELDS}
    elif sized:
        observed = dict(length_delta=child["candidate_bytes"] - parent["candidate_bytes"],
                        removed_candidate_only=None, register_role_diffs=None)
        measurable["length_delta"] = True
    fields = {}
    for name in PREDICTED_FIELDS:
        if predicted.get(name) is None:
            fields[name] = "not_predicted"
        elif not measurable[name]:
            fields[name] = "unmeasurable"
        else:
            fields[name] = "confirmed" if observed[name] == predicted[name] else "refuted"
    states = [s for s in fields.values() if s != "not_predicted"]
    measured = [s for s in states if s != "unmeasurable"]
    if not measured:
        outcome = "unmeasurable"
    elif all(s == "confirmed" for s in states):
        outcome = "confirmed"
    elif all(s == "refuted" for s in measured):
        outcome = "refuted"
    else:
        outcome = "partial"
    basis = "FULL_DIAGNOSTIC" if full else "PAYLOAD_LENGTH_ONLY" if sized else None
    return dict(observed_delta=observed, fields=fields, outcome=outcome, measurement=basis)


def _rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _pointer(number, record):
    return dict(ledger_line=number, timestamp=record.get("timestamp"), manifest=record.get("manifest"),
                variant=record.get("variant"), exact_verdict=record.get("exact_verdict"),
                cache_key=record.get("cache_key"))


def _cached(key):
    if not isinstance(key, str) or re.fullmatch(r"[0-9a-f]{64}", key) is None:
        return None
    from compiler_oracle import cached
    return cached(key)


def measure_key(function_id, key, scope):
    """Metrics of one cached compile, re-diagnosed now; never compiles."""
    if _cached(key) is None:
        return dict(status="UNSUPPORTED", reason="PARENT_NOT_IN_COMPILER_CACHE")
    return diagnostic_metrics(_diagnostic(function_id, dict(cache_key=key), scope))


def _retained_attempt_key(function_id, parent, profile):
    """Cache key of a retained verifier attempt with byte-identical source."""
    try:
        from recovery_state import recovery
        rows = recovery().get("attempts", {}).get(function_id, [])
    except Exception:  # advisory lookup only
        return None
    path = parent.get("source_path")
    digest = (sha256(Path(path).read_bytes()) if path and Path(path).is_file()
              else sha256(parent["source"].encode("ascii", "replace")))
    for row in reversed(rows):
        if row.get("source_sha256") == digest and row.get("profile") == profile and _cached(row.get("cache_key")):
            return row["cache_key"]
    return None


def _ledger_trial(prior, function_id, line=None, digest=None, profile=None):
    for number, record in reversed(prior):
        if record["record_type"] != "trial" or record.get("function_id") != function_id:
            continue
        if line is not None and number == line:
            return number, record
        if digest is not None and record.get("normalized_sha256") == digest and record.get("profile") == profile:
            return number, record
    return None, None


def _from_record(function_id, record, scope):
    """Prefer a fresh measurement of the record's cached compile over its stored metrics."""
    if _cached(record.get("cache_key")) is not None:
        return measure_key(function_id, record["cache_key"], scope)
    return record.get("observed")


def parent_key(function_id, function, variant, prior):
    """Resolve (cache_key or None, basis) for a source/ledger/cache-key parent without compiling."""
    parent = variant["parent"]
    if parent["kind"] == "cache_key":
        return parent["value"], "PARENT_CACHE_KEY"
    if parent["kind"] == "ledger":
        number, record = _ledger_trial(prior, function_id, line=parent["line"])
        return (record.get("cache_key") if record else None), "LEDGER_LINE_" + str(parent["line"])
    digest = normalized_sha256(parent["source"])
    number, record = _ledger_trial(prior, function_id, digest=digest, profile=variant["profile"])
    if record is not None:
        return record.get("cache_key"), "LEDGER_LINE_" + str(number)
    try:
        key, _, _ = identity(parent["source"], variant["profile"], _node(function))
    except (KeyError, FormatError):
        key = None
    if key and _cached(key) is not None:
        return key, "CACHED_PARENT_COMPILE"
    retained = _retained_attempt_key(function_id, parent, variant["profile"])
    if retained:
        return retained, "RETAINED_ATTEMPT_CACHE"
    return None, "NOT_COMPILED" if key else "IDENTITY_REJECTED"


def _parent_metrics(function_id, function, variant, metrics, prior, compiled_parents=None):
    """Measure the declared parent; compiles only through the explicit counted-parent path."""
    parent = variant["parent"]
    scope = variant["diagnostic_scope"]
    if parent["kind"] == "none":
        return None, "NO_PARENT"
    if parent["kind"] == "variant":
        return metrics.get(parent["value"]), "MANIFEST_VARIANT"
    if parent["kind"] == "ledger":
        number, record = _ledger_trial(prior, function_id, line=parent["line"])
        if record is None:
            return dict(status="UNSUPPORTED", reason="PARENT_LEDGER_LINE_NOT_A_TRIAL_FOR_FUNCTION"), parent["value"]
        return _from_record(function_id, record, scope), "LEDGER_LINE_" + str(number)
    if parent["kind"] == "cache_key":
        return measure_key(function_id, parent["value"], scope), "PARENT_CACHE_KEY"
    digest = normalized_sha256(parent["source"])
    number, record = _ledger_trial(prior, function_id, digest=digest, profile=variant["profile"])
    if record is not None:
        return _from_record(function_id, record, scope), "LEDGER_LINE_" + str(number)
    compiled = (compiled_parents or {}).get((digest, variant["profile"]))
    if compiled is not None:
        return compiled["metrics"], compiled["basis"]
    try:
        key, _, _ = identity(parent["source"], variant["profile"], _node(function))
    except (KeyError, FormatError) as exc:
        return dict(status="UNSUPPORTED", reason="parent identity rejected: " + str(exc)), "NOT_COMPILED"
    if _cached(key) is not None:
        return measure_key(function_id, key, scope), "CACHED_PARENT_COMPILE"
    retained = _retained_attempt_key(function_id, parent, variant["profile"])
    if retained:
        return measure_key(function_id, retained, scope), "RETAINED_ATTEMPT_CACHE"
    return dict(status="UNSUPPORTED", reason="PARENT_NOT_IN_COMPILER_CACHE"), "NOT_COMPILED"


def _parents_to_compile(function_id, function, variants, prior, duplicates):
    """Source parents with no ledger, cache or retained-attempt measurement."""
    todo = {}
    for variant in variants:
        parent = variant["parent"]
        if variant["id"] in duplicates or parent["kind"] != "source":
            continue
        key, basis = parent_key(function_id, function, variant, prior)
        if basis == "NOT_COMPILED":
            todo.setdefault((normalized_sha256(parent["source"]), variant["profile"]), variant)
    return todo


def evaluate_hypotheses(function_id, variants, cached_only=False, output_dir=None, ledger=None,
                        manifest=None, now=None, measure_parents=False, budget=None):
    """Run non-duplicate v2 variants and append one ledger record per variant.

    ``measure_parents`` compiles a source parent that has no ledger, cache or
    retained-attempt measurement, as an explicitly counted extra compile inside
    ``budget.max_unique_compiles``; the child record marks it as such.
    """
    path = ledger_path(ledger)
    # The duplicate check is repeated under the ledger lock immediately before
    # compiling, with in-flight reservations, so parallel workers cannot both
    # compile the same (function, normalized source, profile) hypothesis.
    prior, duplicates, reserved, stale = reserve_hypotheses(path, function_id, variants)
    try:
        return _evaluate_reserved(function_id, variants, cached_only, output_dir, path, manifest, now,
                                  prior, duplicates, stale, measure_parents, budget)
    finally:
        release_reservations(reserved)


def _parent_compiles(function_id, function, variants, to_run, prior, duplicates, cached_only, budget):
    """Pseudo-variants for counted parent measurement compiles, and over-budget refusals."""
    todo = _parents_to_compile(function_id, function, variants, prior, duplicates)
    limit = (budget or {}).get("max_unique_compiles", MAX_UNIQUE_COMPILES)
    used = len({(sha256(v["source"].encode("ascii")), v["profile"]) for v in to_run})
    pseudo, refused = [], {}
    for index, (slot, variant) in enumerate(sorted(todo.items(), key=lambda kv: kv[1]["id"])):
        if cached_only:
            refused[slot] = "PARENT_COMPILE_REFUSED_CACHED_ONLY"
        elif used + len(pseudo) >= limit:
            refused[slot] = "PARENT_COMPILE_OVER_BUDGET"
        else:
            parent = variant["parent"]
            pseudo.append(dict(id="parent-measurement-%02d" % index, causal_family="parent_measurement",
                               diagnostic_scope=variant["diagnostic_scope"], profile=variant["profile"],
                               source_path=parent["source_path"], source=parent["source"],
                               manifest_source=parent["value"], slot=slot))
    return pseudo, refused


def _evaluate_reserved(function_id, variants, cached_only, output_dir, path, manifest, now,
                       prior, duplicates, stale, measure_parents=False, budget=None):
    to_run = [v for v in variants if v["id"] not in duplicates]
    function = next((f for f in evidence()["functions"] if f["id"] == function_id), None)
    require(function is not None, "unknown function " + function_id)
    pseudo, refused = ([], {})
    if measure_parents:
        pseudo, refused = _parent_compiles(function_id, function, variants, to_run, prior, duplicates,
                                           cached_only, budget)
    run = to_run + pseudo
    base = evaluate(function_id, run, cached_only, output_dir) if run else dict(evaluated=[], ranking=[])
    compiled_parents = {slot: dict(metrics=dict(status="UNSUPPORTED", reason=reason), basis="NOT_COMPILED",
                                   compile=None) for slot, reason in refused.items()}
    pseudo_ids = {p["id"]: p for p in pseudo}
    for item in base["evaluated"]:
        if item["id"] in pseudo_ids:
            report = item["report"]
            compiled_parents[pseudo_ids[item["id"]]["slot"]] = dict(
                metrics=diagnostic_metrics(item["diagnostic"]), basis="PARENT_COMPILED_COUNTED_TRIAL",
                compile=dict(source=item.get("source"), cache_key=report.get("cache_key"),
                             cache_hit=report.get("cache_hit"), exact_verdict=report.get("verdict"),
                             counted_trial=True))
    base = dict(base, evaluated=[e for e in base["evaluated"] if e["id"] not in pseudo_ids],
                ranking=[r for r in base["ranking"] if r not in pseudo_ids])
    by_id = {item["id"]: item for item in base["evaluated"]}
    metrics = {item_id: diagnostic_metrics(item["diagnostic"]) for item_id, item in by_id.items()}
    metrics.update({item_id: _from_record(function_id, record, record.get("diagnostic_scope"))
                    for item_id, (_, record) in duplicates.items()})
    stamp = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    records, rejected = [], []
    for variant in variants:
        common = dict(ledger_schema=LEDGER_SCHEMA, timestamp=stamp, function_id=function_id,
                      manifest=_rel(manifest) if manifest else None, variant=variant["id"],
                      source=variant["manifest_source"], normalized_sha256=variant["normalized_sha256"],
                      source_sha256=sha256(variant["source"].encode("ascii")), profile=variant["profile"],
                      parent=variant["parent"]["value"], causal_family=variant["causal_family"],
                      diagnostic_scope=variant["diagnostic_scope"], suspected_cause=variant["suspected_cause"],
                      controlled_change=variant["controlled_change"], predicted_effect=variant["predicted_effect"])
        if variant["id"] in duplicates:
            pointer = _pointer(*duplicates[variant["id"]])
            records.append(dict(common, record_type="duplicate_rejected", prior_record=pointer))
            rejected.append(dict(id=variant["id"], prior_record=pointer))
            continue
        item = by_id[variant["id"]]
        report = item["report"]
        parent, basis = _parent_metrics(function_id, function, variant, metrics, prior, compiled_parents)
        score = score_prediction(variant["predicted_effect"], metrics[variant["id"]], parent)
        record = dict(common, record_type="trial", cache_key=report.get("cache_key"),
                      cache_hit=report.get("cache_hit"), exact_verdict=report.get("verdict"),
                      observed=metrics[variant["id"]], parent_observed=parent, parent_basis=basis,
                      observed_delta=score["observed_delta"], prediction=score)
        if basis == "PARENT_COMPILED_COUNTED_TRIAL" and variant["parent"]["kind"] == "source":
            slot = (normalized_sha256(variant["parent"]["source"]), variant["profile"])
            record["parent_compile"] = compiled_parents[slot]["compile"]
        records.append(record)
        item["hypothesis"] = dict(parent=common["parent"], parent_basis=basis,
                                  suspected_cause=variant["suspected_cause"],
                                  controlled_change=variant["controlled_change"],
                                  predicted_effect=variant["predicted_effect"], observed=record["observed"],
                                  parent_observed=parent, prediction=score)
    lines = append_ledger(path, records)
    for line, record in zip(lines, records):
        if record["record_type"] == "trial":
            by_id[record["variant"]]["ledger_line"] = line
    return dict(schema_version=2, function_id=function_id,
                exact_verdict_authority="check_function.check_many isolated comparison",
                promotion="NONE", evaluated=base["evaluated"], ranking=base["ranking"],
                duplicates_rejected=rejected, ledger=dict(path=_rel(path), lines=lines),
                stale_reservations_replaced=stale)


def _record_parent_key(function_id, number, record, prior):
    """Cache key of a recorded trial's parent, resolved read-only from the ledger and caches."""
    basis = record.get("parent_basis") or ""
    parent = record.get("parent")
    if basis == "NO_PARENT" or parent in (None, "none"):
        return None, "NO_PARENT"
    if (record.get("parent_compile") or {}).get("cache_key"):
        return record["parent_compile"]["cache_key"], "PARENT_COMPILED_COUNTED_TRIAL"
    if basis.startswith("LEDGER_LINE_"):
        line = int(basis.split("_")[-1])
        _, prev = _ledger_trial(prior, function_id, line=line)
        return (prev or {}).get("cache_key"), basis
    if basis == "MANIFEST_VARIANT":
        for n, prev in reversed(prior):
            if (n < number and prev["record_type"] == "trial" and prev.get("function_id") == function_id
                    and prev.get("manifest") == record.get("manifest") and prev.get("variant") == parent):
                return prev.get("cache_key"), basis
        return None, basis
    if basis == "PARENT_CACHE_KEY":
        return parent, basis
    if isinstance(parent, str) and parent.endswith(".c"):
        try:
            path = _source_path(parent)
            variant = dict(parent=dict(kind="source", value=parent, source_path=path,
                                       source=path.read_text(encoding="ascii")),
                           profile=record.get("profile"))
            function = next(f for f in evidence()["functions"] if f["id"] == function_id)
        except (FormatError, OSError, UnicodeError, StopIteration):
            return None, "PARENT_SOURCE_UNAVAILABLE"
        return parent_key(function_id, function, variant, [(n, r) for n, r in prior if n < number])
    return None, basis or "UNKNOWN_PARENT"


def _unmeasurable_reason(score, child, parent):
    if score["outcome"] != "unmeasurable":
        return None
    if parent is None:
        return "NO_PARENT"
    for side, value in (("child", child), ("parent", parent)):
        if not isinstance(value, dict) or type(value.get("candidate_bytes")) is not int:
            return side + ":" + str((value or {}).get("reason", "NO_MEASUREMENT"))
    return "PREDICTED_FIELDS_NEED_SUPPORTED_DIAGNOSTIC"


def rescore_ledger(path, function_id=None):
    """Read-only re-measurement of recorded predictions from cached compiles.

    The ledger is append-only and is never rewritten; this reports what the
    current scorer and diagnostics measure for each recorded trial.
    """
    prior = read_ledger(path)
    rows = []
    for number, record in prior:
        if record["record_type"] != "trial" or function_id not in (None, record.get("function_id")):
            continue
        fid, scope = record.get("function_id"), record.get("diagnostic_scope")
        child = _from_record(fid, record, scope)
        key, basis = _record_parent_key(fid, number, record, prior)
        parent = None if basis == "NO_PARENT" else measure_key(fid, key, scope) if key else \
            dict(status="UNSUPPORTED", reason="PARENT_NOT_RESOLVED_" + basis)
        score = score_prediction(record.get("predicted_effect") or {}, child, parent)
        rows.append(dict(line=number, function_id=fid, variant=record.get("variant"), parent_basis=basis,
                         recorded=(record.get("prediction") or {}).get("outcome"), rescored=score["outcome"],
                         measurement=score["measurement"], fields=score["fields"],
                         reason=_unmeasurable_reason(score, child, parent)))
    outcomes = ("confirmed", "partial", "refuted", "unmeasurable")
    return dict(recorded={k: sum(r["recorded"] == k for r in rows) for k in outcomes},
                rescored={k: sum(r["rescored"] == k for r in rows) for k in outcomes},
                unmeasurable_reasons=dict(sorted(Counter(r["reason"] for r in rows
                                                         if r["rescored"] == "unmeasurable").items())),
                trials=rows, note="read-only; the ledger is not rewritten")


def ledger_summary(path, function_id=None, rescore=False):
    """Convergence counts: exact matches per compiler trial and prediction outcomes."""
    records = [r for _, r in read_ledger(path) if function_id in (None, r.get("function_id"))]
    trials = [r for r in records if r["record_type"] == "trial"]
    compiled = {r.get("cache_key") for r in trials if r.get("cache_hit") is False}
    parent_compiles = {(r.get("parent_compile") or {}).get("cache_key") for r in trials
                       if (r.get("parent_compile") or {}).get("cache_hit") is False}
    compiled |= parent_compiles
    exact = sum(r.get("exact_verdict") == "EQUAL" for r in trials)
    # The ratio counts only exact matches produced by a real compile in this
    # ledger, so replaying cached identities cannot inflate convergence.
    fresh = len({r.get("cache_key") for r in trials
                 if r.get("exact_verdict") == "EQUAL" and r.get("cache_hit") is False})
    outcomes = {k: 0 for k in ("confirmed", "partial", "refuted", "unmeasurable")}
    for r in trials:
        outcome = (r.get("prediction") or {}).get("outcome")
        if outcome in outcomes:
            outcomes[outcome] += 1
    summary = dict(ledger=_rel(path), function_id=function_id, evaluations=len(trials),
                   compiler_trials=len(compiled), parent_measurement_compiles=len(parent_compiles),
                   cache_hits=sum(r.get("cache_hit") is True for r in trials),
                   exact_matches=exact, exact_matches_from_compiler_trials=fresh,
                   exact_matches_per_compiler_trial=round(fresh / len(compiled), 4) if compiled else None,
                   predictions=outcomes, duplicates_rejected=sum(r["record_type"] == "duplicate_rejected"
                                                                 for r in records),
                   functions=sorted({r.get("function_id") for r in records}))
    if rescore:
        rescored = rescore_ledger(path, function_id)
        summary["predictions_rescored"] = rescored["rescored"]
        summary["rescored_unmeasurable_reasons"] = rescored["unmeasurable_reasons"]
        summary["rescored_trials"] = [{k: r[k] for k in ("line", "variant", "recorded", "rescored", "measurement",
                                                         "reason")} for r in rescored["trials"]]
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, nargs="?")
    parser.add_argument("--cached-only", action="store_true",
                        help="refuse before verification if any unique compiler identity misses cache")
    parser.add_argument("--output-dir", type=Path,
                        help="save isolated exact reports under experiments/ or build/")
    parser.add_argument("--json", action="store_true", help="emit the complete JSON evaluation")
    parser.add_argument("--ledger", type=Path,
                        help="schema v2 hypothesis ledger (default " + DEFAULT_LEDGER.as_posix() + ")")
    parser.add_argument("--ledger-summary", nargs="?", const="*", metavar="FUNCTION",
                        help="print convergence counts from the ledger, optionally for one function")
    parser.add_argument("--rescore", action="store_true",
                        help="with --ledger-summary: re-measure recorded predictions from cached compiles (read-only)")
    parser.add_argument("--measure-parents", action="store_true",
                        help="compile an unmeasured source parent as a counted trial within max_unique_compiles")
    args = parser.parse_args(argv)
    try:
        if args.ledger_summary is not None:
            function = None if args.ledger_summary == "*" else args.ledger_summary
            print(json.dumps(ledger_summary(ledger_path(args.ledger), function, args.rescore), indent=2, sort_keys=True))
            return 0
        require(args.manifest is not None, "a manifest path is required")
        require(not args.rescore, "--rescore applies only to --ledger-summary")
        function_id, budget, variants = load_manifest(args.manifest)
        output_dir = args.output_dir
        if output_dir is not None:
            output_dir = output_dir.resolve()
            allowed = ((ROOT / "experiments").resolve(), (ROOT / "build").resolve())
            require(any(output_dir.is_relative_to(root) for root in allowed),
                    "output directory must be under experiments/ or build/")
        if variants and "predicted_effect" in variants[0]:
            result = evaluate_hypotheses(function_id, variants, args.cached_only, output_dir,
                                         args.ledger, args.manifest, measure_parents=args.measure_parents,
                                         budget=budget)
        else:
            require(args.ledger is None and not args.measure_parents,
                    "--ledger and --measure-parents apply only to schema_version 2 manifests")
            result = evaluate(function_id, variants, args.cached_only, output_dir)
        print(json.dumps(result, indent=2 if args.json else None, sort_keys=True))
        return 0
    except (FormatError, OSError, UnicodeError, ValueError) as exc:
        print(json.dumps(dict(status="REJECTED", reason=str(exc))), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
