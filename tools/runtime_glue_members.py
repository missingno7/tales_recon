"""Pinned complete resident glue members, including proved public forwarders.

The bounded recipe uses ordinary SDK assembly and library links in two DATA
orders. Every external operand is checked by identity; no masking is admitted.
"""
from names import read_source
import json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path
from hunk import parse
from overlay_experiment import symbols
import runtime_natural_members as n

RECIPE='evidence/contributions/runtime-glue-tail.json'
OUTPUT='evidence/experiments/runtime-members-glue.json'
RECIPE_DIGEST='d11de973cabe4312bb800d3757dfff78b40d967e830f495a6053332744373aa6'


def read(root,path):return (read_source(root, Path(root) / path, scratch=True, names_root=None) if str(path).startswith('src/') else candidate_path(root,Path(root)/path).read_bytes())

def checked(root,record):
    raw=read(root,record['path'])
    require(sha256(raw)==record['sha256'],'glue retained input changed: '+record['path'])
    return raw


def sdk_member(raw,name):
    parts=[]
    for chunk in raw.split(b'\x0c'):
        lines=chunk.splitlines(keepends=True)
        indexes=[i for i,line in enumerate(lines) if line.strip()==(name+'.a68').encode('ascii')]
        if indexes:
            require(len(indexes)==1,'glue duplicate SDK member')
            parts.append(b''.join(lines[indexes[0]+1:]).rstrip(b'\x1a'))
    require(len(parts)==1,'glue missing SDK member: '+name)
    return parts[0]


def producer(root,doc):
    request=json.loads(checked(root,doc['request']));receipt=json.loads(checked(root,doc['receipt']))
    require(receipt['request']==request and receipt['all_steps_succeeded'] and
            all(s['returncode']==0 for s in receipt['steps']) and
            [s['command'] for s in receipt['steps']]==doc['commands']==[s['command'] for s in request['steps']],
            'glue failed/different producing commands')
    require(doc['job'].startswith('build/worker-jobs/') and doc['work']==doc['job']+'/sys/work',
            'glue producer path differs')
    for path,key in [('sys/s/startup-sequence','guest_script_sha256'),('worker.uae','config_sha256'),('kick.rom','rom_sha256')]:
        require(sha256(read(root,doc['job']+'/'+path))==request[key],'glue producer environment changed')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'glue emulator changed')
    pins={p['path']:p['sha256'] for p in request['pinned_inputs']}
    for name in ('SYS1/bin/as','SYS1/bin/ln','SYS2/bin/lb','SYS1/lib/c.lib'):
        path='toolchain/installed/aztec-3.6a/'+name
        require(pins.get(path)==sha256(n.pinned(root,path)),'glue pinned tool/library differs')
    library=checked(root,doc['library'])
    require(library==n.pinned(root,doc['library']['path']),'glue unsupported library')
    archives={Path(a['path']).stem:checked(root,a) for a in doc['archives']}
    expected={r['member']+'.asm':sdk_member(archives[r['archive']],r['member']) for r in doc['producer_members']}
    names=[r['member'] for r in doc['producer_members']]
    commands=['Old2:bin/lb >extract.log Old1:lib/c.lib -x']
    commands+=['Old1:bin/as >'+name+'-as.log -o '+name+'-source.o '+name+'.asm' for name in names]
    commands+=['Old1:bin/as >'+name+'-as.log -o '+name+'.o '+name+'.asm' for name in ('one','two')]
    for order in ('one','two'):
        bases=doc['bases'] if order=='one' else list(reversed(doc['bases']))
        expected[order+'.asm']=('\tdseg\n'+''.join('\tpublic '+b+'\n'+b+'\n\tdc.l 0\n' for b in bases)).encode('ascii')
        for origin in ('lib','source'):
            prefix=order+'-'+origin
            objects=[m+('-source' if origin=='source' else '')+'.o' for m in names]+[order+'.o']
            expected[prefix+'.lnk']=' '.join(objects).encode('ascii')
            commands.append('Old1:bin/ln >'+prefix+'.log -m -t -o '+prefix+' -f '+prefix+'.lnk')
    require(commands==doc['commands'],'glue producer recipe differs')
    sources={s['path']:s['sha256'] for s in request['source_files']}
    require(set(sources)==set(expected),'glue source inventory differs')
    artifacts={a['path']:a for a in receipt['artifacts']}
    require(len(artifacts)==len(receipt['artifacts']),'glue duplicate artifact')
    def artifact(name):
        raw=read(root,doc['work']+'/'+name);a=artifacts.get(name)
        require(a and a['sha256']==sha256(raw) and a['size']==len(raw),'glue producing artifact changed: '+name)
        return raw
    for name,raw in expected.items():require(artifact(name)==raw and sources[name]==sha256(raw),'glue SDK/harness source differs')
    total=0;bounds={}
    for name in names:
        obj=artifact(name+'.o');source=artifact(name+'-source.o');size,ds,bs=n.object_sizes(obj)
        require(library.count(obj)==1 and obj[2:10].rstrip(b'\0').decode('ascii')==name,
                'glue complete object not unique in pinned archive')
        require(ds==bs==0 and n.object_sizes(source)==(size,0,0),'glue complete object extent differs')
        bounds[name]=(total,size);total+=size
    contexts={}
    for order in ('one','two'):
        for origin in ('lib','source'):
            prefix=order+'-'+origin;blob=artifact(prefix);model=parse(blob);sm=symbols(artifact(prefix+'.sym').decode('ascii'))
            require([(h['number'],h['type']) for h in model['hunks']]==[(0,'CODE'),(1,'DATA'),(2,'BSS')],
                    'glue natural hunk topology differs')
            require(n.symbol(sm,'__H0_end')==(0,(total+3)//4*4) and
                    n.extent(blob,model,0,total,(-total)%4)==bytes((-total)%4),
                    'glue complete natural CODE bounds differ')
            require(n.object_sizes(artifact(order+'.o'))==(0,24,0),'glue scalar base provider differs')
            for i,base in enumerate(doc['bases'] if order=='one' else reversed(doc['bases'])):
                require(n.symbol(sm,base)==(1,4*i),'glue DATA order control differs')
            contexts[prefix]=(blob,model,sm)
        require(contexts[order+'-lib']==contexts[order+'-source'],'glue whole SDK/library links differ')
    return contexts,bounds


def bases(root,doc,original):
    recipe=json.loads(canonical_path(root,n.RECIPE).read_text())
    crt=n.producer(root,recipe)['crt'];ids=n.bootstrap(crt,original)
    from startup_callees import dosbase
    require(dosbase(root,*original,ids['_SysBase']['original'][1],32766)==ids['_DOSBase']['original'][1],
            'glue independent DOS initializer differs')
    ledger=json.loads(canonical_path(root,'recovery/ledger.json').read_text())
    for fid,anchor in doc['anchors'].items():
        item=ledger['functions'][fid]
        require(all(item[k]==anchor[k] for k in anchor),'glue canonical initializer anchor changed')
        require(sha256(read(root,item['source']))==item['source_sha256'] and
                sha256(read(root,item['proof']))==item['proof_sha256'],'glue canonical anchor bytes changed')
        ex=item['evidence_extent']
        require(sha256(n.extent(*original,ex['hunk'],ex['start'],ex['size']))==ex['sha256'],'glue original anchor changed')
    for symbol,global_name,library,field in [('_GfxBase','5374','graphics',18),('_IntuitionBase','5378','intuition',68),('_LayersBase','537C','layers',444)]:
        a=doc['anchors']['ov04_F_1E36'];source=read(root,a['source']).decode('ascii');proof=json.loads(read(root,a['proof']))
        require('G_h01_'+global_name+' = F_h00_89D0("'+library+'.library", 0L)' in source,'glue SDK library handle role differs')
        rows=[r['identity'] for r in proof['relocation_proof'] if r['offset']==field]
        require(rows==[dict(symbol='_G_h01_'+global_name,hunk=1,offset=int(global_name,16),addend=0)],
                'glue independent canonical base coordinate differs')
        ids[symbol]=dict(original=(1,int(global_name,16)),basis='CANONICAL_LIBRARY_INITIALIZER')
    source=read(root,doc['anchors']['resident_F_7B24']['source']).decode('ascii')
    require('G_h01_B3C0 = F_h00_89D4("icon.library", 0L)' in source,'glue IconBase role differs')
    ids['_IconBase']=dict(original=n.anchor(root,recipe,'resident_F_7B24',original,24),basis='CANONICAL_LIBRARY_INITIALIZER')
    return ids


def prove_context(candidate,original,specs,bounds,base_ids):
    cb,cm,sm=candidate;ids={name:dict(row,candidate=(1,n.symbol(sm,name)[1])) for name,row in base_ids.items()}
    out={};spec_by={s['member']:s for s in specs}
    require(len(spec_by)==len(specs),'glue duplicate complete member')
    for spec in sorted(specs,key=lambda s:bool(s.get('target'))):
        name=spec['member'];start,size=bounds[name]
        require(size==spec['size'] and size>0,'glue partial member extent')
        entries=sorted([(sym,off-start) for (h,sym),off in sm.items() if h==0 and start<=off<start+size and not sym.startswith('__H')],key=lambda r:(r[1],r[0]))
        require(entries==[tuple(r) for r in spec['entries']],'glue complete member exports differ')
        fields={int(k):v for k,v in spec['fields'].items()}
        if spec.get('target'):
            require(spec['target'] in ids and ids[spec['target']]['original'][0]==0,'glue forwarder lacks proved target')
            require(size==4 and fields=={2:dict(kind='PC',symbol=spec['target'])},'glue unsupported forwarder')
        proof=n.compare_member(candidate,original,spec['original'],start,size,size,fields,ids)
        raw=n.extent(*original,0,spec['original'],size)
        if not spec.get('target'):
            require(n.unique(n.extent(*original,0,0,original[1]['hunks'][0]['initialized_size']),raw)==spec['original'],
                    'glue whole original member is not unique')
        else:
            require(ids[spec['target']]['original']==(0,spec['original']+size),
                    'glue original forwarder is not the proved adjacent pair')
        for symbol,offset in entries:
            ids[symbol]=dict(candidate=(0,start+offset),original=(0,spec['original']+offset),basis='PROVED_COMPLETE_LIBRARY_MEMBER')
        out[name]=dict(member=name,members=[name],profile='aztec36',provider='PINNED_LIBRARY_OBJECT',
                      original=dict(hunk=0,offset=spec['original'],size=size),entries=[dict(name=sym,offset=off) for sym,off in entries],
                      owned_data_size=0,owned_bss_size=0,accounting=spec['accounting'],relocation_identity=[],**proof)
    return [out[s['member']] for s in specs]


def verify(root,*,document=None,original=None):
    if document is None:document=json.loads(canonical_path(root,RECIPE).read_text())
    require(sha256(json_bytes(document))==RECIPE_DIGEST,'glue curated recipe changed')
    if original is None:
        from analysis_support import game
        from census import advisory_image
        with advisory_image():original=game()[:2]
    require(document['schema_version']==1 and sha256(original[0])==document['game_sha256'],'glue game/schema differs')
    contexts,bounds=producer(root,document);base_ids=bases(root,document,original)
    one=prove_context(contexts['one-lib'],original,document['specs'],bounds,base_ids)
    two=prove_context(contexts['two-lib'],original,document['specs'],bounds,base_ids)
    require([(r['member'],r['original'],r['entries'],r['code_sha256']) for r in one]==
            [(r['member'],r['original'],r['entries'],r['code_sha256']) for r in two],'glue independent contexts differ')
    for row in one:
        row.update(library_sha256=document['library']['sha256'],object_sha256s={row['member']:sha256(read(root,document['work']+'/'+row['member']+'.o'))},
                   job_receipt_sha256=document['receipt']['sha256'],recipe_sha256=RECIPE_DIGEST)
    return dict(schema_version=1,status='COMPLETE_RUNTIME_CODE_MATCH',game_sha256=document['game_sha256'],recipe=RECIPE,
                recipe_sha256=RECIPE_DIGEST,contributions=one,exact_compiler_release_selected=False,reconstructed_game_functions=0,
                limitations=['Complete pinned assembly glue only. No original DATA ownership, release attribution, or natural root layout.'])


def input_identity(root):
    path=canonical_path(root,RECIPE)
    if not path.exists():return {str(path):None}
    doc=json.loads(path.read_text());paths={RECIPE,OUTPUT,doc['request']['path'],doc['receipt']['path'],doc['library']['path']}
    paths.update(a['path'] for a in doc['archives'])
    for a in doc['anchors'].values():paths.update((a['source'],a['proof']))
    req=json.loads(read(root,doc['request']['path']));rec=json.loads(read(root,doc['receipt']['path']))
    paths.update(doc['work']+'/'+a['path'] for a in rec['artifacts'])
    paths.update(doc['job']+'/'+p for p in ('sys/s/startup-sequence','worker.uae','kick.rom'))
    paths.update(p['path'] for p in req['pinned_inputs'] if p['path'].startswith('toolchain/installed/aztec-3.6a/'))
    values={str(Path(root)/p):sha256(read(root,p)) if Path(root,p).exists() else None for p in paths}
    values[req['emulator']]=sha256(Path(req['emulator']).read_bytes())
    return values
