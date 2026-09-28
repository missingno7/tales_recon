"""Task queue, packets and intake for parallel autonomous recovery workers.

The supervisor plans tasks from the current frontier, leases them to named
workers, writes self-contained prompt packets, and reviews results through a
re-verifying intake. Nothing here launches a worker, promotes a proof,
relocks fixtures or edits curated/generated ledgers. See docs/fleet.md.

Storage: the task list and leases are ephemeral coordination state in ignored
``build/fleet/`` (lock-protected, regenerable, per checkout). Durable outcomes
are append-only ``fleet_intake`` records in the hypothesis ledger
(``evidence/experiments/hypothesis-ledger.jsonl``); packets and worker outputs
live under ``experiments/fleet/<task_id>/``.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
import uuid

from analysis_support import ROOT
from common import FormatError, require, sha256, write_json
import file_lock


FLEET_DIR = ROOT / "build/fleet"
PACKETS = ROOT / "experiments/fleet"
CANONICAL_STATES = ("FUNCTION_CODE_MATCH", "FUNCTION_WITH_DATA_MATCH", "MODULE_MATCH", "OVERLAY_NODE_MATCH")
KINDS = ("function", "unit", "review", "blocker-probe")
RESULT_STATUSES = ("EQUAL_CANDIDATE", "NEAR", "BLOCKED", "NEEDS_EVIDENCE")
TASK_ID = re.compile(r"[A-Za-z0-9_.+-]{1,80}")
PACKET_TARGET_BYTES = 10240
PACKET_MAX_BYTES = 12288
DEFAULT_LEASE_HOURS = 6.0
BUDGETS = {"function": dict(max_compile_trials=24, max_variants_per_manifest=6),
           "blocker-probe": dict(max_compile_trials=16, max_variants_per_manifest=4),
           "unit": dict(max_compile_trials=12, max_variants_per_manifest=4),
           "review": dict(max_compile_trials=4, max_variants_per_manifest=2)}
UNIT_OPTIONS = ("separate_objects", "allow_original_gaps", "join_direct_callees", "owned_code_data")
FUNCTION_OPTIONS = ("owned_code_data", "with_m_lib")


def now_epoch():
    return time.time()


def iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat(timespec="seconds")


def rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


class Fleet:
    """File locations; tests substitute a temporary directory."""

    def __init__(self, directory=None, ledger=None, packets=None):
        self.dir = Path(directory) if directory else FLEET_DIR
        self.tasks = self.dir / "tasks.json"
        self.state = self.dir / "state.json"
        self.lock = self.dir / "state.lock"
        self.packets = Path(packets) if packets else PACKETS
        self._ledger = ledger

    def ledger(self):
        from shape_search import ledger_path
        return ledger_path(self._ledger)

    def locked(self, purpose):
        return file_lock.locked(self.lock, "fleet " + purpose, 60, "fleet state", 0.05)

    def load_tasks(self):
        require(self.tasks.is_file(), "no task file; run: python tools/fleet.py plan")
        data = json.loads(self.tasks.read_text(encoding="utf-8"))
        require(data.get("schema_version") == 1 and isinstance(data.get("tasks"), list), "malformed task file")
        return data

    def load_state(self):
        if not self.state.is_file():
            return dict(schema_version=1, leases={}, completed={}, reopened={}, history=[])
        state = json.loads(self.state.read_text(encoding="utf-8"))
        require(state.get("schema_version") == 1, "malformed fleet state")
        for key in ("leases", "completed", "reopened"):
            state.setdefault(key, {})
        state.setdefault("history", [])
        return state

    def save_state(self, state):
        state["history"] = state["history"][-300:]
        write_json(self.state, state)

    def task_dir(self, task_id):
        require(TASK_ID.fullmatch(task_id or "") is not None, "invalid task id")
        return self.packets / task_id


# ---------------------------------------------------------------------------
# Planning


def _hex_suffix(fid):
    return fid.rsplit("_", 1)[-1]


def _blocker_class(reason):
    from recovery_plan import _profile_class
    return _profile_class(reason)


UNLOCK_BOOST = 5
UNLOCK_CAP = 4
EVIDENCE_INTAKES = ("NEEDS_EVIDENCE_FOR_CURATION", "BLOCKED_FOR_CURATION")


def mentioned_functions(text, by_id):
    """Evidence ids named in free text, directly or as mechanical F_hNN_XXXX symbols."""
    text = str(text or "")
    found = {m for m in re.findall(r"\b(?:ov\d\d|resident)_F_[0-9A-F]{4}\b", text) if m in by_id}
    mechanical = {"F_h%02d_%04X" % (f.get("hunk", -1), f.get("start", -1)): fid for fid, f in by_id.items()}
    found.update(mechanical[m] for m in re.findall(r"\bF_h\d\d_[0-9A-F]{4}\b", text) if m in mechanical)
    return found


def blocking_graph(items, by_id, intakes=()):
    """{unrecovered function: functions whose recovery waits on it}.

    Edges come from the ranked frontier's pending local dependencies and from
    NEEDS_EVIDENCE/BLOCKED intake records that name a function in their
    explanation or proposed blocker.
    """
    graph = {}
    for item in items.values():
        for dep in item.get("pending_local_dependencies") or []:
            graph.setdefault(dep, set()).add(item["id"])
    for record in intakes:
        if record.get("intake_status") not in EVIDENCE_INTAKES:
            continue
        text = " ".join([str(record.get("explanation") or "")] +
                        [str(v) for v in (record.get("proposed_blocker") or {}).values()])
        targets = set(record.get("targets") or [])
        for fid in mentioned_functions(text, by_id) - targets:
            graph.setdefault(fid, set()).update(targets)
    return graph


def build_tasks(functions, ranked_items, recovery_ledger, packages, max_bytes=1024, max_review_tasks=24,
                include_abi_blockers=False, hypothesis_functions=(), intakes=()):
    """Deterministic task list from supplied ledgers (pure helper).

    Each function target appears in at most one task; canonical exact
    recoveries never become targets. Priority: lower runs first. A task whose
    recovery would unblock other non-review tasks (``unlocks``) is boosted by
    UNLOCK_BOOST per unlocked target, at most UNLOCK_CAP targets.
    """
    from recovery_plan import _constraints
    canonical = {fid for fid, item in recovery_ledger.get("functions", {}).items()
                 if item.get("state") in CANONICAL_STATES}
    blockers = recovery_ledger.get("blockers", {})
    attempts = recovery_ledger.get("attempts", {})
    by_id = {f["id"]: f for f in functions}
    items = {x["id"]: x for x in ranked_items if x["id"] not in canonical}
    tasks, assigned = [], set()

    def add(kind, task_id, targets, priority, title, origin, dependencies=(), verifier=None, notes=()):
        targets = [t for t in targets if t not in canonical]
        if not targets or any(t in assigned for t in targets):
            return None
        assigned.update(targets)
        task = dict(id=task_id, kind=kind, targets=targets, priority=priority, title=title,
                    dependencies=sorted(dependencies), origin=origin, verifier=verifier,
                    budget=dict(BUDGETS[kind]), notes=list(notes))
        tasks.append(task)
        return task

    # Same-hunk call cycles: a complete unit hypothesis, never a function claim.
    for package in packages:
        if not package["kind"].startswith("DEPENDENCY_SCC") or not package.get("members_complete"):
            continue
        members = sorted(package["members"], key=lambda fid: (by_id.get(fid, {}).get("start", 0), fid))
        task_id = "unit-" + members[0] + "".join("-" + _hex_suffix(m) for m in members[1:])
        meta = package.get("metadata", {})
        add("unit", task_id[:80], members, 10 if package["kind"] == "DEPENDENCY_SCC_HYPOTHESIS" else 30,
            "Same-hunk dependency cycle %s as one natural source-unit hypothesis" % ", ".join(members),
            dict(source="recovery_plan", package_kind=package["kind"], rationale=package.get("rationale"),
                 metadata={k: meta.get(k) for k in ("hunk", "interval", "bridge_functions", "canonical_bridge_ids",
                                                     "unknown_bridge_ids", "unclassified_gaps",
                                                     "external_unrecovered_dependencies") if k in meta},
                 blockers={m: blockers[m].get("reason", "")[:400] for m in members if m in blockers}),
            verifier="check_unit",
            notes=["Unit acceptance is complete-object check_unit; original gaps stay unclaimed.",
                   "check_unit verifies one candidate source whose other same-node callees are already canonical; "
                   "a mutual cycle cannot reach EQUAL through it alone. Report the layout evidence (unit_diag, "
                   "isolated receipts) as NEEDS_EVIDENCE/BLOCKED rather than forcing a member claim."])

    # Explicit blockers worth a new hypothesis.
    for fid in sorted(blockers):
        if fid in canonical or fid not in by_id:
            continue
        mechanism = _blocker_class(blockers[fid].get("reason"))
        if mechanism == "ABI_OR_CODEGEN_PROFILE" and not include_abi_blockers:
            continue
        add("blocker-probe", "blk-" + fid, [fid], 70 if mechanism == "ABI_OR_CODEGEN_PROFILE" else 20,
            "Probe blocker %s (%s) with a changed hypothesis" % (fid, mechanism),
            dict(source="recovery_blockers", mechanism=mechanism, reason=blockers[fid].get("reason", "")[:600],
                 next_action=blockers[fid].get("next_action")),
            verifier="check_function")

    # Near matches: retained attempts or ledger hypotheses, not blocked.
    near = sorted({fid for fid in items if fid in attempts or fid in set(hypothesis_functions)} - set(blockers))
    for fid in near:
        item = items[fid]
        rows = attempts.get(fid, [])
        best = max((a.get("mnemonic_similarity") or 0 for a in rows), default=0)
        add("function", "fn-" + fid, [fid], 15 if best >= 0.75 else 25,
            "Continue near-match %s (best mnemonic similarity %.3f over %d attempts)" % (fid, best, len(rows)),
            dict(source="attempt_ledger", attempts=len(rows), best_similarity=best,
                 constraints=_constraints(item, max_bytes, 99, 999)),
            verifier="check_function")

    def workable(item):
        return (item["extent"] == "CLOSED_CFG" and item.get("confidence") == "HIGH" and item["node"] != "resident"
                and not item.get("indirect") and item["size"] <= max_bytes and item["id"] not in blockers)

    fresh = sorted((x for x in items.values() if workable(x) and not x.get("pending_local_dependencies")),
                   key=lambda x: (x["size"], x["id"]))
    for item in fresh:
        add("function", "fn-" + item["id"], [item["id"]], 40 + item["size"] // 128,
            "Recover closed function %s (%d bytes)" % (item["id"], item["size"]),
            dict(source="ranked_frontier", constraints=_constraints(item, max_bytes, 99, 999)),
            verifier="check_function")

    # Closed dependency leaves that block other work. Every workable leaf is
    # already a task above; a leaf whose own local callees are unresolved (for
    # example a same-hunk cycle member) cannot be compiled alone and stays in
    # its unit. Leaves held back only by an excluded ABI-profile blocker are
    # reported, never silently turned into tasks.
    graph = blocking_graph(items, by_id, intakes)
    untasked_leaves = []
    for fid in sorted(graph):
        item = items.get(fid)
        blocks = sorted(graph[fid] - {fid})
        if item is None or fid in assigned or not blocks:
            continue
        closed = (item["extent"] == "CLOSED_CFG" and item.get("confidence") == "HIGH" and item["node"] != "resident"
                  and not item.get("indirect") and item["size"] <= max_bytes)
        if closed and not item.get("pending_local_dependencies"):
            untasked_leaves.append(dict(id=fid, blocks=blocks, size=item["size"],
                                        blocker_class=_blocker_class(blockers[fid].get("reason"))
                                        if fid in blockers else None))

    # Callers whose unrecovered local callees are all tasks themselves. The
    # dependency is satisfied only when those callees become canonical.
    target_task = {t: task["id"] for task in tasks for t in task["targets"]}
    for item in sorted((x for x in items.values() if workable(x) and x.get("pending_local_dependencies")),
                       key=lambda x: (x["size"], x["id"])):
        deps = item["pending_local_dependencies"]
        if all(d in target_task for d in deps):
            add("function", "fn-" + item["id"], [item["id"]], 55 + item["size"] // 128,
                "Recover %s after its local callees %s are canonical" % (item["id"], ", ".join(deps)),
                dict(source="ranked_frontier", pending_local_dependencies=deps,
                     constraints=_constraints(item, max_bytes, 99, 999)),
                dependencies=sorted({target_task[d] for d in deps}), verifier="check_function",
                notes=["check_function builds the caller+callee unit automatically once callees are canonical."])

    # Remaining frontier: bounded read-only review chunks by constraint and node.
    groups = {}
    for item in sorted(items.values(), key=lambda x: x["id"]):
        if item["id"] in assigned:
            continue
        constraints = _constraints(item, max_bytes, 1, 40)
        if not constraints:
            continue
        groups.setdefault((constraints[0], item["node"]), []).append(item["id"])
    review_order = ["UNRECOVERED_LOCAL_DEPENDENCY", "NONCONTIGUOUS_LOCAL_UNIT", "UNKNOWN_CALL_LIMIT",
                    "PC_RELATIVE_DATA_OWNERSHIP", "SIZE_LIMIT", "UNCERTAIN_EXTENT", "INDIRECT_CONTROL_FLOW",
                    "LOW_CONFIDENCE", "DATA_REFERENCE_LIMIT", "RESIDENT_DEFERRED"]
    chunks = []
    for (constraint, node), members in groups.items():
        for start in range(0, len(members), 8):
            chunks.append((review_order.index(constraint) if constraint in review_order else len(review_order),
                           node, start, constraint, members[start:start + 8]))
    chunks.sort()
    omitted = max(0, len(chunks) - max_review_tasks)
    for rank, (_, node, _, constraint, members) in enumerate(chunks[:max_review_tasks]):
        add("review", "rev-" + constraint.lower() + "-" + members[0], members, 80 + rank,
            "Review %s evidence for %d %s functions" % (constraint, len(members), node),
            dict(source="grinder_frontier", constraint=constraint, node=node,
                 constraints={m: _constraints(items[m], max_bytes, 1, 40) for m in members}))
    apply_unlocks(tasks, graph, canonical)
    tasks.sort(key=lambda t: (t["priority"], t["id"]))
    return tasks, dict(omitted_review_chunks=omitted, untasked_blocking_leaves=untasked_leaves)


def apply_unlocks(tasks, graph, canonical=()):
    """Count, per task, the other non-review task targets its recovery would unblock; boost priority."""
    target_task = {t: task for task in tasks for t in task["targets"]}
    waiting_on = {}
    for task in tasks:
        for dep in task.get("dependencies", []):
            waiting_on.setdefault(dep, set()).update(task["targets"])
    needs = {}
    for dep, dependents in graph.items():
        for fid in dependents:
            needs.setdefault(fid, set()).add(dep)
    for task in tasks:
        own = set(task["targets"])
        unlocked = set(waiting_on.get(task["id"], ()))
        for target in own:
            unlocked.update(graph.get(target, ()))
        unlocked = {u for u in unlocked - own if u not in canonical and u in target_task
                    and target_task[u]["kind"] != "review"}
        blocked_by = sorted({d for t in own for d in needs.get(t, ())} - own - set(canonical))
        task["unlocks"] = len(unlocked)
        task["unlocks_targets"] = sorted(unlocked)[:12]
        task["blocked_by"] = blocked_by[:12]
        # A task that itself waits on an unrecovered function is not boosted
        # past that function's own task.
        if unlocked and not blocked_by:
            task["base_priority"] = task["priority"]
            task["priority"] = max(1, task["priority"] - UNLOCK_BOOST * min(len(unlocked), UNLOCK_CAP))
    return tasks


def plan(fleet, max_bytes=1024, max_review_tasks=24, include_abi_blockers=False):
    from recovery_plan import build_plan
    from recovery_state import evidence, ranked, recovery
    functions = evidence()["functions"]
    items = ranked()
    rec = recovery()
    report = build_plan(functions, items, rec, limit=max_bytes, max_packages=1000)
    try:
        from shape_search import read_ledger
        records = read_ledger(fleet.ledger())
    except FormatError:
        records = []
    hyp = {r.get("function_id") for _, r in records if r["record_type"] == "trial"}
    latest = {}
    for _, r in records:
        if r["record_type"] == "fleet_intake":
            latest[r.get("task_id")] = r
    tasks, extra = build_tasks(functions, items, rec, report["packages"], max_bytes, max_review_tasks,
                               include_abi_blockers, hyp, list(latest.values()))
    frontier = dict(recovery_ledger_sha256=sha256((ROOT / "recovery/ledger.json").read_bytes()),
                    function_ledger_sha256=sha256((ROOT / "evidence/functions/ledger.json").read_bytes()))
    document = dict(schema_version=1, generated=iso(now_epoch()), frontier=frontier,
                    options=dict(max_bytes=max_bytes, max_review_tasks=max_review_tasks,
                                 include_abi_blockers=include_abi_blockers),
                    counts=dict(Counter(t["kind"] for t in tasks)), omitted=extra, tasks=tasks)
    with fleet.locked("plan"):
        write_json(fleet.tasks, document)
    return document


# ---------------------------------------------------------------------------
# Leases


def canonical_ids():
    from recovery_state import recovery
    return {fid for fid, item in recovery().get("functions", {}).items() if item.get("state") in CANONICAL_STATES}


def intake_records(fleet):
    from shape_search import read_ledger
    return [(n, r) for n, r in read_ledger(fleet.ledger()) if r["record_type"] == "fleet_intake"]


def completed_ids(fleet, state):
    done = {}
    for number, record in intake_records(fleet):
        tid = record.get("task_id")
        if tid and record.get("timestamp_epoch", 0) > state["reopened"].get(tid, 0):
            done[tid] = dict(ledger_line=number, intake_status=record.get("intake_status"))
    for tid, item in state["completed"].items():
        if item.get("at", 0) > state["reopened"].get(tid, 0):
            done.setdefault(tid, item)
    return done


def task_state(task, state, done, canonical, by_id, at):
    if task["id"] in done:
        return "completed"
    if all(t in canonical for t in task["targets"]):
        return "obsolete"
    lease = state["leases"].get(task["id"])
    if lease and lease["expires_at"] > at:
        return "leased"
    for dep in task.get("dependencies", []):
        dep_task = by_id.get(dep)
        if dep_task is None or not all(t in canonical for t in dep_task["targets"]):
            return "waiting"
    return "expired_lease" if lease else "open"


def claim(fleet, worker, kinds=None, task_id=None, lease_hours=DEFAULT_LEASE_HOURS, dry_run=False, name_for=None):
    """Atomically lease the best open task. Returns (task, lease) or (None, reason)."""
    require(worker is None or re.fullmatch(r"[A-Za-z0-9_.+-]{1,80}", worker), "invalid worker name")
    with fleet.locked("claim"):
        tasks = fleet.load_tasks()["tasks"]
        state = fleet.load_state()
        at = now_epoch()
        by_id = {t["id"]: t for t in tasks}
        if worker and not task_id:
            for tid, lease in state["leases"].items():
                if lease["worker"] == worker and lease["expires_at"] > at and tid in by_id:
                    return by_id[tid], lease
        done = completed_ids(fleet, state)
        canonical = canonical_ids()
        for task in sorted(tasks, key=lambda t: (t["priority"], t["id"])):
            if kinds and task["kind"] not in kinds:
                continue
            if task_id and task["id"] != task_id:
                continue
            status = task_state(task, state, done, canonical, by_id, at)
            if status not in ("open", "expired_lease"):
                if task_id:
                    return None, "task %s is %s" % (task_id, status)
                continue
            name = name_for(task) if name_for else worker
            lease = dict(task_id=task["id"], worker=name, lease_id=uuid.uuid4().hex[:12], claimed_at=at,
                         claimed=iso(at), expires_at=at + lease_hours * 3600,
                         expires=iso(at + lease_hours * 3600))
            if dry_run:
                return task, dict(lease, dry_run=True)
            previous = state["leases"].get(task["id"])
            state["leases"][task["id"]] = lease
            state["history"].append(dict(event="claim", task_id=task["id"], worker=name, at=iso(at),
                                         replaced_expired_lease=previous["worker"] if previous else None))
            fleet.save_state(state)
            return task, lease
    return None, "no claimable task"


def release(fleet, task_id, worker=None, force=False, note=None):
    with fleet.locked("release"):
        state = fleet.load_state()
        lease = state["leases"].get(task_id)
        require(lease is not None, "task has no lease: " + task_id)
        require(force or lease["worker"] == worker, "lease belongs to " + lease["worker"] + "; use --force")
        del state["leases"][task_id]
        state["history"].append(dict(event="release", task_id=task_id, worker=lease["worker"], note=note,
                                     at=iso(now_epoch())))
        fleet.save_state(state)
        return lease


def renew(fleet, task_id, worker, lease_hours=DEFAULT_LEASE_HOURS):
    with fleet.locked("renew"):
        state = fleet.load_state()
        lease = state["leases"].get(task_id)
        require(lease is not None and lease["worker"] == worker, "no lease held by " + worker)
        at = now_epoch()
        lease.update(expires_at=at + lease_hours * 3600, expires=iso(at + lease_hours * 3600))
        fleet.save_state(state)
        return lease


def complete(fleet, task_id, outcome, worker=None, ledger_line=None):
    with fleet.locked("complete"):
        state = fleet.load_state()
        lease = state["leases"].pop(task_id, None)
        at = now_epoch()
        state["completed"][task_id] = dict(at=at, completed=iso(at), outcome=outcome, ledger_line=ledger_line,
                                           worker=worker or (lease or {}).get("worker"))
        state["history"].append(dict(event="complete", task_id=task_id, outcome=outcome, at=iso(at)))
        fleet.save_state(state)


def reopen(fleet, task_id):
    with fleet.locked("reopen"):
        state = fleet.load_state()
        state["reopened"][task_id] = now_epoch()
        state["completed"].pop(task_id, None)
        state["history"].append(dict(event="reopen", task_id=task_id, at=iso(now_epoch())))
        fleet.save_state(state)


def status(fleet):
    with fleet.locked("status"):
        data = fleet.load_tasks()
        state = fleet.load_state()
    at = now_epoch()
    tasks = data["tasks"]
    by_id = {t["id"]: t for t in tasks}
    done = completed_ids(fleet, state)
    canonical = canonical_ids()
    table = Counter()
    rows = []
    for task in tasks:
        s = task_state(task, state, done, canonical, by_id, at)
        table[(task["kind"], s)] += 1
        if s in ("leased", "expired_lease"):
            lease = state["leases"][task["id"]]
            rows.append(dict(task_id=task["id"], state=s, worker=lease["worker"], expires=lease["expires"]))
    orphans = sorted(set(state["leases"]) - set(by_id))
    import compile_queue
    return dict(generated=data.get("generated"), counts={k + ":" + s: n for (k, s), n in sorted(table.items())},
                leases=rows, orphan_leases=orphans, completed=len([t for t in tasks if t["id"] in done]),
                compile_queue=compile_queue.status())


# ---------------------------------------------------------------------------
# Packets


def _j(value):
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _clip(text, limit):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def function_facts(fid, functions, rec, rank_item=None, max_bytes=1024):
    from recovery_plan import _constraints
    f = functions[fid]
    counted = Counter()
    for c in f.get("direct_callees", []):
        name = "F_h%02d_%04X" % (c["hunk"], c["offset"])
        state = rec.get("functions", {}).get(c.get("id"), {}).get("state", "DISCOVERED")
        counted[name + " " + c.get("basis", "?") + " " + state] += 1
    unique_calls = [k + (" x%d" % n if n > 1 else "") for k, n in counted.items()]
    calls = unique_calls[:12]
    data = sorted({"G_h%02d_%04X" % (x["hunk"], x["offset"]) for x in f.get("referenced_data", [])})
    facts = dict(id=fid, node=f.get("node"), hunk=f.get("hunk"), start="0x%04X" % f["start"], end="0x%04X" % f["end"],
                 size=f["size"], extent=f.get("extent_status"), confidence=f.get("confidence"),
                 instructions=len(f.get("instructions", [])), calls=calls,
                 more_calls=max(0, len(unique_calls) - 12), data=data[:16],
                 more_data=max(0, len(data) - 16), strings=len(f.get("referenced_strings", [])),
                 pc_relative_data=sum(x.get("kind") == "PC_RELATIVE_DATA" for x in f.get("referenced_data", [])),
                 jump_tables=len(f.get("jump_tables", [])), indirect=len(f.get("indirect_control_flow", [])))
    if rank_item:
        facts["constraints"] = _constraints(rank_item, max_bytes, 99, 999)
    return facts


def attempt_rows(fid, rec, limit=6):
    rows = rec.get("attempts", {}).get(fid) or rec.get("blockers", {}).get(fid, {}).get("attempts", [])
    out, seen = [], set()
    for a in reversed(rows):
        if len(out) >= limit:
            break
        if (a.get("cache_key"), a.get("profile")) in seen:
            continue
        seen.add((a.get("cache_key"), a.get("profile")))
        src = ROOT / "recovery/candidates" / fid / (a.get("source_sha256", "") + ".c")
        diff = a.get("first_difference") or {}
        out.append(dict(profile=a.get("profile"), verdict=a.get("verdict"), expected=a.get("expected_length"),
                        actual=a.get("actual_length"), similarity=a.get("mnemonic_similarity"),
                        first_diff=diff.get("offset") if isinstance(diff, dict) else None,
                        cache_key=a.get("cache_key"), source=rel(src) if src.is_file() else None))
    out.reverse()
    return out, len(rows)


def best_attempt(rows):
    usable = [r for r in rows if r.get("cache_key") and r.get("verdict") != "BLOCKED"]
    return max(usable, key=lambda r: (r.get("similarity") or 0, r.get("source") is not None), default=None)


def diag_summary(fid, cache_key, max_bytes=1800):
    try:
        import diag
        return diag.compact_summary(diag.diagnose(fid, cache_key), max_bytes)
    except Exception as exc:  # advisory only; never blocks a packet
        return dict(status="UNAVAILABLE", reason=_clip(exc, 200))


def compact_diag(summary):
    if summary.get("status") != "DIAGNOSTIC_ONLY":
        return summary
    keep = {k: summary.get(k) for k in ("status", "extents", "instruction_similarity", "alignment_counts",
                                        "first_nonreference_divergence", "recommended_search_scope")}
    keep["hypotheses"] = [dict(category=h.get("category"), count=h.get("count"), evidence=h.get("evidence", [])[:1])
                          for h in summary.get("hypotheses", [])][:8]
    trace = summary.get("register_trace")
    if trace:
        keep["register_trace"] = dict(first_conflict=trace.get("first_conflict"), remapped=trace.get("remapped"))
    return keep


def type_summary(fid):
    try:
        from type_evidence import function_evidence
        t = function_evidence(fid, allow_stale=True)
    except Exception as exc:
        return dict(status="UNAVAILABLE", reason=_clip(exc, 160))
    stale = dict(stale=True, stale_reason=_clip("; ".join(t["stale_reasons"]), 160)) if t.get("stale") else {}
    return dict(stale,
                globals=["G_h01_%04X w=%s rw=%s" % (g["data_hunk_offset"], g["observed_widths_bytes"],
                                                    g["program_read_write_counts"]) for g in t["globals"][:8]],
                frame=["%+d w=%s n=%d" % (p["frame_offset"], p["observed_widths_bytes"], p["access_count"])
                       for p in t["frame_accesses"][:6]],
                declaration_conflicts=t["declaration_conflict_summary"]["relevant_total"])


def ledger_history(fleet, targets, task_id, limit=12):
    try:
        from shape_search import read_ledger
        records = read_ledger(fleet.ledger())
    except FormatError as exc:
        return dict(status="UNAVAILABLE", reason=str(exc)), []
    trials = [(n, r) for n, r in records if r["record_type"] == "trial" and r.get("function_id") in targets]
    rows = [dict(line=n, fn=r.get("function_id"), variant=r.get("variant"), profile=r.get("profile"),
                 change=_clip(r.get("controlled_change"), 110), verdict=r.get("exact_verdict"),
                 prediction=(r.get("prediction") or {}).get("outcome"),
                 observed_len_delta=(r.get("observed_delta") or {}).get("length_delta"), source=r.get("source"))
            for n, r in trials[-limit:]]
    intakes = [dict(line=n, task=r.get("task_id"), status=r.get("intake_status"),
                    explanation=_clip(r.get("explanation"), 220))
               for n, r in records if r["record_type"] == "fleet_intake"
               and (r.get("task_id") == task_id or set(r.get("targets", [])) & set(targets))][-4:]
    summary = dict(trials=len(trials), shown=len(rows),
                   verdicts=dict(Counter(r.get("exact_verdict") for _, r in trials)),
                   predictions=dict(Counter((r.get("prediction") or {}).get("outcome") for _, r in trials)))
    return dict(summary=summary, trials=rows), intakes


def unit_receipts(members, limit=4):
    rows = []
    for fid in members:
        for path in (ROOT / "recovery/units" / fid).glob("*/*/receipt.json"):
            try:
                receipt = json.loads(path.read_text())
            except (OSError, ValueError):
                continue
            rows.append((path.stat().st_mtime, dict(entry=fid, verdict=receipt.get("verdict"),
                                                     reason=receipt.get("reason"), cache_key=receipt.get("cache_key"),
                                                     expected=receipt.get("expected_length"),
                                                     actual=receipt.get("actual_length"), receipt=rel(path))))
    rows.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in rows[:limit]]


def unit_diag_summary(members, receipt, max_bytes=1800):
    try:
        import unit_diag
        report = unit_diag.diagnose_unit(members, receipt["cache_key"], entry_member=receipt["entry"])
        return unit_diag.compact_summary(report, max_bytes)
    except Exception as exc:
        return dict(status="UNAVAILABLE", reason=_clip(exc, 200))


LIVENESS = """## First step (host liveness)
Run `python tools/fleet.py renew {task_id} --worker {worker}` before anything else. If the shell does not return within about two minutes, or keeps failing to start commands, stop immediately and reply with one line: `TASK {task_id} BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).
"""

RULES = """## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `{dir}/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.
"""

PROTOCOL = """## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md{unit_doc}.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. {record}
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: {run}
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most {trials} compiler trials and {variants} variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `{dir}/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake {task_id} --dry-run`, fix any REJECTED reason, then reply with one line: `TASK {task_id} <STATUS> {dir}/result.json`.
"""

RESULT_SCHEMA = """## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{{"schema_version":1,"task_id":"{task_id}","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"{target}",
 "best":null or {{"source":"{dir}/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"{verifier}","entry":"<evidence id of the member compiled as recovered(), e.g. {target}>",
   "options":[{options}],"expected_length":0,"actual_length":0}},
 "hypotheses":[{{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {{"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
"""


def _task_body(fleet, task, rec, functions, rank):
    """Return ordered (name, text, optional) packet sections."""
    sections = []
    targets = task["targets"]
    origin = task.get("origin", {})
    # Blocker text is rendered once, in its own section below.
    shown = {k: v for k, v in origin.items() if k not in ("reason", "blockers", "next_action")}
    sections.append(("origin", "## Origin\n`" + _j(shown)[:1400] + "`\n", False))
    facts = [function_facts(fid, functions, rec, rank.get(fid)) for fid in targets if fid in functions]
    if task["kind"] == "review":
        compact = [dict(id=x["id"], node=x["node"], start=x["start"], size=x["size"], extent=x["extent"],
                        confidence=x["confidence"], calls=len(x["calls"]) + x["more_calls"],
                        data=len(x["data"]) + x["more_data"], indirect=x["indirect"],
                        constraints=x.get("constraints")) for x in facts]
        sections.append(("facts", "## Members\n" + "\n".join("- `" + _j(x) + "`" for x in compact) + "\n", False))
    else:
        sections.append(("facts", "## Target facts\n" + "\n".join("- `" + _j(x) + "`" for x in facts) + "\n", False))
    history, intakes = ledger_history(fleet, targets, task["id"])
    optional = []
    for fid in targets if task["kind"] != "review" else []:
        rows, total = attempt_rows(fid, rec)
        blocker = rec.get("blockers", {}).get(fid)
        if blocker:
            sections.append(("blocker-" + fid, "## Recorded blocker %s\n%s\nNext action: %s\n" % (
                fid, _clip(blocker.get("reason"), 700), _clip(blocker.get("next_action"), 160)), False))
        if rows:
            sections.append(("attempts-" + fid, "## Prior verifier attempts %s (%d total, latest %d)\n" % (fid, total, len(rows)) +
                             "\n".join("- `" + _j(r) + "`" for r in rows) + "\n", False))
            best = best_attempt(rows)
            if best and task["kind"] != "unit":
                optional.append(("diag-" + fid, "## Cached diagnostic of best attempt %s (advisory)\nkey `%s`\n`%s`\n" % (
                    fid, best["cache_key"], _j(compact_diag(diag_summary(fid, best["cache_key"]))))))
        optional.append(("types-" + fid, "## Type evidence %s (advisory)\n`%s`\n" % (fid, _j(type_summary(fid)))))
    if task["kind"] == "unit":
        receipts = unit_receipts(targets)
        if receipts:
            sections.append(("unit-receipts", "## Prior unit receipts\n" + "\n".join("- `" + _j(r) + "`" for r in receipts) + "\n", False))
            optional.insert(0, ("unit-diag", "## unit_diag of latest receipt (advisory)\n`%s`\n" % _j(unit_diag_summary(targets, receipts[0]))))
    sections.append(("ledger", "## Prior hypotheses (do not repeat)\n`" + _j(history) + "`\n" +
                     ("Prior fleet outcomes: `" + _j(intakes) + "`\n" if intakes else ""), False))
    return sections, optional


def render_packet(fleet, task, lease=None, rec=None, functions=None, rank=None):
    from recovery_state import evidence, ranked, recovery
    rec = recovery() if rec is None else rec
    functions = {f["id"]: f for f in evidence()["functions"]} if functions is None else functions
    rank = {x["id"]: x for x in ranked()} if rank is None else rank
    directory = rel(fleet.task_dir(task["id"]))
    budget = task["budget"]
    target = task["targets"][0] if len(task["targets"]) == 1 else ",".join(task["targets"])
    verifier = task.get("verifier") or "check_function"
    if task["kind"] == "unit":
        record = ("Append one JSON line per hypothesis to `%s/hypotheses.jsonl`: "
                  "{\"id\",\"parent\",\"suspected_cause\",\"controlled_change\",\"prediction\"} with a concrete length/diff prediction. "
                  "Unit member sources: copy candidates into `%s/` and edit there." % (directory, directory))
        run = ("`python tools/fleet.py verify-unit ENTRY %s/<unit>.c --profile aztec36 [--separate-objects] "
               "[--allow-original-gaps] [--join-direct-callees] --output-dir %s/runs` (always isolated); "
               "diagnose with `python tools/unit_diag.py --members A,B --entry ENTRY --cache-key KEY`." % (directory, directory))
        options = "\"separate_objects\",\"allow_original_gaps\",\"join_direct_callees\",\"owned_code_data\""
        unit_doc = ", docs/unit-diagnostics.md"
    else:
        record = ("Write a schema v2 manifest `%s/manifest-NN.json` (docs/source-shape-search.md): every variant has "
                  "parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, "
                  "register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); "
                  "parent `none` leaves every prediction unmeasurable. Sources: `%s/*.c` (self-contained K&R C defining `recovered(...)`, "
                  "mechanical G_hNN_XXXX/F_hNN_XXXX externs)." % (directory, directory))
        run = ("`python tools/shape_search.py %s/manifest-NN.json --output-dir %s/runs --json` (isolated; records the "
               "ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P "
               "[--owned-code-data] [--with-m-lib] --output-dir %s/runs`." % (directory, directory, directory))
        options = "\"owned_code_data\",\"with_m_lib\""
        unit_doc = ""
    head = ["# Fleet task %s (%s)\n" % (task["id"], task["kind"]),
            "You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `%s`. "
            "You have no memory beyond this prompt. %s\n" % (ROOT.as_posix(), task["title"]),
            "Priority %s. Lease: %s.\n" % (task["priority"], ("worker `%s`, expires %s (renew: `python tools/fleet.py renew %s --worker %s`)"
                                                             % (lease["worker"], lease["expires"], task["id"], lease["worker"]))
                                          if lease else "none recorded"),
            LIVENESS.format(task_id=task["id"], worker=lease["worker"] if lease else "<your -n name>"),
            RULES.format(dir=directory)]
    if task["kind"] == "review":
        head.append("## Review task\nRead-only evidence review of the members below. Do not compile unless one member "
                    "becomes a concrete bounded source hypothesis (then use the function protocol, max %d trials). "
                    "Report NEEDS_EVIDENCE with the precise missing evidence per member, or BLOCKED with a mechanism.\n"
                    % budget["max_compile_trials"])
    tail = [PROTOCOL.format(unit_doc=unit_doc, record=record, run=run, trials=budget["max_compile_trials"],
                            variants=budget["max_variants_per_manifest"], dir=directory, task_id=task["id"]),
            RESULT_SCHEMA.format(task_id=task["id"], dir=directory, target=target, verifier=verifier, options=options)]
    sections, optional = _task_body(fleet, task, rec, functions, rank)
    for note in task.get("notes", []):
        sections.append(("note", "Note: " + note + "\n", False))

    def assemble(opt):
        return "\n".join(head + [s[1] for s in sections] + [o[1] for o in opt] + tail)
    text = assemble(optional)
    # Drop advisory sections (diagnostics first) until the packet is small.
    while len(text.encode("utf-8")) > PACKET_TARGET_BYTES and optional:
        optional.pop(0)
        text = assemble(optional)
    if len(text.encode("utf-8")) > PACKET_MAX_BYTES:
        sections = [(n, t[:1500] + ("...\n" if len(t) > 1500 else ""), o) for n, t, o in sections]
        text = assemble(optional)
    require(len(text.encode("utf-8")) <= PACKET_MAX_BYTES, "packet exceeds %d bytes" % PACKET_MAX_BYTES)
    return text


def find_task(fleet, task_id):
    try:
        tasks = fleet.load_tasks()["tasks"]
        task = next((t for t in tasks if t["id"] == task_id), None)
    except FormatError:
        task = None
    if task is None:
        saved = fleet.task_dir(task_id) / "task.json"
        require(saved.is_file(), "unknown task " + task_id)
        task = json.loads(saved.read_text(encoding="utf-8"))["task"]
    return task


def write_packet(fleet, task_id):
    task = find_task(fleet, task_id)
    with fleet.locked("packet"):
        lease = fleet.load_state()["leases"].get(task_id)
    text = render_packet(fleet, task, lease)
    directory = fleet.task_dir(task_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "PROMPT.md").write_text(text, encoding="utf-8", newline="\n")
    write_json(directory / "task.json", dict(schema_version=1, task=task, lease=lease))
    return directory / "PROMPT.md", len(text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Intake


RESULT_KEYS = {"schema_version", "task_id", "worker", "status", "target", "best", "hypotheses", "compile_trials",
               "ledger_lines", "explanation", "proposed_blocker"}
BEST_KEYS = {"source", "profile", "cache_key", "verdict", "verifier", "entry", "options", "expected_length",
             "actual_length"}


def validate_result(fleet, task, result):
    """Closed-schema validation; returns a normalized copy or raises FormatError."""
    from compiler_oracle import PROFILES
    require(isinstance(result, dict) and set(result) == RESULT_KEYS,
            "result.json keys must be exactly " + ", ".join(sorted(RESULT_KEYS)))
    require(result["schema_version"] == 1, "result schema_version must be 1")
    require(result["task_id"] == task["id"], "result task_id does not match")
    require(isinstance(result["worker"], str) and 0 < len(result["worker"]) <= 80, "worker must be text")
    require(result["status"] in RESULT_STATUSES, "status must be one of " + ", ".join(RESULT_STATUSES))
    targets = result["target"].split(",") if isinstance(result["target"], str) else result["target"]
    require(isinstance(targets, list) and set(targets) == set(task["targets"]), "target does not match the task")
    require(isinstance(result["explanation"], str) and 0 < len(result["explanation"]) <= 4000,
            "explanation must be 1..4000 characters")
    require(type(result["compile_trials"]) is int and 0 <= result["compile_trials"] <= 1000,
            "compile_trials must be a nonnegative integer")
    require(isinstance(result["ledger_lines"], list) and all(type(x) is int and x > 0 for x in result["ledger_lines"]),
            "ledger_lines must be positive integers")
    require(isinstance(result["hypotheses"], list) and len(result["hypotheses"]) <= 64, "hypotheses must be a list")
    for h in result["hypotheses"]:
        require(isinstance(h, dict) and set(h) == {"id", "statement", "outcome", "evidence"},
                "each hypothesis needs exactly id, statement, outcome, evidence")
        require(h["outcome"] in ("confirmed", "refuted", "partial", "unmeasurable", "untested"),
                "hypothesis outcome is unsupported")
        require(all(isinstance(h[k], str) for k in ("id", "statement", "evidence")), "hypothesis fields must be text")
    blocker = result["proposed_blocker"]
    if blocker is not None:
        require(isinstance(blocker, dict) and set(blocker) == {"mechanism", "text"}, "proposed_blocker needs mechanism, text")
        require(re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", blocker["mechanism"] or "") is not None,
                "proposed_blocker.mechanism must be UPPER_SNAKE_CASE")
        require(isinstance(blocker["text"], str) and 0 < len(blocker["text"]) <= 2000, "proposed_blocker.text 1..2000 chars")
    best = result["best"]
    if best is not None:
        require(isinstance(best, dict) and set(best) == BEST_KEYS, "best keys must be exactly " + ", ".join(sorted(BEST_KEYS)))
        path = (ROOT / best["source"]).resolve() if isinstance(best["source"], str) else None
        require(path is not None and "\\" not in best["source"] and path.is_relative_to(fleet.task_dir(task["id"]).resolve())
                and path.suffix == ".c" and path.is_file(), "best.source must be an existing .c file in the task directory")
        require(best["profile"] in PROFILES, "best.profile is not a compiler profile")
        require(isinstance(best["cache_key"], str) and re.fullmatch(r"[0-9a-f]{64}", best["cache_key"]) is not None,
                "best.cache_key must be 64 lowercase hex")
        require(best["verdict"] in ("EQUAL", "DIFFER", "BLOCKED"), "best.verdict must be EQUAL, DIFFER or BLOCKED")
        require(best["verifier"] in ("check_function", "check_unit"), "best.verifier must be check_function or check_unit")
        if best["entry"] == "recovered" and best["verifier"] == "check_function" and len(task["targets"]) == 1:
            # Workers name the C entry symbol; for a single-target function
            # task that unambiguously denotes the target itself.
            best["entry"] = task["targets"][0]
        require(best["entry"] in task["targets"], "best.entry must be one of the task targets (evidence id, not the C symbol)")
        allowed = UNIT_OPTIONS if best["verifier"] == "check_unit" else FUNCTION_OPTIONS
        require(isinstance(best["options"], list) and set(best["options"]) <= set(allowed)
                and len(set(best["options"])) == len(best["options"]), "best.options must be a subset of " + ", ".join(allowed))
        for key in ("expected_length", "actual_length"):
            require(best[key] is None or type(best[key]) is int, "best." + key + " must be an integer or null")
    if result["status"] == "EQUAL_CANDIDATE":
        require(best is not None and best["verdict"] == "EQUAL", "EQUAL_CANDIDATE requires best.verdict EQUAL")
    if result["status"] == "NEAR":
        require(best is not None, "NEAR requires best")
    if result["status"] == "BLOCKED":
        require(blocker is not None, "BLOCKED requires proposed_blocker")
    return dict(result, target=targets)


def reverify(fleet, task, best):
    """Re-run the isolated exact verifier; the worker's verdict is never trusted."""
    import compile_queue
    compile_queue.install()
    output = fleet.task_dir(task["id"]) / "intake"
    source = ROOT / best["source"]
    options = set(best["options"])
    if best["verifier"] == "check_unit":
        import check_unit
        reports = check_unit.check(best["entry"], source, [best["profile"]], False, "owned_code_data" in options,
                                   "separate_objects" in options, "allow_original_gaps" in options,
                                   "join_direct_callees" in options, isolated=True, output_dir=output)
    else:
        import check_function
        request = dict(id=best["entry"], source=str(source), profiles=[best["profile"]],
                       owned_code_data="owned_code_data" in options)
        if "with_m_lib" in options:
            request["extra_libraries"] = ["m.lib"]
        reports = check_function.check_many([request], promote_equal=False, isolated=True, output_dir=output)
    require(len(reports) == 1, "verifier returned an unexpected report count")
    report = reports[0]
    return dict(verdict=report.get("verdict"), reason=report.get("reason"), cache_key=report.get("cache_key"),
                cache_hit=report.get("cache_hit"), matches_claimed_cache_key=report.get("cache_key") == best["cache_key"],
                expected_length=report.get("expected_length"), actual_length=report.get("actual_length"),
                output_dir=rel(output))


def promote_command(best):
    options = set(best["options"])
    if best["verifier"] == "check_unit":
        flags = "".join(" --" + o.replace("_", "-") for o in UNIT_OPTIONS if o in options)
        return "python tools/check_unit.py %s %s --profile %s%s" % (best["entry"], best["source"], best["profile"], flags)
    flags = (" --owned-code-data" if "owned_code_data" in options else "") + (" --with-m-lib" if "with_m_lib" in options else "")
    return "python tools/check_function.py %s %s --profile %s%s" % (best["entry"], best["source"], best["profile"], flags)


def intake(fleet, task_id, verify_near=False, record=True, verifier=reverify):
    task = find_task(fleet, task_id)
    path = fleet.task_dir(task_id) / "result.json"
    require(path.is_file(), "missing " + rel(path))
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise FormatError("result.json is not valid JSON: " + str(exc)) from exc
    result = validate_result(fleet, task, raw)
    best = result["best"]
    verification = None
    if best is not None and (result["status"] == "EQUAL_CANDIDATE" or verify_near):
        verification = verifier(fleet, task, best)
    status = result["status"]
    if status == "EQUAL_CANDIDATE":
        intake_status = "CONFIRMED_EQUAL" if verification and verification["verdict"] == "EQUAL" else "EQUAL_CLAIM_REJECTED"
    else:
        intake_status = dict(NEAR="NEAR_RECORDED", BLOCKED="BLOCKED_FOR_CURATION",
                             NEEDS_EVIDENCE="NEEDS_EVIDENCE_FOR_CURATION")[status]
        if verification and verification["verdict"] == "EQUAL":
            intake_status = "UNCLAIMED_EQUAL_FOUND"
    canonical = canonical_ids()
    command = None
    if intake_status in ("CONFIRMED_EQUAL", "UNCLAIMED_EQUAL_FOUND"):
        from recovery_state import recovery
        entry = recovery().get("functions", {}).get(best["entry"])
        source_hash = sha256((ROOT / best["source"]).read_bytes())
        if entry and entry.get("state") in CANONICAL_STATES and entry.get("source_sha256") == source_hash:
            command = None
        else:
            command = promote_command(best)
    stamp = now_epoch()
    entry = dict(ledger_schema=1, record_type="fleet_intake", timestamp=iso(stamp), timestamp_epoch=stamp,
                 function_id=task["targets"][0], task_id=task_id, kind=task["kind"], targets=task["targets"],
                 worker=result["worker"], claimed_status=status, intake_status=intake_status,
                 best=best, verification=verification, compile_trials=result["compile_trials"],
                 ledger_lines=result["ledger_lines"][:64],
                 hypotheses=[dict(id=_clip(h["id"], 40), outcome=h["outcome"], statement=_clip(h["statement"], 200))
                             for h in result["hypotheses"][:16]],
                 explanation=_clip(result["explanation"], 1200), proposed_blocker=result["proposed_blocker"],
                 already_canonical=[t for t in task["targets"] if t in canonical],
                 promote_command=command, promotion="NONE_SUPERVISOR_REVIEW_REQUIRED")
    line = None
    if record:
        from shape_search import append_ledger
        line = append_ledger(fleet.ledger(), [entry])[0]
        complete(fleet, task_id, intake_status, result["worker"], line)
    curation = None
    if status in ("BLOCKED", "NEEDS_EVIDENCE"):
        curation = dict(for_docs_blockers_json=True, written=False, task=task_id, targets=task["targets"],
                        mechanism=(result["proposed_blocker"] or {}).get("mechanism"),
                        text=(result["proposed_blocker"] or {}).get("text"),
                        explanation=_clip(result["explanation"], 600))
    return dict(task_id=task_id, intake_status=intake_status, verification=verification, ledger_line=line,
                promote_command=command, blocker_curation=curation, already_canonical=entry["already_canonical"],
                note="Nothing was promoted. Review the source, then run promote_command yourself if accepted.")


def intake_all(fleet, verify_near=False, record=True, verifier=reverify):
    """Intake every task directory holding a result.json that has not been taken in yet."""
    with fleet.locked("intake-all"):
        state = fleet.load_state()
    taken = {}
    for _, r in intake_records(fleet):
        tid = r.get("task_id")
        if tid and r.get("timestamp_epoch", 0) > state["reopened"].get(tid, 0):
            taken[tid] = max(taken.get(tid, 0), r.get("timestamp_epoch", 0))
    for tid, item in state["completed"].items():
        if item.get("at", 0) > state["reopened"].get(tid, 0):
            taken[tid] = max(taken.get(tid, 0), item["at"])
    groups = dict(confirmed_equal=[], unclaimed_equal=[], near=[], needs_evidence=[], blocked=[], rejected=[],
                  already_intaken=[], changed_after_intake=[])
    directories = sorted(p for p in fleet.packets.iterdir() if p.is_dir()) if fleet.packets.is_dir() else []
    for directory in directories:
        path = directory / "result.json"
        tid = directory.name
        if not path.is_file() or TASK_ID.fullmatch(tid) is None:
            continue
        if tid in taken:
            key = "changed_after_intake" if path.stat().st_mtime > taken[tid] + 1 else "already_intaken"
            groups[key].append(dict(task=tid, note="reopen the task, then intake it" if key != "already_intaken" else None))
            continue
        try:
            out = intake(fleet, tid, verify_near, record, verifier)
        except (FormatError, OSError, ValueError) as exc:
            groups["rejected"].append(dict(task=tid, reason=_clip(exc, 300)))
            continue
        row = dict(task=tid, intake_status=out["intake_status"], ledger_line=out["ledger_line"])
        status = out["intake_status"]
        if status == "CONFIRMED_EQUAL":
            groups["confirmed_equal"].append(dict(row, promote_command=out["promote_command"],
                                                  already_canonical=out["already_canonical"]))
        elif status == "UNCLAIMED_EQUAL_FOUND":
            groups["unclaimed_equal"].append(dict(row, promote_command=out["promote_command"]))
        elif status == "EQUAL_CLAIM_REJECTED":
            v = out["verification"] or {}
            groups["rejected"].append(dict(row, reason="re-verification verdict %s: %s" % (v.get("verdict"),
                                                                                           _clip(v.get("reason"), 200))))
        elif status == "NEAR_RECORDED":
            groups["near"].append(row)
        else:
            curation = out["blocker_curation"] or {}
            groups["needs_evidence" if status == "NEEDS_EVIDENCE_FOR_CURATION" else "blocked"].append(
                dict(row, mechanism=curation.get("mechanism"), explanation=curation.get("explanation")))
    counts = {k: len(v) for k, v in groups.items()}
    return dict(counts=counts, recorded=record, promotion="NONE_SUPERVISOR_REVIEW_REQUIRED", **groups)


# ---------------------------------------------------------------------------
# Launch plan and verifier wrappers


CX_DEFAULT = "~/.codex-dashboard/cx.py"
HOST_MAX_DEFAULT = 20
REPO_MAX_DEFAULT = 6
PS_UTF8 = "$OutputEncoding = [Console]::InputEncoding = [Text.UTF8Encoding]::new($false)"


def parse_cx_ps(text, project=None):
    """(running workers host-wide, running in this repository) from `cx ps` output."""
    project = project or ROOT.name
    total = here = 0
    for line in (text or "").splitlines():
        m = re.search(r"\sup\s+\S+\s+idle\s+\S+\s+cmds-failed\s+\d+/\d+\s+(\S+)", line)
        if m:
            total += 1
            here += m.group(1) == project
    return total, here


def running_workers(cx=CX_DEFAULT, timeout=45, runner=None):
    """Count running cx workers. Returns dict(total, here, status, detail)."""
    import os
    import subprocess
    path = Path(os.path.expanduser(cx))
    if not path.is_file():
        return dict(total=None, here=None, status="CX_MISSING", detail="cx not found at " + str(path))
    try:
        proc = (runner or subprocess.run)([sys.executable, str(path), "ps"], capture_output=True, text=True,
                                          encoding="utf-8", errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return dict(total=None, here=None, status="CX_PS_FAILED", detail=_clip(exc, 200))
    if proc.returncode != 0:
        return dict(total=None, here=None, status="CX_PS_FAILED",
                    detail="exit %s: %s" % (proc.returncode, _clip(proc.stderr or proc.stdout, 200)))
    total, here = parse_cx_ps(proc.stdout)
    return dict(total=total, here=here, status="COUNTED", detail=None)


def host_cap(count, workers, leased_here=0, env=None):
    """Cap a launch count by host-wide and per-repository worker limits; returns (n, reasons)."""
    import os
    env = os.environ if env is None else env
    host_max = int(env.get("TALES_FLEET_HOST_MAX", HOST_MAX_DEFAULT))
    repo_max = int(env.get("TALES_FLEET_MAX", REPO_MAX_DEFAULT))
    reasons = []
    if workers["status"] == "CX_PS_FAILED":
        return 0, ["host guard: could not count running workers (%s); launching nothing. Retry, or pass "
                   "--no-host-guard after checking the host yourself." % workers["detail"]]
    n = count
    if workers["status"] == "CX_MISSING":
        reasons.append("host guard: %s; host-wide count skipped, repository count uses %d live lease(s)"
                       % (workers["detail"], leased_here))
        here = leased_here
    else:
        here = workers["here"]
        host_room = max(0, host_max - workers["total"])
        if host_room < n:
            reasons.append("host guard: %d cx workers running host-wide, TALES_FLEET_HOST_MAX=%d -> at most %d"
                           % (workers["total"], host_max, host_room))
        n = min(n, host_room)
    repo_room = max(0, repo_max - here)
    if repo_room < n:
        reasons.append("host guard: %d running for %s, TALES_FLEET_MAX=%d -> at most %d"
                       % (here, ROOT.name, repo_max, repo_room))
    n = min(n, repo_room)
    return n, reasons


def launch_plan(fleet, count, kinds=None, prefix="luna", model="gpt-6-luna", effort="xhigh",
                lease_hours=DEFAULT_LEASE_HOURS, dry_run=False, cx=CX_DEFAULT, guard=True, workers=None, env=None):
    lines, claimed, commands, ps_commands = [], [], [], []
    if guard:
        if workers is None:
            workers = running_workers(cx)
        with fleet.locked("launch-plan"):
            state = fleet.load_state()
        leased_here = sum(1 for lease in state["leases"].values() if lease["expires_at"] > now_epoch())
        capped, reasons = host_cap(count, workers, leased_here, env)
        lines.extend("# " + r for r in reasons)
        if workers["status"] == "COUNTED":
            lines.append("# host: %d cx workers running, %d in %s; launching %d of %d requested"
                         % (workers["total"], workers["here"], ROOT.name, capped, count))
        count = capped
    ps_cx = cx.replace("~/", "$HOME/", 1) if cx.startswith("~/") else cx
    for _ in range(count):
        task, lease = claim(fleet, None, kinds, lease_hours=lease_hours, dry_run=dry_run,
                            name_for=lambda t: (prefix + "-" + t["id"])[:80])
        if task is None:
            lines.append("# no further claimable task: " + str(lease))
            break
        if dry_run:
            # A dry run does not lease, so the next peek would return the same task.
            lines.append("# would claim %s (%s, priority %s)" % (task["id"], task["kind"], task["priority"]))
            break
        packet, size = write_packet(fleet, task["id"])
        claimed.append(task["id"])
        args = "run -n %s -C %s -m %s -e %s" % (lease["worker"], ROOT.as_posix(), model, effort)
        commands.append("python %s %s < %s   # %s, %d bytes" % (cx, args, rel(packet), task["kind"], size))
        ps_commands.append("Get-Content -Raw -Encoding UTF8 %s | python %s %s" % (rel(packet), ps_cx, args))
    lines.extend(commands)
    if ps_commands:
        # Windows PowerShell 5.1 has no `<` redirection and pipes text to native
        # programs in $OutputEncoding (a BOM or ASCII by default), and does not
        # expand `~` in native arguments. Set BOM-less UTF-8 once per session.
        lines.append("# PowerShell equivalents (run the first line once per session):")
        lines.append(PS_UTF8)
        lines.extend(ps_commands)
    return lines, claimed


def _run_wrapped(module_name, argv):
    import compile_queue
    compile_queue.install()
    forbidden = {"--no-promote", "--replace-canonical", "--batch"}
    require(not forbidden.intersection(argv), "wrapper runs are always isolated; do not pass " + ", ".join(sorted(forbidden)))
    module = __import__(module_name)
    saved = sys.argv
    sys.argv = [module_name + ".py"] + list(argv) + ["--isolated"]
    try:
        return module.main()
    finally:
        sys.argv = saved


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fleet-dir", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--packets-dir", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--ledger", help="hypothesis ledger (default evidence/experiments/hypothesis-ledger.jsonl)")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan", help="regenerate build/fleet/tasks.json from the current frontier")
    p.add_argument("--max-bytes", type=int, default=1024)
    p.add_argument("--max-review-tasks", type=int, default=24)
    p.add_argument("--include-abi-blockers", action="store_true")
    p = sub.add_parser("claim", help="atomically lease the next task")
    p.add_argument("--worker", required=True); p.add_argument("--kind", action="append", choices=KINDS)
    p.add_argument("--task"); p.add_argument("--lease-hours", type=float, default=DEFAULT_LEASE_HOURS)
    for name in ("release", "complete", "renew", "reopen"):
        p = sub.add_parser(name)
        p.add_argument("task")
        if name != "reopen":
            p.add_argument("--worker")
        if name == "release":
            p.add_argument("--force", action="store_true"); p.add_argument("--note")
        if name == "complete":
            p.add_argument("--outcome", required=True)
        if name == "renew":
            p.add_argument("--lease-hours", type=float, default=DEFAULT_LEASE_HOURS)
    sub.add_parser("status")
    p = sub.add_parser("packet", help="write experiments/fleet/<task>/PROMPT.md")
    p.add_argument("task")
    p = sub.add_parser("intake", help="validate and re-verify a worker result; never promotes")
    p.add_argument("task"); p.add_argument("--verify-near", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="validate/verify without recording or completing")
    p = sub.add_parser("intake-all", help="intake every task with a result.json not yet taken in; never promotes")
    p.add_argument("--verify-near", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="validate/verify without recording or completing")
    p = sub.add_parser("launch-plan", help="claim N tasks, write packets, print cx commands (launches nothing)")
    p.add_argument("count", type=int); p.add_argument("--kind", action="append", choices=KINDS)
    p.add_argument("--prefix", default="luna"); p.add_argument("--model", default="gpt-6-luna")
    p.add_argument("--effort", default="xhigh"); p.add_argument("--lease-hours", type=float, default=DEFAULT_LEASE_HOURS)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-host-guard", action="store_true",
                   help="skip the cx ps worker count (TALES_FLEET_HOST_MAX/TALES_FLEET_MAX caps)")
    p.add_argument("--cx", default=CX_DEFAULT, help="path to cx.py (default %(default)s)")
    for name in ("verify-function", "verify-unit"):
        p = sub.add_parser(name, help="isolated check_%s run through the compile queue" % name.split("-")[1])
        p.add_argument("args", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    if args.packets_dir is not None:
        packets = args.packets_dir.resolve()
        require(packets.is_relative_to((ROOT / "experiments").resolve()) or packets.is_relative_to((ROOT / "build").resolve()),
                "--packets-dir must be under experiments/ or build/")
    fleet = Fleet(args.fleet_dir, args.ledger, args.packets_dir and args.packets_dir.resolve())
    try:
        if args.command == "plan":
            doc = plan(fleet, args.max_bytes, args.max_review_tasks, args.include_abi_blockers)
            print(_j(dict(tasks=len(doc["tasks"]), counts=doc["counts"], omitted=doc["omitted"], path=rel(fleet.tasks))))
        elif args.command == "claim":
            task, lease = claim(fleet, args.worker, args.kind, args.task, args.lease_hours)
            if task is None:
                print(_j(dict(status="NONE", reason=lease)))
                return 1
            print(_j(dict(status="LEASED", task=task, lease=lease)))
        elif args.command == "release":
            print(_j(dict(status="RELEASED", lease=release(fleet, args.task, args.worker, args.force, args.note))))
        elif args.command == "complete":
            complete(fleet, args.task, args.outcome, args.worker)
            print(_j(dict(status="COMPLETED", task=args.task)))
        elif args.command == "renew":
            print(_j(dict(status="RENEWED", lease=renew(fleet, args.task, args.worker, args.lease_hours))))
        elif args.command == "reopen":
            reopen(fleet, args.task)
            print(_j(dict(status="REOPENED", task=args.task)))
        elif args.command == "status":
            print(json.dumps(status(fleet), indent=2, sort_keys=True))
        elif args.command == "packet":
            path, size = write_packet(fleet, args.task)
            print(_j(dict(packet=rel(path), bytes=size)))
        elif args.command == "intake":
            print(json.dumps(intake(fleet, args.task, args.verify_near, not args.dry_run), indent=2, sort_keys=True))
        elif args.command == "intake-all":
            print(json.dumps(intake_all(fleet, args.verify_near, not args.dry_run), indent=2, sort_keys=True))
        elif args.command == "launch-plan":
            lines, _ = launch_plan(fleet, args.count, args.kind, args.prefix, args.model, args.effort,
                                   args.lease_hours, args.dry_run, args.cx, not args.no_host_guard)
            print("\n".join(lines))
        elif args.command in ("verify-function", "verify-unit"):
            module = "check_function" if args.command == "verify-function" else "check_unit"
            return _run_wrapped(module, [a for a in args.args if a != "--"])
        return 0
    except (FormatError, OSError, ValueError) as exc:
        print(_j(dict(status="REJECTED", reason=str(exc))), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
