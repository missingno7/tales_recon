"""Verify relocation-free candidate object contributions against immutable game evidence.

The limited AJ header size interpretation is cross-checked by natural combined
linking. This is not a general Manx object parser or an exact-release selector.
"""
import argparse
import json
from pathlib import Path
from common import require, sha256, write_json
from hunk import parse
from census import verify_lock, derive

ROOT = Path(__file__).resolve().parents[1]
NAMES = 'index movmem strcat strcmp strcpy strlen strncpy'.split()


def code(data):
    model = parse(data)
    require(not model['relocations'], 'candidate has relocations: full resolution required')
    initialized = [h for h in model['hunks'] if h['initialized_size']]
    require(len(initialized) == 1 and initialized[0]['type'] == 'CODE', 'expected code-only contribution')
    h = initialized[0]
    return data[h['content_offset']:h['content_offset']+h['initialized_size']]


def find_matches(oracle, model, candidate):
    require(candidate, 'empty candidate')
    matches = []
    for h in model['hunks']:
        if h['type'] != 'CODE':
            continue
        raw = oracle[h['content_offset']:h['content_offset']+h['initialized_size']]
        start = 0
        while True:
            offset = raw.find(candidate, start)
            if offset < 0:
                break
            start = offset + 1
            if offset % 2:
                continue
            relocs = [r for r in model['relocations'] if r['source_hunk'] == h['number']
                      and r['source_offset'] < offset+len(candidate) and r['source_offset']+4 > offset]
            if not relocs:
                matches.append(dict(hunk=h['number'], offset=offset, size=len(candidate)))
    return matches


def analyze(job):
    receipt = json.loads((job/'result.json').read_text())
    work = job/'sys/work'
    for item in receipt['artifacts']:
        require(sha256((work/item['path']).read_bytes()) == item['sha256'], 'job artifact changed')
    verify_lock(ROOT)
    _, files, model = derive(ROOT)
    oracle = files['DT1:DuckTales']
    parts, objects = [], []
    for name in NAMES:
        linked = name+'-linked'
        step = next(s for s in receipt['steps'] if ' -o '+linked+' ' in s['command'])
        require(step['returncode'] == 0, 'candidate link failed')
        obj = (work/(name+'.o')).read_bytes()
        require(obj[:2] == b'AJ' and len(obj) >= 36, 'unsupported object header')
        size = int.from_bytes(obj[10:14], 'big')
        full = code((work/linked).read_bytes())
        require(size > 0 and size % 2 == 0 and len(full) == (size+3)//4*4, 'object/header HUNK sizes disagree')
        require(full[size:] == bytes(len(full)-size), 'nonzero candidate HUNK padding')
        part = full[:size];parts.append(part)
        objects.append(dict(name=name, object_sha256=sha256(obj), code_sha256=sha256(part), code_size=size,
                            candidate_relocations=0, matches=find_matches(oracle, model, part)))
    combined_step = next(s for s in receipt['steps'] if ' -o combined ' in s['command'])
    require(combined_step['returncode'] == 0, 'combined link failed')
    expected = b''.join(parts)
    require(code((work/'combined').read_bytes()) == expected + bytes((-len(expected)) % 4),
            'natural combined link does not corroborate object boundaries')
    return dict(schema_version=1, status='EXACT_CANDIDATE_OBJECT_CODE',
        game_sha256=sha256(oracle), job_receipt_sha256=sha256((job/'result.json').read_bytes()),
        candidate='Aztec Amiga 3.6a SYS1:lib/c.lib',
        candidate_library_sha256=sha256((ROOT/'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib').read_bytes()),
        objects=objects, matched_candidate_bytes=sum(o['code_size'] for o in objects if len(o['matches']) == 1),
        combined_link_size=len(expected), combined_link_padding=(-len(expected)) % 4,
        limitations=['No exact compiler release selection: runtime code can be shared across releases.',
                    'Object names may cover multiple entry points; these are not recovered game functions.',
                    'Only relocation-free contributions checked; no relocation masking or post-link patching.'],
        reconstructed_game_source_bytes=0, reconstruction_proof_level=None)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job',type=Path)
    args=parser.parse_args()
    result=analyze(args.job)
    write_json(ROOT/'evidence/experiments/runtime-matches.json',result)
    print('Unique candidate bytes matched:',result['matched_candidate_bytes'])
