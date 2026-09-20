"""Measure the contiguous recoverable ov11 cycle cluster as one source object.

This is a module-layout experiment, not a function verifier. It intentionally
retains A4/global placement and external-binding differences rather than
normalizing them into source ownership claims.
"""
import argparse
from difflib import SequenceMatcher
import json

from analysis_support import ROOT,decoder,game,instruction
from common import require,sha256,write_json
from compiler_oracle import compile_many


SOURCE=ROOT/'experiments/direct-recovery/ov11_cycle_cluster-v1.c'
MEMBERS=(
    ('ov11_F_4610',0x4610,0x4696),('ov11_F_5962',0x5962,0x59e6),
    ('ov11_LATENT_59E6',0x59e6,0x5a12),('ov11_F_5A12',0x5a12,0x5a62),
    ('ov11_F_5A62',0x5a62,0x5ab0),('ov11_F_5AB0',0x5ab0,0x5bc4),
    ('ov11_F_5BC4',0x5bc4,0x5c1a),('ov11_F_5C1A',0x5c1a,0x5c42),
    ('ov11_F_5C42',0x5c42,0x5cea),('ov11_LATENT_5CEA',0x5cea,0x5d14),
)


def decoded(data):
    md=decoder();result=[];cursor=0
    while cursor<len(data):
        row=instruction(md,data,cursor);require(row is not None,'undecodable code contribution')
        result.append(dict(offset=cursor,size=row.size,raw=bytes(row.bytes).hex(),mnemonic=row.mnemonic,operands=row.op_str))
        cursor+=row.size
    return result


def mechanism(expected,actual):
    if expected['mnemonic']=='jsr' and 'pc' in expected['operands']:
        return 'PC_RELATIVE_LAYOUT_DISPLACEMENT' if 'pc' in actual['operands'] else 'FORWARD_EXTERNAL_CALL_BINDING'
    if 'a4' in expected['operands'] or 'a4' in actual['operands']:
        return 'A4_GLOBAL_LAYOUT'
    return 'OTHER_CODEGEN_DIFFERENCE'


def build():
    source=SOURCE.read_text();compiled=compile_many([dict(source=source,profile='aztec36',target_node=9)])[0]
    require(compiled['status']=='COMPILED','cycle cluster did not compile')
    blob,model,_=game();hunk=next(x for x in model['hunks'] if x['number']==11)
    original=blob[hunk['content_offset']:hunk['content_offset']+hunk['initialized_size']]
    actual=bytes.fromhex(compiled['contribution']['code_hex']);cursor=0;members=[]
    for fid,start,end in MEMBERS:
        expected=original[start:end];piece=actual[cursor:cursor+len(expected)];cursor+=len(expected)
        left=decoded(expected);right=decoded(piece);require(len(left)==len(right),'instruction count differs: '+fid)
        differences=[]
        for expected_instruction,actual_instruction in zip(left,right):
            if expected_instruction['raw']!=actual_instruction['raw']:
                differences.append(dict(offset=expected_instruction['offset'],kind=mechanism(expected_instruction,actual_instruction),
                                        expected=expected_instruction,actual=actual_instruction))
        members.append(dict(id=fid,start=start,end=end,size=len(expected),expected_sha256=sha256(expected),actual_sha256=sha256(piece),
                            mnemonic_similarity=SequenceMatcher(None,[x['mnemonic'] for x in left],[x['mnemonic'] for x in right]).ratio(),
                            instruction_differences=differences,
                            promotion_eligible=False))
    require(cursor==len(actual),'unexpected cluster code contribution length')
    return dict(schema_version=1,kind='ov11_cycle_cluster_codegen_experiment',game_sha256=sha256(blob),
                source=dict(path=SOURCE.relative_to(ROOT).as_posix(),sha256=sha256(source.encode())),
                compiler=dict(profile='aztec36',cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],identity=compiled['identity']),
                comparison=dict(expected_length=cursor,actual_length=len(actual),mnemonic_similarity=SequenceMatcher(None,[x['mnemonic_similarity'] for x in members],[1.0]*len(members)).ratio()),
                members=members,status='CODEGEN_SIMILAR_LAYOUT_ONLY',promotion_eligible=False,
                policy='This receipt is a mechanism map only. It must not update the function census, recovery ledger, source ownership, or recovered bytes.')


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report=build();write_json(ROOT/'evidence/experiments/linker-cycle-cluster.json',report)
    print(json.dumps(dict(status=report['status'],expected=report['comparison']['expected_length'],actual=report['comparison']['actual_length'],
                          mechanisms=sorted({d['kind'] for member in report['members'] for d in member['instruction_differences']}))))
