"""Advisory diagnostics for a complete compiler-unit hypothesis.

A unit hypothesis names ordered original member functions (plus literal tails
already proved by the recovery ledger) and a compiled candidate unit from the
compile cache.  The candidate is bounded only by its own linked symbols and
object sizes; original lengths are never used to slice it.  Members are paired
to candidate contributions by established identity, then each pair reuses
``diag.compare_code`` with a ``diag.ReferenceResolver``.

Original bytes inside the unit interval that no member or proven literal
covers stay ``unknown``.  Candidate-only contributions are reported, never
assigned to a gap.  The output is search guidance only: the unit verdict still
comes exclusively from ``check_unit.py``.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

import diag
from analysis_support import ROOT
from common import FormatError, require, sha256

SCHEMA_VERSION = 1
CLAIM = 'ADVISORY_UNIT_DIAGNOSTIC_NO_EQUALITY_OWNERSHIP_OR_PROMOTION_CLAIM'
AUTHORITY = 'tools/check_unit.py (exact complete-unit comparison); this report never changes it'
_MARKER = re.compile(r'__H\d+_(?:org|end)')


# -- candidate side -----------------------------------------------------------
def _object_sizes(compiled):
    """Object CODE sizes from the candidate's own object files, in link order."""
    directory, prefix = compiled.get('directory'), compiled.get('prefix')
    labels = (compiled.get('identity') or {}).get('object_labels') or ['candidate']
    if not directory or not prefix:
        return None
    sizes = []
    for label in labels:
        p = Path(directory) / ((prefix if label == 'candidate' else prefix + '_' + label) + '.o')
        if not p.is_file():
            return None
        obj = p.read_bytes()
        if obj[:2] not in (b'AJ', b'CJ'):
            return None
        sizes.append((label, int.from_bytes(obj[10:14], 'big')))
    return sizes


def candidate_contributions(compiled):
    """Bound the candidate CODE payload by its own symbols and object sizes.

    Every byte belongs to exactly one segment.  A segment starts at a linked
    symbol or an object boundary; bytes before the next such point stay in the
    segment (a static function without a map symbol is therefore absorbed and
    flagged by ``unsymboled_asm_labels``).
    """
    c = compiled['contribution']
    raw = bytes.fromhex(c['code_hex'])
    size = len(raw)
    names = {}
    for s in c.get('symbols', []):
        if s.get('hunk') == c.get('hunk') and 0 <= s['offset'] < size and not _MARKER.fullmatch(s['name']):
            names.setdefault(s['offset'], []).append(s['name'])
    notes = []
    objects = _object_sizes(compiled)
    bounds = {0: None}
    if objects:
        cursor = 0
        for label, n in objects:
            bounds.setdefault(cursor, None)
            cursor += n
        if cursor != size:
            notes.append('OBJECT_SIZES_DO_NOT_SUM_TO_CODE_PAYLOAD:%d!=%d' % (cursor, size))
            objects = None
    points = sorted(set(names) | set(k for k in bounds if k < size) | ({0} if size else set()))
    obj_at = []
    if objects:
        cursor = 0
        for label, n in objects:
            obj_at.append((cursor, cursor + n, label))
            cursor += n
    segs = []
    for i, start in enumerate(points):
        end = points[i + 1] if i + 1 < len(points) else size
        label = next((lab for lo, hi, lab in obj_at if lo <= start < hi), None)
        segs.append(dict(index=i, start=start, end=end, length=end - start, names=sorted(names.get(start, [])),
                         object=label, bytes=raw[start:end]))
    asm_labels = []
    asm = Path(compiled.get('directory') or '.') / ((compiled.get('prefix') or '') + '.asm')
    if compiled.get('directory') and asm.is_file():
        linked = {n for v in names.values() for n in v}
        text = asm.read_text(errors='replace')
        public = set(re.findall(r'^\s+public\s+(_\w+)\s*$', text, re.M))
        for m in re.finditer(r'^(_\w+):', text, re.M):
            if m[1] in public and m[1] not in linked:
                asm_labels.append(m[1])
    return segs, dict(bytes=size, hunk=c.get('hunk'), objects=[dict(label=l, bytes=n) for l, n in objects] if objects else None,
                      unsymboled_asm_labels=asm_labels, notes=notes,
                      boundary='CANDIDATE_LINKED_SYMBOLS_AND_OBJECT_SIZES_ONLY')


def _candidate_code_extent(raw):
    """Split a contribution at its own lowest in-contribution PC-relative data target.

    Returns (code_end, literal_basis).  Only used when the original member has
    a proven literal tail; the split uses candidate references, never the
    original length.
    """
    md = diag.decoder()
    targets, pc, seen = [], 0, []
    while pc < len(raw):
        if targets and pc >= min(targets):
            break
        ins = diag.instruction(md, raw, pc)
        if ins is None:
            break
        for op in ins.operands:
            if op.type == diag.K.M68K_OP_MEM and op.address_mode == diag.K.M68K_AM_PCI_DISP and diag._stem(ins) not in ('bsr', 'jsr', 'jmp'):
                t = pc + 2 + int(op.mem.disp)
                if 0 < t < len(raw):
                    targets.append(t)
        pc += ins.size
    if targets and pc == min(targets):
        return pc, 'CANDIDATE_PC_RELATIVE_LITERAL_TARGET'
    if not targets and pc == len(raw):
        return len(raw), 'CANDIDATE_FULLY_DECODED_NO_LITERAL'
    return None, 'CANDIDATE_LITERAL_BOUNDARY_UNMAPPED'


def _identity(names, ctx):
    """Candidate contribution names -> original (hunk, start) identity."""
    from function_compare import mechanical
    found = []
    for n in names:
        if n in ctx['entry']:
            found.append((ctx['entry'][n], n, 'unit_entry_convention'))
            continue
        m = mechanical(n)
        if m and m[2] == 'F':
            found.append(((m[0], m[1]), n, 'mechanical_proxy_name'))
        elif n in ctx['recovered']:
            found.append((ctx['recovered'][n], n, 'recovered_function_ids'))
    keys = {f[0] for f in found}
    if len(keys) > 1:
        return None, 'CONFLICTING_CANDIDATE_NAMES'
    if not found:
        return None, 'NO_ESTABLISHED_BINDING' if names else 'UNSYMBOLED_CANDIDATE_BYTES'
    return dict(hunk=found[0][0][0], start=found[0][0][1], symbol=found[0][1], basis=found[0][2]), None


def _member_compiled(compiled, seg):
    """A copy of the candidate whose code/relocations are one bounded segment."""
    piece = copy.copy(compiled)
    c = dict(compiled['contribution'])
    c['code_hex'] = seg['bytes'].hex()
    c['code_size'] = seg['length']
    c['code_offset'] = seg['start']
    c['relocations'] = [dict(r, relative_offset=r['relative_offset'] - seg['start']) for r in compiled['contribution'].get('relocations', [])
                        if seg['start'] <= r['relative_offset'] < seg['end']]
    piece['contribution'] = c
    return piece


class UnitReferenceResolver(diag.ReferenceResolver):
    """ReferenceResolver plus the explicit unit entry-symbol convention.

    ``check_unit`` renames the target member to ``recovered``; the hypothesis
    names that member, so ``_recovered`` binds to it with its own basis label.
    """

    def __init__(self, f, ledger, compiled, entry=None, tail_bytes=0, **kw):
        super().__init__(f, ledger, compiled, **kw)
        self.entry = dict(entry or {})
        self.fid = f.get('id')
        self.end = int(f.get('end', self.start))
        self.tail_bytes = int(tail_bytes)
        c = compiled['contribution']
        self.cand_literal = (c.get('candidate_literal_start'), int(c.get('code_size', 0)))

    # A PC-relative operand into a member's proven literal tail binds to the
    # same byte offset of the candidate's own literal bundle (bounded by the
    # candidate's own lowest PC-relative literal target, never original lengths).
    def expected(self, ins, i, kind):
        if kind == 'pc' and self.tail_bytes:
            t = self.start + int(ins.address) + 2 + int(ins.operands[i].mem.disp)
            if self.end <= t < self.end + self.tail_bytes:
                return dict(key=('literal:' + str(self.fid), t - self.end), symbol=None,
                            basis='proven_literal_tail'), None
        return super().expected(ins, i, kind)

    def actual(self, ins, i, kind):
        lit, size = self.cand_literal
        if kind == 'pc' and lit is not None:
            t = int(ins.address) + 2 + int(ins.operands[i].mem.disp)
            if lit <= t < size:
                return dict(key=('literal:' + str(self.fid), t - lit), symbol=None,
                            basis='candidate_pc_relative_literal_bundle'), None
        return super().actual(ins, i, kind)

    def _bind(self, hunk, offset, function=False):
        ident, why = super()._bind(hunk, offset, function)
        if ident is None:
            for s in self.symbol_map:
                if s['hunk'] == hunk and s['offset'] == offset and s['name'] in self.entry:
                    return dict(key=self.entry[s['name']], symbol=s['name'], addend=0, basis='unit_entry_convention'), None
        return ident, why


# -- core ---------------------------------------------------------------------
def _brief(ins):
    return {k: ins[k] for k in ('offset', 'mnemonic', 'operands') if k in ins} if ins else None


def _member_report(m, seg, compiled, resolver_factory):
    orig_code = m['bytes']
    tail = m.get('tail') or b''
    expected_len = len(orig_code) + len(tail)
    out = dict(id=m['id'], original=dict(start=m['start'], end=m['end'], bytes=len(orig_code), proven_tail_bytes=len(tail)),
               candidate=dict(segment=seg['index'], offset=seg['start'], bytes=seg['length'], names=seg['names'], object=seg['object']),
               length_delta=seg['length'] - expected_len)
    cand = seg['bytes']
    code_end = None
    if tail:
        code_end, basis = _candidate_code_extent(cand)
        out['candidate_literal_boundary'] = basis
        if code_end is None:
            out.update(state='literal_boundary_unmapped', comparison=None)
            return out
        out['literal'] = dict(original_bytes=len(tail), candidate_bytes=len(cand) - code_end,
                              bytes_equal=cand[code_end:] == tail)
        cand = cand[:code_end]
    resolver, resolver_error = None, None
    if resolver_factory is not None:
        try:
            piece = _member_compiled(compiled, seg)
            if tail and code_end is not None:
                piece['contribution']['candidate_literal_start'] = code_end
            resolver = resolver_factory(m, piece)
        except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
            resolver_error = type(exc).__name__ + ': ' + str(exc)
    core = diag.compare_code(orig_code, cand, resolver=resolver)
    if core.get('status') != 'DIAGNOSTIC_ONLY':
        out.update(state='comparison_unsupported', comparison=dict(status=core.get('status'), reason=core.get('reason'),
                                                                   decode=core.get('decode')))
        return out
    align = core['alignment']
    refs = core['reference_identity']['counts']
    groups = {g: v for g, v in core['hypothesis_groups'].items() if v['total']}
    aligned = not align['expected_only'] and not align['actual_only']
    literal_ok = out.get('literal', {}).get('bytes_equal', True)
    if orig_code + tail == seg['bytes']:
        state = 'same_bytes'
    elif out['length_delta'] == 0 and aligned and not core['hypotheses'] and literal_ok and \
            refs['different_identity'] == 0 and refs['unresolved'] == 0:
        state = 'same_after_reference_identity'
    elif not core['hypotheses'] and aligned and literal_ok and refs['different_identity'] == 0:
        state = 'no_shape_difference_references_unresolved'
    else:
        state = 'differs'
    first = core.get('first_nonreference_divergence')
    out.update(state=state, comparison=dict(
        aligned=aligned, instruction_similarity=align['instruction_similarity'],
        paired=len(align['pairs']), expected_only=len(align['expected_only']), actual_only=len(align['actual_only']),
        hypothesis_groups=groups,
        categories={h['category']: h['count'] for h in core['hypotheses']},
        reference_identity=refs,
        unresolved_reasons=core['reference_identity'].get('unresolved_reasons', {}),
        first_divergence=({k: (_brief(v) if isinstance(v, dict) else v) for k, v in first.items() if k in ('side', 'expected', 'actual', 'instruction')}
                          if first else None),
        register_first_divergence=((lambda fd: dict(expected=_brief(fd.get('expected')), actual=_brief(fd.get('actual'))) if fd else None)(
            (core.get('register_trace') or {}).get('first_divergence')))))
    if resolver_error:
        out['comparison']['resolver_error'] = resolver_error
    if resolver is not None and getattr(resolver, 'notes', None):
        out['comparison']['resolver_notes'] = list(resolver.notes)
    return out


def analyze_unit(members, compiled, *, discovered=(), interval=None, entry_member=None, resolver_factory=None,
                 recovered_ids=None, rejected_ranges=(), new_members=None):
    """Diagnose a unit hypothesis against one compiled candidate.

    ``members``: ordered dicts with id, hunk, start, end, bytes and optional
    proven ``tail`` bytes (already established by evidence).  ``discovered``:
    (id, hunk, start, end) for every discovered original function, used only to
    name identities and to list discovered extents inside unknown gaps.
    ``resolver_factory(member, member_compiled)`` returns a reference resolver
    or None (bytes-only comparison).  ``new_members`` names the members whose
    source the candidate authors (``check_unit --member`` plus the entry); the
    rest are canonical bridges.  It only labels rows.  No ownership is assigned.
    """
    members = sorted(members, key=lambda m: m['start'])
    require(members, 'unit hypothesis has no members')
    require(len({m['hunk'] for m in members}) == 1, 'unit members cross original CODE hunks')
    new_members = None if new_members is None else sorted(set(new_members))
    require(new_members is None or set(new_members) <= {m['id'] for m in members},
            'new members are not in the unit hypothesis')
    hunk = members[0]['hunk']
    lo = min(m['start'] for m in members)
    hi = max(m['end'] + len(m.get('tail') or b'') for m in members)
    if interval is not None:
        lo, hi = interval
    report = dict(schema_version=SCHEMA_VERSION, claim=CLAIM, authority=AUTHORITY,
                  hypothesis=dict(hunk=hunk, interval=[lo, hi], members=[m['id'] for m in members],
                                  entry_member=entry_member))
    if new_members is not None:
        report['hypothesis']['new_members'] = new_members
    # Original coverage: members plus proven literal tails; the rest is unknown.
    covered, conflicts = [], []
    for m in members:
        covered.append((m['start'], m['end'], m['id'], 'function'))
        if m.get('tail'):
            covered.append((m['end'], m['end'] + len(m['tail']), m['id'], 'proven_literal_tail'))
    covered.sort()
    outside = [c[2] for c in covered if c[0] < lo or c[1] > hi]
    cursor, gaps = lo, []
    for a, b, fid, kind in covered:
        if a < cursor:
            conflicts.append(dict(id=fid, kind=kind, start=a, end=b, reason='OVERLAPS_PREVIOUS_CLAIM'))
        elif a > cursor:
            gaps.append((cursor, min(a, hi)))
        cursor = max(cursor, b)
    if cursor < hi:
        gaps.append((cursor, hi))
    gap_rows = []
    for a, b in gaps:
        if b <= a:
            continue
        inside = [d[0] for d in discovered if d[1] == hunk and a <= d[2] < b]
        gap_rows.append(dict(state='unknown', ownership='UNKNOWN_NOT_ASSIGNED', hunk=hunk, start=a, end=b,
                             offset=a - lo, length=b - a, discovered_function_starts_inside=inside))
    report['original'] = dict(
        claimed_bytes=sum(b - a for a, b, _, _ in covered if lo <= a and b <= hi),
        unknown_bytes=sum(g['length'] for g in gap_rows), unknown_gaps=gap_rows,
        claim_conflicts=conflicts, members_outside_interval=outside,
        rejected_owned_ranges=list(rejected_ranges))
    # Candidate segments and identity pairing.
    segs, cand_meta = candidate_contributions(compiled)
    by_key = {(m['hunk'], m['start']): m for m in members}
    disc = {(d[1], d[2]): d[0] for d in discovered}
    ctx = dict(entry={}, recovered=dict(recovered_ids or {}))
    if entry_member is not None:
        em = next((m for m in members if m['id'] == entry_member), None)
        require(em is not None, 'entry member is not in the unit hypothesis')
        ctx['entry']['_recovered'] = (em['hunk'], em['start'])
    paired, candidate_only, seen = {}, [], {}
    for seg in segs:
        ident, why = _identity(seg['names'], ctx)
        key = (ident['hunk'], ident['start']) if ident else None
        if key in by_key and key not in seen:
            seen[key] = seg['index']
            paired[by_key[key]['id']] = (seg, ident)
            continue
        row = dict(segment=seg['index'], offset=seg['start'], bytes=seg['length'], names=seg['names'], object=seg['object'],
                   ownership='CANDIDATE_ONLY_NOT_ASSIGNED')
        if ident:
            row['identity'] = dict(hunk=ident['hunk'], start=ident['start'], basis=ident['basis'])
            if key in seen:
                row['note'] = 'DUPLICATE_BINDING_TO_PAIRED_MEMBER:' + by_key[key]['id']
            elif key in disc:
                row['note'] = 'BINDS_TO_DISCOVERED_FUNCTION_OUTSIDE_HYPOTHESIS:' + disc[key]
            else:
                row['note'] = 'PROXY_IDENTITY_IS_NOT_A_DISCOVERED_FUNCTION_START'
                g = next((g for g in gap_rows if g['hunk'] == ident['hunk'] and g['start'] <= ident['start'] < g['end']), None)
                if g:
                    row['proxy_location_in_unknown_gap'] = [g['start'], g['end']]
        else:
            row['identity'] = None
            row['note'] = why
        candidate_only.append(row)
    results = []
    for m in members:
        if m['id'] not in paired:
            results.append(dict(id=m['id'], state='missing_in_candidate',
                                original=dict(start=m['start'], end=m['end'], bytes=len(m['bytes']),
                                              proven_tail_bytes=len(m.get('tail') or b''))))
            continue
        seg, ident = paired[m['id']]
        r = _member_report(m, seg, compiled, resolver_factory)
        r['pairing'] = dict(symbol=ident['symbol'], basis=ident['basis'])
        results.append(r)
    if new_members is not None:
        for r in results:
            r['authored'] = r['id'] in new_members
    report['members'] = results
    orig_order = [m['id'] for m in members if m['id'] in paired]
    cand_order = [mid for mid, _ in sorted(paired.items(), key=lambda kv: kv[1][0]['start'])]
    pos = {mid: i for i, mid in enumerate(cand_order)}
    inversions = [[a, b] for i, a in enumerate(orig_order) for b in orig_order[i + 1:] if pos[a] > pos[b]]
    paired_idx = sorted(seg['index'] for seg, _ in paired.values())
    interleaved = [c['segment'] for c in candidate_only if paired_idx and paired_idx[0] < c['segment'] < paired_idx[-1]]
    report['order'] = dict(original=orig_order, candidate=cand_order, matches=orig_order == cand_order,
                           inversions=inversions, candidate_only_segments_between_members=interleaved)
    report['candidate'] = dict(cand_meta, segments=len(segs), candidate_only=candidate_only,
                               candidate_only_bytes=sum(c['bytes'] for c in candidate_only),
                               paired_bytes=sum(seg['length'] for seg, _ in paired.values()))
    states = {}
    for r in results:
        states[r['state']] = states.get(r['state'], 0) + 1
    report['member_states'] = states
    report['unit_shape'] = dict(
        all_members_paired=len(paired) == len(members),
        all_members_same=all(r['state'] in ('same_bytes', 'same_after_reference_identity') for r in results),
        unknown_gap_count=len(gap_rows), candidate_only_count=len(candidate_only),
        order_matches=report['order']['matches'],
        total_length_delta=len(bytes.fromhex(compiled['contribution']['code_hex'])) -
        sum(len(m['bytes']) + len(m.get('tail') or b'') for m in members))
    return report


# -- repository loaders -------------------------------------------------------
def exact_receipts(cache_key, root=ROOT):
    """Existing check_unit receipts for this cache key (read-only)."""
    out = []
    for p in sorted((root / 'recovery' / 'units').glob('*/' + cache_key + '/*/receipt.json')):
        try:
            r = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        out.append(dict(path=p.relative_to(root).as_posix(), verdict=r.get('verdict'), reason=r.get('reason'),
                        target=r.get('id'), ordered_members=[m.get('id') for m in r.get('ordered_members', [])]))
    return out


def package_hypothesis(package_id, root=ROOT):
    """Members and interval of a recovery-plan dependency package."""
    plan = json.loads((root / 'evidence' / 'experiments' / 'recovery-plan.json').read_text())
    pkg = next((p for p in plan['packages'] if p['id'] == package_id), None)
    require(pkg is not None, 'unknown recovery-plan package ' + package_id)
    meta = pkg.get('metadata') or {}
    require(pkg.get('members_complete', False), 'package member list is truncated')
    ids = list(pkg['members']) + list(meta.get('canonical_bridge_ids', []))
    return dict(package=package_id, kind=pkg.get('kind'), members=ids,
                interval=tuple(meta['interval']) if meta.get('interval') else None,
                package_unclassified_gaps=meta.get('unclassified_gaps', []),
                unknown_bridge_ids=meta.get('unknown_bridge_ids', []))


def diagnose_unit(member_ids, cache_key, *, entry_member=None, interval=None, root=ROOT, new_members=None):
    """Load validated originals and a cached compile, then run ``analyze_unit``."""
    from check_function import validated_function
    from check_unit import proven_tail
    from compiler_oracle import cached
    from recovery_state import recovery
    compiled = cached(cache_key)
    require(compiled is not None, 'compiler cache entry not found: ' + cache_key)
    base = dict(schema_version=SCHEMA_VERSION, claim=CLAIM, authority=AUTHORITY, cache_key=cache_key,
                compiler=(compiled.get('identity') or {}).get('profile'),
                diagnostic_sha256=sha256((root / 'tools' / 'unit_diag.py').read_bytes()),
                exact_receipts=exact_receipts(cache_key, root))
    if compiled.get('status') != 'COMPILED':
        return dict(base, status='UNSUPPORTED', reason='CACHED_COMPILER_OUTPUT_NOT_COMPILED')
    rec = recovery()
    members, ledger, ledgers = [], None, {}
    for fid in member_ids:
        f, ledger = validated_function(fid)
        ledgers[fid] = f
        tail, _ = proven_tail(f, rec)
        members.append(dict(id=fid, hunk=f['hunk'], start=f['start'], end=f['end'],
                            bytes=bytes.fromhex(f['raw_bytes']), tail=tail))
    discovered = [(f['id'], f['hunk'], f['start'], f['end']) for f in ledger['functions']]
    recovered_ids = {}
    try:
        for r in json.loads((root / 'docs' / 'symbols.json').read_text()).get('recovered_functions', []):
            if r.get('state') == 'FUNCTION_CODE_MATCH':
                recovered_ids['_' + r['id']] = (int(r['hunk']), int(r['start']))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    entry = {}
    if entry_member is not None:
        em = next((m for m in members if m['id'] == entry_member), None)
        require(em is not None, 'entry member is not in the unit hypothesis')
        entry['_recovered'] = (em['hunk'], em['start'])

    def factory(m, piece):
        return UnitReferenceResolver(ledgers[m['id']], ledger, piece, entry=entry,
                                     tail_bytes=len(m.get('tail') or b''), root=root)

    report = analyze_unit(members, compiled, discovered=discovered, interval=interval, entry_member=entry_member,
                          resolver_factory=factory, recovered_ids=recovered_ids, new_members=new_members)
    report.update({k: v for k, v in base.items() if k not in report})
    report['status'] = 'DIAGNOSTIC_ONLY'
    report['exact_verdict'] = (sorted({r['verdict'] for r in report['exact_receipts']})
                               or 'NOT_RUN_FOR_THIS_CACHE_KEY')
    report['provenance'] = dict(original_game_sha256=ledger['game_sha256'], cache_key=cache_key,
                                compiler_cache_hit=bool(compiled.get('cache_hit')))
    return report


def compact_summary(report, max_bytes=5000):
    """Bounded fleet-worker feedback (default <= 5 KB)."""
    s = dict(schema_version=SCHEMA_VERSION, claim=CLAIM, status=report.get('status'),
             exact_verdict=report.get('exact_verdict'), authority='check_unit.py',
             cache_key=report.get('cache_key'), hypothesis=report.get('hypothesis'))
    if report.get('status') not in (None, 'DIAGNOSTIC_ONLY'):
        s['reason'] = report.get('reason')
        return s
    s['unit_shape'] = report.get('unit_shape')
    s['member_states'] = report.get('member_states')
    s['unknown_gaps'] = [dict(start=g['start'], end=g['end'], length=g['length'],
                              discovered_inside=g['discovered_function_starts_inside'])
                         for g in report['original']['unknown_gaps']]
    s['candidate_only'] = [{k: c[k] for k in ('offset', 'bytes', 'names', 'note', 'proxy_location_in_unknown_gap') if c.get(k) is not None}
                           for c in report['candidate']['candidate_only']]
    if report['candidate'].get('unsymboled_asm_labels'):
        s['unsymboled_asm_labels'] = report['candidate']['unsymboled_asm_labels']
    o = report['order']
    s['order'] = dict(matches=o['matches'], inversions=o['inversions'][:6],
                      candidate_only_between=o['candidate_only_segments_between_members'])
    rows = []
    for m in report['members']:
        row = dict(id=m['id'], state=m['state'])
        if 'authored' in m:
            row['new'] = m['authored']
        if 'length_delta' in m:
            row['delta'] = m['length_delta']
        cmp_ = m.get('comparison') or {}
        if cmp_.get('instruction_similarity') is not None:
            row['sim'] = cmp_['instruction_similarity']
            row['unpaired'] = [cmp_['expected_only'], cmp_['actual_only']]
            row['groups'] = {g: v['total'] for g, v in cmp_['hypothesis_groups'].items()}
            row['cats'] = cmp_['categories']
            row['refs'] = {k: v for k, v in cmp_['reference_identity'].items() if v}
            if cmp_.get('first_divergence'):
                row['first'] = cmp_['first_divergence']
        elif cmp_.get('reason'):
            row['reason'] = cmp_['reason']
        if m.get('literal'):
            row['literal'] = m['literal']
        rows.append(row)
    s['members'] = rows
    s['note'] = 'Unknown gaps are never assigned; candidate-only bytes are not ownership. Verdict comes from check_unit only.'

    def size():
        return len(json.dumps(s, separators=(',', ':'), sort_keys=True).encode())
    for step in ('first', 'cats', 'candidate_only', 'members'):
        if size() <= max_bytes:
            break
        s['truncated'] = True
        if step in ('first', 'cats'):
            for r in s['members']:
                r.pop(step, None)
        elif step == 'candidate_only':
            s['candidate_only'] = s['candidate_only'][:4]
        else:
            s['members'] = [r for r in s['members'] if r['state'] not in ('same_bytes', 'same_after_reference_identity')][:12]
    return s


def natural_receipt_summary(receipt, limit=8):
    """Bounded echo of a check_unit --natural-interval receipt (verdict authority stays check_unit)."""
    n = receipt.get('natural_interval') or {}
    crossings = n.get('gap_crossings') or []
    flagged = [c for c in crossings if c.get('classification') != 'GAP_INDEPENDENT_ENCODING']
    keep = ('member', 'kind', 'site', 'target_id', 'original_displacement', 'compact_displacement',
            'distance_delta', 'original_class', 'compact_class', 'classification')
    return dict(interval=n.get('interval'), receipt_verdict=receipt.get('verdict'), receipt_reason=receipt.get('reason'),
                member_verdict=receipt.get('member_verdict'), blocked_reason=n.get('blocked_reason'),
                compaction_spans=[{k: s.get(k) for k in ('start', 'end', 'size', 'kind')}
                                  for s in n.get('compaction_spans') or []],
                unknown_gaps=[[g['start'], g['end']] for g in n.get('unknown_gaps') or []],
                gap_crossing_counts=n.get('gap_crossing_counts'),
                flagged_crossings=[{k: c.get(k) for k in keep} for c in flagged[:limit]],
                canonical_not_equal=[c['id'] for c in receipt.get('canonical_regressions') or []
                                     if c.get('verdict') != 'EQUAL'])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache-key', required=True, help='validated key in build/compile-cache')
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--members', help='comma-separated original function ids')
    src.add_argument('--package', help='recovery-plan package id (members + canonical bridges, interval)')
    src.add_argument('--receipt', type=Path, help='check_unit receipt.json (ordered members, entry = target)')
    ap.add_argument('--entry', help='member compiled as `recovered` (check_unit target naming)')
    ap.add_argument('--new-members', help='comma-separated members authored by the candidate (entry plus check_unit --member ids)')
    ap.add_argument('--interval', help='START:END original hunk offsets (hex with 0x or decimal)')
    ap.add_argument('--json', action='store_true', help='print the full report instead of the compact summary')
    a = ap.parse_args(argv)
    interval, extra = None, {}
    entry = a.entry
    new_members = [x.strip() for x in a.new_members.split(',') if x.strip()] if a.new_members else None
    if a.package:
        h = package_hypothesis(a.package)
        ids, interval = h['members'], h['interval']
        extra = dict(package=h)
    elif a.receipt:
        r = json.loads(a.receipt.read_text())
        ids = [m['id'] for m in r['ordered_members']]
        entry = entry or r.get('id')
        if new_members is None and r.get('member_sources'):
            new_members = sorted(r['member_sources'])
        if r.get('natural_interval'):
            # Unknown gaps are measured over the claimed interval only; the
            # linked callees outside it are listed as outside members.
            interval = tuple(r['natural_interval']['interval'])
            extra = dict(natural_interval=natural_receipt_summary(r))
    else:
        ids = [x.strip() for x in a.members.split(',') if x.strip()]
    if a.interval:
        lo, hi = a.interval.split(':')
        interval = (int(lo, 0), int(hi, 0))
    report = diagnose_unit(ids, a.cache_key, entry_member=entry, interval=interval, new_members=new_members)
    report.update(extra)
    out = report if a.json else compact_summary(report)
    if extra.get('natural_interval'):
        out['natural_interval'] = extra['natural_interval']
    if extra.get('package') and report.get('original'):
        measured = [[g['start'], g['end']] for g in report['original']['unknown_gaps']]
        out['package_unclassified_gaps'] = extra['package']['package_unclassified_gaps']
        out['package_gaps_agree'] = measured == [list(g) for g in out['package_unclassified_gaps']]
    print(json.dumps(out, indent=2 if a.json else None, sort_keys=True, default=lambda b: b.hex() if isinstance(b, bytes) else str(b)))
    return 0 if report.get('status') == 'DIAGNOSTIC_ONLY' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError, OSError, KeyError, ValueError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)
