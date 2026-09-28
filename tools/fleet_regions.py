"""Strongly connected recovery regions for fleet planning (pure, read-only).

A region is a set of unrecovered same-hunk functions that no worker can prove
one at a time. Its members are strongly connected through hard constraints:

- ``call``: a same-hunk PC-relative direct call between unrecovered functions;
- ``pending_dependency``: the ranked frontier's pending local dependency;
- ``layout_interval``: a curated DEPENDENCY_LAYOUT recovery blocker (for
  example CYCLIC_INTER_OBJECT_PC_CALL) that names a physical interval
  ``0xAAAA..0xBBBB``. Its blocked function depends on every unrecovered
  candidate inside that interval;
- ``short_form_if_compacted``: a long PC-relative call form (``JSR d16(PC)``
  or ``BSR.W``) whose displacement is outside the short BSR.B range in the
  original, but would fall inside it if every byte between site and target
  were absent. Its encoding then depends on the unrecovered bytes between.

Intake explanations that merely mention a function are advisory and are not
region edges. Each strongly connected component is widened to its physical
interval (address span, plus any overlapping curated layout interval or cycle
layout audit interval), and overlapping regions in one hunk are merged. Every
unrecovered function inside the widened interval is a new member; canonical
ones are reused. Bytes covered by no discovered function and no proven literal
tail stay ``UNKNOWN_NOT_ASSIGNED`` gaps.

Nothing here compiles, claims ownership, or promotes. Regions are planning
hypotheses; ``check_unit`` of the complete unit remains the only acceptance.
"""
import re

from recovery_plan import _profile_class, _sccs


REGION_MAX_NEW = 12
INTERVAL_TEXT = re.compile(r"\b0x([0-9A-Fa-f]{2,6})\s*\.\.\s*0x([0-9A-Fa-f]{2,6})\b")
LONG_CALL_PREFIXES = ("4eba", "6100")  # JSR d16(PC), BSR.W
SHORT_MIN, SHORT_MAX = -128, 127
EDGE_KINDS = ("call", "pending_dependency", "layout_interval", "short_form_if_compacted")


def layout_intervals(by_id, blockers, audits=()):
    """Curated physical intervals that an exact natural layout proof needs."""
    found = {}
    for fid in sorted(blockers):
        f = by_id.get(fid)
        blocker = blockers[fid] or {}
        if f is None or _profile_class(blocker.get("reason")) != "DEPENDENCY_LAYOUT":
            continue
        text = " ".join(str(blocker.get(k) or "") for k in ("reason", "next_action"))
        for m in INTERVAL_TEXT.finditer(text):
            start, end = int(m.group(1), 16), int(m.group(2), 16)
            if start >= end:
                continue
            entry = found.setdefault((f["hunk"], start, end), dict(dependents=set(), sources=set()))
            entry["dependents"].add(fid)
            entry["sources"].add("recovery_blocker:" + fid)
    for audit in audits:
        interval = (audit or {}).get("interval") or {}
        key = (interval.get("hunk"), interval.get("start"), interval.get("end"))
        if None in key or key[1] >= key[2]:
            continue
        entry = found.setdefault(key, dict(dependents=set(), sources=set()))
        entry["sources"].add(str(audit.get("kind") or "layout_audit"))
    return [dict(hunk=h, start=s, end=e, dependents=sorted(v["dependents"]), sources=sorted(v["sources"]))
            for (h, s, e), v in sorted(found.items())]


def _size(f):
    return f.get("size", f["end"] - f["start"])


def _overlap(a0, a1, b0, b1):
    return max(0, min(a1, b1) - max(a0, b0))


def region_edges(by_id, items, unrecovered, intervals):
    """{(from, to): set(kind)} among unrecovered functions; ``from`` needs ``to``."""
    edges = {}

    def edge(a, b, kind):
        if a != b and a in unrecovered and b in unrecovered:
            edges.setdefault((a, b), set()).add(kind)

    by_hunk = {}
    for fid in unrecovered:
        by_hunk.setdefault(by_id[fid].get("hunk"), []).append(fid)
    for fid in sorted(unrecovered):
        f = by_id[fid]
        for d in (items.get(fid) or {}).get("pending_local_dependencies") or []:
            edge(fid, d, "pending_dependency")
        instructions = {i.get("offset"): i for i in f.get("instructions") or []}
        for call in f.get("direct_callees") or []:
            target = call.get("id")
            if call.get("basis") != "PC_RELATIVE" or call.get("hunk") != f.get("hunk") or not target:
                continue
            edge(fid, target, "call")
            ins = instructions.get(call.get("site"))
            if not ins or ins.get("size") != 4 or not str(ins.get("raw", "")).lower().startswith(LONG_CALL_PREFIXES):
                continue
            origin = call["site"] + 2
            displacement = call.get("offset", 0) - origin
            if SHORT_MIN <= displacement <= SHORT_MAX:
                continue
            lo, hi = sorted((origin, call.get("offset", 0)))
            between = [x for x in by_hunk.get(f.get("hunk"), ()) if x not in (fid, target)
                       and _overlap(lo, hi, by_id[x]["start"], by_id[x]["end"])]
            if not between:
                continue
            # Only the unrecovered bytes between are missing from a compact
            # link; canonical bridges and unknown gaps keep their size.
            kept = (hi - lo) - sum(_overlap(lo, hi, by_id[x]["start"], by_id[x]["end"]) for x in between)
            compact = kept if displacement > 0 else -kept
            if SHORT_MIN <= compact <= SHORT_MAX:
                for x in between:
                    edge(fid, x, "short_form_if_compacted")
    for interval in intervals:
        inside = [x for x in by_hunk.get(interval["hunk"], ())
                  if interval["start"] <= by_id[x]["start"] and by_id[x]["end"] <= interval["end"]]
        for dependent in interval["dependents"]:
            for x in inside:
                edge(dependent, x, "layout_interval")
    return edges


def _widen(regions, by_id, hunk_functions, intervals):
    """Merge overlapping regions of one hunk and widen them to whole extents and layout intervals."""
    changed = True
    while changed:
        changed = False
        for region in regions:
            start, end = region["start"], region["end"]
            for interval in intervals:
                if interval["hunk"] == region["hunk"] and interval["start"] < end and interval["end"] > start:
                    start, end = min(start, interval["start"]), max(end, interval["end"])
            for f in hunk_functions.get(region["hunk"], ()):
                if f["start"] < end and f["end"] > start:
                    start, end = min(start, f["start"]), max(end, f["end"])
            if (start, end) != (region["start"], region["end"]):
                region.update(start=start, end=end)
                changed = True
        merged = []
        for region in sorted(regions, key=lambda r: (r["hunk"], r["start"])):
            last = merged[-1] if merged else None
            if last and last["hunk"] == region["hunk"] and region["start"] < last["end"]:
                last.update(end=max(last["end"], region["end"]), scc=sorted(set(last["scc"]) | set(region["scc"])))
                changed = True
            else:
                merged.append(region)
        regions = merged
    return regions


def region_id(node, start, end):
    """Stable per physical interval, short enough for packet command lines."""
    return "reg-%s_%04X-%04X" % (node or "h", start, end)


def member_candidates(fid, attempts, intakes, existing_dirs=(), source_exists=None, limit=3):
    """Best known candidate sources for one member (advisory; nothing is trusted)."""
    rows = []
    for record in intakes:
        best = record.get("best") or {}
        source = best.get("source") if best.get("entry") == fid else (best.get("members") or {}).get(fid)
        if source:
            rows.append(dict(origin="fleet_intake:" + str(record.get("task_id")), source=source,
                             verdict=best.get("verdict"), intake_status=record.get("intake_status"),
                             cache_key=best.get("cache_key"), expected=best.get("expected_length"),
                             actual=best.get("actual_length"), entry=best.get("entry")))
    retained = []
    for a in attempts.get(fid) or []:
        path = "recovery/candidates/%s/%s.c" % (fid, a.get("source_sha256", ""))
        if a.get("source_sha256") and (source_exists is None or source_exists(path)):
            retained.append((a.get("mnemonic_similarity") or 0, path, a))
    for similarity, path, a in sorted(retained, key=lambda x: -x[0])[:2]:
        if any(r["source"] == path for r in rows):
            continue
        rows.append(dict(origin="recovery_attempt", source=path, verdict=a.get("verdict"), similarity=similarity,
                         cache_key=a.get("cache_key"), expected=a.get("expected_length"),
                         actual=a.get("actual_length"), profile=a.get("profile")))
    suffix = fid.rsplit("_", 1)[-1]
    dirs = sorted(d for d in existing_dirs if d in ("fn-" + fid, "blk-" + fid)
                  or (d.startswith(("unit-", "reg-")) and (fid in d or "-" + suffix in d)))
    return dict(candidates=rows[:limit], experiment_dirs=["experiments/fleet/" + d for d in dirs][:4])


def build_regions(functions, items, canonical, blockers, attempts=None, intakes=(), tail_ends=None, audits=(),
                  existing_dirs=(), source_exists=None, max_new=REGION_MAX_NEW):
    """Deterministic list of region dicts from supplied ledgers (pure helper)."""
    by_id = {f["id"]: f for f in functions}
    items = {x["id"]: x for x in items} if isinstance(items, list) else dict(items)
    canonical = set(canonical)
    attempts = attempts or {}
    unrecovered = {fid for fid in by_id if fid not in canonical}
    tail_ends = tail_ends or {}

    def contribution_end(f):
        return tail_ends.get(f["id"], f["end"]) if f["id"] in canonical else f["end"]

    intervals = layout_intervals(by_id, blockers, audits)
    edges = region_edges(by_id, items, unrecovered, intervals)
    graph = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
    hunk_functions = {}
    for f in sorted(functions, key=lambda f: (f.get("hunk", -1), f["start"], f["id"])):
        hunk_functions.setdefault(f.get("hunk"), []).append(f)
    seeds = []
    for component in _sccs(graph):
        if len(component) < 2:
            continue
        members = [by_id[m] for m in component]
        seeds.append(dict(hunk=members[0]["hunk"], start=min(m["start"] for m in members),
                          end=max(m["end"] for m in members), scc=sorted(component)))
    regions = []
    for seed in _widen(seeds, by_id, hunk_functions, intervals):
        hunk, start, end = seed["hunk"], seed["start"], seed["end"]
        inside = [f for f in hunk_functions[hunk] if start <= f["start"] and f["end"] <= end]
        new = [f["id"] for f in inside if f["id"] in unrecovered]
        member_set = set(new)
        scc = set(seed["scc"])
        out_edges = {}
        for (a, b), kinds in edges.items():
            if a in member_set:
                out_edges.setdefault(a, []).append((b, kinds))
        independent = [m for m in new if m not in scc and not out_edges.get(m)]
        external = sorted({b for m in new for b, _ in out_edges.get(m, ()) if b not in member_set})
        cursor, gaps, ordered = start, [], []
        for f in inside:
            if f["start"] > cursor:
                gaps.append(dict(start=cursor, end=f["start"], size=f["start"] - cursor,
                                 ownership="UNKNOWN_NOT_ASSIGNED"))
                ordered.append(dict(gap=True, start=cursor, size=f["start"] - cursor))
            role = "new" if f["id"] in member_set else "canonical"
            ordered.append(dict(id=f["id"], start=f["start"], size=_size(f), role=role,
                                **({"scc": True} if f["id"] in scc else {}),
                                **({"independent": True} if f["id"] in independent else {})))
            cursor = max(cursor, contribution_end(f))
        if cursor < end:
            gaps.append(dict(start=cursor, end=end, size=end - cursor, ownership="UNKNOWN_NOT_ASSIGNED"))
            ordered.append(dict(gap=True, start=cursor, size=end - cursor))
        # What check_unit will link: the new members plus the canonical call
        # closure (prepare_unit follows every same-hunk direct callee).
        linked, stack = set(new), list(new)
        while stack:
            f = by_id[stack.pop()]
            for call in f.get("direct_callees") or []:
                dep = call.get("id")
                if call.get("hunk") == hunk and dep in canonical and dep in by_id and dep not in linked:
                    linked.add(dep)
                    stack.append(dep)
        lo = min(by_id[m]["start"] for m in linked)
        hi = max(contribution_end(by_id[m]) for m in linked)
        cursor, compact = lo, True
        for f in hunk_functions[hunk]:
            if f["end"] <= lo or f["start"] >= hi:
                continue
            if (f["id"] not in linked and f["id"] not in canonical) or f["start"] != cursor:
                compact = False
                break
            cursor = contribution_end(f)
        compact = compact and cursor == hi
        if compact:
            linked.update(f["id"] for f in hunk_functions[hunk] if lo <= f["start"] and f["end"] <= hi)
        linked_order = sorted(linked, key=lambda m: (by_id[m]["start"], m))
        bridges_not_linked = [f["id"] for f in inside if f["id"] in canonical and f["id"] not in linked]
        applied = [dict(i, dependents=i["dependents"]) for i in intervals
                   if i["hunk"] == hunk and i["start"] < end and i["end"] > start]
        kinds = {}
        for (a, b), ks in edges.items():
            if a in member_set and b in member_set:
                for k in ks:
                    kinds[k] = kinds.get(k, 0) + 1
        internal = sorted("%s>%s:%s" % (a.rsplit("_", 1)[-1], b.rsplit("_", 1)[-1], "+".join(sorted(ks)))
                          for (a, b), ks in edges.items() if a in member_set and b in member_set)
        options = ["separate_objects"] + ([] if compact else ["allow_original_gaps"])
        new_bytes = sum(_size(by_id[m]) for m in new)
        node = (items.get(new[0]) or {}).get("node") or by_id[new[0]].get("node")
        regions.append(dict(
            id=region_id(node, start, end), hunk=hunk, node=node,
            interval=[start, end], interval_hex="0x%04X..0x%04X" % (start, end), size=end - start,
            new_members=new, new_bytes=new_bytes, scc_members=sorted(scc), independent_members=independent,
            canonical_members=[f["id"] for f in inside if f["id"] in canonical],
            canonical_bytes=sum(_size(f) for f in inside if f["id"] in canonical),
            gaps=gaps, gap_bytes=sum(g["size"] for g in gaps), ordered=ordered,
            edge_kinds=dict(sorted(kinds.items())), internal_edges=internal[:48],
            layout_intervals=applied, external_prerequisites=external,
            entry=new[0], linked_members=linked_order, linked_compact=compact,
            bridges_not_linked=bridges_not_linked, options=options,
            oversized=len(new) > max_new,
            candidates={m: member_candidates(m, attempts, intakes, existing_dirs, source_exists) for m in new}))
    regions.sort(key=lambda r: (r["hunk"], r["interval"][0]))
    return regions


def region_check_args(region, directory, sources=None, members=None, profile="aztec36", extra=()):
    """check_unit argv (without --isolated) for one region candidate.

    ``sources`` is the variant directory holding ``<ID>.c`` for every new
    member; ``members`` restricts to the still-unrecovered new members, in
    address order. The first one is the entry compiled as ``recovered``.
    """
    sources = sources or directory + "/vNN"
    members = list(members if members is not None else region["new_members"])
    entry = members[0]
    argv = [entry, "%s/%s.c" % (sources, entry)]
    for m in members[1:]:
        argv += ["--member", "%s=%s/%s.c" % (m, sources, m)]
    argv += ["--profile", profile] + ["--" + o.replace("_", "-") for o in region["options"]] + list(extra)
    return argv + ["--output-dir", directory + "/runs"]


def region_commands(region, directory):
    """Worker/supervisor command shapes for one region; ``directory`` is the task directory."""
    entry = region["entry"]
    argv = region_check_args(region, directory)
    shape = " ".join(argv[:-2])
    return dict(
        verify_region="python tools/fleet.py verify-region %s --sources %s/vNN" % (region["id"], directory),
        verify="python tools/fleet.py verify-unit " + " ".join(argv),
        diag_receipt="python tools/unit_diag.py --receipt %s/runs/%s/aztec36-<KEY12>/receipt.json --cache-key KEY"
                     % (directory, entry),
        diag="python tools/unit_diag.py --members %s --entry %s --new-members %s --cache-key KEY"
             % (",".join(region["linked_members"]), entry, ",".join(region["new_members"])),
        promote_shape="python tools/check_unit.py " + shape)
