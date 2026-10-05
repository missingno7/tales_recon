"""Observed runtime targets with explicit loaded-overlay identity, never CFG closure.

History adjacency is advisory only: interrupts and ring-buffer gaps can occur.
Only records explicitly obtained by single stepping without an exception may
say an indirect edge occurred. All other records stay candidate observations.
"""
import argparse
import json
import sys
from pathlib import Path
from analysis_support import ROOT,game,decoder,instruction,K
from common import require,sha256,FormatError,write_json
from repo_paths import candidate_path


def analyze(document,blob,model):
    require(document['game_sha256']==sha256(blob),'runtime oracle identity changed')
    loads={};pcs=[];edges=[]
    for e in document['events']:
        kind=e['kind']
        if kind=='LOAD':
            epoch=e['epoch'];require(epoch not in loads,'duplicate load epoch')
            h=next((h for h in model['hunks'] if h['number']==e['hunk']),None)
            require(h and h['type']=='CODE' and e['node']==h['node'] and e['content_sha256']==h['sha256'],
                    'unproved runtime overlay identity')
            require(e['base']>=0,'invalid load base')
            loads[epoch]=dict(e,hunk_model=h,active=True)
        elif kind=='UNLOAD':
            require(e['epoch'] in loads and loads[e['epoch']]['active'],'unknown unload epoch')
            loads[e['epoch']]['active']=False
        elif kind=='PC':
            epoch=loads.get(e['epoch']);require(epoch and epoch['active'],'PC names inactive overlay epoch')
            h=epoch['hunk_model'];offset=e['pc']-epoch['base']
            require(0<=offset<h['initialized_size'],'PC outside loaded overlay')
            raw=blob[h['content_offset']:h['content_offset']+h['initialized_size']]
            ins=instruction(decoder(),raw,offset);require(ins is not None,'runtime PC is not statically decodable')
            require(bytes(ins.bytes).hex()==e['opcode_hex'],'runtime opcode disagrees with immutable image')
            pcs.append(dict(epoch=e['epoch'],node=h['node'],hunk=h['number'],pc=e['pc'],offset=offset))
            if ins.mnemonic.split('.')[0] in ('jmp','jsr'):
                op=ins.operands[-1]
                indirect=op.type!=K.M68K_OP_BR_DISP and op.address_mode not in (
                    K.M68K_AM_ABSOLUTE_DATA_LONG,K.M68K_AM_ABSOLUTE_DATA_SHORT,K.M68K_AM_PCI_DISP)
                if indirect and e.get('next_pc') is not None:
                    observed=e.get('acquisition')=='SINGLE_STEP' and e.get('exception') is False
                    edges.append(dict(source=pcs[-1],destination_pc=e['next_pc'],
                                      instruction=ins.mnemonic,confidence='OBSERVED_EDGE' if observed else 'CANDIDATE_HISTORY_EDGE',
                                      all_targets_proved=False))
        else:raise FormatError('unsupported runtime event: '+kind)
    return dict(schema_version=1,game_sha256=sha256(blob),pcs=pcs,indirect_edges=edges,
                proof_level=None,policy='Execution can establish this target occurred, never that these are all targets. Return to static table/extent proof.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('events',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    input_path=candidate_path(ROOT,a.events);output=candidate_path(ROOT,a.output)
    require(output.is_relative_to(ROOT/'build'),'runtime reports belong under build/')
    blob,model,_=game();write_json(output,analyze(json.loads(input_path.read_text()),blob,model))


if __name__=='__main__':
    try:main()
    except (FormatError,OSError,KeyError,ValueError) as e:print('BLOCKED: '+str(e),file=sys.stderr);sys.exit(1)
