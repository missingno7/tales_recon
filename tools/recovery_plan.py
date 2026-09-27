"""Read-only, bounded planning for recovery work after the grinder frontier empties.

This module diagnoses the existing evidence ledgers.  It never proposes source,
invokes a compiler, edits recovery state, or promotes a proof.
"""
from collections import Counter, defaultdict

from common import sha256
from recovery_state import ROOT, evidence, ranked, recovery


MAX_PACKAGE_MEMBERS = 8


def _constraints(item, limit, max_unknown_calls=1, max_data_references=40):
    """Return every applicable grinder constraint, not only its first reason."""
    found = []
    if item.get('extent') != 'CLOSED_CFG': found.append('UNCERTAIN_EXTENT')
    if item.get('node') == 'resident': found.append('RESIDENT_DEFERRED')
    if item.get('size', 0) > limit: found.append('SIZE_LIMIT')
    if item.get('confidence', 'HIGH') != 'HIGH': found.append('LOW_CONFIDENCE')
    if item.get('indirect', 0): found.append('INDIRECT_CONTROL_FLOW')
    if item.get('unknown_calls', 0) > max_unknown_calls: found.append('UNKNOWN_CALL_LIMIT')
    if item.get('pc_relative_data', 0): found.append('PC_RELATIVE_DATA_OWNERSHIP')
    if item.get('data_references', 0) > max_data_references: found.append('DATA_REFERENCE_LIMIT')
    if item.get('pending_local_dependencies'): found.append('UNRECOVERED_LOCAL_DEPENDENCY')
    if not item.get('same_node_unit_ready', True): found.append('NONCONTIGUOUS_LOCAL_UNIT')
    return found


def _profile_class(reason):
    text = (reason or '').upper()
    if any(x in text for x in ('BYTE_RETURN_ABI', 'CHAR_RETURN', 'ZERO_EXTENSION')):
        return 'ABI_OR_CODEGEN_PROFILE'
    if 'PERSISTENT_CODEGEN' in text:
        return 'SOURCE_OR_ALGORITHM_SHAPE'
    if 'CYCLIC_INTER_OBJECT_PC_CALL' in text:
        return 'DEPENDENCY_LAYOUT'
    if any(x in text for x in ('FFP', 'PRIVATE_HELPER', 'EXTERNAL_FIXUP', 'REGISTER_CALL_ABI')):
        return 'EXTERNAL_CALL_BINDING'
    if any(x in text for x in ('DATA', 'GLOBAL', 'TABLE')):
        return 'DATA_OWNERSHIP'
    return 'PROOF_OR_SOURCE_HYPOTHESIS'


def _source_state(fid, attempts, blockers):
    rows = attempts.get(fid, []) or blockers.get(fid, {}).get('attempts', [])
    if not rows:
        return {'state': 'NO_RETAINED_ATTEMPT_RECEIPT', 'attempts': 0, 'profiles': []}
    latest = rows[-1]
    source = ROOT / 'recovery' / 'candidates' / fid / (latest.get('source_sha256', '') + '.c')
    available = source.is_file() and sha256(source.read_bytes()) == latest.get('source_sha256')
    return {
        'state': 'RETAINED_CANDIDATE_SOURCE' if available else 'ATTEMPT_RECEIPTS_AVAILABLE',
        'attempts': len(rows),
        'profiles': sorted({x.get('profile', 'UNKNOWN') for x in rows}),
        'latest_verdict': latest.get('verdict'),
        'latest_reason': latest.get('reason'),
        'source_available': available,
    }


def _sccs(graph):
    """Tarjan SCCs, deterministic and intentionally limited to supplied nodes."""
    index = 0
    stack, on_stack, indexes, low = [], set(), {}, {}
    result = []

    def visit(node):
        nonlocal index
        indexes[node] = low[node] = index
        index += 1
        stack.append(node); on_stack.add(node)
        for child in sorted(graph.get(node, ())):
            if child not in indexes:
                visit(child); low[node] = min(low[node], low[child])
            elif child in on_stack:
                low[node] = min(low[node], indexes[child])
        if low[node] == indexes[node]:
            component = []
            while True:
                child = stack.pop(); on_stack.remove(child); component.append(child)
                if child == node: break
            result.append(sorted(component))

    for node in sorted(graph):
        if node not in indexes: visit(node)
    return result


def _dependency_components(functions, unresolved_ids):
    unresolved = set(unresolved_ids)
    by_id = {f['id']: f for f in functions}
    graph = {}
    for f in functions:
        if f['id'] not in unresolved: continue
        graph[f['id']] = {c['id'] for c in f.get('direct_callees', [])
                          if c.get('basis') == 'PC_RELATIVE' and c.get('id') in unresolved
                          and c.get('id') != f['id']
                          and by_id.get(c.get('id'), {}).get('hunk') == f.get('hunk')}
    return [part for part in _sccs(graph) if len(part) > 1]


def _make_packages(items, functions, state, limit, max_packages,
                   max_unknown_calls=1, max_data_references=40):
    by_id = {f['id']: f for f in functions}
    item_by_id = {x['id']: x for x in items}
    blockers, attempts = state.get('blockers', {}), state.get('attempts', {})
    packages = []
    serial = 0

    def add(kind, members, action, evidence, priority, rationale, metadata=None):
        nonlocal serial
        all_members = sorted(set(members))
        members = all_members[:MAX_PACKAGE_MEMBERS]
        if not all_members: return
        serial += 1
        ids = members
        package = {
            'id': f'RP{serial:02d}', 'kind': kind, 'members': ids,
            'member_count': len(all_members), 'members_complete': len(all_members) <= MAX_PACKAGE_MEMBERS,
            'priority': priority, 'rationale': rationale,
            'dispatch': {'action': action, 'ids': ids, 'read_only': True},
            'diagnostics': [{
                'id': fid,
                'node': item_by_id[fid].get('node'),
                'extent': item_by_id[fid].get('extent'),
                'size': item_by_id[fid].get('size'),
                'constraints': _constraints(item_by_id[fid], limit, max_unknown_calls, max_data_references),
                'source': _source_state(fid, attempts, blockers),
                'proof_blocker': blockers.get(fid, {}).get('reason'),
            } for fid in ids if fid in item_by_id],
            'evidence_refs': evidence,
        }
        if metadata: package['metadata'] = metadata
        packages.append(package)

    # A closed same-node call cycle needs a compact, naturally ordered unit;
    # the package names only proved function entries and leaves gaps unclaimed.
    for part in _dependency_components(functions, item_by_id):
        members = sorted((by_id[fid] for fid in part if fid in by_id),
                         key=lambda f: (f.get('hunk', -1), f.get('start', -1), f['id']))
        if not members: continue
        hunk, first, last = members[0].get('hunk'), members[0], members[-1]
        interior = sorted((f for f in functions if f.get('hunk') == hunk
                           and first.get('start', 0) <= f.get('start', -1)
                           and f.get('end', 0) <= last.get('end', 0)), key=lambda f: f.get('start', -1))
        owned, member_ids = set(state.get('functions', {})), set(part)
        cursor, gaps, unknown = first.get('start'), [], []
        for f in interior:
            if f.get('start') != cursor: gaps.append([cursor, f.get('start')])
            if f['id'] not in member_ids and f['id'] not in owned: unknown.append(f['id'])
            cursor = f.get('end')
        if cursor != last.get('end'): gaps.append([cursor, last.get('end')])
        bounded_members = [item_by_id.get(fid, {}) for fid in part]
        members_well_bounded = all(x.get('extent') == 'CLOSED_CFG' and x.get('confidence') == 'HIGH'
                                   for x in bounded_members)
        missing_sources = [fid for fid in part
                           if not _source_state(fid, attempts, blockers).get('source_available', False)]
        external_local = {}
        for fid in part:
            f = by_id.get(fid, {})
            for call in f.get('direct_callees', []):
                dep = call.get('id')
                if (call.get('basis') == 'PC_RELATIVE' and call.get('hunk') == hunk
                        and dep and dep not in member_ids):
                    external_local.setdefault(dep, 'CANONICAL_RECOVERY' if dep in owned else 'UNRECOVERED')
        external_dependencies = sorted(dep for dep, status in external_local.items() if status == 'UNRECOVERED')
        canonical_dependencies = sorted(dep for dep, status in external_local.items()
                                         if status == 'CANONICAL_RECOVERY')
        interval_tiled = not gaps and not unknown
        meta = {'hunk': hunk, 'interval': [first.get('start'), last.get('end')],
                'bridge_functions': [f['id'] for f in interior if f['id'] not in member_ids],
                'canonical_bridge_ids': [f['id'] for f in interior if f['id'] in owned and f['id'] not in member_ids],
                'unknown_bridge_ids': unknown, 'unclassified_gaps': gaps,
                'interval_tiled_by_bounded_candidates_and_canonical_bridges': interval_tiled,
                'bounded_members_high_confidence_closed_cfg': members_well_bounded,
                'missing_candidate_sources': missing_sources,
                'external_canonical_dependencies': canonical_dependencies,
                'external_unrecovered_dependencies': external_dependencies,
                'call_graph_scope': 'direct same-hunk PC-relative callees',
                'compiler_component_closed_by_scc': False,
                'source_unit_compile_ready': False}
        reviewable = len(part) <= MAX_PACKAGE_MEMBERS and interval_tiled and members_well_bounded and not external_dependencies
        kind, action = ('DEPENDENCY_SCC_HYPOTHESIS', 'inspect_dependency_scc') if reviewable else ('DEPENDENCY_SCC_REVIEW', 'inspect_dependency_scc')
        rationale = ('A bounded same-hunk call-cycle interval is tiled by candidate functions and canonical bridge entries; inspect its source/layout hypothesis. This is not a compiler-ready unit or a proof.'
                     if reviewable else 'A same-hunk call cycle exists, but its bounded interval or dependency closure is incomplete; this is a review hypothesis, not a unit-ready claim.')
        add(kind, part, action, [{'kind': 'PC_RELATIVE_CALL_GRAPH', 'members': part}], 10, rationale, meta)

    # Failed exact checks are grouped by mechanism so an exhausted runner can
    # point to a changed hypothesis, rather than send the same candidate again.
    groups = defaultdict(list)
    for fid, blocker in blockers.items():
        if fid in item_by_id:
            groups[_profile_class(blocker.get('reason'))].append(fid)
    for mechanism, members in sorted(groups.items()):
        action = 'audit_profile_or_codegen' if mechanism == 'ABI_OR_CODEGEN_PROFILE' else 'review_proof_blocker'
        add('PROOF_BLOCKER_REVIEW', members, action,
            [{'kind': 'RECOVERY_BLOCKER_LEDGER', 'mechanism': mechanism}], 20,
            'A prior exact comparison is blocked; inspect the named mechanism and change the hypothesis before any retry.')

    extent_ids = [x['id'] for x in items if 'UNCERTAIN_EXTENT' in _constraints(x, limit, max_unknown_calls, max_data_references)]
    if extent_ids:
        add('UNKNOWN_EXTENT_AUDIT', extent_ids, 'audit_extent',
            [{'kind': 'FUNCTION_CENSUS', 'field': 'extent_status'}], 30,
            'Resolve only bounded control-flow/ownership boundaries from independent evidence; do not infer missing targets.')

    dep_ids = [x['id'] for x in items if 'UNRECOVERED_LOCAL_DEPENDENCY' in _constraints(x, limit, max_unknown_calls, max_data_references)]
    dep_ids = [fid for fid in dep_ids if not any(fid in p['members'] for p in packages if p['kind'] in ('DEPENDENCY_SCC_UNIT', 'DEPENDENCY_SCC_REVIEW'))]
    if dep_ids:
        add('LOCAL_DEPENDENCY_REVIEW', dep_ids, 'inspect_dependency_closure',
            [{'kind': 'DIRECT_CALLEE_LEDGER', 'basis': 'PC_RELATIVE'}], 40,
            'Check whether a complete contiguous same-node unit can include the required local entries and bridge members.')

    profile_ids = [x['id'] for x in items if x.get('state') in ('CODEGEN_SIMILAR', 'CANDIDATE_C')
                   and x['id'] not in blockers]
    if profile_ids:
        add('SOURCE_CONTEXT_AND_PROFILE_REVIEW', profile_ids, 'inspect_retained_source_context',
            [{'kind': 'ATTEMPT_LEDGER', 'fields': ['source_sha256', 'profile', 'verdict', 'first_difference']}], 50,
            'Compare retained source attempts and exact mismatch receipts; only propose a new profile or source-context test when evidence supports it.')

    # Remaining candidates are grouped under their dominant mechanical limits.
    residual = [x for x in items if not any(x['id'] in p['members'] for p in packages)]
    mechanism_groups = defaultdict(list)
    for x in residual:
        cs = _constraints(x, limit, max_unknown_calls, max_data_references)
        if not cs: continue
        primary = cs[0]
        mechanism_groups[primary].append(x['id'])
    labels = {
        'SIZE_LIMIT': ('SIZE_BOUNDARY_REVIEW', 'inspect_size_boundary'),
        'RESIDENT_DEFERRED': ('RESIDENT_OWNERSHIP_REVIEW', 'inspect_resident_context'),
        'UNKNOWN_CALL_LIMIT': ('CALL_IDENTITY_REVIEW', 'inspect_call_identities'),
        'PC_RELATIVE_DATA_OWNERSHIP': ('DATA_OWNERSHIP_REVIEW', 'inspect_data_references'),
        'DATA_REFERENCE_LIMIT': ('DATA_CONTEXT_REVIEW', 'inspect_data_references'),
        'NONCONTIGUOUS_LOCAL_UNIT': ('SOURCE_UNIT_BOUNDARY_REVIEW', 'inspect_source_unit_boundary'),
        'LOW_CONFIDENCE': ('ENTRY_CONFIDENCE_REVIEW', 'inspect_entry_evidence'),
        'INDIRECT_CONTROL_FLOW': ('INDIRECT_CONTROL_FLOW_REVIEW', 'inspect_indirect_targets'),
    }
    for reason, members in sorted(mechanism_groups.items()):
        kind, action = labels.get(reason, ('FRONTIER_REVIEW', 'inspect_frontier_evidence'))
        add(kind, members, action,
            [{'kind': 'GRINDER_FRONTIER', 'mechanism': reason, 'limit': limit}], 60,
            f'The grinder boundary is {reason}; gather the specific missing proof before requeueing work.')
    packages.sort(key=lambda p: (p['priority'], p['kind'], p['members']))
    return packages


def build_plan(functions, ranked_items, state, node=None, ids=None, limit=512, max_packages=8,
               max_unknown_calls=1, max_data_references=40):
    """Build a deterministic bounded plan from supplied ledgers (pure helper)."""
    if limit < 1 or max_packages < 0:
        raise ValueError('limit must be positive and max_packages nonnegative')
    chosen = set(ids or ())
    selected = [x for x in ranked_items if (node is None or x.get('node') == node)
                and (not chosen or x['id'] in chosen)]
    counts = Counter()
    overlap = Counter()
    eligible = []
    for item in selected:
        cs = _constraints(item, limit, max_unknown_calls, max_data_references)
        is_blocked = item['id'] in state.get('blockers', {})
        if not cs and not is_blocked: eligible.append(item['id'])
        else:
            counts[cs[0] if cs else 'RECOVERY_BLOCKER'] += 1
            for reason in cs: overlap[reason] += 1
        if is_blocked: overlap['RECOVERY_BLOCKER'] += 1
    packages = _make_packages(selected, functions, state, limit, max_packages,
                              max_unknown_calls, max_data_references)
    package_count_total = len(packages)
    omitted_package_count = max(0, package_count_total - max_packages)
    packages = packages[:max_packages]
    return {
        'schema_version': 1,
        'mode': 'RECOVERY_REVIEW_REQUIRED' if not eligible and selected else ('ACTIONABLE' if eligible else 'NO_CANDIDATES'),
        'read_only': True,
        'scope': {'node': node, 'ids': sorted(chosen) if chosen else None,
                  'candidate_count': len(selected), 'max_bytes': limit,
                  'max_packages': max_packages, 'max_package_members': MAX_PACKAGE_MEMBERS,
                  'max_unknown_calls': max_unknown_calls, 'max_data_references': max_data_references},
        'measurement': {
            'eligible_count': len(eligible), 'eligible_ids': eligible[:16],
            'dominant_first_constraint': counts.most_common(1)[0][0] if counts else None,
            'first_constraint_counts': dict(sorted(counts.items())),
            'all_constraint_counts': dict(sorted(overlap.items())),
            'constraint_note': 'Counts overlap in all_constraint_counts; first_constraint_counts follows grinder deferral order.',
        },
        'package_count_total': package_count_total,
        'omitted_package_count': omitted_package_count,
        'packages': packages,
        'claim_policy': 'Planning is not recovery evidence or promotion. Never copy original bytes into reconstructed outputs; do not relock fixtures or infer semantic names from numeric containers.',
    }


def plan(node=None, ids=None, limit=512, max_packages=8, max_unknown_calls=1, max_data_references=40):
    """Public repo-backed entry point used by the grinder supervisor."""
    return build_plan(evidence()['functions'], ranked(node), recovery(), node=node,
                      ids=ids, limit=limit, max_packages=max_packages,
                      max_unknown_calls=max_unknown_calls, max_data_references=max_data_references)


def main(argv=None):
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node')
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--limit', type=int, default=512)
    parser.add_argument('--max-packages', type=int, default=8)
    parser.add_argument('--max-unknown-calls', type=int, default=1)
    parser.add_argument('--max-data-references', type=int, default=40)
    args = parser.parse_args(argv)
    print(json.dumps(plan(args.node, args.ids, args.limit, args.max_packages,
                          args.max_unknown_calls, args.max_data_references), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
