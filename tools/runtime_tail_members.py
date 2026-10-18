"""Complete pinned resident tail leaves; exhaustive field identity, no byte rewriting.

The larger scanf/port/IO objects remain outside this route. Private storage,
A4 call routing, release attribution and root layout are not inferred here.
"""
from names import read_source
import json
from pathlib import Path
from common import require, sha256, json_bytes
from repo_paths import candidate_path, canonical_path
from hunk import parse
from overlay_experiment import symbols
import runtime_natural_members as n

RECIPE='evidence/contributions/runtime-tail-leaves.json'
RECIPE_DIGEST='6bab3831ab1319324cfaae6c755a0278dad09c06b6058cc4c6f718da580aff4b'
OUTPUT='evidence/experiments/runtime-members-tail.json'
EXPECTED=[('_output','__Output',0x86ee,8,2,'_DOSBase'),('_write','__Write',0x871a,14,8,'_DOSBase'),
          ('addport','_AddPort',0x8866,12,6,'_SysBase'),('allocsig','_AllocSignal',0x8872,12,6,'_SysBase'),
          ('freesign','_FreeSignal',0x8990,12,6,'_SysBase'),('newlist','_NewList',0x89a8,18,None,None),
          ('remport','_RemPort',0x89fa,12,6,'_SysBase')]


def checked(root, record):
    raw=(read_source(root, Path(root) / record['path'], scratch=True) if record['path'].startswith('src/') else candidate_path(root,Path(root)/record['path']).read_bytes())
    require(sha256(raw)==record['sha256'],'tail retained input changed: '+record['path'])
    return raw


def coordinate(model, sm, name):
    """A4 uses combined DATA/COMMON offsets in Aztec ln -t symbol maps."""
    hn,off=n.symbol(sm,name)
    require(hn in (1,2),'tail base symbol is not DATA/COMMON')
    dh=next(h for h in model['hunks'] if h['number']==1)
    bh=next(h for h in model['hunks'] if h['number']==2)
    require(dh['type']=='DATA' and bh['type']=='BSS' and bh['initialized_size']==0,
            'tail DATA/COMMON hunk type differs')
    require(n.symbol(sm,'__H1_org')==(1,0) and n.symbol(sm,'__H2_org')==(2,dh['initialized_size']),
            'tail combined DATA/COMMON origin differs')
    require(n.symbol(sm,'__H1_end')==(1,dh['initialized_size']) and
            n.symbol(sm,'__H2_end')==(2,dh['allocated_size']),
            'tail combined DATA/COMMON bounds differ')
    lo,hi=(0,dh['initialized_size']) if hn==1 else (dh['initialized_size'],dh['allocated_size'])
    require(lo<=off and off+4<=hi,'tail base symbol outside its complete storage hunk')
    return off,dict(hunk=1,map_segment=hn,offset=off,storage_start=lo,storage_end=hi)


def compare_leaf(candidate, original, spec, bases):
    require(tuple(spec[k] for k in ('member','export','original','size','field','base')) in EXPECTED,
            'tail unsupported complete leaf contract')
    cb,cm,sm=candidate;ob,om=original
    name=spec['export'];hn,start=n.symbol(sm,name);size=spec['size'];field=spec['field']
    require(hn==0,'tail entry is not root CODE')
    raw=n.extent(cb,cm,0,start,size);expected=n.extent(ob,om,0,spec['original'],size)
    require(not n.relocations(cm,0,start,size) and not n.relocations(om,0,spec['original'],size),
            'tail leaf has unchecked relocation')
    exports=sorted((name,off-start) for (h,name),off in sm.items() if h==0 and
                   start<=off<start+size and not name.startswith('__H'))
    require(exports==[(spec['export'],0)],'tail complete leaf entries differ')
    ci,err=n.fc.decode_all(raw,[]);oi,oerr=n.fc.decode_all(expected,[])
    require(err is None and oerr is None and sum(i.size for i in ci)==sum(i.size for i in oi)==size,
            'tail complete leaf does not decode')
    require([(i.address,i.size) for i in ci]==[(i.address,i.size) for i in oi],
            'tail instruction shape differs')
    a4=[]
    for seq in (ci,oi):
        fields=[]
        for ins in seq:
            for operand in ins.operands:
                if operand.type==n.K.M68K_OP_MEM and operand.mem.base_reg==n.K.M68K_REG_A4:
                    require(operand.address_mode==n.K.M68K_AM_REGI_ADDR_DISP,
                            'tail unsupported A4 addressing')
                    site=n.fc.unique_word_site(ins,operand.mem.disp)
                    require(site is not None,'tail ambiguous A4 field')
                    fields.append(ins.address+site)
        a4.append(fields)
    require(a4==([[],[]] if field is None else [[field],[field]]),'tail exhaustive A4 contract differs')
    identity=[]
    if field is None:
        require(raw==expected,'tail whole leaf bytes differ')
    else:
        require(raw[field-2:field]==expected[field-2:field]==bytes.fromhex('2c6c'),
                'tail base load opcode differs')
        # Compare every non-address byte as emitted. Never modify either buffer.
        require(raw[:field]==expected[:field] and raw[field+2:]==expected[field+2:],
                'tail ordinary leaf bytes differ')
        actual,storage=coordinate(cm,sm,spec['base'])
        require(32766+int.from_bytes(raw[field:field+2],'big',signed=True)==actual,
                'tail candidate base identity differs')
        want=bases[spec['base']]['original']
        require(want[0]==1 and 32766+int.from_bytes(expected[field:field+2],'big',signed=True)==want[1],
                'tail original CRT0 base identity differs')
        h=next(h for h in om['hunks'] if h['number']==1)
        require(h['type']=='DATA' and 0<=want[1]<=h['allocated_size']-4,
                'tail original base outside root allocation')
        identity=[dict(field=field,width=2,kind='A4_BASE',symbol=spec['base'],
                       candidate=storage,original=list(want),basis='PINNED_CRT0_INITIALIZER')]
    oh=next(h for h in om['hunks'] if h['number']==0)
    require(oh['type']=='CODE' and oh['node']=='resident' and
            n.unique(n.extent(ob,om,0,0,oh['initialized_size']),expected)==spec['original'],
            'tail whole resident leaf is not unique')
    return dict(member=spec['member'],members=[spec['member']],profile='aztec36',
                original=dict(hunk=0,offset=spec['original'],size=size),size=size,
                entries=[dict(name=name,offset=0)],owned_data_size=0,owned_bss_size=0,
                raw_equal=raw==expected,code_sha256=sha256(expected),candidate_code_sha256=sha256(raw),
                operand_identity=identity,relocation_identity=[])


def verify(root, *, document=None, original=None):
    root=Path(root).resolve()
    if document is None:document=json.loads(canonical_path(root,RECIPE).read_bytes())
    require(sha256(json_bytes(document))==RECIPE_DIGEST,'tail curated recipe changed')
    if original is None:
        from analysis_support import game
        original=game()[:2]
    require(document['schema_version']==1 and sha256(original[0])==document['game_sha256'],
            'tail oracle/schema differs')
    specs=document['members']
    require([(s['member'],s['export'],s['original'],s['size'],s['field'],s['base']) for s in specs]==EXPECTED,
            'tail bounded member campaign differs')
    library=checked(root,document['library'])
    from resident_mixed import pinned
    require(document['library']['path']=='toolchain/installed/aztec-3.6a/SYS1/lib/c.lib' and
            pinned(root,document['library']['path'])==library,'tail library is not pinned')
    job=document['job'];request=json.loads(checked(root,job['request']));receipt=json.loads(checked(root,job['receipt']))
    require(receipt['request']==request and [s['command'] for s in receipt['steps']]==
            [s['command'] for s in request['steps']],'tail producer request/receipt differs')
    parent=Path(job['request']['path']).parent
    for path,key in [(parent/'sys/s/startup-sequence','guest_script_sha256'),(parent/'worker.uae','config_sha256'),
                     (parent/'kick.rom','rom_sha256')]:
        require(sha256(candidate_path(root,root/path).read_bytes())==request[key],'tail producer environment changed')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'tail emulator changed')
    for path in ['toolchain/installed/aztec-3.6a/SYS1/bin/ln','toolchain/installed/aztec-3.6a/SYS2/bin/lb',document['library']['path']]:
        pins=[p for p in request['pinned_inputs'] if p['path']==path]
        require(len(pins)==1 and sha256(pinned(root,path))==pins[0]['sha256'],'tail tool pin differs')
    artifacts={a['path']:a for a in receipt['artifacts']}
    require(len(artifacts)==len(receipt['artifacts']),'tail duplicate producer artifact')
    extraction=[s for s in receipt['steps'] if s['command']=='Old2:bin/lb >extract.log Old1:lib/c.lib -x']
    require(len(extraction)==1 and extraction[0]['returncode']==0,'tail extraction failed')
    # Other independent sweep links may fail; each accepted link must succeed.
    contexts=n.producer(root,json.loads(canonical_path(root,n.RECIPE).read_bytes()))
    bases=n.bootstrap(contexts['crt'],original)
    out=[]
    for spec in specs:
        expected='Old1:bin/ln >ln-'+spec['member']+'.log -m -t -o m_'+spec['member']+' '+spec['member']+'.o Old1:lib/c.lib'
        require(spec['link_command']==expected,'tail link command differs')
        steps=[s for s in receipt['steps'] if s['command']==expected]
        require(len(steps)==1 and steps[0]['returncode']==0,'tail selected link failed')
        inputs={}
        for key in ('object','executable','symbols'):
            claim=spec[key];name=Path(claim['path']).name
            require(Path(claim['path']).parent.as_posix()==job['work'],'tail artifact outside selected work')
            raw=checked(root,claim);a=artifacts.get(name)
            require(a and a['sha256']==claim['sha256'] and a['size']==len(raw),'tail artifact receipt differs')
            inputs[key]=raw
        obj=inputs['object']
        require(n.object_sizes(obj)==(spec['size'],0,0) and obj[2:10].rstrip(b'\0').decode('ascii')==spec['member'],
                'tail whole object extent/name differs')
        require(library.count(obj)==1,'tail complete object is not unique in pinned archive')
        cb=inputs['executable'];cm=parse(cb);sm=symbols(inputs['symbols'].decode('ascii'))
        require([(h['number'],h['type']) for h in cm['hunks']]==[(0,'CODE'),(1,'DATA'),(2,'BSS')],
                'tail standalone hunk topology differs')
        h=cm['hunks'][0]
        require(h['initialized_size']==h['allocated_size']==(spec['size']+3)//4*4 and
                n.symbol(sm,spec['export'])==(0,0) and n.symbol(sm,'__H0_end')==(0,h['initialized_size']),
                'tail linked whole object bounds differ')
        require(n.extent(cb,cm,0,spec['size'],(-spec['size'])%4)==bytes((-spec['size'])%4),
                'tail nonzero serialization padding')
        result=compare_leaf((cb,cm,sm),original,spec,bases)
        result.update(library_sha256=sha256(library),object_sha256s={spec['member']:sha256(obj)},
                      job_receipt_sha256=job['receipt']['sha256'],recipe_sha256=RECIPE_DIGEST)
        out.append(result)
    return dict(schema_version=1,status='COMPLETE_RUNTIME_CODE_MATCH',game_sha256=document['game_sha256'],
                recipe=RECIPE,recipe_sha256=RECIPE_DIGEST,contributions=out,
                exact_compiler_release_selected=False,reconstructed_game_functions=0,
                limitations=['Complete leaf CODE only; external base storage contents/ownership and root layout are unproved.',
                             'No private BSS, routed calls, opcode conversion, masking or emitted-byte rewriting.'])
