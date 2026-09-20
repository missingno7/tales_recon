"""Measure the recoverable prefix of the ov11 reciprocal-call cluster.

The result is explicitly layout-only evidence. It cannot promote either the
ordinary function or the latent window because forward external-call binding
and the complete original module layout remain unproved.
"""
import argparse
from difflib import SequenceMatcher
import json

from analysis_support import ROOT,decoder,game,instruction
from common import require,sha256,write_json
from compiler_oracle import compile_many


SOURCE=ROOT/'experiments/direct-recovery/ov11_cycle_prefix-v1.c'
START=0x5962
END=0x5a12


def mnemonics(data):
    md=decoder();result=[];cursor=0
    while cursor<len(data):
        row=instruction(md,data,cursor)
        require(row is not None,'compiled prefix contains undecodable bytes')
        result.append(row.mnemonic);cursor+=row.size
    return result


def build():
    source=SOURCE.read_text();compiled=compile_many([dict(source=source,profile='aztec36',target_node=9)])[0]
    require(compiled['status']=='COMPILED','historical prefix experiment did not compile')
    blob,model,_=game();h=next(x for x in model['hunks'] if x['number']==11)
    data=blob[h['content_offset']:h['content_offset']+h['initialized_size']]
    expected=data[START:END];actual=bytes.fromhex(compiled['contribution']['code_hex'])
    first=next((i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b),None)
    expected_mnemonics=mnemonics(expected);actual_mnemonics=mnemonics(actual)
    return dict(schema_version=1,kind='ov11_cycle_prefix_codegen_experiment',game_sha256=sha256(blob),
                source=dict(path=SOURCE.relative_to(ROOT).as_posix(),sha256=sha256(source.encode())),
                compiler=dict(profile='aztec36',cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'],
                              identity=compiled['identity']),extent=dict(hunk=11,start=START,end=END,size=len(expected)),
                comparison=dict(expected_length=len(expected),actual_length=len(actual),expected_sha256=sha256(expected),
                                actual_sha256=sha256(actual),mnemonic_similarity=SequenceMatcher(None,expected_mnemonics,actual_mnemonics).ratio(),
                                first_difference=None if first is None else dict(offset=first,expected=expected[first:first+16].hex(),actual=actual[first:first+16].hex())),
                observed_bindings=dict(latent_backward_call='PC-relative JSR matches within the natural combined source object',
                                       forward_calls='remain external A4-relative JSRs until the larger physical source layout is reproduced'),
                status='CODEGEN_SIMILAR_LAYOUT_ONLY',promotion_eligible=False,
                policy='This experiment does not add a function-census entry, recovery ledger state, source ownership, or recovered bytes.')


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report=build();write_json(ROOT/'evidence/experiments/linker-cycle-prefix.json',report)
    print(json.dumps(dict(status=report['status'],comparison=report['comparison'])))
