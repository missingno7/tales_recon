"""Map the physical ov11 source frontier needed by the cycle layout proof.

The interval is evidence for a future normal source unit.  It never classifies
the unclaimed bytes as code, invents a function boundary, or grants ownership.
"""
import argparse
import json

from analysis_support import ROOT
from common import require, sha256, write_json
from check_unit import proven_tail


HUNK = 11
START = 0x4790
END = 0x5962
RECOVERED = {'FUNCTION_CODE_MATCH', 'FUNCTION_WITH_DATA_MATCH', 'MODULE_MATCH', 'OVERLAY_NODE_MATCH'}


def contribution_end(span):
    return span.get('contribution_end', span['end'])


def contiguous_runs(spans, wanted):
    """Group only adjacent physical spans in the requested recovery class."""
    runs=[];current=[]
    for span in spans:
        if (span['recovery_state'] in RECOVERED) != wanted:
            if current:runs.append(current);current=[]
            continue
        if current and contribution_end(current[-1]) != span['start']:
            runs.append(current);current=[]
        current.append(span)
    if current:runs.append(current)
    return [dict(start=run[0]['start'],end=contribution_end(run[-1]),
                 size=contribution_end(run[-1])-run[0]['start'],
                 members=[x['id'] for x in run],promotion_eligible=False) for run in runs]


def build():
    evidence = json.loads((ROOT/'evidence/functions/ledger.json').read_text())
    recovery = json.loads((ROOT/'recovery/ledger.json').read_text())
    functions = sorted((f for f in evidence['functions']
                        if f['hunk'] == HUNK and START <= f['start'] and f['end'] <= END),
                       key=lambda f: f['start'])
    require(functions and functions[0]['start'] == START and functions[-1]['end'] == END,
            'physical interval is not bounded by discovered candidates')
    cursor = START
    gaps = []
    spans = []
    for f in functions:
        require(f['start'] >= cursor, 'overlapping candidate extents')
        if cursor < f['start']:
            gaps.append(dict(start=cursor, end=f['start'], size=f['start']-cursor,
                             state='UNCLAIMED', promotion_eligible=False))
        state = recovery.get('functions', {}).get(f['id'], {}).get('state', 'DISCOVERED')
        span=dict(id=f['id'], start=f['start'], end=f['end'], size=f['size'],
                  confidence=f['confidence'], recovery_state=state,
                  direct_callees=[c['id'] for c in f['direct_callees']],
                  contribution_end=f['end'], promotion_eligible=False)
        if state == 'FUNCTION_WITH_DATA_MATCH':
            tail, ownership = proven_tail(f, recovery)
            item = recovery['functions'][f['id']]
            proof_bytes = (ROOT/item['proof']).read_bytes()
            require(sha256(proof_bytes) == item['proof_sha256'],
                    'canonical CODE-data proof receipt hash changed')
            proof = json.loads(proof_bytes)
            claimed = proof['data_ownership']
            require(len(tail) == claimed['actual_tail_length'] and
                    sha256(tail) == claimed['actual_tail_sha256'] == claimed['expected_tail_sha256'],
                    'canonical CODE-data contribution changed')
            span['contribution_end'] = ownership['end']
            span['owned_code_data'] = dict(
                start=ownership['start'], end=ownership['end'], size=len(tail),
                sha256=sha256(tail), alignment_padding=ownership['alignment_padding'],
                strings=ownership['strings'], proof=item['proof'],
                proof_sha256=item['proof_sha256'])
        require(span['contribution_end'] <= END, 'compiler-owned contribution exceeds physical interval')
        spans.append(span)
        cursor = span['contribution_end']
    if cursor < END:
        gaps.append(dict(start=cursor, end=END, size=END-cursor,
                         state='UNCLAIMED', promotion_eligible=False))
    canonical = [s for s in spans if s['recovery_state'] in RECOVERED]
    pending = [s for s in spans if s['recovery_state'] not in RECOVERED]
    in_interval={s['id'] for s in spans}
    states={s['id']:s['recovery_state'] for s in spans}
    for span in spans:
        internal=[callee for callee in span['direct_callees'] if callee in in_interval]
        span['layout_dependencies']=dict(
            internal=internal,
            recovered=[callee for callee in internal if states[callee] in RECOVERED],
            pending=[callee for callee in internal if states[callee] not in RECOVERED])
    return dict(
        schema_version=2, kind='ov11_cycle_physical_layout_frontier',
        interval=dict(hunk=HUNK, start=START, end=END, size=END-START),
        evidence_inputs=dict(function_ledger_sha256=sha256((ROOT/'evidence/functions/ledger.json').read_bytes()),
                             recovery_ledger_sha256=sha256((ROOT/'recovery/ledger.json').read_bytes())),
        candidate_spans=spans, unclaimed_spans=gaps,
        source_layout_capsule=dict(
            canonical_runs=contiguous_runs(spans,True),
            pending_runs=contiguous_runs(spans,False),
            contract=('Recover each pending span through its normal function verifier, preserve this physical order '
                      'when assembling a larger source unit, and explain every unclaimed span independently. '
                      'The runs are planning evidence only and never source ownership.')),
        summary=dict(candidate_count=len(spans), canonical_candidate_count=len(canonical),
                     canonical_candidate_bytes=sum(s['size'] for s in canonical),
                     unrecovered_candidate_count=len(pending),
                     unrecovered_candidate_bytes=sum(s['size'] for s in pending),
                     unclaimed_bytes=sum(s['size'] for s in gaps)),
        status='LAYOUT_FRONTIER_ONLY', promotion_eligible=False,
        next_action=('Recover the remaining candidates in this physical order before attempting another normal '
                     'source-layout proof. Account for separately proved compiler-owned CODE-data contributions '
                     'as part of their owning source object. Do not add padding or copied original bytes to force '
                     'the call distance.'),
        policy=('This audit is a planning receipt only. It must not update the function census, recovery ledger, '
                'source ownership, or recovered-byte total.'))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build()
    write_json(ROOT/'evidence/experiments/linker-cycle-layout-frontier.json', report)
    print(json.dumps(dict(status=report['status'], interval=report['interval']['size'],
                          candidates=report['summary']['candidate_count'],
                          unrecovered=report['summary']['unrecovered_candidate_count'],
                          unclaimed=report['summary']['unclaimed_bytes'])))
