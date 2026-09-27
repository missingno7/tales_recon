"""Shift-tolerant M68K comparison diagnostics.

This module is advisory evidence only. Its output never establishes semantic,
source, or machine-code equality and is not read by the exact verifier.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from analysis_support import K, ROOT, decoder, instruction, basic
from common import FormatError, sha256
from compiler_oracle import cached
from check_function import validated_function

SCHEMA_VERSION = 1


def _decode(raw: bytes, data_spans=()):
    """Decode a complete byte extent, refusing partial/invalid instruction streams."""
    md = decoder()
    spans = sorted((int(a), int(b)) for a, b in data_spans)
    out, pc, si = [], 0, 0
    while pc < len(raw):
        while si < len(spans) and pc == spans[si][0]:
            if spans[si][1] <= pc or spans[si][1] > len(raw):
                return None, dict(offset=pc, reason='INVALID_DATA_SPAN')
            pc = spans[si][1]
            si += 1
        if si < len(spans) and spans[si][0] < pc < spans[si][1]:
            return None, dict(offset=pc, reason='OVERLAPPING_DATA_SPAN')
        ins = instruction(md, raw, pc)
        if ins is None:
            return None, dict(offset=pc, reason='UNDECODABLE_OR_TRUNCATED')
        out.append(ins)
        pc += ins.size
    if si < len(spans):
        return None, dict(offset=spans[si][0], reason='UNCONSUMED_DATA_SPAN')
    return out, None


def _mnemonic(ins):
    return ins.mnemonic.lower()


def _stem(ins):
    # Keep operation families alignable when the width suffix is itself the
    # hypothesis under review (move.w vs move.l, etc.).
    return _mnemonic(ins).split('.', 1)[0]


def _operand_shape(ins):
    shapes = []
    for op in ins.operands:
        if op.type == K.M68K_OP_REG:
            shapes.append(('reg',))
        elif op.type == K.M68K_OP_IMM:
            shapes.append(('imm',))
        elif op.type == K.M68K_OP_MEM:
            shapes.append(('mem', int(op.address_mode)))
        elif op.type == K.M68K_OP_BR_DISP:
            shapes.append(('branch',))
        else:
            shapes.append(('other', int(op.type)))
    return tuple(shapes)


def _token(ins):
    return (_stem(ins), _operand_shape(ins))


def _branch_target(ins):
    if not _is_branch(ins):
        return None
    if not ins.operands:
        return None
    op = ins.operands[-1]
    if op.type == K.M68K_OP_BR_DISP:
        return int(ins.address) + 2 + int(op.br_disp.disp)
    if op.type == K.M68K_OP_MEM and op.address_mode == K.M68K_AM_PCI_DISP:
        return int(ins.address) + 2 + int(op.mem.disp)
    return None


def _is_branch(ins):
    mn = _stem(ins)
    if mn in ('bra', 'jmp') or _is_conditional(mn):
        return True
    return mn in ('dbra', 'dbf') or bool(re.fullmatch(r'db(?:cc|cs|eq|ge|gt|hi|le|ls|lt|mi|ne|pl|t|vc|vs)', mn))


def _is_conditional(mn):
    return bool(re.fullmatch(r'b(?:cc|cs|eq|f|ge|gt|hi|le|ls|lt|mi|ne|pl|t|vc|vs)', mn.split('.', 1)[0]))


def _is_unconditional(ins):
    return _stem(ins) in ('bra', 'jmp')


def _is_return(ins):
    return _stem(ins) in ('rts', 'rte', 'rtr', 'rtm')


def _insn_record(ins):
    return basic(ins)


def _alignment(expected, actual):
    """Coarse instruction alignment which tolerates inserted code and shifts."""
    akeys = [_token(x) for x in expected]
    bkeys = [_token(x) for x in actual]
    matcher = difflib.SequenceMatcher(None, akeys, bkeys, autojunk=False)
    pairs, expected_only, actual_only = [], [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                pairs.append(dict(expected_index=i, actual_index=j, kind='shape', confidence='coarse'))
        elif tag == 'replace':
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                pairs.append(dict(expected_index=i1+k, actual_index=j1+k, kind='substitution', confidence='low'))
            expected_only.extend(range(i1+n, i2))
            actual_only.extend(range(j1+n, j2))
        elif tag == 'delete':
            expected_only.extend(range(i1, i2))
        else:
            actual_only.extend(range(j1, j2))
    pairs.sort(key=lambda p: (p['expected_index'], p['actual_index']))
    return pairs, expected_only, actual_only, matcher.ratio()


def _blocks(insns):
    if not insns:
        return [], dict(reason='EMPTY_CODE')
    by_off = {int(i.address): i for i in insns}
    leaders = {int(insns[0].address)}
    for idx, ins in enumerate(insns):
        mn = _mnemonic(ins)
        target = _branch_target(ins)
        if target is not None:
            if target not in by_off:
                return None, dict(offset=int(ins.address), target=target, reason='CONTROL_TARGET_OUTSIDE_DECODED_EXTENT')
            leaders.add(target)
        if (_is_branch(ins) or _is_return(ins)) and idx + 1 < len(insns):
            leaders.add(int(insns[idx+1].address))
    sorted_leaders = sorted(leaders)
    result = []
    for i, start in enumerate(sorted_leaders):
        end = sorted_leaders[i+1] if i+1 < len(sorted_leaders) else int(insns[-1].address)+int(insns[-1].size)
        members = [x for x in insns if start <= int(x.address) < end]
        if not members:
            return None, dict(offset=start, reason='EMPTY_BLOCK')
        last = members[-1]
        target = _branch_target(last)
        mn = _mnemonic(last)
        term = ('return' if _is_return(last) else 'jump' if _is_unconditional(last) else
                'branch' if _is_branch(last) else None)
        result.append(dict(start=start, end=end, instructions=members, terminator=term, condition=mn.split('.', 1)[0] if term == 'branch' else None,
                           target=target, fallthrough=(not _is_unconditional(last) and not _is_return(last))))
    return result, None


def _registers(ins):
    regs = set()
    for op in ins.operands:
        if op.type == K.M68K_OP_REG:
            regs.add(ins.reg_name(op.reg))
        elif op.type == K.M68K_OP_MEM:
            for r in (op.mem.base_reg, op.mem.index_reg):
                if r:
                    regs.add(ins.reg_name(r))
    return regs


def _register_roles(ins):
    """Ordered register use, retaining operand position and addressing role."""
    out = []
    for i, op in enumerate(ins.operands):
        if op.type == K.M68K_OP_REG:
            out.append((i, 'operand', ins.reg_name(op.reg)))
        elif op.type == K.M68K_OP_MEM:
            if op.mem.base_reg:
                out.append((i, 'base', ins.reg_name(op.mem.base_reg)))
            if op.mem.index_reg:
                out.append((i, 'index', ins.reg_name(op.mem.index_reg)))
    return out


def _mem_layout(op):
    return (int(op.address_mode), int(op.mem.base_reg), int(op.mem.index_reg),
            int(op.mem.scale), int(op.mem.disp))


def _hypotheses(expected, actual, pairs, expected_only, actual_only, exp_blocks, act_blocks):
    counts = {}
    examples = {}
    def add(kind, confidence, exp=None, act=None, note=None):
        cur = counts.setdefault(kind, dict(category=kind, count=0, confidence=confidence, evidence=[]))
        cur['count'] += 1
        if len(cur['evidence']) < 4:
            item = {}
            if exp is not None: item['expected'] = _insn_record(exp)
            if act is not None: item['actual'] = _insn_record(act)
            if note: item['note'] = note
            cur['evidence'].append(item)
    for p in pairs:
        e, a = expected[p['expected_index']], actual[p['actual_index']]
        before_count = sum(x['count'] for x in counts.values())
        if _is_branch(e) and _is_branch(a) and _mnemonic(e).split('.', 1)[0] != _mnemonic(a).split('.', 1)[0]:
            add('branch_condition_or_kind', 'medium', e, a,
                'Branch opcode/condition differs; matching target addresses would not prove matching edges.')
        if _mnemonic(e) != _mnemonic(a) and _stem(e) == _stem(a):
            add('operand_width', 'low', e, a, 'Mnemonic width suffix differs; this is a code-shape observation.')
        er, ar = _registers(e), _registers(a)
        eroles, aroles = _register_roles(e), _register_roles(a)
        if (er != ar or eroles != aroles) and _stem(e) == _stem(a):
            add('register_assignment', 'low', e, a,
                'Ordered register roles differ; register allocation or operand lifetime is a hypothesis, not a source claim.')
        frame_regs = tuple(r for r in (getattr(K, 'M68K_REG_A5', 0), getattr(K, 'M68K_REG_A6', 0), K.M68K_REG_A7) if r)
        frame_e = [o for o in e.operands if o.type == K.M68K_OP_MEM and o.mem.base_reg in frame_regs]
        frame_a = [o for o in a.operands if o.type == K.M68K_OP_MEM and o.mem.base_reg in frame_regs]
        if frame_e or frame_a:
            if [(o.mem.base_reg, o.mem.disp, o.address_mode) for o in frame_e] != [(o.mem.base_reg, o.mem.disp, o.address_mode) for o in frame_a]:
                add('frame_or_stack_reference', 'low', e, a, 'Frame-relative operand differs; slot ownership is unproved.')
        if bytes(e.bytes) != bytes(a.bytes):
            if _stem(e) in ('bsr', 'jsr') or _stem(a) in ('bsr', 'jsr'):
                add('call_target_or_encoding', 'low', e, a, 'Call encoding/target differs; callee identity is unresolved.')
            else:
                em = [o for o in e.operands if o.type == K.M68K_OP_MEM]
                am = [o for o in a.operands if o.type == K.M68K_OP_MEM]
                mem_diffs = []
                for eo, ao in zip(em, am):
                    if _mem_layout(eo) != _mem_layout(ao):
                        # Base/index register changes are handled as register
                        # assignment hypotheses. A layout hypothesis needs a
                        # changed displacement or addressing mode.
                        if eo.address_mode != ao.address_mode or eo.mem.disp != ao.mem.disp:
                            mem_diffs.append((eo, ao))
                a4 = getattr(K, 'M68K_REG_A4', 0)
                if any(eo.mem.base_reg == ao.mem.base_reg == a4 and
                       (eo.address_mode != ao.address_mode or eo.mem.disp != ao.mem.disp) for eo, ao in mem_diffs):
                    add('a4_global_layout', 'low', e, a, 'A4-relative displacement/addressing mode differs; symbol identity is unresolved.')
                elif any(eo.address_mode == K.M68K_AM_PCI_DISP and ao.address_mode == K.M68K_AM_PCI_DISP
                         and eo.mem.disp != ao.mem.disp for eo, ao in mem_diffs):
                    add('pc_relative_layout', 'low', e, a, 'PC-relative displacement differs; data-vs-control target is not inferred.')
                elif mem_diffs:
                    add('memory_reference_or_layout', 'low', e, a, 'Memory displacement/addressing mode differs; ownership is unresolved.')
                if any(eo.imm != ao.imm for eo, ao in zip(
                        [o for o in e.operands if o.type == K.M68K_OP_IMM],
                        [o for o in a.operands if o.type == K.M68K_OP_IMM])):
                    add('immediate_constant', 'low', e, a, 'Immediate value differs; semantic role is unknown.')
        after_count = sum(x['count'] for x in counts.values())
        if bytes(e.bytes) != bytes(a.bytes) and before_count == after_count and not (_is_branch(e) and _is_branch(a)):
            add('unknown_codegen', 'low', e, a,
                'Bytes differ without a classified operand change; retain this as unexplained code generation evidence.')
    if expected_only or actual_only:
        add('instruction_layout', 'medium', note='Unpaired instructions remain after shift-tolerant alignment.')
    if exp_blocks is None or act_blocks is None:
        add('control_flow_unresolved', 'low', note='At least one stream did not yield a fully bounded direct-target CFG.')
    else:
        if len(exp_blocks) != len(act_blocks):
            add('control_flow_shape', 'medium', note='Basic-block counts differ; block correspondence is incomplete.')
    return [counts[k] for k in sorted(counts)]


def compare_code(expected_bytes: bytes, actual_bytes: bytes, *, data_spans=()):
    """Compare two explicit extents for diagnostic guidance only.

    ``data_spans`` applies only to the expected stream. Candidate literal/data
    boundaries are not inferred. If expected evidence contains data, callers
    must independently supply a corresponding mapped candidate span or retain
    the unsupported result.
    """
    if data_spans:
        return dict(schema_version=SCHEMA_VERSION, status='UNSUPPORTED',
                    claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM',
                    reason='DATA_SPAN_MAPPING_REQUIRED_FOR_BOTH_STREAMS',
                    expected_extent=dict(bytes=len(expected_bytes)), actual_extent=dict(bytes=len(actual_bytes)),
                    alignment=None, blocks=None, hypotheses=[])
    exp, exp_bad = _decode(expected_bytes)
    act, act_bad = _decode(actual_bytes)
    base = dict(schema_version=SCHEMA_VERSION, claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM',
                expected_extent=dict(bytes=len(expected_bytes)), actual_extent=dict(bytes=len(actual_bytes)))
    if exp_bad or act_bad:
        base.update(status='UNSUPPORTED', reason='UNDECODABLE_OR_UNMAPPED_DATA_EXTENT',
                    decode=dict(expected=exp_bad, actual=act_bad), alignment=None, blocks=None, hypotheses=[])
        return base
    pairs, eo, ao, ratio = _alignment(exp, act)
    exp_blocks, ebad = _blocks(exp)
    act_blocks, abad = _blocks(act)
    idx_map = {p['expected_index']: p['actual_index'] for p in pairs}
    bpair, bunpaired = [], {'expected': [], 'actual': []}
    if exp_blocks is None or act_blocks is None:
        bunpaired['expected'] = [b['start'] for b in exp_blocks or []]
        bunpaired['actual'] = [b['start'] for b in act_blocks or []]
    else:
        actual_by_start = {b['start']: b for b in act_blocks}
        actual_starts = set(actual_by_start)
        by_exp_start = {b['start']: b for b in exp_blocks}
        by_act_start = {b['start']: b for b in act_blocks}
        paired_starts = {}
        for bi, eb in enumerate(exp_blocks):
            ei = next((i for i, x in enumerate(exp) if int(x.address) == eb['start']), None)
            mapped = idx_map.get(ei) if ei is not None else None
            candidate_start = int(act[mapped].address) if mapped is not None else None
            ab = actual_by_start.get(candidate_start)
            if ab is None:
                bunpaired['expected'].append(eb['start'])
                continue
            paired_starts[eb['start']] = ab['start']
            actual_starts.discard(candidate_start)
            target_state = 'not_applicable'
            if eb['terminator'] != ab['terminator'] or eb['condition'] != ab['condition']:
                target_state = 'different_or_unresolved'
            if eb['target'] is not None or ab['target'] is not None:
                mapped_target = None
                if eb['target'] is not None:
                    target_i = next((i for i, x in enumerate(exp) if int(x.address) == eb['target']), None)
                    ti = idx_map.get(target_i) if target_i is not None else None
                    mapped_target = int(act[ti].address) if ti is not None else None
                target_state = ('consistent' if target_state == 'not_applicable' and mapped_target is not None and mapped_target == ab['target']
                                else 'different_or_unresolved')
            if eb['fallthrough']:
                enext = exp_blocks[bi+1]['start'] if bi+1 < len(exp_blocks) else None
                if enext is not None:
                    ni = next((i for i, x in enumerate(exp) if int(x.address) == enext), None)
                    na = idx_map.get(ni) if ni is not None else None
                    mapped_next = int(act[na].address) if na is not None else None
                    abi = next((i for i, b in enumerate(act_blocks) if b['start'] == ab['start']), None)
                    actual_next = act_blocks[abi+1]['start'] if abi is not None and abi+1 < len(act_blocks) else None
                    if mapped_next is None or actual_next != mapped_next or not ab['fallthrough']:
                        target_state = 'different_or_unresolved'
            bpair.append(dict(expected_start=eb['start'], actual_start=ab['start'],
                              terminators=[eb['terminator'], ab['terminator']], conditions=[eb['condition'], ab['condition']], target_check=target_state,
                              confidence='coarse'))
        bunpaired['actual'] = sorted(actual_starts)
    hypotheses = _hypotheses(exp, act, pairs, eo, ao, exp_blocks, act_blocks)
    if any(b.get('target_check') == 'different_or_unresolved' for b in bpair):
        hypotheses.append(dict(category='control_flow_target_or_edge', count=sum(
            b.get('target_check') == 'different_or_unresolved' for b in bpair), confidence='low',
            evidence=[dict(note='Paired block targets, branch conditions, or fallthrough edges do not map cleanly.')]))
        hypotheses.sort(key=lambda h: h['category'])
    # Unresolved indirect transfers are surfaced instead of counted as CFG proof.
    indirect = []
    for side, stream in (('expected', exp), ('actual', act)):
        for ins in stream:
            if _stem(ins) in ('jmp', 'jsr') and _branch_target(ins) is None:
                indirect.append(dict(side=side, offset=int(ins.address), instruction=_insn_record(ins)))
    base.update(status='DIAGNOSTIC_ONLY', alignment=dict(instruction_similarity=round(ratio, 4),
        pairs=[dict(expected_offset=int(exp[p['expected_index']].address), actual_offset=int(act[p['actual_index']].address),
                    kind=p['kind'], confidence=p['confidence']) for p in pairs],
        expected_only=[_insn_record(exp[i]) for i in eo], actual_only=[_insn_record(act[i]) for i in ao]),
        blocks=dict(paired=bpair, unpaired=bunpaired, conservative=True,
                    unresolved_edges=dict(expected=ebad, actual=abad), indirect_transfers=indirect),
        hypotheses=hypotheses)
    first_shape = next((p for p in pairs if p['kind'] == 'substitution' or
                        _mnemonic(exp[p['expected_index']]) != _mnemonic(act[p['actual_index']])), None)
    first_unpaired = min([int(exp[i].address) for i in eo] + [int(act[i].address) for i in ao], default=None)
    if first_shape:
        p = first_shape
        base['first_nonreference_divergence'] = dict(expected=_insn_record(exp[p['expected_index']]),
            actual=_insn_record(act[p['actual_index']]), confidence='low',
            note='First coarse-aligned instruction-shape difference; operand reference identity is not evaluated.')
    elif first_unpaired is not None:
        if eo and (not ao or int(exp[eo[0]].address) <= int(act[ao[0]].address)):
            idx = eo[0]
            base['first_nonreference_divergence'] = dict(side='expected', instruction=_insn_record(exp[idx]), confidence='medium',
                note='First unpaired expected instruction after shift-tolerant alignment.')
        else:
            idx = ao[0]
            base['first_nonreference_divergence'] = dict(side='candidate', instruction=_insn_record(act[idx]), confidence='medium',
                note='First unpaired candidate instruction after shift-tolerant alignment.')
    else:
        base['first_nonreference_divergence'] = None
    return base


def diagnose(function_id: str, cache_key: str):
    """Load a closed original function and a validated cached standalone compile."""
    f, ledger = validated_function(function_id)
    compiled = cached(cache_key)
    if compiled is None:
        raise FormatError('compiler cache entry not found: '+cache_key)
    report = dict(schema_version=SCHEMA_VERSION, function=function_id,
                  original_extent=dict(hunk=f['hunk'], start=f['start'], end=f['end'], bytes=f['size'],
                                       extent_status=f['extent_status']),
                  cache_key=cache_key, compiler=compiled.get('identity', {}).get('profile'),
                  diagnostic_sha256=sha256((ROOT/'tools'/'diag.py').read_bytes()),
                  claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM')
    reason = None
    if f.get('extent_status') != 'CLOSED_CFG': reason = 'ORIGINAL_EXTENT_NOT_CLOSED_CFG'
    elif compiled.get('status') != 'COMPILED': reason = 'CACHED_COMPILER_OUTPUT_NOT_COMPILED'
    else:
        c = compiled.get('contribution') or {}
        ident = compiled.get('identity') or {}
        if int(c.get('entry_offset', 0)) != 0: reason = 'CANDIDATE_ENTRY_NOT_AT_OBJECT_START'
        elif len(ident.get('object_labels', ['candidate'])) != 1: reason = 'MULTI_OBJECT_UNIT_UNBOUNDED'
        elif c.get('data_size', 0) or c.get('bss_size', 0): reason = 'CANDIDATE_HAS_UNMAPPED_DATA_OR_BSS'
        elif any(s.get('hunk') == c.get('hunk') and s.get('name') not in ('_recovered', 'recovered')
                 and not re.fullmatch(r'__H\d+_(?:org|end)', s.get('name', ''))
                 and 0 <= s.get('offset', -1) < c.get('code_size', 0) for s in c.get('symbols', [])):
            reason = 'MULTIPLE_OR_UNIDENTIFIED_CODE_SYMBOLS'
    if reason:
        report.update(status='UNSUPPORTED', reason=reason, candidate_extent=None)
        return report
    raw = bytes.fromhex(compiled['contribution']['code_hex'])
    report['candidate_extent'] = dict(bytes=len(raw), hunk=compiled['contribution'].get('hunk'),
                                      entry_offset=compiled['contribution'].get('entry_offset', 0),
                                      boundary='ENTIRE_SINGLE_OBJECT_CODE_PAYLOAD; may include compiler-owned code data')
    if f.get('jump_tables') or any(r.get('kind') == 'PC_RELATIVE_DATA' for r in f.get('referenced_data', [])):
        report.update(status='UNSUPPORTED', reason='ORIGINAL_DATA_BOUNDARY_HAS_NO_MAPPED_CANDIDATE_BOUNDARY',
                      alignment=None, blocks=None, hypotheses=[dict(category='data_ownership_review', count=1,
                      confidence='high', evidence=[dict(note='Original contains separately evidenced data; candidate boundary is not independently mapped.')])])
        return report
    core = compare_code(bytes.fromhex(f['raw_bytes']), raw)
    report.update(core)
    report['provenance'] = dict(original_game_sha256=ledger['game_sha256'], cache_key=cache_key,
                                compiler_cache_hit=bool(compiled.get('cache_hit')),
                                diagnostic_sha256=report['diagnostic_sha256'])
    return report


def compact_summary(result, max_bytes=6000):
    """Return bounded, non-authoritative feedback suitable for attempt facts."""
    summary = dict(schema_version=SCHEMA_VERSION, status=result.get('status'),
                   claim='DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM',
                   function=result.get('function'), cache_key=result.get('cache_key'))
    if result.get('status') != 'DIAGNOSTIC_ONLY':
        summary['reason'] = result.get('reason', 'UNSUPPORTED')
        return summary
    align = result.get('alignment') or {}
    blocks = result.get('blocks') or {}
    summary['extents'] = dict(expected=(result.get('original_extent') or {}).get('bytes',
                                        (result.get('expected_extent') or {}).get('bytes')),
                              candidate=(result.get('candidate_extent') or {}).get('bytes',
                                        (result.get('actual_extent') or {}).get('bytes')))
    summary['instruction_similarity'] = align.get('instruction_similarity')
    summary['alignment_counts'] = dict(paired=len(align.get('pairs', [])),
                                       expected_only=len(align.get('expected_only', [])),
                                       actual_only=len(align.get('actual_only', [])))
    summary['hypotheses'] = []
    for h in result.get('hypotheses', []):
        examples = []
        for ex in h.get('evidence', [])[:4]:
            item = {k: ex[k] for k in ('note',) if k in ex}
            for side in ('expected', 'actual'):
                ins = ex.get(side)
                if ins:
                    item[side] = {k: ins[k] for k in ('offset', 'mnemonic', 'operands') if k in ins}
            examples.append(item)
        summary['hypotheses'].append(dict(category=h.get('category'), count=h.get('count'),
                                          confidence=h.get('confidence'), evidence=examples))
    first = result.get('first_nonreference_divergence')
    if first:
        summary['first_nonreference_divergence'] = {k: first[k] for k in ('side', 'confidence', 'note') if k in first}
        for side in ('expected', 'actual', 'instruction'):
            ins = first.get(side)
            if ins:
                summary['first_nonreference_divergence'][side] = {k: ins[k] for k in ('offset', 'mnemonic', 'operands') if k in ins}
    else:
        summary['first_nonreference_divergence'] = None
    summary['cfg'] = dict(paired_blocks=len(blocks.get('paired', [])),
                          expected_unpaired=len((blocks.get('unpaired') or {}).get('expected', [])),
                          actual_unpaired=len((blocks.get('unpaired') or {}).get('actual', [])),
                          target_checks={state: sum(b.get('target_check') == state for b in blocks.get('paired', []))
                                         for state in ('consistent', 'different_or_unresolved', 'not_applicable')},
                          condition_or_terminator_changes=sum(b.get('terminators', [None, None])[0] != b.get('terminators', [None, None])[1]
                              or b.get('conditions', [None, None])[0] != b.get('conditions', [None, None])[1]
                              for b in blocks.get('paired', [])),
                          unresolved_indirect=len(blocks.get('indirect_transfers', [])))
    unresolved_edges = blocks.get('unresolved_edges') or {}
    summary['cfg']['unresolved_edges'] = dict(expected=unresolved_edges.get('expected'),
                                               actual=unresolved_edges.get('actual'))
    summary['uncertainty'] = [
        'Coarse instruction alignment is heuristic and does not establish semantic correspondence.',
        'Reference identity, data ownership, and source intent are not proved by this report.'
    ]
    cats = {h.get('category') for h in result.get('hypotheses', [])}
    suggestions = []
    if 'register_assignment' in cats: suggestions.append('register roles or temporary lifetime')
    if 'operand_width' in cats: suggestions.append('expression or declaration width')
    if 'instruction_layout' in cats: suggestions.append('local statement structure around the inserted or missing instructions')
    if 'control_flow_shape' in cats or 'branch_condition_or_kind' in cats: suggestions.append('branch condition and block structure')
    if suggestions:
        summary['recommended_search_scope'] = suggestions
    elif cats.intersection({'a4_global_layout', 'pc_relative_layout', 'memory_reference_or_layout', 'call_target_or_encoding'}):
        summary['recommended_search_scope'] = ['reference identity and data-boundary evidence']
    else:
        summary['recommended_search_scope'] = ['inspect paired instruction evidence']
    encoded = json.dumps(summary, separators=(',', ':'), sort_keys=True).encode()
    if len(encoded) > max_bytes:
        for h in summary.get('hypotheses', []):
            h['evidence'] = h['evidence'][:1]
        summary['truncated'] = True
        if len(json.dumps(summary, separators=(',', ':'), sort_keys=True).encode()) > max_bytes:
            for h in summary.get('hypotheses', []): h['evidence'] = []
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('function', help='evidence function id, such as ov09_F_298E')
    ap.add_argument('--cache-key', required=True, help='validated key in build/compile-cache')
    ap.add_argument('--json', action='store_true', help='print the complete JSON diagnostic')
    args = ap.parse_args(argv)
    result = diagnose(args.function, args.cache_key)
    print(json.dumps(result, indent=2 if args.json else None, sort_keys=True))
    return 0 if result.get('status') == 'DIAGNOSTIC_ONLY' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError, OSError, KeyError, ValueError) as exc:
        print('ERROR: '+str(exc), file=sys.stderr)
        sys.exit(2)
