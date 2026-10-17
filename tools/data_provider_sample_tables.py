"""Slices of independently bounded sample and asset pointer access prefixes.

Canonical consumers establish the uniform descriptor pointer view through the
highest witnessed index. This recovers holes inside that prefix, never table
capacity. Every target separately re-proves its consumed records and sentinel.
No bytes after the first nonpositive duration are admitted.
"""
import re
from common import require,sha256,json_bytes
from audio_sequence_data import payload
from overlay_experiment import relocation_profile
import data_provider_cells as cells

KIND='EXTERNAL_DATA_POINTER_TABLE'
CONTROL_NAMES=['_DP_'+chr(97+i) for i in range(14)]
CONTROL_TARGETS=CONTROL_NAMES+[CONTROL_NAMES[0],CONTROL_NAMES[-1]]
CONTROL_SOURCE=(''.join('extern int '+n[1:]+';\n' for n in CONTROL_NAMES)+
    'int *DP_table_probe[16] = {'+', '.join('&'+n[1:] for n in CONTROL_TARGETS)+'};\n').encode('ascii')


def shape(f):
    require(set(f)=={'schema_version','kind','id','source','original','definitions','bindings','anchors','object_sections','historical_owner','historical_tu','original_filename','producer'},'sample pointer slice fact fields')
    o=f['original'];require(f['schema_version']==1 and f['kind']==KIND and set(o)=={'hunk','start','size'} and o['hunk']==1,'sample DATA slice schema')
    require(type(o['start']) is int and type(o['size']) is int and o['start']>=0x320 and o['start']%2==0,'sample pointer coordinate/stride')
    require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','sample pointer slice identity')
    require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown historical provenance')
    require(isinstance(f['definitions'],list) and len(f['definitions'])==1,'one aggregate slice definition')
    d=f['definitions'][0]
    require(set(d)==({'target_record_count'} if d.get('type')=='struct DP_Sample *' else set())|{'symbol','type','offset','count','first_index','targets','bounds'} and d['symbol']=='G_h01_%04X'%o['start'] and d['type'] in ('struct DP_Sample *','unsigned char *') and d['offset']==0,'typed descriptor pointer array')
    require(type(d['count']) is int and 1<=d['count']<=14 and type(d['first_index']) is int and o['start']==(0x27e4 if d['type']=='struct DP_Sample *' else 0x1f9e)+4*d['first_index'],'complete contiguous index slice')
    if d['type']=='struct DP_Sample *':require(type(d['target_record_count']) is int and d['target_record_count']>0,'complete compatible target record declaration')
    size=4*d['count'];require(o['size']==size and d['bounds']==dict(kind='SAMPLE_ACCESS_PREFIX_SLICE' if d['type']=='struct DP_Sample *' else 'ASSET_ACCESS_PREFIX_SLICE',bytes=size) and f['object_sections']==dict(CODE=0,DATA=size,BSS=0,COMMON=0),'whole typed pointer object/extent')
    require(isinstance(d['targets'],list) and len(d['targets'])==d['count'] and set(d['targets'])==set(f['bindings']),'complete named pointer targets')
    for n,b in f['bindings'].items():
        require(re.fullmatch('G_h01_[0-9A-F]{4}',n) and set(b)=={'fact','sha256'} and b['fact']=='evidence/data-providers/resident_data_'+n[-4:]+'.json' and re.fullmatch('[0-9a-f]{64}',b['sha256']),'independently named typed target fact')
    require(isinstance(f['anchors'],dict) and f['anchors'],'independent canonical access-domain anchors')
    return size


def source(f):
    shape(f);d=f['definitions'][0]
    from data_provider_sequences import sequence_declaration
    if d['type']=='struct DP_Sample *':
        decl=sequence_declaration(d['target_record_count'])+''.join('extern struct DP_Sequence '+n+';\n' for n in sorted(f['bindings']));values=['(struct DP_Sample *)&'+n for n in d['targets']]
    else:
        decl=''.join('extern unsigned char '+n+'[];\n' for n in sorted(f['bindings']));values=d['targets']
    return (decl+d['type']+d['symbol']+'[%d] = {'%d['count']+', '.join(values)+'};\n').encode('ascii')



def binder_names(facts):
    return sorted(set(CONTROL_NAMES)|{'_'+n for f in facts for n in f['bindings']})


def evidence_paths(root,f):
    from data_providers import document,producer_paths
    from data_provider_sequences import evidence_paths as target_paths
    names=set(target_paths(root,f))
    for b in f['bindings'].values():
        target=document(root,b['fact']);recipe=document(root,target['producer']['batch'])
        names.update([b['fact'],target['producer']['batch'],*target_paths(root,target),*producer_paths(root,recipe)])
    return sorted(names)


def typed_evidence(root,f,analysis,ledger,promotions):
    from data_provider_sequences import anchors,sample_domain,pointer_target,asset_prefix
    from data_providers import document,verify,source as target_source
    from census import advisory_image
    from game_image import game
    from evidence_snapshot import memoized
    shape(f);d=f['definitions'][0]
    with advisory_image():blob,model,_=game()
    a=anchors(root,f,analysis,ledger,promotions)
    asset=d['type']=='unsigned char *';base=0x1f9e if asset else 0x27e4
    if asset:highest,witnesses=asset_prefix(a);end=highest+1
    else:domain,details=sample_domain(a,blob,model);end=max(domain)+1
    require(0<=d['first_index']<d['first_index']+d['count']<=end,'sample slice exceeds independently accessed prefix')
    proofs=[]
    for j,n in enumerate(d['targets']):
        b=f['bindings'][n];target=document(root,b['fact']);index=d['first_index']+j
        require(sha256(json_bytes(target))==b['sha256'],'typed pointer target fact changed')
        require(target['kind']=='BOUNDED_DATA_TABLE' and target['route'] in (('ASSET_ID_PROGRAM','ASSET_ID_PREFIX_MEMBER') if asset else ('SAMPLE_RECORD_PREFIX','SAMPLE_RECORD_PREFIX_MEMBER')) and target['selector_index']==index and target['definitions'][0]['symbol']==n,'pointer target is not the independently selected descriptor')
        if not asset:require(len(target['definitions'][0]['initializer']['records'])==d['target_record_count'],'target extern must use its complete separately proved record shape')
        require(pointer_target(blob,model,base,index)==target['original']['start'],'original sample pointer target differs')
        identity=b['sha256']+';'+sha256(blob)+';'+sha256(json_bytes(ledger))
        report=memoized(root,'data-sample-slice-target',identity,lambda:verify(root,blob,model,analysis,ledger,promotions,target,target_source(target),None),strict=True)
        require(report['state']=='DATA_LAYOUT_MATCH','separately typed complete target object did not verify')
        proofs.append(dict(symbol=n,fact=b['fact'],fact_sha256=b['sha256'],object_sha256=report['object_sha256'],index=index))
    return [dict(kind=d['bounds']['kind'],prefix_count=end,first_index=d['first_index'],count=d['count'],element_width=4,anchors=f['anchors'],target_proofs=proofs,capacity_claim=False,historical_extent='UNKNOWN; reconstructed prefix slice only')]


def compare_data(original,model,f,obj,linked,map_text):
    from data_providers import document
    from analysis_support import ROOT
    shape(f);d=f['definitions'][0];recipe=document(ROOT,f['producer']['batch']);facts=[document(ROOT,m['fact']) for m in recipe['members']]
    targets=['_'+n for n in d['targets']]
    parsed,m,actual=cells.linked_view(obj,linked,map_text,'_'+d['symbol'],targets,binder_names(facts),max_externals=14)
    expected=payload(original,model,1)[f['original']['start']:f['original']['start']+f['original']['size']]
    values=[int(n[-4:],16) for n in d['targets']]
    require(expected==b''.join(v.to_bytes(4,'big') for v in values),'all original named DATA pointer values')
    rels=relocation_profile(model,1,f['original']['start'],f['original']['size'])
    require(rels==[dict(offset=4*i,type='HUNK_RELOC32',width=4,target_hunk=1,addend=v) for i,v in enumerate(values)],'complete original pointer relocations')
    return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=f['id'],original=dict(f['original'],sha256=sha256(expected)),sections=parsed['sections'],symbols=parsed['definitions'],relocation_bindings=parsed['fixups'],original_relocations=rels,candidate_relocations=relocation_profile(m,1,0,len(expected)),actual_sha256=sha256(actual),source_sha256=sha256(source(f)),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=expected.hex(),zero_fill_credit=0,root_layout_proof=False)


def control_report(files,names):
    old=cells.control_report(files,names)
    require(files['datatablesprobe.c']==CONTROL_SOURCE,'independent fourteen-external DATA control source')
    parsed,m,actual=cells.linked_view(files['datatablesprobe.o'],files['datatablesprobe.exe'],files['datatablesprobe.sym'].decode('ascii'),'_DP_table_probe',CONTROL_TARGETS,names,max_externals=14)
    return dict(cell_control=old,DATA=64,relocations=16,unique_test_targets=14,repeated_targets=2,object_sha256=sha256(files['datatablesprobe.o']),game_credit=0)
