"""Typed asset-ID programs and audio descriptor prefixes.

Extents come from canonical sentinel readers, never the next symbol. Sample
prefixes end at the terminal duration WORD: its unconsumed six-byte tail stays
raw. Pointer-table cells are separate scalar objects; no capacity is inferred.
"""
from names import to_mechanical
import json,re
from common import require,sha256
from repo_paths import canonical_path
from audio_sequence_data import payload
from overlay_experiment import relocation_profile

ROUTES={'ASSET_ID_PROGRAM','ASSET_FLAG_CELL','SAMPLE_RECORD_PREFIX','SAMPLE_RECORD_PREFIX_MEMBER','ASSET_ID_PREFIX_MEMBER','ASSET_FLAG_PREFIX_MEMBER'}
C_SAMPLE={'resident_F_4AF0','resident_F_48D4','resident_F_49A0','resident_F_46CE','resident_F_4D04','ov05_F_0000'}
ASM_SAMPLE={'resident_asm_59A4','resident_frameless_55D6'}
SAMPLE_HEADER='struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };\n'

def shape(f):
    require(set(f)=={'schema_version','kind','id','source','original','definitions','route','selector_index','anchors','object_sections','historical_owner','historical_tu','original_filename','producer'},'sentinel provider fields')
    o=f['original'];route=f['route'];ds=f['definitions'];index=f['selector_index']
    require(f['schema_version']==1 and f['kind']=='BOUNDED_DATA_TABLE' and route in ROUTES,'closed typed sentinel route')
    require(set(o)=={'hunk','start','size'} and o['hunk']==1 and type(o['start']) is int and o['start']>=0x320 and type(o['size']) is int and o['size']>0,'initialized DATA only')
    require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','sentinel provider identity')
    require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown historical provenance')
    require(type(index) is int and 0<=index<=255 and isinstance(f['anchors'],dict) and f['anchors'] and isinstance(ds,list) and len(ds)==1,'one exact indexed target/cell')
    d=ds[0];require(set(d)=={'symbol','type','offset','dimensions','initializer','bounds'} and d['symbol']=='G_h01_%04X'%o['start'] and d['offset']==0,'named typed target')
    if route in ('ASSET_ID_PROGRAM','ASSET_ID_PREFIX_MEMBER'):
        vals=d['initializer'];require(d['type']=='unsigned char' and isinstance(vals,list) and vals and d['dimensions']==[len(vals)] and all(type(v) is int and 0<=v<255 for v in vals[:-1]) and vals[-1]==255,'asset IDs followed by first FF sentinel only')
        size=len(vals)
    elif route in ('ASSET_FLAG_CELL','ASSET_FLAG_PREFIX_MEMBER'):
        require(d['type']=='unsigned char' and d['dimensions']==[] and type(d['initializer']) is int and 0<=d['initializer']<=255 and o['start']==0x2042+index,'one archive-selector byte cell, no table-capacity inference')
        size=1
    else:
        v=d['initializer'];require(d['type']=='struct DP_Sequence' and isinstance(v,dict) and set(v)=={'records','terminal_duration'} and d['dimensions']==[],'typed descriptor prefix plus terminal word')
        require(isinstance(v['records'],list) and v['records'] and type(v['terminal_duration']) is int and -32768<=v['terminal_duration']<=0,'first duration sentinel required')
        for row in v['records']:
            require(isinstance(row,dict) and set(row)=={'duration','length_words','sample_data'},'complete consumed sample fields')
            require(type(row['duration']) is int and 0<row['duration']<=32767 and type(row['length_words']) is int and 0<=row['length_words']<=65535 and row['sample_data'] is None,'positive duration, unsigned length and null pointer; integer addresses reject')
        size=8*len(v['records'])+2
    require(o['size']==size and d['bounds']==dict(kind=route,bytes=size),'sentinel-derived extent')
    require(f['object_sections']==dict(CODE=0,DATA=(size+1)&~1,BSS=0,COMMON=0),'whole typed object; compiler alignment earns no credit')
    return size

def sequence_declaration(count):
    require(type(count) is int and count>0,'positive descriptor count')
    return SAMPLE_HEADER+'struct DP_Sequence { struct DP_Sample records[%d]; int terminal_duration; };\n'%count

def source(f):
    shape(f);d=f['definitions'][0];n=d['symbol'];v=d['initializer'];route=f['route']
    if route in ('ASSET_ID_PROGRAM','ASSET_ID_PREFIX_MEMBER'):return ('unsigned char '+n+'[%d] = {'%len(v)+', '.join(map(str,v))+'};\n').encode('ascii')
    if route in ('ASSET_FLAG_CELL','ASSET_FLAG_PREFIX_MEMBER'):return ('unsigned char '+n+' = '+str(v)+';\n').encode('ascii')
    rows=['{'+str(x['duration'])+', '+str(x['length_words'])+', 0}' for x in v['records']]
    return (sequence_declaration(len(rows))+'struct DP_Sequence '+n+' = {{'+', '.join(rows)+'}, '+str(v['terminal_duration'])+'};\n').encode('ascii')

def semantic(f):
    shape(f);d=f['definitions'][0];v=d['initializer']
    if f['route'] in ('ASSET_ID_PROGRAM','ASSET_ID_PREFIX_MEMBER'):return bytes(v)
    if f['route'] in ('ASSET_FLAG_CELL','ASSET_FLAG_PREFIX_MEMBER'):return bytes([v])
    return b''.join(x['duration'].to_bytes(2,'big')+x['length_words'].to_bytes(2,'big')+bytes(4) for x in v['records'])+v['terminal_duration'].to_bytes(2,'big',signed=True)

def evidence_paths(root,f):
    from data_providers import document
    ledger=document(root,'recovery/ledger.json');names=set()
    for fid in f['anchors']:
        item=ledger['functions'].get(fid) or ledger['reconstructed_asm'][fid]
        names.update(item[k] for k in ('source','proof'))
        if 'fact' in item:names.add(item['fact'])
    return sorted(names)

def anchors(root,f,analysis,ledger,promotions):
    from data_provider_tables import canonical_anchors
    from storage_plan import clean
    cids={fid:pin for fid,pin in f['anchors'].items() if fid in ledger['functions']}
    a={fid:(clean(c),p,fun) for fid,(c,p,fun) in canonical_anchors(root,dict(f,anchors=cids),analysis,ledger,promotions).items()}
    for fid,pin in f['anchors'].items():
        if fid in cids:continue
        item=ledger['reconstructed_asm'][fid];src=to_mechanical(canonical_path(root,item['source']).read_bytes());proof=canonical_path(root,item['proof']).read_bytes()
        require(item['state']=='FUNCTION_CODE_MATCH' and pin=={k:item[k] for k in ('source_sha256','proof_sha256')} and sha256(src)==pin['source_sha256'] and sha256(proof)==pin['proof_sha256'],'stale accepted ASM consumer')
        p=json.loads(proof);require(p['regression'].get('passed') is True and p['comparison'].get('state')=='FUNCTION_CODE_MATCH','canonical ASM proof/gate absent')
        a[fid]=(clean(src.decode('ascii'),assembly=True),p,None)
    return a

def asset_index(a,index):
    from data_provider_tables import fragments,compact
    c=a['resident_F_4D04'][0]
    fragments(c,'unsigned int n;','G_h01_46DA = G_h01_A7CE[G_h01_2042[n]];','for (i = 0; G_h01_1F9E[n][i] != 0xff; i++) {','v = G_h01_1F9E[n][i];','F_h00_291E(v, 0L)')
    witnesses=[]
    for fid,(src,_,_) in a.items():
        if fid in ('resident_F_4D04','resident_F_4EC6'):continue
        calls=re.findall(r'F_h00_4D04\(\s*(0x[0-9a-fA-F]+|[0-9]+)\s*\)',src)
        if any(int(x,0)==index for x in calls):witnesses.append(fid)
        if fid=='ov04_F_1AA2' and index in (15,16):
            fragments(src,'value=(F_h00_463E()&1) ? 15 : 16;','F_h00_4D04(value);');witnesses.append(fid)
    require(witnesses,'asset index lacks a canonical literal/closed conditional argument')
    return sorted(set(witnesses))

def asset_prefix(a):
    # One independently executed literal selector is sufficient to establish
    # a uniform pointer/flag view through that index, not historical capacity.
    values=[int(x,0) for fid,(src,_,_) in a.items() if fid not in ('resident_F_4D04','resident_F_4EC6') for x in re.findall(r'F_h00_4D04\(\s*(0x[0-9a-fA-F]+|[0-9]+)\s*\)',src)]
    require(values,'asset prefix lacks a literal canonical selector witness')
    highest=max(values);return highest,asset_index(a,highest)


def pointer_target(blob,model,base,index):
    site=base+index*4;rs=relocation_profile(model,1,site,4)
    require(len(rs)==1 and rs[0]['offset']==0 and rs[0]['type']=='HUNK_RELOC32' and rs[0]['width']==4 and rs[0]['target_hunk']==1,'typed pointer cell lacks exact resident DATA relocation')
    target=rs[0]['addend'];require(payload(blob,model,1)[site:site+4]==target.to_bytes(4,'big'),'original pointer operand/relocation differ')
    return target

def sample_domain(a,blob,model):
    from data_provider_tables import fragments,binding
    require(set(a)==C_SAMPLE|ASM_SAMPLE,'complete sample access-domain anchors')
    fragments(a['resident_F_4AF0'][0],'F_h00_48D4(0);','k=1;','F_h00_48D4(k);','slot=G_h01_28C4;')
    fragments(a['resident_F_48D4'][0],'a=a*6;','slot=G_h01_27E4[a];','k=1;','slot=G_h01_27E4[k+a];','}while(k<6);')
    fragments(a['resident_F_49A0'][0],'for (i = 0; i < 7; i++) {','G_h01_27E4[i + 48]','F_h00_46CE(8,','F_h00_46CE(9,')
    fragments(a['resident_F_46CE'][0],'L8=n*3;','hdr=G_h01_27E4[L8];','plane=G_h01_27E4[L8]+1;','for(p=0;p<3;p++)')
    fragments(a['resident_F_4D04'][0],'k = 0;','F_h00_46CE(k++ + 11,','pt = G_h01_27E4[i + 57];')
    fragments(a['ov05_F_0000'][0],'F_h00_4D04(5);')
    binding(a['resident_F_4D04'],'G_h01_1F9E',0x1f9e)
    # The concrete five-ID program establishes both i and k domains without
    # inventing a capacity for any borrowed [1]/[55] pointer-table declaration.
    target=pointer_target(blob,model,0x1f9e,5);data=payload(blob,model,1);end=data.find(b'\xff',target)
    require(end>=target,'asset program lacks terminator');count=end-target
    require(count>0,'empty witness program')
    slots=set(range(12))|set(range(24,30))|set(range(48,55))|{56}|{57+i for i in range(count)}|{(11+i)*3+p for i in range(count) for p in range(3)}
    # Descriptor stride and sentinel follow from register-ABI readers, not a
    # source declaration's convenient allocation size.
    fragments(a['resident_asm_59A4'][0],'lea _G_h01_27E4_A4(a4),a4','movea.l 0(a4,d0.w),a4','move.w (a4)+,(a2)','move.w (a4)+,4(a3)','move.l (a4)+,(a3)')
    fragments(a['resident_frameless_55D6'][0],'movea.l _G_h01_2B52,a0','move.w (a0)+,d0','tst.w d0','bmi _recon_h00_563C','beq _recon_h00_561C','move.w (a0)+,$dff0a4','move.l (a0)+,$dff0a0','move.l a0,_G_h01_2B52')
    return slots,dict(witness_asset_program_index=5,witness_ids=count,descriptor_stride=8,terminal_width=2,full_pointer_table_capacity='UNKNOWN')

def typed_evidence(root,f,analysis,ledger,promotions):
    from data_provider_tables import fragments,binding
    from census import advisory_image
    from game_image import game
    shape(f);a=anchors(root,f,analysis,ledger,promotions);route=f['route'];index=f['selector_index'];o=f['original']
    with advisory_image():blob,model,_=game()
    if route in ('ASSET_ID_PROGRAM','ASSET_FLAG_CELL','ASSET_ID_PREFIX_MEMBER','ASSET_FLAG_PREFIX_MEMBER'):
        require({'resident_F_4D04','resident_F_4EC6'}<=set(a),'asset reader/free-loop anchors')
        if route in ('ASSET_ID_PREFIX_MEMBER','ASSET_FLAG_PREFIX_MEMBER'):
            highest,witnesses=asset_prefix(a);require(index<=highest,'asset member exceeds independently accessed prefix')
        else:witnesses=asset_index(a,index)
        binding(a['resident_F_4D04'],'G_h01_1F9E',0x1f9e)
        fragments(a['resident_F_4EC6'][0],'G_h01_1F9E[G_h01_B1F0][i]!=0xff')
        if route in ('ASSET_ID_PROGRAM','ASSET_ID_PREFIX_MEMBER'):
            require(pointer_target(blob,model,0x1f9e,index)==o['start'],'independently selected program target moved')
            details=dict(selector_index=index,witnesses=witnesses,element_semantics='archive asset ID passed to291E; first FF terminator',capacity_claim=False)
        else:
            binding(a['resident_F_4D04'],'G_h01_2042',0x2042)
            details=dict(selector_index=index,witnesses=witnesses,element_semantics='archive pointer selector byte',capacity_claim=False)
    else:
        slots,details=sample_domain(a,blob,model)
        if route=='SAMPLE_RECORD_PREFIX_MEMBER':
            require(index<=max(slots),'sample member exceeds independently accessed prefix')
            details=dict(details,access_domain_prefix_count=max(slots)+1,member_not_individually_witnessed=True)
        else:require(index in slots,'sample slot lacks independently finite C access domain')
        require(pointer_target(blob,model,0x27e4,index)==o['start'],'sample prefix lacks independently selected named target')
        details=dict(details,selector_index=index,records=len(f['definitions'][0]['initializer']['records']),terminal='first nonpositive signed duration; unconsumed six-byte suffix stays RAW')
    return [dict(kind=route,anchors=f['anchors'],details=details,historical_extent='complete reconstructed provider; no historical TU/capacity claim')]

def compare_data(original,model,f,obj,linked,map_text):
    from data_provider_tables import numeric_compare
    return numeric_compare(original,model,f,obj,linked,map_text,shape(f),semantic(f),source(f))
