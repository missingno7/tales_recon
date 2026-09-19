"""Prove complete arithmetic library contributions and their exported entries."""
import argparse
import json
from pathlib import Path
from analysis_support import game, ROOT
from common import require, sha256, write_json
from runtime_match import code, find_matches
from overlay_experiment import symbols


def aliases(compiled, blob, original, original_model, evidence):
    """Resolve library symbols only after complete original and linked byte proofs."""
    require(evidence['game_sha256'] == sha256(original), 'runtime oracle identity changed')
    c=compiled['contribution']; result=[]; proofs=[]
    for item in evidence['contributions']:
        if item['profile'] != compiled['identity']['profile'] or item['library_sha256'] != compiled['identity']['library_sha256']:
            continue
        extent=item['original']; size=item['size']
        require(size > 0 and extent['size'] == size, 'bad runtime extent')
        oh=next(h for h in original_model['hunks'] if h['number']==extent['hunk'])
        require(oh['type']=='CODE' and 0<=extent['offset']<=oh['initialized_size']-size, 'runtime outside original CODE')
        start=oh['content_offset']+extent['offset']
        require(sha256(original[start:start+size])==item['code_sha256'], 'original runtime changed')
        require(not any(r['source_hunk']==extent['hunk'] and r['source_offset']<extent['offset']+size and r['source_offset']+r['width']>extent['offset'] for r in original_model['relocations']), 'original runtime needs relocation proof')
        for entry in item['entries']:
            require(0<=entry['offset']<size, 'runtime entry outside contribution')
            matches=[s for s in c['symbols'] if s['name']==entry['name']]
            if len(matches)!=1:continue
            s=matches[0]; offset=s['offset']-entry['offset']
            h=next(h for h in c['hunks'] if h['number']==s['hunk'])
            if h['type']!='CODE' or not 0<=offset<=h['initialized_size']-size:continue
            if any(r['source_hunk']==s['hunk'] and r['source_offset']<offset+size and r['source_offset']+r['width']>offset for r in c['all_relocations']):continue
            at=h['content_offset']+offset
            if sha256(blob[at:at+size])!=item['code_sha256']:continue
            name='F_h%02d_%04X'%(extent['hunk'],extent['offset']+entry['offset'])
            result.append(dict(hunk=s['hunk'],offset=s['offset'],name=name))
            proofs.append(dict(symbol=entry['name'],identity=name,original=extent,
                               linked=dict(hunk=s['hunk'],offset=offset,size=size),
                               code_sha256=item['code_sha256'],library_sha256=item['library_sha256']))
    return result,proofs


def analyze(job):
    receipt = json.loads((job/'result.json').read_text())
    require(receipt['all_steps_succeeded'], 'runtime experiment failed')
    work = job/'sys/work'
    for item in receipt['artifacts']:
        require(sha256((work/item['path']).read_bytes()) == item['sha256'], 'runtime artifact changed')
    original, model, _ = game()
    results = []
    for prefix, profile, library in (
        ('mul36', 'aztec36', 'aztec-3.6a/SYS1/lib/c.lib'),
        ('mul50', 'aztec50-short', 'aztec-5.0a/Aztec2/lib/c16.lib')):
        obj = (work/(prefix+'.o')).read_bytes()
        require(obj[:2] in (b'AJ', b'CJ'), 'unsupported object')
        size = int.from_bytes(obj[10:14], 'big')
        require(obj[14:22] == bytes(8), 'runtime owns data/BSS')
        linked = code((work/prefix).read_bytes())
        require(size > 0 and len(linked) == (size+3)//4*4 and linked[size:] == bytes((-size)%4), 'runtime extent mismatch')
        raw = linked[:size]
        matches = find_matches(original, model, raw)
        require(len(matches) == 1, 'runtime does not match uniquely')
        entries = [dict(name=n, offset=o) for (h,n),o in symbols((work/(prefix+'.sym')).read_text()).items()
                   if h == 0 and not n.startswith('__H')]
        require(entries and all(0 <= e['offset'] < size for e in entries), 'invalid runtime entries')
        results.append(dict(profile=profile, library_sha256=sha256((ROOT/'toolchain/installed'/library).read_bytes()),
                            object_sha256=sha256(obj), code_sha256=sha256(raw), size=size,
                            original=matches[0], entries=entries))
    return dict(schema_version=1, game_sha256=sha256(original), status='COMPLETE_RUNTIME_CODE_MATCH',
                job_receipt_sha256=sha256((job/'result.json').read_bytes()), contributions=results,
                reconstructed_game_functions=0, exact_compiler_release_selected=False)


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('job', type=Path)
    args=ap.parse_args()
    result=analyze(args.job)
    write_json(ROOT/'evidence/experiments/runtime-arithmetic.json', result)
    print(json.dumps(result, indent=2))
