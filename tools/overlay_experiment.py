"""Validate independent overlay linking and a complete candidate segload contribution.

No linker masking, fixed placement, or game code enters the experiment build.
Shape equality is explicitly weaker than matching the game's content/layout.
"""
import argparse
import json
from pathlib import Path
import re
from common import require, sha256, write_json
from census import verify_lock, derive
from hunk import parse, manx_overlay, overlay_shape as shape

ROOT=Path(__file__).resolve().parents[1]


def symbols(text):
    result={};hunk=None
    for line in text.splitlines():
        header=re.fullmatch(r'Segment ([0-9a-fA-F]+):\s+Hunk ([0-9a-fA-F]+)',line)
        if header:
            hunk=int(header[2],16)
            continue
        entry=re.fullmatch(r'\s+([0-9a-fA-F]{8}) (\S+)',line)
        if entry:
            require(hunk is not None,'symbol before hunk header')
            key=(hunk,entry[2]);require(key not in result,'duplicate symbol in map')
            result[key]=int(entry[1],16)
    return result


def relocation_profile(model,hunk,start,size):
    result=[]
    for r in model['relocations']:
        if r['source_hunk']!=hunk:
            continue
        lo,hi=r['source_offset'],r['source_offset']+r['width']
        if hi<=start or lo>=start+size:
            continue
        require(lo>=start and hi<=start+size,'relocation straddles contribution boundary')
        result.append(dict(offset=lo-start,type=r['type'],width=r['width'],
                           target_hunk=r['target_hunk'],addend=r['addend_raw']))
    return sorted(result,key=lambda r:(r['offset'],r['type']))


def contribution(blob,model,hunk,start,size):
    h=next(h for h in model['hunks'] if h['number']==hunk)
    require(h['type']=='CODE' and start>=0 and size>0 and start+size<=h['initialized_size'],
            'contribution outside initialized CODE')
    return blob[h['content_offset']+start:h['content_offset']+start+size]


def verified_job(job):
    receipt=json.loads((job/'result.json').read_text());work=job/'sys/work'
    require(receipt['all_steps_succeeded'] and all(s['returncode']==0 for s in receipt['steps']),
            'overlay experiment has failed steps')
    for item in receipt['artifacts']:
        require(sha256((work/item['path']).read_bytes())==item['sha256'],'job artifact changed')
    return receipt,work


def analyze(job,comparison_job):
    receipt,work=verified_job(job)
    candidate=(work/'topology').read_bytes();model=parse(candidate);tree=manx_overlay(model,candidate)
    sym=symbols((work/'topology.sym').read_text())
    start=sym[(0,'_segload')];manager=sym[(0,'.segload')];end=sym[(0,'.begin')]
    obj=(work/'segload.o').read_bytes()
    require(obj[:2]==b'AJ','unexpected object dialect')
    size=int.from_bytes(obj[10:14],'big')
    require(end-start==size==244 and manager-start==18,'segload contribution boundary mismatch')
    require(tree['manager_entry_offsets']==[manager],'symbol map and overlay bridge disagree')
    verify_lock(ROOT);_,files,original_model=derive(ROOT);original=files['DT1:DuckTales']
    original_tree=manx_overlay(original_model,original)
    require(shape(model,tree)==shape(original_model,original_tree),'overlay shape differs')
    original_manager=original_tree['manager_entry_offsets'][0]
    original_start=original_manager-(manager-start)
    generated=contribution(candidate,model,0,start,size)
    observed=contribution(original,original_model,0,original_start,size)
    require(generated==observed,'complete runtime contribution bytes differ')
    relocs=relocation_profile(model,0,start,size)
    require(relocs==relocation_profile(original_model,0,original_start,size),
            'runtime relocation profile differs')
    require(len(relocs)==2,'unexpected runtime relocation count')
    require([h['type'] for h in model['hunks'][:2]]==[h['type'] for h in original_model['hunks'][:2]]==['CODE','DATA'],
            'root relocation target types differ')
    other_receipt,other_work=verified_job(comparison_job)
    other_blob=(other_work/'sparse').read_bytes();other_model=parse(other_blob)
    other_symbols=symbols((other_work/'sparse.sym').read_text())
    other_start=other_symbols[(0,'_segload')]
    other_obj=(other_work/'segload.o').read_bytes()
    require(other_obj[:2]==b'CJ' and int.from_bytes(other_obj[10:14],'big')==size,
            '5.0a object extent differs')
    # Internal .segload is at +18; the next symbol after the contribution is
    # __wb_parse here, not .begin as in the 3.6a experiment.
    other_end=min(v for (h,n),v in other_symbols.items() if h==0 and v>other_start+18)
    require(other_end-other_start==size,'5.0a map does not corroborate extent')
    require(contribution(other_blob,other_model,0,other_start,size)==generated,
            '5.0a runtime bytes differ')
    require(relocation_profile(other_model,0,other_start,size)==relocs,
            '5.0a runtime relocation profile differs')
    return dict(schema_version=1,status='NATURAL_OVERLAY_SHAPE_AND_CANDIDATE_RUNTIME_VALIDATED',
        game_sha256=sha256(original),candidate_executable_sha256=sha256(candidate),
        receipt_sha256=sha256((job/'result.json').read_bytes()),job_name=receipt['request']['name'],
        shape=shape(model,tree),candidate_hunks=model['hunks'],candidate_overlay=tree,
        cross_release_counterexample=dict(candidate='Aztec Amiga 5.0a c.lib(segload)',
            job_name=other_receipt['request']['name'],object_sha256=sha256(other_obj),
            receipt_sha256=sha256((comparison_job/'result.json').read_bytes()),
            candidate_offset=other_start,size=size,bytes_equal=True,relocations_equal=True,
            conclusion='This complete runtime contribution cannot uniquely select 3.6a over 5.0a.'),
        runtime=dict(candidate_object='Aztec 3.6a SYS1:lib/c.lib(segload)',
                     object_sha256=sha256(obj),code_sha256=sha256(generated),size=size,
                     candidate_hunk=0,candidate_offset=start,game_hunk=0,game_offset=original_start,
                     manager_entry_delta=18,relocations=relocs,
                     boundary_basis='Named extracted AJ object code size equals symbol-map distance _segload to next .begin'),
        reconstruction_proof_level=None,reconstructed_game_source_bytes=0,
        limitations=['Shape agreement does not match full hunk contents, allocations or complete relocation tables.',
                     'Exact library code identity does not uniquely identify the historical compiler release.',
                     'Return code validates only the independent test program, not original game behavior.'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('job',type=Path)
    parser.add_argument('--comparison-job',type=Path,required=True)
    args=parser.parse_args();report=analyze(args.job,args.comparison_job)
    write_json(ROOT/'evidence/experiments/overlay-topology.json',report)
    print('Natural shape verified; complete segload match:',report['runtime']['size'],'bytes and',len(report['runtime']['relocations']),'relocations')
