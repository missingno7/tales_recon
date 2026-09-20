"""Compile latent ov11 gap candidates without granting source ownership."""
import argparse
from difflib import SequenceMatcher
import json

from analysis_support import ROOT,decoder,game,instruction
from common import require,sha256,write_json
from compiler_oracle import compile_many


CASES=(
    dict(id='ov11_LATENT_59E6',start=0x59e6,end=0x5a12,source='experiments/direct-recovery/ov11_LATENT_59E6-v1.c'),
    dict(id='ov11_LATENT_5CEA',start=0x5cea,end=0x5d14,source='experiments/direct-recovery/ov11_LATENT_5CEA-v1.c'),
)


def sequence(data):
    md=decoder();result=[];cursor=0
    while cursor<len(data):
        row=instruction(md,data,cursor);require(row is not None,'undecodable compiler contribution')
        result.append(row.mnemonic);cursor+=row.size
    return result


def build():
    blob,model,_=game();h=next(x for x in model['hunks'] if x['number']==11)
    data=blob[h['content_offset']:h['content_offset']+h['initialized_size']]
    sources=[(ROOT/case['source']).read_text() for case in CASES]
    compiled=compile_many([dict(source=source,profile='aztec36',target_node=9) for source in sources])
    results=[]
    for case,source,item in zip(CASES,sources,compiled):
        require(item['status']=='COMPILED','latent candidate did not compile: '+case['id'])
        expected=data[case['start']:case['end']];actual=bytes.fromhex(item['contribution']['code_hex'])
        first=next((i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b),None)
        results.append(dict(case,source_sha256=sha256(source.encode()),compiler=dict(profile='aztec36',cache_key=item['cache_key'],cache_hit=item['cache_hit'],identity=item['identity']),
                            expected_length=len(expected),actual_length=len(actual),expected_sha256=sha256(expected),actual_sha256=sha256(actual),
                            mnemonic_similarity=SequenceMatcher(None,sequence(expected),sequence(actual)).ratio(),
                            first_difference=None if first is None else dict(offset=first,expected=expected[first:first+16].hex(),actual=actual[first:first+16].hex()),
                            promotion_eligible=False))
    return dict(schema_version=1,kind='ov11_latent_gap_codegen_experiment',game_sha256=sha256(blob),cases=results,
                status='CODEGEN_SIMILAR_LAYOUT_ONLY',policy='Latent gap candidates are not function-ledger entries and cannot promote source ownership or recovered bytes.')


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report=build();write_json(ROOT/'evidence/experiments/linker-cycle-gap-codegen.json',report)
    print(json.dumps(dict(status=report['status'],cases=[dict(id=x['id'],expected=x['expected_length'],actual=x['actual_length'],mnemonics=x['mnemonic_similarity']) for x in report['cases']])))
