"""Audit the two unclaimed code windows that separate the ov11 call cycle.

These windows are deliberately kept outside the recursive function ledger:
they have no permitted discovery seed.  The audit records their local
instruction evidence for future complete-module reconstruction without
promoting heuristic boundaries into recovered functions.
"""
import argparse
import json

from analysis_support import ROOT,decoder,game,instruction
from common import require,sha256,write_json


WINDOWS=(
    dict(id='ov11_LATENT_59E6',hunk=11,start=0x59e6,end=0x5a12,
         predecessor='ov11_F_5962',successor='ov11_F_5A12'),
    dict(id='ov11_LATENT_5CEA',hunk=11,start=0x5cea,end=0x5d14,
         predecessor='ov11_F_5C42',successor='ov11_F_5D14'),
)


def decode_window(data,start,end):
    md=decoder();result=[];cursor=start
    while cursor<end:
        row=instruction(md,data,cursor)
        require(row is not None and cursor+row.size<=end,'window contains undecodable or overrun bytes')
        result.append(dict(offset=cursor,size=row.size,raw=bytes(row.bytes).hex(),mnemonic=row.mnemonic,operands=row.op_str))
        cursor+=row.size
    require(cursor==end,'window did not decode exactly')
    require(result[0]['mnemonic'].startswith('link') and result[-1]['mnemonic']=='rts',
            'window is not bounded by a normal function prologue/return')
    return result


def build():
    blob,model,_=game();functions=json.loads((ROOT/'evidence/functions/ledger.json').read_text())['functions']
    by_id={f['id']:f for f in functions};hunks={h['number']:h for h in model['hunks']}
    output=[]
    for spec in WINDOWS:
        h=hunks[spec['hunk']];data=blob[h['content_offset']:h['content_offset']+h['initialized_size']]
        before=by_id[spec['predecessor']];after=by_id[spec['successor']]
        require(before['hunk']==spec['hunk'] and before['end']==spec['start'],'predecessor no longer bounds latent window')
        require(after['hunk']==spec['hunk'] and after['start']==spec['end'],'successor no longer bounds latent window')
        raw=data[spec['start']:spec['end']]
        output.append(dict(spec,raw_bytes=raw.hex(),sha256=sha256(raw),instructions=decode_window(data,spec['start'],spec['end']),
                           entry_evidence='ADJACENT_TO_CLOSED_CFG_RETURN_ONLY',confidence='LATENT',
                           promotion_eligible=False,
                           policy='Do not add this window to function recovery coverage until an allowed entry seed or complete-module boundary proof exists.'))
    return dict(schema_version=1,kind='ov11_cyclic_gap_audit',game_sha256=sha256(blob),
                tool_sha256=sha256((ROOT/'tools/cycle_gap_audit.py').read_bytes()),windows=output,
                conclusion='Both cycle-separating gaps decode as self-contained LINK...RTS windows, but neither has an allowed function-discovery seed. They remain latent layout evidence, not recovered functions.')


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report=build();write_json(ROOT/'evidence/experiments/linker-cycle-gap-audit.json',report)
    print(json.dumps(dict(windows=len(report['windows']),status='LATENT_NOT_PROMOTABLE')))
