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
KINDS = ("function", "unit", "region", "review", "blocker-probe")
RESULT_STATUSES = ("EQUAL_CANDIDATE", "NEAR", "BLOCKED", "NEEDS_EVIDENCE")
TASK_ID = re.compile(r"[A-Za-z0-9_.+-]{1,80}")
PACKET_TARGET_BYTES = 10240
PACKET_MAX_BYTES = 12288
DEFAULT_LEASE_HOURS = 6.0
DECLARATIONS_SIDECAR = "canonical-declarations.h"
# Fallback clipping when a packet exceeds PACKET_MAX_BYTES: history and notes
# first (full copies live in the ledger and task.json), then every section.
CLIP_STEPS = (("ledger", 700), ("note", 320), ("decls", 420), (None, 1500), (None, 1000), (None, 700))
BUDGETS = {"function": dict(max_compile_trials=24, max_variants_per_manifest=6),
           "blocker-probe": dict(max_compile_trials=16, max_variants_per_manifest=4),
           "unit": dict(max_compile_trials=12, max_variants_per_manifest=4),
           "region": dict(max_compile_trials=40, max_variants_per_manifest=4),
           "review": dict(max_compile_trials=4, max_variants_per_manifest=2)}
UNIT_OPTIONS = ("separate_objects", "allow_original_gaps", "join_direct_callees", "owned_code_data", "natural_interval")
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


def region_tasks(regions, canonical):
    """Region task dicts (targets = new members); member tasks are marked separately."""
    out = []
    for region in regions:
        targets = [t for t in region["new_members"] if t not in canonical]
        if len(targets) < 2:
            continue
        deferred = []
        if region["oversized"]:
            deferred.append("OVERSIZED_REGION")
        if region.get("node") == "resident":
            deferred.append("RESIDENT_DEFERRED")
        if not region.get("members_well_bounded", True):
            deferred.append("MEMBER_EXTENT_UNCERTAIN")
        notes = []
        if "natural_interval" in region["options"]:
            notes.append("check_unit --natural-interval %s links every function of the interval in address order "
                         "(canonical members from their canonical sources, as regression checks that must stay EQUAL) "
                         "plus %d canonical callees outside it. Unknown gaps stay unclaimed; a PC-relative reference "
                         "crossing a gap or unlinked span whose displacement class could change BLOCKS the unit "
                         "(GAP_DEPENDENT_ENCODING). `verify-region --prepare-only` shows the layout without compiling."
                         % (region["interval_hex"], len(region.get("linked_outside_interval", []))))
        elif region["bridges_not_linked"]:
            notes.append("With --allow-original-gaps, check_unit links only the new members and their canonical call "
                         "closure; %d canonical bridges of the natural interval are not linked, so the linked object "
                         "is compact, not the natural layout. Report that as evidence if encodings depend on it."
                         % len(region["bridges_not_linked"]))
        if deferred:
            notes.append("Deferred region (%s): gather split/extent evidence before compiling." % ", ".join(deferred))
        summary = {k: region[k] for k in ("hunk", "interval_hex", "size", "new_bytes", "canonical_bytes", "gap_bytes",
                                          "edge_kinds", "external_prerequisites", "options", "entry")}
        out.append(dict(id=region["id"], kind="region", targets=targets, priority=70 if deferred else 10,
                        title="Recover strongly connected region %s %s (%d new members, %d bytes) as one natural unit"
                              % (region["node"], region["interval_hex"], len(targets), region["new_bytes"]),
                        dependencies=[], origin=dict(source="fleet_regions", summary=summary, deferred=deferred,
                                                     region=region),
                        verifier="check_unit", budget=dict(BUDGETS["region"]), notes=notes))
    return out


def build_tasks(functions, ranked_items, recovery_ledger, packages, max_bytes=1024, max_review_tasks=24,
                include_abi_blockers=False, hypothesis_functions=(), intakes=(), regions=None, region_context=None):
    """Deterministic task list from supplied ledgers (pure helper).

    Canonical exact recoveries never become targets. A strongly connected
    region (fleet_regions) becomes one ``region`` task over all of its new
    members; a member's own function or blocker-probe task is kept but marked
    ``blocked_by_region`` (never claimable) unless the member is independently
    provable. Otherwise each function target appears in at most one task.
    Priority: lower runs first. A task whose recovery would unblock other
    non-review tasks (``unlocks``) is boosted by UNLOCK_BOOST per unlocked
    target, at most UNLOCK_CAP targets.
    """
    from recovery_plan import _constraints
    canonical = {fid for fid, item in recovery_ledger.get("functions", {}).items()
                 if item.get("state") in CANONICAL_STATES}
    blockers = recovery_ledger.get("blockers", {})
    attempts = recovery_ledger.get("attempts", {})
    by_id = {f["id"]: f for f in functions}
    items = {x["id"]: x for x in ranked_items if x["id"] not in canonical}
    tasks, assigned = [], set()
    if regions is None:
        import fleet_regions
        regions = fleet_regions.build_regions(functions, ranked_items, canonical, blockers, attempts, intakes,
                                              **(region_context or {}))
    for region in regions:
        region["members_well_bounded"] = all(items.get(m, {}).get("extent") == "CLOSED_CFG"
                                             and items.get(m, {}).get("confidence") == "HIGH"
                                             for m in region["new_members"])
    in_region, region_of = set(), {}
    for task in region_tasks(regions, canonical):
        tasks.append(task)
        region = task["origin"]["region"]
        in_region.update(task["targets"])
        for fid in task["targets"]:
            if fid not in region["independent_members"]:
                region_of[fid] = task["id"]

    def add(kind, task_id, targets, priority, title, origin, dependencies=(), verifier=None, notes=()):
        targets = [t for t in targets if t not in canonical]
        if not targets or any(t in assigned for t in targets):
            return None
        assigned.update(targets)
        task = dict(id=task_id, kind=kind, targets=targets, priority=priority, title=title,
                    dependencies=sorted(dependencies), origin=origin, verifier=verifier,
                    budget=dict(BUDGETS[kind]), notes=list(notes))
        blocking = sorted({region_of[t] for t in targets if t in region_of})
        if blocking:
            # Kept visible, never claimable: this member cannot be proved alone.
            task["blocked_by_region"] = blocking[0]
            task["notes"].append("Blocked by region %s: this member is strongly connected to other unrecovered "
                                 "members and is proved only by the whole region." % blocking[0])
        tasks.append(task)
        return task

    # Same-hunk call cycles: a complete unit hypothesis, never a function claim.
    for package in packages:
        if not package["kind"].startswith("DEPENDENCY_SCC") or not package.get("members_complete"):
            continue
        if in_region.intersection(package["members"]):
            continue  # superseded by the region that contains this cycle
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
                   "Author every unrecovered member: the ENTRY source is compiled as recovered(), each other new member "
                   "is passed as `--member ID=SRC` (its source also defines recovered(); calls use mechanical F_hNN_XXXX "
                   "names, including calls back to the entry). The unit is EQUAL only if every member is EQUAL; "
                   "report the non-entry sources in best.members."])

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
        if item is None or fid in assigned or fid in in_region or not blocks:
            continue
        closed = (item["extent"] == "CLOSED_CFG" and item.get("confidence") == "HIGH" and item["node"] != "resident"
                  and not item.get("indirect") and item["size"] <= max_bytes)
        if closed and not item.get("pending_local_dependencies"):
            untasked_leaves.append(dict(id=fid, blocks=blocks, size=item["size"],
                                        blocker_class=_blocker_class(blockers[fid].get("reason"))
                                        if fid in blockers else None))

    # Callers whose unrecovered local callees are all tasks themselves. The
    # dependency is satisfied only when those callees become canonical.
    target_task = {t: task["id"] for task in tasks for t in task["targets"] if not task.get("blocked_by_region")}
    target_task.update(region_of)
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
        if item["id"] in assigned or item["id"] in in_region:
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
    # A region waits on the tasks of its unrecovered prerequisites outside it
    # (check_unit needs every other same-node callee canonical).
    final_target = {t: task["id"] for task in tasks for t in task["targets"]
                    if not task.get("blocked_by_region") and task["kind"] != "review"}
    final_target.update(region_of)
    for task in tasks:
        if task["kind"] != "region":
            continue
        external = task["origin"]["region"]["external_prerequisites"]
        task["dependencies"] = sorted({final_target[d] for d in external if d in final_target} - {task["id"]})
        untasked = [d for d in external if d not in final_target and d not in canonical]
        if untasked:
            task["origin"]["untasked_prerequisites"] = untasked
            task["priority"] = max(task["priority"], 70)
            task["notes"].append("Prerequisites without any task: %s; the region cannot be verified until they are "
                                 "canonical." % ", ".join(untasked[:8]))
    apply_unlocks(tasks, graph, canonical)
    tasks.sort(key=lambda t: (t["priority"], t["id"]))
    return tasks, dict(omitted_review_chunks=omitted, untasked_blocking_leaves=untasked_leaves)


def apply_unlocks(tasks, graph, canonical=()):
    """Count, per task, the other non-review task targets its recovery would unblock; boost priority."""
    target_task = {t: task for task in tasks for t in task["targets"] if not task.get("blocked_by_region")}
    member_tasks = Counter(task["blocked_by_region"] for task in tasks if task.get("blocked_by_region"))
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
        if task["kind"] == "region":
            task["member_tasks_blocked"] = member_tasks.get(task["id"], 0)
        # A task that itself waits on an unrecovered function, or on its
        # region, is not boosted past that task.
        if unlocked and not blocked_by and not task.get("blocked_by_region"):
            task["base_priority"] = task["priority"]
            task["priority"] = max(1, task["priority"] - UNLOCK_BOOST * min(len(unlocked), UNLOCK_CAP))
    return tasks


def plan(fleet, max_bytes=1024, max_review_tasks=24, include_abi_blockers=False, write=True):
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
                               include_abi_blockers, hyp, list(latest.values()),
                               region_context=region_context(fleet, functions, rec))
    frontier = dict(recovery_ledger_sha256=sha256((ROOT / "recovery/ledger.json").read_bytes()),
                    function_ledger_sha256=sha256((ROOT / "evidence/functions/ledger.json").read_bytes()))
    document = dict(schema_version=1, generated=iso(now_epoch()), frontier=frontier,
                    options=dict(max_bytes=max_bytes, max_review_tasks=max_review_tasks,
                                 include_abi_blockers=include_abi_blockers),
                    counts=dict(Counter(t["kind"] for t in tasks)), omitted=extra,
                    regions=region_summaries(tasks), tasks=tasks)
    if write:
        with fleet.locked("plan"):
            write_json(fleet.tasks, document)
    return document


LAYOUT_AUDITS = ("evidence/experiments/linker-cycle-layout-frontier.json",)


def region_context(fleet, functions, rec):
    """Repository inputs for fleet_regions: proven literal-tail ends, layout audits, prior task dirs."""
    tail_ends = {}
    by_id = {f["id"]: f for f in functions}
    for fid, item in rec.get("functions", {}).items():
        if item.get("state") == "FUNCTION_WITH_DATA_MATCH" and fid in by_id:
            try:
                from check_unit import proven_tail
                tail, _ = proven_tail(by_id[fid], rec)
                tail_ends[fid] = by_id[fid]["end"] + len(tail)
            except Exception:  # an unprovable tail stays an unknown gap
                pass
    audits = []
    for path in LAYOUT_AUDITS:
        try:
            audits.append(json.loads((ROOT / path).read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    dirs = sorted(p.name for p in fleet.packets.iterdir() if p.is_dir()) if fleet.packets.is_dir() else []
    return dict(tail_ends=tail_ends, audits=audits, existing_dirs=dirs,
                source_exists=lambda path: (ROOT / path).is_file())


def region_summaries(tasks):
    rows = []
    for task in tasks:
        if task["kind"] != "region":
            continue
        region = task["origin"]["region"]
        rows.append(dict(id=task["id"], priority=task["priority"], interval=region["interval_hex"],
                         new_members=len(task["targets"]), new_bytes=region["new_bytes"],
                         canonical_members=len(region["canonical_members"]), gap_bytes=region["gap_bytes"],
                         edge_kinds=region["edge_kinds"], unlocks=task.get("unlocks", 0),
                         unlocks_targets=task.get("unlocks_targets", []),
                         member_tasks_blocked=task.get("member_tasks_blocked", 0),
                         dependencies=task["dependencies"], deferred=task["origin"]["deferred"],
                         options=region["options"], bridges_not_linked=len(region["bridges_not_linked"])))
    return rows


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
    if task.get("blocked_by_region"):
        return "blocked_by_region"
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


def declaration_views(task, functions):
    """Canonical declaration views for the task's targets (advisory; never blocks a packet)."""
    if task["kind"] == "review":
        return None
    try:
        import declaration_views as dv
        return dv.views_for(task["targets"], functions=functions)
    except Exception as exc:
        return dict(status="UNAVAILABLE", reason=_clip(exc, 160))


def declaration_section(views, directory):
    """Required pointer section text and the optional inline paste block."""
    title = "## Declarations already used by canonical sources (candidate views, not provenance)\n"
    if views.get("status") == "UNAVAILABLE":
        return title + "Unavailable: %s\n" % views["reason"], ""
    import declaration_views as dv
    conflicts, structs = views["conflicting_symbols"], views["struct_conflicts"]
    differing = ""
    if conflicts:
        differing = ": " + ", ".join(conflicts[:6]) + (" ..." if len(conflicts) > 6 else "")
    if structs:
        differing += "; struct bodies differ: " + ", ".join(structs[:4])
    # Instruction first: a fallback clip keeps the head of the section.
    text = (title + "Paste-ready block: `%s/%s` (details: task.json `declaration_views`). Reuse these names, views "
            "and struct definitions unless a hypothesis needs another view; that view change is then the "
            "recorded controlled change. They compiled exactly elsewhere; they are not historical types, and "
            "access widths do not determine a type. %d referenced symbols have canonical views (%d differ%s); "
            "%d have none.\n" % (directory, DECLARATIONS_SIDECAR, len(views["symbols"]), len(conflicts), differing,
                                 len(views["without_canonical_view"])))
    return text, dv.extern_block(views)


def _clip_section(text, limit):
    """Clip a packet section to ``limit`` bytes, at a line end when one is near."""
    if len(text) <= limit:
        return text
    cut = text.rfind("\n", 0, limit)
    cut = cut + 1 if cut >= limit // 2 else limit
    return text[:cut] + "... (clipped; full facts in task.json / the ledger)\n"


def _clip_block(block, room):
    """Whole lines of ``block`` fenced as C within ``room`` bytes (empty when too small)."""
    lines, used, kept = block.splitlines(), 0, []
    reserve = len("```c\n```\n(999 more lines in the sidecar)\n")
    for line in lines:
        if used + len(line) + 1 + reserve > room:
            break
        kept.append(line)
        used += len(line) + 1
    if len(kept) < 3:
        return ""
    more = len(lines) - len(kept)
    return "```c\n" + "\n".join(kept) + "\n```\n" + ("(%d more lines in the sidecar)\n" % more if more else "")


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
        report = unit_diag.diagnose_unit(members, receipt["cache_key"], entry_member=receipt["entry"],
                                         new_members=members)
        return unit_diag.compact_summary(report, max_bytes)
    except Exception as exc:
        return dict(status="UNAVAILABLE", reason=_clip(exc, 200))


LIVENESS = """## First step (host liveness)
Run `python tools/fleet.py renew {task_id} --worker {worker}` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK {task_id} BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).
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
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"{verifier}","entry":"<evidence id of the member compiled as recovered(), e.g. {entry}>",
   "options":[{options}],"expected_length":0,"actual_length":0}},
 "hypotheses":[{{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {{"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{{"<other member id>":"{dir}/<file>.c"}}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
"""


REGION_PROTOCOL = """## Region protocol (staged; the whole region is the only acceptance unit)
Full member facts, candidates and edges are in `{dir}/task.json` (`task.origin.region`); read that file and `python tools/grinder.py facts ID` per member instead of asking for more context.
A. Stage sources: each variant is one directory `{dir}/vNN/` holding `<ID>.c` for EVERY new member (copy the best candidate listed below, else author it; later variants copy their parent directory and change one member). Each file is self-contained K&R C defining `recovered(...)`; calls to other members, including back to the entry, use mechanical `F_hNN_XXXX` names. The entry file is compiled as recovered(); every other new member is one `--member ID=SRC`. Canonical members are reused automatically; never copy their bytes or source into your files.
B. Baseline: compile the complete region once with the verify command below and run the diagnostics command on its receipt and cache key. It reports per-member states (`same_after_reference_identity`, `differs`, ...), unknown gaps and candidate-only bytes.
C. Improve members one at a time: pick the worst `differs` member, record a hypothesis for THAT member (`"member"` field, `"parent"` = parent variant directory), change only that member's file in a new variant directory, recompile the whole region, rerun unit_diag. A member already `same_after_reference_identity` is frozen unless a hypothesis names it.
D. Unknown gaps stay unknown: never fill them with bytes, padding, data or asm. With `--natural-interval` every canonical function of the interval is linked as well and must stay EQUAL. A BLOCKED verdict `GAP_DEPENDENT_ENCODING` or `TARGET_IN_UNLINKED_SPAN` (receipt `natural_interval.gap_crossings`) means the gap itself blocks equality: report NEEDS_EVIDENCE or BLOCKED naming the gap.
E. The region is EQUAL only if the complete object and every member are EQUAL. Report every non-entry source in best.members.
F. Object grouping is a hypothesis like any variant. `--object-group ID,ID,...` (repeatable, passed to verify-region) compiles address-consecutive members with no gap or unlinked span between them as ONE ordinary object (their sources concatenated in address order; a canonical member only inside its whole proven object group). Record it as a hypothesis with a machine-checkable prediction first (e.g. "grouping 583A with 5962 turns 583A's JSR d16(PC) into the original BSR.B"). It never establishes a source file; keep member sources unchanged in a grouping variant.
"""


def _region_body(fleet, task, rec, directory):
    import fleet_regions
    region = task["origin"]["region"]
    sections = []
    summary = dict(task["origin"]["summary"], deferred=task["origin"].get("deferred"),
                   independent=region["independent_members"], layout_intervals=[
                       dict(interval="0x%04X..0x%04X" % (i["start"], i["end"]), dependents=i["dependents"],
                            sources=i["sources"]) for i in region["layout_intervals"]],
                   linked_outside_interval=len(region.get("linked_outside_interval", [])),
                   bridges_not_linked=len(region["bridges_not_linked"]),
                   blocked_by=task.get("blocked_by"), waits_on=task.get("dependencies"))
    summary = {k: v for k, v in summary.items() if v not in ([], {}, None) and k not in ("hunk", "interval_hex")}
    sections.append(("region", "## Region\n`" + _j(summary)[:1200] + "`\n(internal edges: "
                     "`task.origin.region.internal_edges`)\n", False))
    rows, run = [], []

    def flush():
        if run:
            rows.append("- 0x%04X +%d canonical (reused): %s" % (run[0]["start"], sum(x["size"] for x in run),
                                                                ", ".join(x["id"] for x in run)))
            run.clear()
    for m in region["ordered"]:
        if m.get("role") == "canonical":
            run.append(m)
            continue
        flush()
        if m.get("gap"):
            rows.append("- 0x%04X +%d GAP UNKNOWN_NOT_ASSIGNED (stays unclaimed)" % (m["start"], m["size"]))
            continue
        line = "- 0x%04X +%d NEW %s" % (m["start"], m["size"], m["id"])
        line += " scc" if m.get("scc") else (" independent" if m.get("independent") else "")
        info = region["candidates"].get(m["id"], {})
        for c in info.get("candidates", [])[:2]:
            line += "; cand `%s` %s %s/%s key %s" % (c["source"], c.get("verdict") or c.get("intake_status"),
                                                    c.get("actual"), c.get("expected"),
                                                    (c.get("cache_key") or "-")[:12])
        if info.get("experiment_dirs"):
            line += "; dirs " + ",".join(info["experiment_dirs"])
        rows.append(line)
    flush()
    sections.append(("members", "## Members in address order (region interval %s)\n" % region["interval_hex"]
                     + "\n".join(rows) + "\n", False))
    commands = fleet_regions.region_commands(region, directory)
    sections.append(("commands", "## Commands\n- verify (isolated, queued): `python tools/fleet.py verify-region %s "
                     "--sources %s/vNN` compiles `vNN/<ID>.c` for every new member: entry `%s` as recovered(), the "
                     "others as `--member`, flags `%s`, output under `%s/runs` (explicit form: `commands.verify` in "
                     "task.json). Add `--prepare-only` to see member order, spacing and gap crossings without "
                     "compiling.\n- per-member diagnostics: `%s` (explicit `--members` form: `commands.diag`).\n"
                     "Promotion is the supervisor's `check_unit.py` with the same arguments; never run it yourself.\n"
                     % (task["id"], directory, region["entry"],
                        " ".join(fleet_regions.region_flags(region)), directory,
                        commands["diag_receipt"]), False))
    history, intakes = ledger_history(fleet, task["targets"], task["id"], limit=4)
    sections.append(("ledger", "## Prior hypotheses (do not repeat)\n`" + _j(history)[:600] + "`\n" +
                     ("Prior fleet outcomes: `" + _j(intakes)[:500] + "`\n" if intakes else ""), False))
    optional = []
    receipts = unit_receipts(task["targets"], limit=3)
    if receipts:
        optional.append(("unit-receipts", "## Prior unit receipts (advisory)\n" +
                         "\n".join("- `" + _j(r) + "`" for r in receipts) + "\n"))
    return sections, optional


def _task_body(fleet, task, rec, functions, rank):
    """Return ordered (name, text, optional) packet sections."""
    if task["kind"] == "region":
        return _region_body(fleet, task, rec, rel(fleet.task_dir(task["id"])))
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


def render_packet(fleet, task, lease=None, rec=None, functions=None, rank=None, views=None):
    from recovery_state import evidence, ranked, recovery
    rec = recovery() if rec is None else rec
    functions = {f["id"]: f for f in evidence()["functions"]} if functions is None else functions
    views = declaration_views(task, functions) if views is None else views
    rank = {x["id"]: x for x in ranked()} if rank is None else rank
    directory = rel(fleet.task_dir(task["id"]))
    budget = task["budget"]
    target = task["targets"][0] if len(task["targets"]) == 1 else ",".join(task["targets"])
    verifier = task.get("verifier") or "check_function"
    if task["kind"] == "region":
        record = ("Append one JSON line per hypothesis to `%s/hypotheses.jsonl`: "
                  "{\"id\",\"parent\",\"member\",\"suspected_cause\",\"controlled_change\",\"prediction\"} with a concrete "
                  "per-member length/state prediction (for example `member ov11_F_54F8 becomes same_after_reference_identity`)."
                  % directory)
        run = ("the verify command in the Commands section (always isolated; one --member per other new member, exactly "
               "the listed flags), then the per-member diagnostics command with the new cache key.")
        options = "\"separate_objects\",\"natural_interval\",\"join_direct_callees\",\"owned_code_data\""
        unit_doc = ", docs/unit-diagnostics.md, docs/fleet.md (Regions)"
    elif task["kind"] == "unit":
        record = ("Append one JSON line per hypothesis to `%s/hypotheses.jsonl`: "
                  "{\"id\",\"parent\",\"suspected_cause\",\"controlled_change\",\"prediction\"} with a concrete length/diff prediction. "
                  "Unit member sources: copy candidates into `%s/` and edit there." % (directory, directory))
        run = ("`python tools/fleet.py verify-unit ENTRY %s/<entry>.c [--member ID=%s/<member>.c ...] --profile aztec36 "
               "[--separate-objects] [--allow-original-gaps] [--join-direct-callees] --output-dir %s/runs` (always isolated; "
               "one --member per other unrecovered member); diagnose with "
               "`python tools/unit_diag.py --members A,B --entry ENTRY --new-members A,B --cache-key KEY`."
               % (directory, directory, directory))
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
    if task["kind"] == "region":
        head.append(REGION_PROTOCOL.format(dir=directory))
    tail = [PROTOCOL.format(unit_doc=unit_doc, record=record, run=run, trials=budget["max_compile_trials"],
                            variants=budget["max_variants_per_manifest"], dir=directory, task_id=task["id"]),
            RESULT_SCHEMA.format(task_id=task["id"], dir=directory, target=target, verifier=verifier, options=options,
                                 entry=task["origin"]["region"]["entry"] if task["kind"] == "region" else target)]
    sections, optional = _task_body(fleet, task, rec, functions, rank)
    for note in task.get("notes", []):
        sections.append(("note", "Note: " + note + "\n", False))
    block = ""
    if views:
        pointer, block = declaration_section(views, directory)
        at = next((i for i, s in enumerate(sections) if s[0] == "ledger"), len(sections))
        sections.insert(at, ("decls", pointer, False))

    def assemble(opt):
        return "\n".join(head + [s[1] for s in sections] + [o[1] for o in opt] + tail)
    text = assemble(optional)
    # Drop advisory sections (diagnostics first) until the packet is small.
    while len(text.encode("utf-8")) > PACKET_TARGET_BYTES and optional:
        optional.pop(0)
        text = assemble(optional)
    # The paste block goes inline only into room left below the target size;
    # the complete block is always in the sidecar file.
    inline = _clip_block(block, PACKET_TARGET_BYTES - len(text.encode("utf-8"))) if block else ""
    if inline:
        sections = [(n, t + inline if n == "decls" else t, o) for n, t, o in sections]
        text = assemble(optional)
    for name, limit in CLIP_STEPS:
        if len(text.encode("utf-8")) <= PACKET_MAX_BYTES:
            break
        sections = [(n, _clip_section(t, limit) if name is None or n == name else t, o) for n, t, o in sections]
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
    from recovery_state import evidence
    functions = {f["id"]: f for f in evidence()["functions"]}
    views = declaration_views(task, functions)
    text = render_packet(fleet, task, lease, functions=functions, views=views)
    directory = fleet.task_dir(task_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "PROMPT.md").write_text(text, encoding="utf-8", newline="\n")
    extra = {}
    if views:
        extra["declaration_views"] = views
        if views.get("status") != "UNAVAILABLE":
            import declaration_views as dv
            (directory / DECLARATIONS_SIDECAR).write_text(dv.extern_block(views), encoding="ascii", newline="\n")
    if task["kind"] == "region":
        import fleet_regions
        extra["commands"] = fleet_regions.region_commands(task["origin"]["region"], rel(directory))
    write_json(directory / "task.json", dict(schema_version=1, task=task, lease=lease, **extra))
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
        require(isinstance(best, dict) and BEST_KEYS <= set(best) <= BEST_KEYS | {"members", "object_groups"},
                "best keys must be exactly " + ", ".join(sorted(BEST_KEYS)) +
                " (optional members and object_groups for check_unit)")
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
        if "members" in best:
            # Other new members of one complete unit, each with its own source.
            members = best["members"]
            require(best["verifier"] == "check_unit" and isinstance(members, dict) and members,
                    "best.members is a non-empty {member id: source} map for check_unit only")
            for member_id, member_source in members.items():
                require(member_id in task["targets"] and member_id != best["entry"],
                        "best.members ids must be task targets other than best.entry")
                member_path = (ROOT / member_source).resolve() if isinstance(member_source, str) else None
                require(member_path is not None and "\\" not in member_source
                        and member_path.is_relative_to(fleet.task_dir(task["id"]).resolve())
                        and member_path.suffix == ".c" and member_path.is_file(),
                        "best.members sources must be existing .c files in the task directory")
        if "object_groups" in best:
            # Translation-unit hypotheses the verifier must reproduce exactly.
            groups = best["object_groups"]
            require(best["verifier"] == "check_unit" and "separate_objects" in best["options"] and isinstance(groups, list)
                    and groups and all(isinstance(g, list) and len(g) > 1 and all(isinstance(x, str) for x in g)
                                       for g in groups),
                    "best.object_groups is a non-empty list of member-id lists (check_unit with separate_objects)")
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
        extra = {}
        if "natural_interval" in options:
            extra["natural_interval"] = natural_interval(task)
        reports = check_unit.check(best["entry"], source, [best["profile"]], False, "owned_code_data" in options,
                                   "separate_objects" in options, "allow_original_gaps" in options,
                                   "join_direct_callees" in options, isolated=True, output_dir=output,
                                   member_sources={k: ROOT / v for k, v in best.get("members", {}).items()},
                                   object_groups=best.get("object_groups"), **extra)
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


def natural_interval(task):
    """The claimed interval of a region task (the only source of --natural-interval)."""
    require(task is not None and task["kind"] == "region", "natural_interval is only defined for region tasks")
    start, end = task["origin"]["region"]["interval"]
    return start, end


def promote_command(best, task=None):
    options = set(best["options"])
    if best["verifier"] == "check_unit":
        flags = "".join(" --" + o.replace("_", "-") for o in UNIT_OPTIONS if o in options and o != "natural_interval")
        if "natural_interval" in options:
            flags += " --natural-interval 0x%04X..0x%04X" % natural_interval(task)
        flags += "".join(" --member %s=%s" % item for item in sorted(best.get("members", {}).items()))
        flags += "".join(" --object-group " + ",".join(g) for g in best.get("object_groups") or ())
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
            command = promote_command(best, task)
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


def region_verify_argv(fleet, task_id, sources=None, profile="aztec36", join_direct_callees=False, canonical=None,
                       prepare_only=False, object_groups=()):
    """Isolated check_unit argv for a region variant directory (see fleet_regions.region_check_args)."""
    import fleet_regions
    task = find_task(fleet, task_id)
    require(task["kind"] == "region", "not a region task: " + task_id)
    directory = fleet.task_dir(task_id)
    source_dir = Path(sources).resolve() if sources else directory.resolve()
    require(source_dir.is_relative_to(directory.resolve()), "--sources must be inside the task directory")
    canonical = canonical_ids() if canonical is None else canonical
    members = [m for m in task["targets"] if m not in canonical]
    require(len(members) >= 1, "every region member is already canonical")
    for m in members:
        require((source_dir / (m + ".c")).is_file(), "missing member source " + rel(source_dir / (m + ".c")))
    extra = (["--join-direct-callees"] if join_direct_callees else []) + (["--prepare-only"] if prepare_only else [])
    for group in object_groups or ():
        # One translation-unit hypothesis per group; check_unit validates it.
        extra += ["--object-group", group]
    return fleet_regions.region_check_args(task["origin"]["region"], rel(directory), rel(source_dir), members, profile,
                                           extra)


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
    p = sub.add_parser("regions", help="print the strongly connected recovery regions (writes nothing)")
    p.add_argument("--max-bytes", type=int, default=1024)
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
    p = sub.add_parser("verify-region", help="isolated whole-region check_unit of one variant directory")
    p.add_argument("task"); p.add_argument("--sources", help="variant directory with <ID>.c per new member")
    p.add_argument("--profile", default="aztec36"); p.add_argument("--join-direct-callees", action="store_true")
    p.add_argument("--print", action="store_true", help="print the check_unit arguments without compiling")
    p.add_argument("--prepare-only", action="store_true",
                   help="print the planned natural-interval unit (order, spacing, gap crossings, cache keys); no compile")
    p.add_argument("--object-group", action="append", default=[], metavar="ID,ID,...",
                   help="compile these address-consecutive members as one object (a hypothesis; repeatable)")
    args = ap.parse_args(argv)
    if args.packets_dir is not None:
        packets = args.packets_dir.resolve()
        require(packets.is_relative_to((ROOT / "experiments").resolve()) or packets.is_relative_to((ROOT / "build").resolve()),
                "--packets-dir must be under experiments/ or build/")
    fleet = Fleet(args.fleet_dir, args.ledger, args.packets_dir and args.packets_dir.resolve())
    try:
        if args.command == "plan":
            doc = plan(fleet, args.max_bytes, args.max_review_tasks, args.include_abi_blockers)
            print(_j(dict(tasks=len(doc["tasks"]), counts=doc["counts"], omitted=doc["omitted"],
                          regions=[r["id"] for r in doc["regions"]], path=rel(fleet.tasks))))
        elif args.command == "regions":
            doc = plan(fleet, args.max_bytes, write=False)
            print(json.dumps(sorted(doc["regions"], key=lambda r: (r["priority"], -r["unlocks"], r["id"])),
                             indent=1, sort_keys=True))
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
        elif args.command == "verify-region":
            argv = region_verify_argv(fleet, args.task, args.sources, args.profile, args.join_direct_callees,
                                      prepare_only=args.prepare_only, object_groups=args.object_group)
            if args.print:
                print(" ".join(argv + ["--isolated"]))
                return 0
            return _run_wrapped("check_unit", argv)
        elif args.command in ("verify-function", "verify-unit"):
            module = "check_function" if args.command == "verify-function" else "check_unit"
            return _run_wrapped(module, [a for a in args.args if a != "--"])
        return 0
    except (FormatError, OSError, ValueError) as exc:
        print(_j(dict(status="REJECTED", reason=str(exc))), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
