"""Bounded pinned-library units with independently controlled A4 references.

Only the retained graphics/OpenLibrary campaign is supported. This consumer
produces a validation comparison buffer, never patched executable output.
Library membership is checked against complete objects in the pinned archive;
SDK source, ordinary link recipes and actual symbol maps remain independent.
"""
import json
import re
from pathlib import Path
from common import require,sha256
from repo_paths import canonical_path
from hunk import parse
from overlay_experiment import symbols

INPUT='evidence/contributions/library-a4.json'

def checked(root,item):
    raw=canonical_path(root,item['path']).read_bytes()
    require(sha256(raw)==item['sha256'],'library A4 retained input changed: '+item['path'])
    return raw

def load_library_a4(root,blob,model,analysis,promotions,ledger,*,document=None):
    root=Path(root).resolve()
    if document is None:
        p=canonical_path(root,INPUT)
        if not p.exists():return []
        document=json.loads(p.read_bytes())
    require(document.get('schema_version')==1 and document.get('game_sha256')==sha256(blob),'library A4 game/schema differs')
    require(analysis['game_sha256']==sha256(blob),'library A4 analysis differs')
    basis=json.loads(checked(root,document['basis']));fid=basis['id'];item=ledger['functions'].get(fid)
    require(item and any(p['id']==fid for p in promotions),'library A4 requires accepted caller')
    require(all(basis[k]==item[k] for k in ('source','source_sha256','proof','proof_sha256')),'library A4 caller dependencies stale')
    source=checked(root,dict(path=item['source'],sha256=item['source_sha256'])).decode('ascii')
    proof=json.loads(checked(root,dict(path=item['proof'],sha256=item['proof_sha256'])))
    require(proof['comparison']['verdict']=='EQUAL','library A4 caller not exact')
    refs=proof['comparison']['code_comparison']['relocation_proof']
    opened=re.findall(r'G_h01_([0-9A-F]+)\s*=\s*F_h00_([0-9A-F]+)\("graphics\.library",\s*0L\)',source)
    require(len(opened)==1,'library A4 graphics handle producer ambiguous')
    gfx,producer=(int(x,16) for x in opened[0])
    require(basis['original_graphics_base']==dict(hunk=1,offset=gfx),'library A4 graphics handle binding differs')
    require(any(r['identity']==dict(symbol='_G_h01_%04X'%gfx,hunk=1,offset=gfx,addend=0) for r in refs),
            'library A4 graphics handle reference not independently proved')
    library=checked(root,document['library'])
    require(document['library']['path']=='toolchain/installed/aztec-3.6a/SYS1/lib/c.lib','library A4 unsupported library')
    inventory=json.loads(canonical_path(root,'evidence/toolchain/aztec-3.6a.json').read_bytes())
    pins=[e['sha256'] for d in inventory['disks'] if d['status']=='VALIDATED' and d['manifest']['volume']=='SYS1'
          for e in d['manifest']['entries'] if e.get('path')=='lib/c.lib' and e['kind']=='file']
    require(pins==[sha256(library)],'library A4 archive differs from pinned distribution')
    tool_pins={'toolchain/installed/aztec-3.6a/'+d['manifest']['volume']+'/'+e['path']:e['sha256']
               for d in inventory['disks'] if d['status']=='VALIDATED'
               for e in d['manifest']['entries'] if e['kind']=='file'}
    archives={a['path']:checked(root,a).decode('ascii') for a in document['archives']}
    receipts={}
    for claim in document['receipts']:
        receipt=json.loads(checked(root,claim));directory=Path(claim['path']).parent
        require(receipt['schema_version']==1 and all(s['returncode']==0 for s in receipt['steps']),'library A4 failed job')
        for tool in receipt['tool_inputs']:
            require(tool_pins.get(tool['path'])==tool['sha256'],'library A4 tool differs from pinned distribution')
            checked(root,tool)
        require(any(t['path'].endswith('/SYS1/bin/ln') for t in receipt['tool_inputs']) and
                any(t['path'].endswith('/SYS1/bin/as') for t in receipt['tool_inputs']) and
                any(t['path'].endswith('/SYS2/bin/lb') for t in receipt['tool_inputs']),'library A4 tool identities missing')
        receipts[directory]=receipt
    for directory,receipt in receipts.items():
        members=[o['member'] for g in document['groups'] for o in g['objects'] if Path(o['library']['path']).parent==directory]
        extraction='Old2:bin/lb >extract.log Old1:lib/c.lib -x '+' '.join(members)
        require(sum(s['command']==extraction for s in receipt['steps'])==1,'library A4 extraction recipe differs')
    out=[];seen=set()
    groups=document['groups']
    require(len(groups)==6 and len({g['id'] for g in groups})==6,'library A4 requires complete bounded campaign')
    open_group=next((g for g in groups if g['id']=='openlibrary_unit'),None)
    require(open_group and open_group['original']['start']==producer,'library A4 OpenLibrary producer differs')
    for group in groups:
        original=group['original'];start=original['start'];size=original['size'];reference=group['reference'];symbol=reference['symbol']
        require(original['hunk']==0 and size>0 and start not in seen,'library A4 original extent invalid');seen.add(start)
        require(any(r['identity']==dict(symbol='_F_h00_%04X'%start,hunk=0,offset=start,addend=0) for r in refs),
                'library A4 original caller binding missing')
        target=gfx if symbol=='_GfxBase' else basis['original_sys_base']['offset']
        require(symbol in ('_GfxBase','_SysBase') and reference['original_hunk']==1 and reference['original_offset']==target,
                'library A4 base identity differs')
        field=reference['offset'];require(reference['width']==2 and 2<=field<size-1,'library A4 field extent invalid')
        specs=group['objects'];definitions=group['definitions'];code_sum=0
        for spec,definition in zip(specs,definitions):
            obj=checked(root,spec['library']);assembled=checked(root,spec['assembled'])
            require(obj[:2]==assembled[:2]==b'AJ' and obj[2:10].rstrip(b'\0').decode('ascii')==spec['member'],
                    'library A4 object member differs')
            require(library.count(obj)==1,'library A4 complete object not uniquely in pinned archive')
            require(obj[14:22]==assembled[14:22]==bytes(8),'library A4 object owns DATA/BSS')
            n=int.from_bytes(obj[10:14],'big');require(n>0 and n%2==0 and n==int.from_bytes(assembled[10:14],'big'),
                                                       'library A4 object extent differs')
            require(definition['offset']==code_sum,'library A4 ordinary object order differs');code_sum+=n
            sdk=next((p.split('\n',1)[1] for p in archives[spec['archive']].split('\f')
                      if p.strip().startswith(spec['member']+'.a68')),None)
            rawsource=canonical_path(root,spec['source']).read_bytes()
            require(sdk is not None and rawsource==sdk.encode('ascii') and
                    '\tpublic\t'+definition['symbol'] in sdk,'library A4 retained SDK source differs')
            producing=receipts.get(Path(spec['library']['path']).parent)
            require(producing is not None and Path(spec['assembled']['path']).parent==Path(spec['library']['path']).parent,
                    'library A4 object receipt absent')
            for kind in ('library','assembled'):
                matches=[a for a in producing['artifacts'] if a['path']==Path(spec[kind]['path']).name]
                require(len(matches)==1 and matches[0]['sha256']==spec[kind]['sha256'],'library A4 object receipt differs')
            inputs=[a for a in producing['source_files'] if a['path']==spec['member']+'.asm']
            require(len(inputs)==1 and inputs[0]['sha256']==sha256(rawsource),'library A4 source receipt differs')
            command='Old1:bin/as >'+spec['member']+'-as.log -o '+spec['member']+'-source.o '+spec['member']+'.asm'
            require(sum(s['command']==command for s in producing['steps'])==1,'library A4 source assembly recipe differs')
        require(len(specs)==len(definitions) and code_sum==size,'library A4 complete object bounds differ')
        controls=group['controls'];require([(c['root'],c['kind']) for c in controls]==
            [('root1','lib'),('root1','source'),('root2','lib'),('root2','source')],'library A4 control set/order differs')
        variants=[];targets=[]
        for control in controls:
            executable=checked(root,control['executable']);text=checked(root,control['symbols']).decode('ascii')
            directory=Path(control['executable']['path']).parent;receipt=receipts.get(directory)
            require(receipt is not None,'library A4 missing producing receipt')
            root_object=checked(root,control['root_object'])
            root_source=canonical_path(root,control['root_source']).read_bytes()
            root_inputs=[a for a in receipt['source_files'] if a['path']==control['root']+'.asm']
            require(len(root_inputs)==1 and root_inputs[0]['sha256']==sha256(root_source),
                    'library A4 authored root source receipt differs')
            root_command=f'Old1:bin/as >{control["root"]}-as.log -o {control["root"]}.o {control["root"]}.asm'
            require(sum(s['command']==root_command for s in receipt['steps'])==1,'library A4 root assembly recipe differs')
            require(root_object[:2]==b'AJ' and int.from_bytes(root_object[10:14],'big')==0 and
                    int.from_bytes(root_object[14:18],'big')==(4 if control['root']=='root1' else 10) and
                    int.from_bytes(root_object[18:22],'big')==0,'library A4 authored root object bounds differ')
            name=Path(control['executable']['path']).name
            objects=' '.join(Path(s['library' if control['kind']=='lib' else 'assembled']['path']).name for s in specs)
            command=f'Old1:bin/ln >{name}.log -m -t -o {name} {objects} {control["root"]}.o'
            require(sum(s['command']==command for s in receipt['steps'])==1,'library A4 natural link recipe differs')
            for k in ('executable','symbols','root_object'):
                a=control[k];matches=[x for x in receipt['artifacts'] if x['path']==Path(a['path']).name]
                require(len(matches)==1 and matches[0]['sha256']==a['sha256'],'library A4 artifact receipt differs')
            sm=symbols(text);m=parse(executable);h=next(x for x in m['hunks'] if x['number']==0)
            require(len(m['hunks'])==3 and not m['relocations'] and h['type']=='CODE' and
                    h['allocated_size']==h['initialized_size']==(size+3)//4*4,'library A4 natural link extent differs')
            require(all(sm[(0,d['symbol'])]==d['offset'] for d in definitions) and sm[(0,'__H0_end')]==h['initialized_size'],
                    'library A4 linked definitions differ')
            actual=executable[h['content_offset']:h['content_offset']+size]
            require(executable[h['content_offset']+size:h['content_offset']+h['initialized_size']]==bytes((-size)%4),
                    'library A4 nonzero serialization padding')
            require(actual[field-2:field]==bytes.fromhex('2c6c'),'library A4 load instruction differs')
            bias=analysis['a4']['bias'];resolved=bias+int.from_bytes(actual[field:field+2],'big',signed=True)
            require(resolved==sm[(1,symbol)]== (0 if control['root']=='root1' else 6),'library A4 actual base binding differs')
            data=next(x for x in m['hunks'] if x['number']==1)
            expected_data=bytes(4) if control['root']=='root1' else bytes.fromhex('000100020003000000000000')
            require(data['type']=='DATA' and data['initialized_size']==data['allocated_size']==len(expected_data) and
                    executable[data['content_offset']:data['content_offset']+len(expected_data)]==expected_data,
                    'library A4 authored DATA-order control differs')
            bss=next(x for x in m['hunks'] if x['number']==2)
            # The pinned linker emits its four-byte empty BSS sentinel. It is
            # a control-layout obligation, never part of these CODE claims.
            require(bss['type']=='BSS' and bss['allocated_size']==4 and bss['initialized_size']==0,
                    'library A4 control BSS sentinel differs')
            if group['id']=='openlibrary_unit':require(actual[:4]==bytes.fromhex('4efa0002') and definitions[1]['offset']==4,
                                                      'library A4 separate helper PC binding differs')
            variants.append(actual[:field]+bytes(2)+actual[field+2:]);targets.append(resolved)
        require(len(set(variants))==1 and targets==[0,0,6,6],'library A4 source/library DATA-order control differs')
        h=next(x for x in model['hunks'] if x['number']==0)
        require(start+size<=h['initialized_size'],'library A4 original extent exceeds hunk')
        expected=blob[h['content_offset']+start:h['content_offset']+start+size]
        require(sha256(expected)==original['sha256'] and expected[field-2:field]==bytes.fromhex('2c6c') and
                bias+int.from_bytes(expected[field:field+2],'big',signed=True)==target and
                expected[:field]+bytes(2)+expected[field+2:]==variants[0],'library A4 complete original match failed')
        require(not any(r['source_hunk']==0 and r['source_offset']<start+size and r['source_offset']+r['width']>start
                        for r in model['relocations']),'library A4 original relocation unsupported')
        payload=variants[0][:field]+(target-bias).to_bytes(2,'big',signed=True)+variants[0][field+2:]
        out.append(dict(id='runtime_'+group['id'],hunk=0,start=start,end=start+size,bytes=payload,
                        category='PINNED_RUNTIME',relocations=[]))
    require(sum(c['end']-c['start'] for c in out)==88,'library A4 campaign byte count differs')
    return out
