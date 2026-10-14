"""Replayed complete runtime specimens; validation accounting, never a build."""
import json
from pathlib import Path
from common import require, sha256
from repo_paths import canonical_path, candidate_path
from resident_mixed import pinned
import runtime_members as relocated
import runtime_natural_members as natural

SEG_JOB = 'build/worker-jobs/runtime-segload-c36'
DATA = [('FORMAT_LOCAL_DIGITS', 'format', 18), ('_ctp_', 'ctype', 130),
        ('_Cbuffs', 'getbuff', 440)]


def checked_report(root, path, replay):
    require(json.loads(canonical_path(root,path).read_text()) ==
            json.loads(json.dumps(replay)), 'runtime accounting proof stale: '+path)


def specimen(identity, hn, start, raw, **proof):
    return dict(id=identity,hunk=hn,start=start,end=start+len(raw),
                actual_hex=raw.hex(),actual_sha256=sha256(raw),
                representation="RESOLVED_VALIDATION_COMPARISON",**proof)


def resolve_fields(raw, start, fields):
    """Derive values from independently proved coordinates, never oracle bytes."""
    out=bytearray(raw);seen=set()
    for r in fields:
        if 'field' not in r:continue
        off=r['field'];width=r['width']
        require(width==2 and 0<=off<=len(raw)-width, 'runtime field extent differs')
        require(not seen.intersection(range(off,off+width)), 'runtime fields overlap')
        seen.update(range(off,off+width));hn,target=r['original']
        if r['kind']=='PC':
            require(hn==0, 'runtime PC target hunk differs')
            value=target-(start+r['site']+2)
        else:
            require(r['kind']=='A4', 'runtime unsupported field kind')
            if 'original_slot' in r:
                slot=r['original_slot']
                require(slot['slot_hunk']==1, 'runtime route slot hunk differs')
                target=slot['slot_offset']
            else:require(hn==1, 'runtime A4 target hunk differs')
            value=target-32766
        require(-32768<=value<=32767, 'runtime field width changed')
        out[off:off+2]=value.to_bytes(2,'big',signed=True)
    return bytes(out)


def capture_runtime_members(root, blob, model):
    """Replay both complete proofs; payloads come only from producing artifacts."""
    root=Path(root).resolve()
    seg=relocated.relocated_contribution(relocated.RELOCATED_SPECS[0],blob,model,root=root)
    replay=dict(schema_version=1,game_sha256=sha256(blob),status='COMPLETE_RUNTIME_CODE_MATCH',
        contributions=[seg],limitations=['Root hunk-origin RELOC32 identities only; no normalization.',
        'Nonzero owned DATA/BSS requires a separate complete ownership proof.'],
        reconstructed_game_functions=0,exact_compiler_release_selected=False)
    checked_report(root,relocated.RELOCATED_OUTPUT,replay)
    work=root/SEG_JOB/'sys/work';obj=(work/'segload36.o').read_bytes()
    archive=pinned(root,'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib')
    require(archive.count(obj)==1, 'runtime segload object not unique in pinned archive')
    linked=(work/'segload36').read_bytes();lm=natural.parse(linked)
    raw=natural.extent(linked,lm,0,0,seg['size']);o=seg['original']
    rels=[dict(source_offset=o['offset']+r['offset'],target_hunk=r['target']['hunk'],
               type=r['type'],width=r['width'],addend_raw=r['target']['addend'])
          for r in seg['relocation_identity']]
    # Preserve parser record order, deriving each field from the proved identity.
    rels.sort(key=lambda r: next(i for i,x in enumerate(model['relocations']) if
        x['source_hunk']==o['hunk'] and all(x[k]==v for k,v in r.items())))
    result=[specimen('runtime_member_segload',o['hunk'],o['offset'],raw,
        relocations=rels,proof=dict(receipt=relocated.RELOCATED_OUTPUT,member='segload',
        relocation_identity=seg['relocation_identity'],object_sha256s=seg['object_sha256s']))]
    recipe=json.loads(canonical_path(root,natural.RECIPE).read_text())
    report=natural.verify(root,recipe=recipe,original=(blob,model))
    checked_report(root,natural.OUTPUT,report)
    contexts=natural.producer(root,recipe)
    for row in report['contributions']:
        spec=natural.SPECS[row['member']];o=row['original'];payloads=[]
        for prefix in ('natural','reverse'):
            b,m,sm=contexts[prefix];start=natural.symbol(sm,spec['export'])[1]+spec['delta']
            raw=natural.extent(b,m,0,start,row['size'])
            payloads.append(resolve_fields(raw,o['offset'],row['operand_identity']))
        require(payloads[0]==payloads[1] and sha256(payloads[0])==row['code_sha256'],
                'runtime resolved specimens differ')
        result.append(specimen('runtime_member_'+row['member'],o['hunk'],o['offset'],payloads[0],
            relocations=[],proof=dict(receipt=natural.OUTPUT,member=row['member'],
            provider=row['provider'],operand_identity=row['operand_identity'],
            object_sha256s=row['object_sha256s'])))
    for symbol,member,size in DATA:
        ids=[c['identities'][symbol] for c in report['contexts']];payloads=[]
        for prefix,identity in zip(('natural','reverse'),ids):
            b,m,_=contexts[prefix];hn,off=identity['candidate']
            payloads.append(natural.extent(b,m,hn,off,size))
        require(ids[0]['original']==ids[1]['original'] and ids[0]['size']==ids[1]['size']==size
                and payloads[0]==payloads[1] and sha256(payloads[0])==ids[0]['sha256']==ids[1]['sha256'],
                'runtime complete DATA specimens differ')
        hn,off=ids[0]['original']
        result.append(specimen('runtime_data_'+member,hn,off,payloads[0],relocations=[],
            proof=dict(receipt=natural.OUTPUT,member=member,symbol=symbol,identity=ids[0])))
    validate_disjoint(result)
    return json.loads(json.dumps(result))


def validate_disjoint(rows):
    seen=set();ids=set()
    for r in rows:
        require(r['id'] not in ids, 'duplicate runtime specimen identity');ids.add(r['id'])
        raw=bytes.fromhex(r['actual_hex'])
        require(r['start']>=0 and r['end']-r['start']==len(raw)>0 and
                sha256(raw)==r['actual_sha256'], 'runtime specimen length/hash differs')
        locations={(r['hunk'],i) for i in range(r['start'],r['end'])}
        require(not seen.intersection(locations), 'overlapping runtime specimens');seen.update(locations)


def contributions(rows):
    validate_disjoint(rows)
    return [dict(id=r['id'],hunk=r['hunk'],start=r['start'],end=r['end'],
                 category='PINNED_RUNTIME',bytes=bytes.fromhex(r['actual_hex']),
                 relocations=r['relocations']) for r in rows]


def merge_accounting(existing, runtime):
    """Only wbparse may replace existing 158 C + 22 literal accounting bytes.

    The accepted source proof remains canonical; accounting reports its exact
    pinned member once. Every other ownership collision fails.
    """
    out=list(existing)
    for row in runtime:
        overlaps=[r for r in out if r['hunk']==row['hunk'] and
                  r['start']<row['end'] and row['start']<r['end']]
        if overlaps:
            require(row['id']=='runtime_member_wbparse' and
                    (row['hunk'],row['start'],row['end'])==(0,0x7b24,0x7bd8) and
                    {(r['id'],r['start'],r['end'],r['category']) for r in overlaps}=={
                    ('resident_F_7B24',0x7b24,0x7bc2,'RECOVERED_C'),
                    ('resident_F_7B24_tail',0x7bc2,0x7bd8,'COMPILER_OWNED_DATA')},
                    'runtime accounting ownership overlap')
            require(all(r['bytes']==row['bytes'][r['start']-row['start']:r['end']-row['start']]
                        and not r.get('relocations') for r in overlaps), 'runtime reclassification bytes differ')
            out=[r for r in out if r not in overlaps]
        out.append(row)
    return out


def candidate_union(occupied, rows, overlay_extent):
    """CODE-only census metric; topology segload remains one contribution."""
    validate_disjoint(rows);out=set(occupied)
    for r in rows:
        if r['hunk']!=0:continue
        locations={(0,i) for i in range(r['start'],r['end'])}
        if out.intersection(locations):
            require(r['id']=='runtime_member_segload' and
                    (r['hunk'],r['start'],r['end'])==overlay_extent and locations<=out,
                    'overlapping runtime candidate contributions')
        out.update(locations)
    return out


def input_identity(root):
    """Snapshot closure includes explicit retained inputs, including ignored jobs."""
    root=Path(root).resolve();path=canonical_path(root,natural.RECIPE)
    if not path.exists():return {str(path):None}
    recipe=json.loads(path.read_text())
    paths={natural.RECIPE,natural.OUTPUT,relocated.RELOCATED_OUTPUT,recipe['sdk']['path'],
           recipe['request']['path'],recipe['receipt']['path'],*recipe['tools']}
    paths.update(recipe['work']+'/'+name for name in recipe['artifacts'])
    for anchor in recipe['anchors'].values():paths.update((anchor['source'],anchor['proof']))
    paths.add(SEG_JOB+'/result.json')
    paths.update(SEG_JOB+'/sys/work/'+name for name in ('segload36.o','segload36','segload36.sym'))
    job=Path(recipe['request']['path']).parent.as_posix()
    paths.update(job+'/'+name for name in ('sys/s/startup-sequence','worker.uae','kick.rom'))
    values={str(candidate_path(root,root/p)):sha256(candidate_path(root,root/p).read_bytes()) for p in paths}
    request=json.loads(candidate_path(root,root/recipe['request']['path']).read_text())
    emulator=Path(request['emulator']).resolve()
    values[str(emulator)]=sha256(emulator.read_bytes())
    return values
