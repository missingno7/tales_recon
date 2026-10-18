"""Typed tables with closed canonical consumers; no inferred byte carriers.

These are reconstructed provider objects. Historical owner, TU and filenames
remain unknown. Complete object alignment is checked but earns no DATA credit.
"""
from names import read_source
import json,re
from common import require,sha256
from repo_paths import canonical_path
from audio_sequence_data import payload
from hunk import parse
from overlay_experiment import symbols,relocation_profile

KIND='BOUNDED_DATA_TABLE'
CONTROL_SOURCE=b'char DP_odd[1][3] = {"AB"};\n'
ROUTES={'PALETTE_FADE32','CREDIT_TEXT_ROWS','TILE_CHARACTER_ROWS','ADPCM_TABLES','COORDINATE_PAIRS','LEVEL_ENTRY_ROWS','RENDERED_C_STRING','STOCK_EVENT_MASKS'}


def shape(f):
    from data_provider_audio_fields import ROUTES as AUDIO_ROUTES
    if f.get('route') in AUDIO_ROUTES:
        from data_provider_audio_fields import shape as audio_route
        return audio_route(f)
    from data_provider_sequences import ROUTES as SEQUENCE_ROUTES
    if f.get('route') in SEQUENCE_ROUTES:
        from data_provider_sequences import shape as sequence_route
        return sequence_route(f)
    from data_provider_more import ROUTES as MORE_ROUTES
    if f.get('route') in MORE_ROUTES:
        from data_provider_more import shape as more
        return more(f)
    require(set(f)=={'schema_version','kind','id','source','original','definitions','route','anchors','object_sections','historical_owner','historical_tu','original_filename','producer'},'bounded table fact fields')
    o=f['original'];route=f['route']
    require(f['schema_version']==1 and f['kind']==KIND and route in ROUTES,'bounded table schema/route')
    require(set(o)=={'hunk','start','size'} and o['hunk']==1 and type(o['start']) is int and o['start']>=0 and (o['start']%2==0 or route=='RENDERED_C_STRING') and type(o['size']) is int,'initialized aligned resident DATA only')
    require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','bounded provider identity/source')
    require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'table historical provenance unknown')
    require(isinstance(f['anchors'],dict) and f['anchors'],'canonical bounds anchors required')
    defs=f['definitions']; require(isinstance(defs,list) and len(defs)==(2 if route=='ADPCM_TABLES' else 1),'complete table definitions')
    cursor=0
    for d in defs:
        require(set(d)=={'symbol','type','offset','dimensions','initializer','bounds'},'typed table definition fields; opaque carriers reject')
        require(d['offset']==cursor and type(d['offset']) is int and d['symbol']=='G_h01_%04X'%(o['start']+cursor),'named complete table offset/order')
        dims=d['dimensions'];require(isinstance(dims,list) and all(type(n) is int and n>0 for n in dims),'closed positive dimensions')
        if route=='PALETTE_FADE32':
            require(d['type']=='unsigned int' and dims==[32],'palette WORD32 type/extent')
            require(len(d['initializer'])==32 and all(type(v) is int and 0<=v<=4095 for v in d['initializer']),'typed RGB4 palette words only')
            size=64
        elif route in ('CREDIT_TEXT_ROWS','TILE_CHARACTER_ROWS'):
            rows,stride=(24,26) if route=='CREDIT_TEXT_ROWS' else (25,21)
            require(d['type']=='char' and dims==[rows,stride],'independently decoded row count/stride')
            require(isinstance(d['initializer'],list) and len(d['initializer'])==rows,'complete character rows')
            for text in d['initializer']:
                require(isinstance(text,str) and len(text)==stride-1 and all(32<=ord(c)<127 for c in text),'exact character row plus implicit NUL; no explicit padding')
                if route=='TILE_CHARACTER_ROWS':require(set(text)<=set('012345678F'),'character tile IDs (F empty, decimal sprite index)')
            size=rows*stride
        elif route=='COORDINATE_PAIRS':
            require(d['type']=='short' and len(dims)==1 and dims[0]%2==0 and 0<dims[0]<=128,'complete signed coordinate WORD pairs')
            require(len(d['initializer'])==dims[0] and all(type(v) is int and -32768<=v<=32767 for v in d['initializer']),'coordinate scalar values')
            size=2*dims[0]
        elif route=='LEVEL_ENTRY_ROWS':
            require(d['type']=='struct DP_LevelEntry' and dims==[25] and o['start'] in (0x10f2,0x1188,0x121e),'closed six-byte level entry rows')
            require(isinstance(d['initializer'],list) and len(d['initializer'])==25,'complete level entry rows')
            for row in d['initializer']:
                require(isinstance(row,dict) and set(row)=={'kind','active','pos','t'},'complete independently accessed fields')
                require(all(type(row[k]) is int and 0<=row[k]<=255 for k in ('kind','active')) and all(type(row[k]) is int and -32768<=row[k]<=32767 for k in ('pos','t')),'strict entry field types')
            size=150
        elif route=='RENDERED_C_STRING':
            value=d['initializer']
            require(d['type']=='char' and isinstance(value,str) and value and all(32<=ord(x)<127 for x in value),'character string plus implicit NUL only')
            require(dims==[len(value)+1] and o['start'] in (0x668,0x68b,0x6a6,0x6bf,0x6db),'renderer string identity and NUL-terminated extent')
            size=len(value)+1
        elif route=='STOCK_EVENT_MASKS':
            require(o['start']==0x468 and d['type']=='unsigned char' and dims==[14] and len(d['initializer'])==14 and all(type(v) is int and 0<=v<=255 for v in d['initializer']),'bounded14 byte bit-mask lookup')
            size=14
        else:
            require(d['type']=='int' and dims==([8] if cursor==0 else [49]),'independent ADPCM domain')
            require(len(d['initializer'])==dims[0] and all(type(v) is int and -32768<=v<=32767 for v in d['initializer']),'strict signed WORD lookup values')
            size=2*dims[0]
        require(d['bounds']==dict(kind=route,bytes=size),'closed route extent')
        cursor+=size
    require(o['size']==cursor and f['object_sections']==dict(CODE=0,DATA=(cursor+1)&~1,BSS=0,COMMON=0),'entire DATA object/typed extent; no filler obligations')
    if route=='CREDIT_TEXT_ROWS':require(o['start']==0x6fe,'canonical credit identity')
    if route=='TILE_CHARACTER_ROWS':require(o['start'] in (0xac4,0xcd2,0xee0),'canonical selected map identities')
    if route=='ADPCM_TABLES':require(o['start']==0x1e32,'canonical decoder table identities')
    return cursor


def source(f):
    from data_provider_audio_fields import ROUTES as AUDIO_ROUTES
    if f.get('route') in AUDIO_ROUTES:
        from data_provider_audio_fields import source as audio_route
        return audio_route(f)
    from data_provider_sequences import ROUTES as SEQUENCE_ROUTES
    if f.get('route') in SEQUENCE_ROUTES:
        from data_provider_sequences import source as sequence_route
        return sequence_route(f)
    from data_provider_more import ROUTES as MORE_ROUTES
    if f.get('route') in MORE_ROUTES:
        from data_provider_more import source as more
        return more(f)
    shape(f);lines=[]
    if f['route']=='LEVEL_ENTRY_ROWS':lines.append('struct DP_LevelEntry { unsigned char kind, active; int pos, t; };\n')
    for d in f['definitions']:
        name=d['symbol']+''.join('[%d]'%n for n in d['dimensions'])
        if f['route']=='RENDERED_C_STRING':
            lines.append('char '+d['symbol']+'[] = '+json.dumps(d['initializer'])+';\n');continue
        if f['route']=='LEVEL_ENTRY_ROWS':
            values=['{'+', '.join(str(row[k]) for k in ('kind','active','pos','t'))+'}' for row in d['initializer']]
        else:values=[json.dumps(v) if isinstance(v,str) else str(v) for v in d['initializer']]
        lines.append(d['type']+' '+name+' = {\n  '+',\n  '.join(values)+'\n};\n')
    return ''.join(lines).encode('ascii')


def semantic(f):
    from data_provider_audio_fields import ROUTES as AUDIO_ROUTES
    if f.get('route') in AUDIO_ROUTES:
        from data_provider_audio_fields import semantic as audio_route
        return audio_route(f)
    from data_provider_sequences import ROUTES as SEQUENCE_ROUTES
    if f.get('route') in SEQUENCE_ROUTES:
        from data_provider_sequences import semantic as sequence_route
        return sequence_route(f)
    from data_provider_more import ROUTES as MORE_ROUTES
    if f.get('route') in MORE_ROUTES:
        from data_provider_more import semantic as more
        return more(f)
    shape(f);raw=bytearray()
    for d in f['definitions']:
        if f['route']=='RENDERED_C_STRING':raw+=d['initializer'].encode('ascii')+b'\0'
        elif f['route']=='LEVEL_ENTRY_ROWS':
            for row in d['initializer']:
                raw+=bytes((row['kind'],row['active']))+row['pos'].to_bytes(2,'big',signed=True)+row['t'].to_bytes(2,'big',signed=True)
        elif d['type']=='char':
            for text in d['initializer']:raw+=text.encode('ascii')+b'\0'
        elif d['type']=='unsigned char':raw+=bytes(d['initializer'])
        else:
            for v in d['initializer']:raw+=v.to_bytes(2,'big',signed=d['type'] in ('int','short'))
    return bytes(raw)


def evidence_paths(root,f):
    from data_provider_audio_fields import ROUTES as AUDIO_ROUTES
    if f.get('route') in AUDIO_ROUTES:
        from data_provider_audio_fields import evidence_paths as audio_route
        return audio_route(root,f)
    from data_provider_sequences import ROUTES as SEQUENCE_ROUTES
    if f.get('route') in SEQUENCE_ROUTES:
        from data_provider_sequences import evidence_paths as sequence_route
        return sequence_route(root,f)
    from data_provider_more import ROUTES as MORE_ROUTES
    if f.get('route') in MORE_ROUTES:
        from data_provider_more import evidence_paths as more
        return more(root,f)
    from data_providers import document
    ledger=document(root,'recovery/ledger.json')
    return sorted({ledger['functions'][fid][k] for fid in f['anchors'] for k in ('source','proof')})


def canonical_anchors(root,f,analysis,ledger,promotions):
    accepted={p['id'] for p in promotions};by={x['id']:x for x in analysis['functions']};out={}
    for fid,pin in f['anchors'].items():
        require(fid in accepted and fid in ledger['functions'] and fid in by,'table bounds consumer not currently canonical')
        item=ledger['functions'][fid];src=read_source(root, item['source'], names_root=None);pr=canonical_path(root,item['proof']).read_bytes()
        require(pin==dict(source_sha256=item['source_sha256'],proof_sha256=item['proof_sha256']) and sha256(src)==pin['source_sha256'] and sha256(pr)==pin['proof_sha256'],'stale table bounds anchor')
        out[fid]=(src.decode('ascii'),json.loads(pr),by[fid])
    return out


def compact(c):return ''.join(c.split())


def fragments(c,*parts):
    c=compact(c)
    require(all(compact(p) in c for p in parts),'canonical closed bounds/source transfer differs')


def instruction(f,site,mnemonic,operands):
    got=next((i for i in f['instructions'] if i['offset']==site),None)
    require(got and got['mnemonic']==mnemonic and got['operands']==operands,'decoded bounds/stride/width differs')
    return got


def binding(anchor,symbol,address,mnemonics=('lea.l','pea.l')):
    c,p,f=anchor;found=[]
    for b in p['comparison']['relocation_proof']:
        if b.get('kind') not in ('A4_D16_SYMBOL','HUNK_RELOCATION') or b.get('identity')!=dict(symbol='_'+symbol,hunk=1,offset=address,addend=0):continue
        site=f['start']+b['offset']-2
        i=next((i for i in f['instructions'] if i['offset']==site),None)
        if not i or i['mnemonic'] not in mnemonics:continue
        raw=i['raw'];op=raw[:4]
        if i['size']==4:
            require(op in ('41ec','486c') and raw[4:]==(address-32766).to_bytes(2,'big',signed=True).hex(),'decoded A4 table address differs')
        else:
            require(i['size']==6 and op in ('41f9','4879') and raw[4:]==address.to_bytes(4,'big').hex(),'decoded absolute table address differs')
            require(any(r['source_offset']==site+2 and r['target_hunk']==1 and r['addend_raw']==address and r['width']==4 and r['type']=='HUNK_RELOC32' for r in f['relocations']),'absolute table address lacks exact RELOC32')
        found.append(site)
    require(found,'independent canonical named table address absent')
    return found


def typed_evidence(root,f,analysis,ledger,promotions):
    from data_provider_audio_fields import ROUTES as AUDIO_ROUTES
    if f.get('route') in AUDIO_ROUTES:
        from data_provider_audio_fields import typed_evidence as audio_route
        return audio_route(root,f,analysis,ledger,promotions)
    from data_provider_sequences import ROUTES as SEQUENCE_ROUTES
    if f.get('route') in SEQUENCE_ROUTES:
        from data_provider_sequences import typed_evidence as sequence_route
        return sequence_route(root,f,analysis,ledger,promotions)
    from data_provider_more import ROUTES as MORE_ROUTES
    if f.get('route') in MORE_ROUTES:
        from data_provider_more import typed_evidence as more
        return more(root,f,analysis,ledger,promotions)
    shape(f);a=canonical_anchors(root,f,analysis,ledger,promotions);route=f['route'];o=f['original'];defs=f['definitions'];name=defs[0]['symbol'];details={}
    if route=='PALETTE_FADE32':
        require('resident_F_31AA' in a and len(a)>1,'reader and direct palette caller required')
        c,pr,reader=a['resident_F_31AA']
        fragments(c,'unsigned int *target;','for (j = 0; j < 32; j++) {','tr = (target[j] >> 8) & 0xf;','tg = (target[j] >> 4) & 0xf;','tb = target[j] & 0xf;')
        for site,m,op in [(0x31b2,'clr.w','-$12(a5)'),(0x31d0,'asl.l','#$1, d0'),(0x31d2,'movea.l','$8(a5), a0'),(0x31d6,'move.w','(a0, d0.l), d1'),(0x31ec,'movea.l','$8(a5), a0'),(0x31f0,'move.w','(a0, d0.l), d1'),(0x3206,'movea.l','$8(a5), a0'),(0x320a,'move.w','(a0, d0.l), d1'),(0x32e0,'addq.w','#$1, -$12(a5)'),(0x32e4,'cmpi.w','#$20, -$12(a5)'),(0x32ea,'blt.w','$31b6')]:instruction(reader,site,m,op)
        callers={}
        for fid,anchor in a.items():
            if fid=='resident_F_31AA':continue
            call=re.findall(r'F_h00_31AA\(([^;]*)\);',anchor[0])
            valid={name,'&'+name,'&'+name+'[0]','(char *)&'+name}
            require(any(compact(x) in {compact(v) for v in valid} for x in call),'direct palette argument is not independently named base')
            callers[fid]=binding(anchor,name,o['start'])
        details=dict(domain=list(range(32)),element_width=2,direct_callers=callers)
    elif route=='CREDIT_TEXT_ROWS':
        require(set(a)=={'ov04_F_18A6','resident_F_35DC'},'credit reader and character renderer required')
        c,p,reader=a['ov04_F_18A6'];fragments(c,'i = 0;','F_h00_35DC(64, 192, G_h01_06FE + (long)i * 26, 1, 3);','++i;','} while (i < 24);')
        for site,m,op in [(0x1902,'clr.w','-$2(a5)'),(0x1912,'muls.w','#$1a, d0'),(0x194e,'addq.w','#$1, -$2(a5)'),(0x1952,'cmpi.w','#$18, -$2(a5)'),(0x1958,'blt.b','$1906')]:instruction(reader,site,m,op)
        binding(a['ov04_F_18A6'],name,o['start']);fragments(a['resident_F_35DC'][0],'char *text;','F_h00_8BEA(G_h01_46CA, text, (long)F_h00_8044(text));')
        details=dict(rows=24,stride=26,character_semantics='canonical text renderer and length operation')
    elif route=='TILE_CHARACTER_ROWS':
        require(set(a)=={'ov08_F_0000','ov08_F_1C30'},'complete grid selector/reader anchors required')
        c,p,reader=a['ov08_F_1C30'];fragments(c,'if (a+block<25) {','p=(char *)(G_h01_6EB0+(long)(a+block)*21);','digit=0;','if (*p!=\'F\') {','G_h01_34CE=*p-\'0\';','++p;','} while (++digit<20);')
        for site,m,op in [(0x1c8a,'cmp.w','#$19, d0'),(0x1c98,'muls.w','#$15, d0'),(0x1cb0,'cmpi.b','#$46, (a0)'),(0x1cba,'move.b','(a0), d0'),(0x1cd2,'addq.l','#$1, -$c(a5)'),(0x1ce0,'cmpi.w','#$14, -$4(a5)')]:instruction(reader,site,m,op)
        fragments(a['ov08_F_0000'][0],'G_h01_6EB0 = '+name+';','c5d = 0;','F_h08_1C30(c5d);')
        require(re.search(r'unsigned char [^;]*\bc5d\b',a['ov08_F_0000'][0]),'unsigned row argument establishes nonnegative reader domain')
        binding(a['ov08_F_0000'],name,o['start'])
        details=dict(rows=25,stride=21,read_columns=list(range(20)),character_semantics='F empty or ASCII digit minus 0; implicit C literal terminator occupies row byte20',limits='row guard gives upper bound; no claim of memory safety for arbitrary negative caller input')
    elif route=='COORDINATE_PAIRS':
        require(set(a)=={'ov10_F_0000','ov10_F_2CF4'},'coordinate caller and reader required')
        c,p,reader=a['ov10_F_2CF4'];fragments(c,'short *pairs;','for (i = 0; i < count; i++, frame++) {','G_h01_7236 = pairs[2 * i];','G_h01_7238 = pairs[2 * i + 1];')
        for site,m,op in [(0x2d82,'clr.w','-$2(a5)'),(0x2da0,'asl.w','#$1, d0'),(0x2da4,'asl.l','#$1, d0'),(0x2da6,'movea.l','$c(a5), a0'),(0x2daa,'move.w','(a0, d0.l), -$dc8(a4)'),(0x2db6,'addq.w','#$1, d0'),(0x2dc0,'move.w','(a0, d0.l), -$dc6(a4)'),(0x2e46,'addq.w','#$1, -$2(a5)'),(0x2e52,'cmp.w','$a(a5), d0'),(0x2e56,'blt.w','$2d8a')]:instruction(reader,site,m,op)
        counts=[]
        for call in re.findall(r'F_h10_2CF4\(([^;]+)\);',a['ov10_F_0000'][0]):
            args=[compact(x) for x in call.split(',')]
            if len(args)!=5 or args[2]!=name:continue
            require(re.fullmatch(r'[1-9][0-9]*',args[1]),'coordinate call extent is not a positive literal')
            counts.append(int(args[1]))
        require(counts and max(counts)*2==defs[0]['dimensions'][0],'all independently bounded coordinate call domains')
        binding(a['ov10_F_0000'],name,o['start']);details=dict(pair_counts=counts,word_indices=list(range(max(counts)*2)),element_width=2)
    elif route=='LEVEL_ENTRY_ROWS':
        require(set(a)=={'ov08_F_0000','ov08_F_1F4C'},'level entry selector and reader required')
        c,p,reader=a['ov08_F_1F4C'];fragments(c,'struct Entry { unsigned char kind; unsigned char active; int pos; int t; };','for (i = P - base; i < P - base + 5 && i < 25; i++) {','if (i > 0) {','e = G_h01_6F3C + i;','switch (e->kind) {')
        for site,m,op in [(0x1f80,'muls.w','#$6, d0'),(0x1f84,'add.l','-$10c2(a4), d0'),(0x1f92,'move.b','(a0), d0'),(0x1fea,'move.b','$1(a0), d0'),(0x1ff6,'move.w','$2(a0), -$12(a5)'),(0x2034,'subq.w','#$1, $4(a0)')]:instruction(reader,site,m,op)
        require(any(i['mnemonic']=='cmpi.w' and i['operands'].startswith('#$19,') for i in reader['instructions']),'decoded25 entry ceiling')
        fragments(a['ov08_F_0000'][0],'G_h01_6F3C = (struct Entry *)'+name+';')
        binding(a['ov08_F_0000'],name,o['start']);details=dict(rows=25,stride=6,fields=[dict(name=n,offset=p,width=z) for n,p,z in [('kind',0,1),('active',1,1),('pos',2,2),('t',4,2)]],limits='row0 is the typed base record; forward loop reads positive rows below25; no guessed bytes or struct holes')
    elif route=='RENDERED_C_STRING':
        require(set(a)=={'resident_F_033E','resident_F_35DC'},'direct string caller and character renderer required')
        fragments(a['resident_F_35DC'][0],'char *text;','F_h00_8BEA(G_h01_46CA, text, (long)F_h00_8044(text));')
        calls=re.findall(r'F_h00_35DC\(([^;]+)\);',a['resident_F_033E'][0])
        require(any(len(args:=call.split(','))==5 and compact(args[2])=='&'+name for call in calls),'string address is not directly passed to canonical character renderer')
        binding(a['resident_F_033E'],name,o['start'],('pea.l',))
        details=dict(termination='first NUL consumed by canonical renderer string length; exact character initializer includes implicit NUL only',bytes=o['size'])
    elif route=='STOCK_EVENT_MASKS':
        require(set(a)=={'ov09_F_298E'},'event bit-mask reader required')
        c,p,reader=a['ov09_F_298E'];fragments(c,'value=(unsigned)F_h00_463E()%5;','value=(int)F_h00_463E()&3;','G_h01_0468[value]','G_h01_0468[value+5]','G_h01_0468[value+9]')
        for site,m,op in [(0x29e8,'divu.w','#$5, d0'),(0x2aae,'and.w','#$3, d0'),(0x2b6c,'divu.w','#$5, d0'),(0x2a10,'move.b','(a0, d0.w), d2'),(0x2ad6,'move.b','(a0, d0.w), d2'),(0x2b98,'move.b','(a0, d0.w), d2')]:instruction(reader,site,m,op)
        require(len(binding(a['ov09_F_298E'],name,o['start']))==3,'all three bit-mask table bases')
        domain=sorted(set(range(5))|{x+5 for x in range(4)}|{x+9 for x in range(5)});require(domain==list(range(14)),'closed mask index domain')
        details=dict(index_domain=domain,element_width=1,declared16_view='minimum borrowed declaration is not the recovered extent; next coordinate base0476 is not consumed')
    else:
        require(set(a)=={'resident_F_4184'},'complete ADPCM reader required')
        c,p,reader=a['resident_F_4184'];fragments(c,'index = 1;','nibble = (packed >> 4) & 15;','nibble &= 15;','magnitude = (bit4 = nibble & 4) + (bit2 = nibble & 2) + (bit1 = nibble & 1);','step = G_h01_1E42[index - 1];','index += G_h01_1E32[magnitude];','if (index > 0 && index <= 49) {','index = index < 1 ? 1 : 49;')
        require(compact(c).count('step=G_h01_1E42[index-1];')==2 and compact(c).count('index=index<1?1:49;')==2,'both nibble transitions require clamp closure')
        for site,m,op in [(0x4190,'move.w','#$1, -$4(a5)'),(0x41e0,'asl.l','#$1, d0'),(0x41e8,'move.w','(a0, d0.l), -$8(a5)'),(0x4216,'move.w','(a0, d0.l), d1'),(0x4224,'cmpi.w','#$31, -$4(a5)'),(0x42b2,'move.w','(a0, d0.l), -$8(a5)'),(0x42e0,'move.w','(a0, d0.l), d1'),(0x42ee,'cmpi.w','#$31, -$4(a5)')]:instruction(reader,site,m,op)
        for d in defs:binding(a['resident_F_4184'],d['symbol'],o['start']+d['offset'])
        require({(x&4)+(x&2)+(x&1) for x in range(16)}==set(range(8)),'nibble magnitude domain')
        details=dict(magnitude_domain=list(range(8)),step_indices=list(range(49)),element_width=2,initial_index=1,transition='clamp every index update to1..49 before next read')
    return [dict(kind=route,anchors=f['anchors'],details=details,historical_extent='complete reconstructed provider; no original TU/owner claim')]


def linked_data(obj,linked,map_text,definitions,typed,sections):
    from data_providers import data_object
    parsed=data_object(obj,terminal_padding=len(typed)%2);require(parsed['sections']==sections and parsed['definitions']==definitions and not parsed['fixups'],'complete typed DATA object sections/symbols/fixups')
    size=len(typed);obj_size=sections['DATA'];require(obj_size==(size+1)&~1 and parsed['bytes']==typed+bytes(obj_size-size),'entire source-produced DATA and implicit terminal alignment')
    lm=parse(linked);sm=symbols(map_text);rounded=(obj_size+3)&~3
    require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[(0,'CODE',4,4),(1,'DATA',rounded,rounded),(2,'BSS',4,0)],'whole DATA link topology/allocations')
    require(payload(linked,lm,0)==b'\x4e\x75\0\0' and payload(linked,lm,1)==parsed['bytes']+bytes(rounded-obj_size),'complete harness/DATA/linker alignment')
    expected={(0,'.begin'):0,(0,'__H0_org'):0,(0,'__H0_end'):4,(1,'__H1_org'):0,(1,'__H1_end'):rounded,(2,'__H2_org'):rounded,(2,'__H2_end'):rounded}
    expected.update({(1,d['name']):d['offset'] for d in definitions});require(sm==expected and not lm['relocations'],'complete linked symbols and exhaustive empty relocation inventory')
    return parsed


def compare_data(original,model,f,obj,linked,map_text):
    from data_provider_audio_fields import ROUTES as AUDIO_ROUTES
    if f.get('route') in AUDIO_ROUTES:
        from data_provider_audio_fields import compare_data as audio_route
        return audio_route(original,model,f,obj,linked,map_text)
    from data_provider_sequences import ROUTES as SEQUENCE_ROUTES
    if f.get('route') in SEQUENCE_ROUTES:
        from data_provider_sequences import compare_data as sequence_route
        return sequence_route(original,model,f,obj,linked,map_text)
    from data_provider_more import ROUTES as MORE_ROUTES
    if f.get('route') in MORE_ROUTES:
        from data_provider_more import compare_data as more
        return more(original,model,f,obj,linked,map_text)
    return numeric_compare(original,model,f,obj,linked,map_text,shape(f),semantic(f),source(f))


def numeric_compare(original,model,f,obj,linked,map_text,size,typed,source_bytes):
    defs=[dict(name='_'+d['symbol'],offset=d['offset']) for d in f['definitions']]
    parsed=linked_data(obj,linked,map_text,defs,typed,f['object_sections']);o=f['original']
    require(o['start']+size<=len(payload(original,model,1)),'provider outside initialized DATA')
    expected=payload(original,model,1)[o['start']:o['start']+size]
    require(typed==expected,'complete typed original DATA differs')
    require(not any(r['source_hunk']==1 and r['source_offset']<o['start']+size and o['start']<r['source_offset']+r['width'] for r in model['relocations']),'unproved original relocation intersects numeric/character DATA')
    return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=f['id'],original=dict(o,sha256=sha256(expected)),sections=parsed['sections'],symbols=defs,relocation_bindings=[],original_relocations=[],candidate_relocations=[],actual_sha256=sha256(typed),source_sha256=sha256(source_bytes),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=typed.hex(),uncredited_object_padding=parsed['sections']['DATA']-size,zero_fill_credit=0,root_layout_proof=False)


def control_report(files):
    require(files['tableprobe.c']==CONTROL_SOURCE,'independently authored odd character control source differs')
    parsed=linked_data(files['tableprobe.o'],files['tableprobe.exe'],files['tableprobe.sym'].decode('ascii'),[dict(name='_DP_odd',offset=0)],b'AB\0',dict(CODE=0,DATA=4,BSS=0,COMMON=0))
    return dict(DATA=4,typed_characters_including_NUL=3,uncredited_terminal_alignment=1,object_sha256=sha256(files['tableprobe.o']),game_credit=0)
