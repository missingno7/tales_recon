"""Map the physical ov11 source frontier needed by the cycle layout proof.

The interval is evidence for a future normal source unit.  It never classifies
the unclaimed bytes as code, invents a function boundary, or grants ownership.
"""
import argparse
import json

from analysis_support import ROOT
from common import require, sha256, write_json


HUNK = 11
START = 0x4790
END = 0x5962
RECOVERED = {'FUNCTION_CODE_MATCH', 'FUNCTION_WITH_DATA_MATCH', 'MODULE_MATCH', 'OVERLAY_NODE_MATCH'}


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
        spans.append(dict(id=f['id'], start=f['start'], end=f['end'], size=f['size'],
                          confidence=f['confidence'], recovery_state=state,
                          direct_callees=[c['id'] for c in f['direct_callees']],
                          promotion_eligible=False))
        cursor = f['end']
    if cursor < END:
        gaps.append(dict(start=cursor, end=END, size=END-cursor,
                         state='UNCLAIMED', promotion_eligible=False))
    canonical = [s for s in spans if s['recovery_state'] in RECOVERED]
    pending = [s for s in spans if s['recovery_state'] not in RECOVERED]
    return dict(
        schema_version=1, kind='ov11_cycle_physical_layout_frontier',
        interval=dict(hunk=HUNK, start=START, end=END, size=END-START),
        evidence_inputs=dict(function_ledger_sha256=sha256((ROOT/'evidence/functions/ledger.json').read_bytes()),
                             recovery_ledger_sha256=sha256((ROOT/'recovery/ledger.json').read_bytes())),
        candidate_spans=spans, unclaimed_spans=gaps,
        summary=dict(candidate_count=len(spans), canonical_candidate_count=len(canonical),
                     canonical_candidate_bytes=sum(s['size'] for s in canonical),
                     unrecovered_candidate_count=len(pending),
                     unrecovered_candidate_bytes=sum(s['size'] for s in pending),
                     unclaimed_bytes=sum(s['size'] for s in gaps)),
        status='LAYOUT_FRONTIER_ONLY', promotion_eligible=False,
        next_action=('Recover the remaining candidates and independently explain the unclaimed span in this '
                     'physical order before attempting another normal source-layout proof. Do not add padding '
                     'or copied original bytes to force the call distance.'),
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
