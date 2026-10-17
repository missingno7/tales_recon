"""Additional closed consumer recipes; storage gaps never set a bound.

A slice partitions a proved access domain at already accepted typed members.
No route establishes a historical array capacity or original translation unit.
"""
import re,json
from fractions import Fraction
from common import require,sha256
from repo_paths import canonical_path
from audio_sequence_data import payload

ROUTES={'PALETTE_SLICE','PALETTE_COPY32','FRAME_COORDINATES','FFP_COORDINATES32','FFP_SPEED','LZW_MASKS4','INDEXED_WORD_SUFFIX','SCALAR_CELL','ABSOLUTE_SCALAR','LOCATION_OPTION_ROWS'}
WIDTHS={'char':1,'unsigned char':1,'short':2,'unsigned short':2,'int':2,'unsigned int':2,'long':4,'unsigned long':4,'float':4}

def ffp(text):
    require(isinstance(text,str) and re.fullmatch(r'-?(?:0|[1-9][0-9]*)\.[0-9]+',text),'finite decimal float initializer required')
    v=Fraction(text)
    if not v:return bytes(4)
    sign=128 if v<0 else 0;v=abs(v);exp=0
    while v>=1:v/=2;exp+=1
    while v<Fraction(1,2):v*=2;exp-=1
    mant=(v*2**24+Fraction(1,2)).numerator//(v*2**24+Fraction(1,2)).denominator
    if mant==2**24:mant//=2;exp+=1
    require(0<exp+64<128,'FFP range')
    return mant.to_bytes(3,'big')+bytes([sign+exp+64])

def shape(f):
    require(set(f)=={'schema_version','kind','id','source','original','definitions','route','anchors','object_sections','historical_owner','historical_tu','original_filename','producer'},'closed game-table fact fields')
    o=f['original'];route=f['route'];ds=f['definitions']
    require(f['schema_version']==1 and f['kind']=='BOUNDED_DATA_TABLE' and route in ROUTES,'closed game-table recipe')
    require(set(o)=={'hunk','start','size'} and o['hunk']==1 and type(o['start']) is int and o['start']>=0x320 and type(o['size']) is int and o['size']>0,'initialized game DATA only')
    require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','provider identity')
    require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown historical provenance')
    require(isinstance(f['anchors'],dict) and f['anchors'] and isinstance(ds,list) and len(ds)==1,'one independently bounded definition')
    d=ds[0];require(set(d)=={'symbol','type','offset','dimensions','initializer','bounds'},'typed game definition fields')
    require(d['symbol']=='G_h01_%04X'%o['start'] and d['offset']==0 and d['type'] in WIDTHS,'named typed scalar/array')
    dims=d['dimensions'];require(isinstance(dims,list) and (not dims or len(dims)<=2 and all(type(n) is int and n>0 for n in dims)),'closed dimension')
    vals=d['initializer'] if dims else [d['initializer']]
    if route=='LOCATION_OPTION_ROWS':
        require(o['start']==0x12c0 and d['type']=='int' and dims==[6,5] and isinstance(vals,list) and len(vals)==6 and all(isinstance(row,list) and len(row)==5 for row in vals),'independent six-row/five-WORD domain')
        vals=[v for row in vals for v in row]
    else:require(isinstance(vals,list) and len(vals)==(dims[0] if dims else 1),'complete initializer')
    if route=='LOCATION_OPTION_ROWS':pass
    elif route=='PALETTE_SLICE':
        sizes={0x15e6:17,0x1610:11,0x16e6:17,0x1710:11}
        require(o['start'] in sizes and dims==[sizes[o['start']]] and d['type']=='unsigned int','proved32 palette minus accepted middle words')
    elif route=='PALETTE_COPY32':require(o['start']==0x1666 and dims==[32] and d['type']=='short','canonical32-WORD copy')
    elif route=='FRAME_COORDINATES':require(o['start'] in (0x60a,0x612,0x626,0x636,0x646,0x656) and dims==[{0x60a:2,0x612:10}.get(o['start'],8)] and d['type']=='short','closed frame-coordinate domain')
    elif route=='FFP_COORDINATES32':require(o['start']==0x9b2 and dims==[32] and d['type']=='float','sixteen coordinate pairs')
    elif route=='FFP_SPEED':require(o['start']==0xa7e and not dims and d['type']=='float','scalar speed')
    elif route=='LZW_MASKS4':require(o['start']==0x1e26 and dims==[4] and d['type']=='unsigned short','LZW9..12 bits')
    elif route=='INDEXED_WORD_SUFFIX':require(o['start']==0x131a and dims==[3] and d['type']=='int','explicit13..15 word cells only')
    else:require(not dims and d['type']!='float','direct scalar access only')
    for v in vals:
        if d['type']=='float':ffp(v)
        else:
            width=WIDTHS[d['type']];unsigned=d['type'].startswith('unsigned')
            require(type(v) is int and (0 if unsigned else -(1<<(width*8-1)))<=v<(1<<(width*8-(0 if unsigned else 1))),'strict scalar range')
            if route in ('PALETTE_SLICE','PALETTE_COPY32'):require(0<=v<=4095,'RGB4 words')
    size=WIDTHS[d['type']]*len(vals)
    require(WIDTHS[d['type']]==1 or o['start']%2==0,'natural scalar alignment')
    require(o['size']==size and d['bounds']==dict(kind=route,bytes=size),'independent typed extent')
    require(f['object_sections']==dict(CODE=0,DATA=(size+1)&~1,BSS=0,COMMON=0),'complete source object; alignment uncredited')
    return size

def source(f):
    shape(f);d=f['definitions'][0];ty=d['type'];vals=d['initializer'] if d['dimensions'] else [d['initializer']]
    if f['route']=='LOCATION_OPTION_ROWS':
        rows=['{'+', '.join(str(v) for v in row)+'}' for row in d['initializer']]
        return ('int '+d['symbol']+'[6][5] = {'+', '.join(rows)+'};\n').encode('ascii')
    texts=[v if ty=='float' else str(v)+('L' if ty.endswith('long') else '') for v in vals]
    name=d['symbol']+''.join('[%d]'%n for n in d['dimensions'])
    value='{'+', '.join(texts)+'}' if d['dimensions'] else texts[0]
    return (ty+' '+name+' = '+value+';\n').encode('ascii')

def semantic(f):
    shape(f);d=f['definitions'][0];vals=d['initializer'] if d['dimensions'] else [d['initializer']]
    if f['route']=='LOCATION_OPTION_ROWS':vals=[v for row in vals for v in row]
    return b''.join(ffp(v) if d['type']=='float' else (v%(1<<(8*WIDTHS[d['type']]))).to_bytes(WIDTHS[d['type']],'big') for v in vals)

def evidence_paths(root,f):
    from data_providers import document
    ledger=document(root,'recovery/ledger.json')
    names={ledger['functions'][fid][k] for fid in f['anchors'] for k in ('source','proof')}
    if f['route']=='PALETTE_SLICE':
        base=0x1608 if f['original']['start']<0x16e6 else 0x1708
        item=ledger['data_providers']['resident_data_%04X'%base]
        names.update(item[k] for k in ('source','proof','fact'))
    if f['route']=='LOCATION_OPTION_ROWS':
        from data_provider_locrows import evidence_paths as archive_paths
        names.update(archive_paths(root))
    return sorted(names)

def scalar_access(site,width):
    return site.get('width_bytes')==width and (site.get('direction') in ('READ','WRITE','READ_WRITE') or site.get('direction')=='UNKNOWN' and width==2 and site.get('mnemonic')=='cmp.w')


def typed_evidence(root,f,analysis,ledger,promotions):
    from data_provider_tables import canonical_anchors,fragments,binding,instruction,compact
    from data_providers import document
    from storage_plan import clean
    shape(f);a={fid:(clean(c),p,fun) for fid,(c,p,fun) in canonical_anchors(root,f,analysis,ledger,promotions).items()};route=f['route'];o=f['original'];d=f['definitions'][0];n=d['symbol'];details={}
    if route=='LOCATION_OPTION_ROWS':
        from data_provider_locrows import prove
        details=prove(root,f,a)
    elif route=='PALETTE_SLICE':
        caller='ov08_F_0000' if o['start']<0x16e6 else 'ov11_F_0000';base=0x15e6 if caller=='ov08_F_0000' else 0x16e6;middle=base+34
        require(set(a)=={'resident_F_31AA',caller},'palette reader and selector')
        fragments(a['resident_F_31AA'][0],'unsigned int *target;','for (j = 0; j < 32; j++) {','tb = target[j] & 0xf;')
        fragments(a[caller][0],'F_h00_31AA(G_h01_%04X);'%base)
        binding(a[caller],'G_h01_%04X'%base,base)
        instruction(a['resident_F_31AA'][2],0x32e4,'cmpi.w','#$20, -$12(a5)')
        item=ledger['data_providers']['resident_data_%04X'%middle];fact=document(root,item['fact'])
        require(item['state']=='DATA_LAYOUT_MATCH' and fact['original']==dict(hunk=1,start=middle,size=8),'accepted independently typed four-word partition moved')
        require(o['start'] in (base,base+42) and o['size']==(34 if o['start']==base else 22),'exact complement within64-byte domain')
        details=dict(palette_base=base,domain_words=32,accepted_middle=[middle,middle+8],slice=[o['start'],o['start']+o['size']],capacity_claim=False)
    elif route=='PALETTE_COPY32':
        require(set(a)=={'ov09_F_0000','resident_F_3178'},'copy selector and reader')
        fragments(a['ov09_F_0000'][0],'F_h00_3178(&G_h01_1666);');binding(a['ov09_F_0000'],n,o['start'])
        fragments(a['resident_F_3178'][0],'short *src;','for (i = 0; i < 0x20; i++)','*dst++ = *src++;')
        details=dict(words=32,element_width=2,semantic='display palette WORD copy')
    elif route=='FRAME_COORDINATES':
        require(set(a)=={'ov10_F_0000','ov10_F_2CF4','ov10_F_2634'},'frame selector, loop and typed reader')
        c=a['ov10_F_2634'][0];fragments(c,'short *shape;','frame_index = frame;','shape[frame_index * 2]','shape[frame_index * 2 + 1]')
        binding(a['ov10_F_2634'],'G_h01_060A' if o['start']==0x612 else n,0x60a if o['start']==0x612 else o['start'])
        fragments(a['ov10_F_2CF4'][0],'frame = start;','for (i = 0; i < count; i++, frame++) {','if (frame > 3)','frame = 0;','F_h10_2634(&G_h01_7236, kind, frame);')
        parts={0x60a:('if (kind == 17) {','shape = G_h01_060A;',17),0x612:('if (kind == 17) {','shape = G_h01_060A;',17),0x626:('else if (kind == 10) {','shape = G_h01_0626;',10),0x636:('else if (kind == 11) {','shape = G_h01_0636;',11),0x646:('} else {','shape = G_h01_0646;',12),0x656:('else if (kind == 13) {','shape = G_h01_0656;',13)}
        x,y,kind=parts[o['start']];fragments(c,x,y)
        calls=re.findall(r'F_h10_2CF4\(([^;]*)\);',a['ov10_F_0000'][0]);domains=[]
        for call in calls:
            args=[compact(x) for x in call.split(',')]
            if len(args)==5 and args[3]==str(kind):
                start,count=int(args[0]),int(args[1]);frame=start;domain=[]
                for _ in range(count):
                    if frame>3:frame=0
                    domain.append(frame);frame+=1
                domains+=domain
        if kind==17:
            frames=set()
            for call in re.findall(r'F_h10_2634\(([^;]*)\);',a['ov10_F_0000'][0]):
                args=[compact(x) for x in call.split(',')]
                if len(args)==3 and args[1]=='17':
                    require(re.fullmatch('[0-9]+',args[2]),'new nonliteral frame witness needs a bounds route')
                    frames.add(int(args[2]))
            require(frames=={0,2,3,4,5,6},'changed frame domain requires repartition; never fill missing frame1')
            domains=[0] if o['start']==0x60a else list(range(2,7))
            require(set(domains)<=frames and len(domains)*2==d['dimensions'][0],'exact frame slice extent')
        else:require(set(domains)==set(range(d['dimensions'][0]//2)),'closed frame domain differs')
        details=dict(kind=kind,frame_domain=sorted(set(domains)),pair_width=4,unproved_frame1=(kind==17),capacity_claim=False)
    elif route=='FFP_COORDINATES32':
        require(set(a)=={'ov05_F_0000'},'coordinate initialization consumer')
        c=a['ov05_F_0000'][0];fragments(c,'extern float G_h01_09B2[32];','for (i = 0; i < 16; i++) {','G_h01_5DAC[2 * i] = G_h01_09B2[2 * i] * 0.6;','G_h01_5DAC[2 * i + 1] = G_h01_09B2[2 * i + 1] * 0.6;')
        binding(a['ov05_F_0000'],n,o['start'])
        details=dict(pair_domain=list(range(16)),element_width=4,float_format='Manx Motorola FFP; independently decimal source compiled and whole object compared',capacity_claim=False)
    elif route=='LZW_MASKS4':
        require(set(a)=={'resident_F_3C4C','resident_F_3E9C'},'LZW state transitions and reader')
        c=a['resident_F_3C4C'][0];fragments(c,'G_h01_B1DA = 9;','G_h01_B1DA < 0xc','G_h01_B1DA++;')
        require(len(re.findall(r'G_h01_B1DA\s*=',c))==2,'new bit-width writer requires audit')
        fragments(a['resident_F_3E9C'][0],'extern unsigned short G_h01_1E26[1];','G_h01_1E26[(unsigned short)(G_h01_B1DA - 9)]')
        binding(a['resident_F_3E9C'],n,o['start']);details=dict(bit_width_states=[9,10,11,12],index_domain=[0,1,2,3],element_width=2)
    elif route=='INDEXED_WORD_SUFFIX':
        require(set(a)=={'ov11_F_2A3A'},'explicit indexed word writer')
        c=a['ov11_F_2A3A'][0];fragments(c,'extern int G_h01_1300[16];','G_h01_1300[13] = 50;','G_h01_1300[14] = 75;','G_h01_1300[15] = 75;')
        # Accepted proof identifies each displaced reference with the base symbol.
        pr=a['ov11_F_2A3A'][1];ids=[b.get('identity') for b in pr['comparison']['relocation_proof'] if b.get('kind')=='A4_D16_SYMBOL']
        for i in (13,14,15):require(any(x and x.get('symbol')=='_G_h01_1300' and x.get('hunk')==1 and x.get('offset')==0x1300+2*i and x.get('addend')==2*i for x in ids),'indexed word lacks canonical named binding')
        details=dict(base=0x1300,indices=[13,14,15],element_width=2,capacity_claim=False)
    elif route=='ABSOLUTE_SCALAR':
        expected={0x96e:'int',0x970:'int',0x1e2e:'unsigned short',0x1f34:'int'}
        require(o['start'] in expected and d['type']==expected[o['start']] and len(a)==1,'closed absolute scalar identity/type')
        fid=next(iter(a));c,p,fun=a[fid];width=WIDTHS[d['type']]
        fragments(c,'extern '+d['type']+' '+n+';')
        matches=[]
        for b in p['comparison']['relocation_proof']:
            if b.get('kind')!='HUNK_RELOCATION' or b.get('identity')!=dict(symbol='_'+n,hunk=1,offset=o['start'],addend=0):continue
            site=fun['start']+b['offset'];ins=next((i for i in fun['instructions'] if i['offset']<=site<i['offset']+i['size']),None)
            if not ins or not ins['mnemonic'].endswith('.w') or ins['mnemonic'].startswith(('lea','pea')):continue
            if any(r['source_offset']==site and r['target_hunk']==1 and r['addend_raw']==o['start'] and r['width']==4 and r['type']=='HUNK_RELOC32' for r in fun['relocations']):matches.append(dict(site=site,instruction=ins['offset']))
        require(matches,'no decoded direct WORD scalar operand with accepted absolute binding')
        details=dict(symbol=n,type=d['type'],bytes=width,absolute_operands=matches,low_byte_alias='G_h01_0971' if o['start']==0x970 else None)
    else:
        require(len(a)==1,'one exact scalar witness');fid=next(iter(a));c,p,fun=a[fid];ty=d['type'];width=WIDTHS[ty]
        require('extern '+ty+' '+n+';' in c,'exact scalar declaration absent')
        types=document(root,'evidence/types.json');require(types['inputs']['function_ledger_sha256']==sha256(canonical_path(root,'evidence/functions/ledger.json').read_bytes()),'stale scalar width observations');g=next((g for g in types['globals'] if g['data_hunk_offset']==o['start']),None)
        require(g is not None and not g['address_taken'],'scalar needs direct access; address-taking requires bounds')
        require(set(g['observed_widths_bytes'])=={width},'conflicting scalar widths')
        sites=[x for x in g['accesses'] if x['function']==fid and scalar_access(x,width)]
        require(sites,'original scalar width access absent')
        proof=p['comparison']['relocation_proof'];matched=[]
        for site in sites:
            ins=next((i for i in fun['instructions'] if i['offset']==site['offset'] and i['raw']==site['raw']),None)
            if ins and any(b.get('kind')=='A4_D16_SYMBOL' and b.get('identity')==dict(symbol='_'+n,hunk=1,offset=o['start'],addend=0) and ins['offset']<=fun['start']+b['offset']<ins['offset']+ins['size'] for b in proof):matched.append(site)
        require(matched,'scalar lacks exact named accepted binding')
        # Only the independently identified low-byte depth alias is permitted.
        for other in types['globals']:
            at=other['data_hunk_offset'];ow=max(other['observed_widths_bytes'],default=0)
            if at!=o['start'] and ow and at<o['start']+width and o['start']<at+ow:
                require(o['start']==0x970 and at==0x971 and width==2 and ow==1,'additional scalar overlap needs a typed aggregate')
        details=dict(symbol=n,type=ty,access=matched[0],bounds='scalar ABI',low_byte_alias='G_h01_0971' if o['start']==0x970 else None)
    return [dict(kind=route,anchors=f['anchors'],details=details,historical_extent='complete reconstructed provider; historical capacity/TU unknown')]

def compare_data(original,model,f,obj,linked,map_text):
    from data_provider_tables import numeric_compare
    return numeric_compare(original,model,f,obj,linked,map_text,shape(f),semantic(f),source(f))
