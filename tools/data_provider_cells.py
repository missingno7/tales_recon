"""Single typed external DATA pointer cells, with separately proved targets.

No aggregate pointer-table extent is claimed. Every cell has a finite canonical
index witness, one named target fact, and an exact original RELOC32. Synthetic
binder DATA is fully checked and has zero game credit.
"""
import json,re
from common import require,sha256
from repo_paths import canonical_path
from audio_sequence_data import payload
from overlay_experiment import symbols,relocation_profile
from hunk import parse

KIND='EXTERNAL_DATA_POINTER_CELL'
CONTROL_SOURCE=b'extern int DP_a, DP_b;\nint *DP_p[3] = {&DP_a, &DP_b, &DP_a};\n'
CONTROL_NAMES=['_DP_a','_DP_b']

def shape(f):
    require(set(f)=={'schema_version','kind','id','source','original','definitions','target_fact','target_fact_sha256','object_sections','historical_owner','historical_tu','original_filename','producer'},'external DATA cell fact fields')
    o=f['original'];require(f['schema_version']==1 and f['kind']==KIND and set(o)=={'hunk','start','size'} and o['hunk']==1 and type(o['start']) is int and o['start']>=0x320 and o['start']%2==0 and o['size']==4,'one aligned DATA pointer cell')
    require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','pointer cell identity')
    require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown historical provenance')
    require(f['object_sections']==dict(CODE=0,DATA=4,BSS=0,COMMON=0),'whole pointer cell object')
    require(isinstance(f['definitions'],list) and len(f['definitions'])==1,'one pointer definition')
    d=f['definitions'][0];require(set(d)=={'symbol','type','offset','target','target_type','target_count','target_offset','selector_index','bounds'} and d['symbol']=='G_h01_%04X'%o['start'] and d['offset']==0 and d['bounds']==dict(kind='NAMED_DATA_POINTER_CELL',bytes=4),'complete typed pointer definition')
    require(d['type'] in ('unsigned char *','struct DP_Sequence *','struct DP_Channel *') and d['target_type']=={'unsigned char *':'unsigned char','struct DP_Sequence *':'struct DP_Sequence','struct DP_Channel *':'unsigned long'}[d['type']],'independent typed target, no integer pointer')
    require(type(d['target_offset']) is int and d['target']=='G_h01_%04X'%d['target_offset'] and f['target_fact']=='evidence/data-providers/resident_data_%04X.json'%d['target_offset'],'independently named target identity')
    require(type(d['target_count']) is int and d['target_count']>0 and type(d['selector_index']) is int and 0<=d['selector_index']<=255,'closed selector witness/target shape')
    require(o['start']=={'unsigned char *':0x1f9e,'struct DP_Sequence *':0x27e4,'struct DP_Channel *':0x29fa}[d['type']]+4*d['selector_index'],'typed slot coordinate from base plus exact index')
    require(isinstance(f['target_fact_sha256'],str) and re.fullmatch('[0-9a-f]{64}',f['target_fact_sha256']),'target fact SHA pin')
    return 4

def source(f):
    from data_provider_sequences import sequence_declaration
    shape(f);d=f['definitions'][0]
    if d['type']=='unsigned char *':decl='extern unsigned char '+d['target']+'[%d];\n'%d['target_count'];value=d['target']
    elif d['type']=='struct DP_Channel *':decl='struct DP_Channel;\nextern unsigned long '+d['target']+';\n';value='(struct DP_Channel *)&'+d['target']
    else:decl=sequence_declaration(d['target_count'])+'extern struct DP_Sequence '+d['target']+';\n';value='&'+d['target']
    return (decl+d['type']+' '+d['symbol']+' = '+value+';\n').encode('ascii')

def binder_names(facts):return sorted(set(CONTROL_NAMES)|{'_'+f['definitions'][0]['target'] for f in facts})

def binder_source(names):
    require(names==sorted(set(names)) and all(re.fullmatch('_[A-Za-z_]\\w*',n) for n in names),'unique complete synthetic DATA target names')
    return ''.join('int '+n[1:]+' = '+str(i+1)+';\n' for i,n in enumerate(names)).encode('ascii')

def commands(prefixes):
    out=[]
    for p in prefixes:out += [f'Old1:bin/cc >{p}-cc.log -a +b {p}.c',f'Old1:bin/as >{p}-as.log -o {p}.o {p}.asm']
    out+=['Old1:bin/cc >binddata-cc.log -a +b binddata.c','Old1:bin/as >binddata-as.log -o binddata.o binddata.asm','Old1:bin/as >h000-as.log -o h000.o h000.asm']
    for p in prefixes:out += [f'Old1:bin/ln >{p}-ln.log -m -t -o {p}.exe h000.o {p}.o'+('' if p=='relprobe' else ' binddata.o')]
    return out

def evidence_paths(root,f):
    from data_providers import document,producer_paths
    from data_provider_tables import evidence_paths as target_paths
    target=document(root,f['target_fact']);recipe=document(root,target['producer']['batch'])
    return sorted(set([f['target_fact'],target['producer']['batch'],*target_paths(root,target),*producer_paths(root,recipe)]))

def typed_evidence(root,f,blob,model,analysis,ledger,promotions):
    from data_providers import document,verify,source as target_source
    from evidence_snapshot import memoized
    shape(f);target=document(root,f['target_fact']);d=f['definitions'][0]
    from common import json_bytes
    require(sha256(json_bytes(target))==f['target_fact_sha256'],'independently named target fact changed')
    require(target['kind']=='BOUNDED_DATA_TABLE' and target['route']=={'unsigned char *':'ASSET_ID_PROGRAM','struct DP_Sequence *':'SAMPLE_RECORD_PREFIX','struct DP_Channel *':'AUDIO_CHANNEL_FIELD'}[d['type']] and target['original']['start']==d['target_offset'] and target['selector_index']==d['selector_index'],'pointer target is not the independently typed selected program/descriptor')
    if d['type']=='struct DP_Channel *':
        require(target['field']=='period_accumulator' and d['selector_index']<4,'channel pointer requires its independently named first scalar field; no channel capacity inferred')
        count=1
    else:count=target['definitions'][0]['dimensions'][0] if d['type']=='unsigned char *' else len(target['definitions'][0]['initializer']['records'])
    require(count==d['target_count'],'target declaration shape changed')
    # Reprove the separately named complete object. A pending provider can be a
    # dependency, but neither its cached verdict nor publication is assumed.
    identity=f['target_fact_sha256']+';'+sha256(blob)+';'+sha256(json_bytes(ledger))
    report=memoized(root,'data-cell-independent-target',identity,lambda:verify(root,blob,model,analysis,ledger,promotions,target,target_source(target),None),strict=True)
    require(report['state']=='DATA_LAYOUT_MATCH' and report['source_sha256']==sha256(target_source(target)),'independent target object did not verify')
    rs=relocation_profile(model,1,f['original']['start'],4)
    require(rs==[dict(offset=0,type='HUNK_RELOC32',width=4,target_hunk=1,addend=d['target_offset'])],'original pointer cell target relocation differs')
    return [dict(kind='NAMED_DATA_POINTER_CELL',selector_index=d['selector_index'],target_fact=f['target_fact'],target_fact_sha256=f['target_fact_sha256'],target_symbol=d['target'],target_type=d['target_type'],target_object_sha256=report['object_sha256'],capacity_claim=False)]

def object_data(raw,symbol,targets,max_externals=2):
    """Measured030a DATA definition,072a DATA extern and fd7i00 fixups.

    Only packed indices1/2 are exercised by this scalar route and its independent
    duplicate-target control. No arbitrary record or external class is accepted.
    """
    require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'external DATA AJ header')
    u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
    size=4*len(targets);externs=list(dict.fromkeys(targets));require(max_externals in (2,14) and 1<=len(externs)<=max_externals,'only measured external DATA index range')
    require((u32(10),u32(14),u32(18))==(0,size,0),'whole external DATA-only object')
    syms=u16(28)*4;end=u16(30)*4
    require(u32(24)*4==36 and syms<=end==u16(32)*4==len(raw) and u16(22)==1+len(externs) and raw[34:36]==b'\xc0\0','whole external DATA object boundaries')
    p=syms
    for i,n in enumerate([symbol]+externs):
        require(raw[p:p+2]==(b'\x03\x0a' if i==0 else b'\x07\x2a') and u16(p+2)==0,'DATA definition/external class or value differs');p+=4
        if i:require(u16(p)==targets.count(n),'external DATA reference count differs');p+=2
        z=raw.find(b'\0',p,end);require(z>p and raw[p:z].decode('ascii')==n,'complete external DATA symbol inventory/order');p=z+1
    require(end-p<=3 and raw[p:]==bytes(end-p),'external DATA symbol trailer')
    p=36;require(raw[p]==0xf5,'external DATA stream');p+=1;fixups=[]
    for i,n in enumerate(targets):
        require(raw[p:p+3]==bytes([0xfd,0x71+externs.index(n),0]),'exact measured named DATA relocation record');p+=3
        fixups.append(dict(offset=i*4,width=4,type='HUNK_RELOC32',symbol=n,addend=0))
    require(raw[p:p+2]==b'\xf4\xf5','empty CODE/DATA transition');p+=2
    require(syms==((p+4)//4)*4 and raw[p:syms]==bytes(syms-p),'entire pointer DATA stream/trailer')
    return dict(bytes=bytes(size),definitions=[dict(name=symbol,offset=0)],fixups=fixups,sections=dict(CODE=0,DATA=size,BSS=0,COMMON=0))

def linked_view(obj,linked,map_text,symbol,targets,names,max_externals=2):
    parsed=object_data(obj,symbol,targets,max_externals);m=parse(linked);sm=symbols(map_text);size=4*len(targets);binder=b''.join((i+1).to_bytes(2,'big') for i in range(len(names)));rounded=(size+len(binder)+3)&~3
    require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in m['hunks']]==[(0,'CODE',4,4),(1,'DATA',rounded,rounded),(2,'BSS',4,0)],'whole DATA-cell link topology/allocations')
    require(payload(linked,m,0)==b'\x4e\x75\0\0','independent zero-DATA harness')
    expected={(0,'__H0_org'):0,(0,'.begin'):0,(0,'__H0_end'):4,(1,'__H1_org'):0,(1,symbol):0,(1,'__H1_end'):rounded,(2,'__H2_org'):rounded,(2,'__H2_end'):rounded}
    expected.update({(1,n):size+2*i for i,n in enumerate(names)});require(sm==expected,'complete linked DATA pointer/binder symbol inventory')
    data=payload(linked,m,1);require(data[size:]==binder+bytes(rounded-size-len(binder)),'complete independently authored binder DATA and linker alignment')
    for i,n in enumerate(targets):require(data[4*i:4*i+4]==sm[(1,n)].to_bytes(4,'big'),'named DATA pointer payload')
    wanted=[dict(source_hunk=1,source_offset=4*i,target_hunk=1,addend_raw=sm[(1,n)],type='HUNK_RELOC32',width=4) for i,n in enumerate(targets)]
    require([{k:r[k] for k in ('source_hunk','source_offset','target_hunk','addend_raw','type','width')} for r in m['relocations']]==wanted,'exhaustive DATA-cell linked relocation inventory')
    return parsed,m,data[:size]

def compare_data(original,model,f,obj,linked,map_text):
    from data_providers import document
    from analysis_support import ROOT
    shape(f);d=f['definitions'][0];recipe=document(ROOT,f['producer']['batch']);facts=[document(ROOT,m['fact']) for m in recipe['members']];names=binder_names(facts)
    parsed,m,actual=linked_view(obj,linked,map_text,'_'+d['symbol'],['_'+d['target']],names);expected=payload(original,model,1)[f['original']['start']:f['original']['start']+4]
    require(expected==d['target_offset'].to_bytes(4,'big'),'original named DATA pointer value differs')
    rels=relocation_profile(model,1,f['original']['start'],4);require(rels==[dict(offset=0,type='HUNK_RELOC32',width=4,target_hunk=1,addend=d['target_offset'])],'exact original DATA-cell relocation')
    return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=f['id'],original=dict(f['original'],sha256=sha256(expected)),sections=parsed['sections'],symbols=parsed['definitions'],relocation_bindings=parsed['fixups'],original_relocations=rels,candidate_relocations=relocation_profile(m,1,0,4),actual_sha256=sha256(actual),source_sha256=sha256(source(f)),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=expected.hex(),zero_fill_credit=0,root_layout_proof=False)

def control_report(files,names):
    from data_providers import data_object
    require(files['dataprobe.c']==CONTROL_SOURCE and files['binddata.c']==binder_source(names),'independently authored DATA relocation control/binder source')
    binder=data_object(files['binddata.o']);require(binder['sections']==dict(CODE=0,DATA=2*len(names),BSS=0,COMMON=0) and binder['definitions']==[dict(name=n,offset=2*i) for i,n in enumerate(names)] and not binder['fixups'] and binder['bytes']==b''.join((i+1).to_bytes(2,'big') for i in range(len(names))),'complete synthetic binder object')
    parsed,m,actual=linked_view(files['dataprobe.o'],files['dataprobe.exe'],files['dataprobe.sym'].decode('ascii'),'_DP_p',['_DP_a','_DP_b','_DP_a'],names)
    return dict(DATA=12,relocations=3,unique_test_targets=2,binder_DATA=2*len(names),binder_sha256=sha256(files['binddata.o']),object_sha256=sha256(files['dataprobe.o']),game_credit=0)
