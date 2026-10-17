"""Strict typed DATA providers, including independently bounded C string literals.

No instructions, guessed arrays, filler or unknown fixups.

Admits initialized scalars, independently bounded lookup arrays and one internal int-pointer fixup to
an independently evidenced first int scalar. BSS/COMMON must both be zero.
This proves a reconstructed provider contribution, never historical TU identity.
"""
import json
import re
from pathlib import Path
from common import require, sha256, json_bytes
from repo_paths import canonical_path, candidate_path
from hunk import parse
from overlay_experiment import symbols, relocation_profile
from runtime_natural_members import object_sizes
from type_evidence import DECL_RE, _type_shape
from validation_memo import shared

WIDTHS={'char':1,'unsigned char':1,'short':2,'unsigned short':2,'int':2,'unsigned int':2,'long':4,'unsigned long':4,'int *':4}
ROOT_SOURCE='src/recovered/data/'
ROOT_FACT='evidence/data-providers/'
HARNESSSOURCE=b'\tpublic .begin\n.begin\n\trts\n'


def document(root, path):
    return json.loads(canonical_path(root,path).read_bytes())


def shape(fact):
    if fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
        from data_provider_cells import shape as cell_route
        return cell_route(fact)
    if fact.get('kind')=='BOUNDED_DATA_TABLE':
        from data_provider_tables import shape as tables_route
        return tables_route(fact)
    if fact.get('kind')=='LITERAL_LINE_RECORDS':
        from data_provider_literals import shape as literal_shape
        return literal_shape(fact)
    if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
        from data_provider_pointers import shape as external_shape
        return external_shape(fact)
    require(fact.get('schema_version')==1 and re.fullmatch(r'resident_data_[0-9A-F]{4}',fact.get('id','')), 'provider identity/schema')
    require(fact.get('source')==ROOT_SOURCE+fact['id']+'.c','provider source path')
    origin=fact['original']; require(origin['hunk']==1 and type(origin['start']) is int and type(origin['size']) is int and origin['start']>=0 and origin['start']%2==0,'naturally aligned initialized H1 DATA only')
    require(fact['id']=='resident_data_%04X'%origin['start'],'provider span identity')
    require(fact.get('historical_owner')==fact.get('historical_tu')=='UNKNOWN' and fact.get('original_filename') is None,'historical ownership is not established')
    defs=fact['definitions'];require(isinstance(defs,list) and defs,'empty provider')
    cursor=0;seen=set();pointers=0
    for d in defs:
        ty=d.get('type');require(ty in WIDTHS or ty.startswith('struct '),'unsupported/opaque/array type')
        size=definition_size(d);require(type(d.get('bounds',{}).get('bytes')) is int,'non-integer bounds');require(type(d.get('offset')) is int and d.get('offset')==cursor and (size==1 or cursor%2==0),'gap, padding filler or unaligned scalar')
        require((d.get('count') is None and d.get('bounds')==dict(kind='STRUCT_ABI' if ty.startswith('struct ') else 'SCALAR_ABI',bytes=size)) or (d.get('count') is not None and d.get('bounds',{}).get('kind') in ('MASKED_INDEX','INPUT_BITS','EXPLICIT_LOOPS','GUARDED_BYTE','COORDINATES','STATE16') and d['bounds'].get('bytes')==size), 'guessed extent: independent closed bounds route required')
        absolute=origin['start']+cursor;require(re.fullmatch(r'[A-Za-z_]\w*',d.get('symbol','')),'invalid provider C symbol')
        require(d['symbol'] not in seen,'duplicate symbol');seen.add(d['symbol'])
        if ty=='int *':
            pointers+=1
            require(pointers==1 and d.get('target')==defs[0]['symbol'] and defs[0]['type']=='int' and cursor>0,
                    'v1 pointer requires the independently evidenced first int target, zero addend')
            require('initializer' not in d,'integer pointer or opaque address initializer')
        elif ty.startswith('struct '):
            fields=struct_layout(d);values=d.get('initializer')
            require(isinstance(values,list) and len(values)==len(fields),'complete struct field initializers required')
            for f,v in zip(fields,values):check_value(f['type'],v)
        else:
            values=d.get('initializer');values=values if d.get('count') is not None else [values]
            require(isinstance(values,list) and len(values)==d.get('count',1) and all(type(v) is int for v in values),'complete typed numeric initializers required')
            value=values[0]
            width=WIDTHS[ty];lo=0 if ty.startswith('unsigned') else -(1<<(8*width-1));hi=(1<<(8*width-(0 if ty.startswith('unsigned') else 1)))-1
            require(all(lo<=v<=hi for v in values),'initializer outside strict scalar type')
        cursor+=size
    require(cursor%2==0,'v1 rejects unowned terminal object padding')
    require(origin['size']==cursor,'guessed/partial provider extent')
    require(fact.get('object_sections')==dict(CODE=0,DATA=cursor,BSS=0,COMMON=0),'unproved section/BSS/COMMON obligation')
    return cursor



def check_value(ty,v):
    require(ty in WIDTHS and ty!='int *' and type(v) is int,'typed scalar field initializer required')
    w=WIDTHS[ty];unsigned=ty.startswith('unsigned');lo=0 if unsigned else -(1<<(8*w-1));hi=(1<<(8*w-(0 if unsigned else 1)))-1
    require(lo<=v<=hi,'field initializer outside type')


def struct_layout(d):
    require(re.fullmatch(r'struct [A-Za-z_]\w*',d['type']) and d.get('count') is None,'unsupported struct shape')
    fields=d.get('fields');require(isinstance(fields,list) and fields,'complete struct fields required')
    cursor=0;seen=set();result=[]
    for f in fields:
        require(set(f)=={'name','type','offset'} and f['type'] in WIDTHS and f['type']!='int *','opaque/pointer/array field rejected')
        require(re.fullmatch(r'[A-Za-z_]\w*',f['name']) and not re.search('pad|rest|unused|filler|reserved',f['name'],re.I),'padding filler/unknown field rejected')
        require(f['name'] not in seen,'duplicate struct field');seen.add(f['name'])
        if WIDTHS[f['type']]>1:cursor=(cursor+1)&~1
        require(type(f['offset']) is int and f['offset']==cursor,'struct ABI field offset/order differs')
        result.append(dict(f));cursor+=WIDTHS[f['type']]
    return result


STRUCT_CONTROL_SOURCE=b'struct DP_Abi { char mode; long count; char state; int value; };\nstruct DP_Abi DP_abi = {7, 305419896L, -1, 23};\n'


def struct_control_fact():
    return dict(schema_version=1,id='resident_data_0000',source=ROOT_SOURCE+'resident_data_0000.c',original=dict(hunk=1,start=0,size=10),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,object_sections=dict(CODE=0,DATA=10,BSS=0,COMMON=0),definitions=[dict(symbol='DP_abi',type='struct DP_Abi',offset=0,fields=[dict(name=n,type=t,offset=o) for n,t,o in [('mode','char',0),('count','long',2),('state','char',6),('value','int',8)]],initializer=[7,305419896,-1,23],bounds=dict(kind='STRUCT_ABI',bytes=10))])

def definition_size(d):
    ty=d.get('type')
    if ty=='LITERAL_LINE_RECORD':
        require(type(d.get('count')) is int and d['count'] in (15,26),'closed story array count')
        return 8*d['count']
    if ty=='CODE_ENTRY_POINTER':
        require(type(d.get('count')) is int and 0<d['count']<=44,'bounded CODE pointer count')
        return 4*d['count']
    if isinstance(ty,str) and ty.startswith('struct '):
        fields=struct_layout(d);return (fields[-1]['offset']+WIDTHS[fields[-1]['type']]+1)&~1
    require(ty in WIDTHS,'unsupported/opaque element type')
    count=d.get('count')
    if count is not None:
        require(ty in ('int','char','unsigned char') and type(count) is int and count>0,
                'only independently bounded integer/input lookup arrays; opaque byte carriers reject')
    return WIDTHS[ty]*(count if count is not None else 1)


def source(fact):
    if fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
        from data_provider_cells import source as cell_route
        return cell_route(fact)
    if fact.get('kind')=='BOUNDED_DATA_TABLE':
        from data_provider_tables import source as tables_route
        return tables_route(fact)
    if fact.get('kind')=='LITERAL_LINE_RECORDS':
        from data_provider_literals import source as literal_source
        return literal_source(fact)
    if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
        from data_provider_pointers import source as external_source
        return external_source(fact)
    shape(fact);lines=[];tags=set()
    for d in fact['definitions']:
        name=d['symbol'];ty=d['type']
        if ty.startswith('struct '):
            if ty not in tags:
                lines.append(ty+' { '+''.join(f['type']+' '+f['name']+'; ' for f in struct_layout(d))+'};\n');tags.add(ty)
            value='{'+', '.join(str(v)+('L' if f['type'].endswith('long') else '') for f,v in zip(struct_layout(d),d['initializer']))+'}'
        elif d.get('count') is not None:
            name+='['+str(d['count'])+']';value='{'+', '.join(str(v) for v in d['initializer'])+'}'
        else:value='&'+d['target'] if ty=='int *' else str(d['initializer'])+('L' if ty.endswith('long') else '')
        lines.append(ty+' '+name+' = '+value+';\n')
    return ''.join(lines).encode('ascii')


def typed_evidence(root,fact,analysis,ledger,promotions,image=None):
    if fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
        from data_provider_cells import typed_evidence as cell_route
        if image is None:
            from census import advisory_image
            from game_image import game
            with advisory_image():image=game()[:2]
        return cell_route(root,fact,*image,analysis,ledger,promotions)
    if fact.get('kind')=='BOUNDED_DATA_TABLE':
        from data_provider_tables import typed_evidence as tables_route
        return tables_route(root,fact,analysis,ledger,promotions)
    if fact.get('kind')=='LITERAL_LINE_RECORDS':
        from data_provider_literals import typed_evidence as literal_evidence
        if image is None:
            from census import advisory_image
            from game_image import game
            with advisory_image():image=game()[:2]
        return literal_evidence(root,fact,*image,analysis,ledger,promotions)
    if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
        from data_provider_pointers import typed_evidence as external_evidence
        if image is None:
            # Census replays providers while deriving the game itself, so a
            # strict game() read here would re-enter derivation. Only the
            # immutable image is needed.
            from census import advisory_image
            from game_image import game
            with advisory_image():image=game()[:2]
        blob,model=image
        return external_evidence(root,fact,blob,model,analysis,ledger)
    """Require current accepted consumers, exact declarations and bound operands."""
    shape(fact); accepted={p['id'] for p in promotions}
    types=document(root,'evidence/types.json')
    require(types['inputs']['function_ledger_sha256']==sha256(canonical_path(root,'evidence/functions/ledger.json').read_bytes()),'stale type observations')
    by={f['id']:f for f in analysis['functions']};globals_={g['data_hunk_offset']:g for g in types['globals']};out=[]
    # The existing type miner is A4-only. Do not silently ignore accepted +D
    # accesses which could enlarge/alias this provider. V1 defers such spans
    # rather than guessing an absolute operand's type or address-taking extent.
    lo=fact['original']['start'];hi=lo+fact['original']['size']
    scalar_spans=[(lo+d['offset'],lo+d['offset']+definition_size(d)) for d in fact['definitions'] if d.get('count') is None and not d['type'].startswith('struct ')]
    require(not any(f['id'] in accepted and r['target_hunk']==1 and any(a-3<=r['addend_raw']<b for a,b in scalar_spans)
                    for f in analysis['functions'] for r in f.get('relocations',[])),
            'absolute DATA reference requires a separate decoded bounds route')

    # V2's aggregate route closes over current accepted absolute consumers.
    # A new interior/alternate absolute reference must acquire its own typed
    # bounds evidence rather than hide behind the A4-only type miner.
    for d in fact['definitions']:
        if d.get('count') is None:continue
        off=lo+d['offset'];end=off+definition_size(d)
        for f in analysis['functions']:
            if f['id'] not in accepted:continue
            for r in f.get('relocations',[]):
                if r['target_hunk']==1 and off<=r['addend_raw']<end:
                    require(f['id']==d['evidence']['function'] and r['addend_raw']==off and r['source_offset']==d['evidence']['field_site'], 'additional absolute aggregate consumer/interior identity requires typed bounds evidence')
    for d in fact['definitions']:
        e=d['evidence']; fid=e['function']; require(fid in accepted and fid in ledger['functions'],'consumer is not currently canonical')
        item=ledger['functions'][fid]; c=canonical_path(root,item['source']).read_bytes();praw=canonical_path(root,item['proof']).read_bytes()
        require(sha256(c)==item['source_sha256']==e['source_sha256'] and sha256(praw)==item['proof_sha256']==e['proof_sha256'],'stale typed consumer')
        declaration=e['declaration']; require(declaration in c.decode('ascii').splitlines(),'typed declaration absent from canonical source')
        if d['bounds']['kind'] in ('STRUCT_ABI','GUARDED_BYTE','COORDINATES','STATE16'):
            from data_provider_bounds import verify_definition
            out.append(verify_definition(root,fact,d,analysis,ledger,promotions,types));continue
        if d.get('count') is not None:
            out.append(array_evidence(fact,d,by[fid],json.loads(praw),c.decode('ascii'),types));continue
        parsed=DECL_RE.fullmatch(declaration);require(parsed and not parsed['array'] and parsed['name']==d['symbol'],'array/partial declaration is not scalar evidence')
        declared=' '.join(parsed['type'].split())+(' *' if parsed['ptr'] else '')
        require(declared==d['type'],'canonical type differs')
        f=by[fid]; off=fact['original']['start']+d['offset'];size=WIDTHS[d['type']]
        g=globals_.get(off);require(g,'missing independently decoded global access')
        matches=[a for a in g['accesses'] if a['function']==fid and a['offset']==e['access_site'] and a['width_bytes']==size and a['direction'] in ('READ','WRITE','READ_WRITE')]
        require(len(matches)==1 and e['width']==size,'missing exact typed access site')
        ins=next((i for i in f['instructions'] if i['offset']==e['access_site']),None);require(ins and ins['raw']==matches[0]['raw'],'type evidence differs from original instruction')
        proof=json.loads(praw);comparison=proof['comparison'];bindings=comparison.get('relocation_proof',[])
        require(any(b.get('kind')=='A4_D16_SYMBOL' and b.get('expected')==[1,off] and b.get('identity',{}).get('addend')==0 and b.get('identity',{}).get('symbol')=='_'+d['symbol'] and b.get('identity',{}).get('hunk')==1 and b.get('identity',{}).get('offset')==off and
                    e['access_site']<=f['start']+b['offset']<e['access_site']+ins['size'] for b in bindings),'access lacks accepted named operand binding')
        require(set(g['observed_widths_bytes'])=={size},'conflicting access widths require stronger typed-object evidence')
        # No indexed/address-taking use can silently enlarge this scalar extent.
        require(not g['address_taken'],'address-taken scalar requires a separate bounds route')
        for other in types['globals']:
            o=other['data_hunk_offset'];w=max(other['observed_widths_bytes'],default=0)
            require(not(o!=off and w and o<off+size and off<o+w),'overlapping/interior access identity needs struct/union evidence')
        out.append(dict(symbol=d['symbol'],type=d['type'],bytes=size,original_offset=off,function=fid,source=item['source'],proof=item['proof'],access=matches[0],bounds='SCALAR_ABI'))
    return out


def array_evidence(fact,d,f,proof,c,types):
    """Closed decoded bounds recipes, never an extent inferred from DATA values.

    These three narrow forms deliberately reject general structs, guessed arrays
    and pointer tables until their independent bounds/targets have a proved route.
    """
    symbol=d['symbol'];count=d['count'];width=WIDTHS[d['type']]
    require(d['evidence']['declaration']=='extern '+d['type']+' '+symbol+'['+str(count)+'];', 'array declaration/type/extent differs')
    require(d['evidence']['width']==width,'array element width differs')
    kind=d['bounds']['kind'];ins=f['instructions'];by={i['offset']:i for i in ins}
    site=d['evidence']['access_site'];base=d['evidence']['base_site'];field=d['evidence']['field_site']
    require(site in by and base in by and by[base]['mnemonic']=='lea.l','decoded array base/read absent')
    off=fact['original']['start']+d['offset'];b=by[base]
    require(field==base+2,'array address field differs')
    identities=proof['comparison']['relocation_proof']
    require(any(x['offset']==field-f['start'] and x.get('kind') in ('A4_D16_SYMBOL','HUNK_RELOCATION') and
                x.get('identity')==dict(symbol='_'+symbol,hunk=1,offset=off,addend=0) for x in identities),'array lacks current accepted named address binding')
    if b['size']==6:
        require(b['raw']=='41f9'+off.to_bytes(4,'big').hex() and any(r['source_offset']==field and r['target_hunk']==1 and r['addend_raw']==off and r['width']==4 and r['type']=='HUNK_RELOC32' for r in f['relocations']), 'absolute array address/RELOC32 differs')
    else:
        require(b['size']==4 and b['raw']=='41ec'+(off-32766).to_bytes(2,'big',signed=True).hex(), 'A4 array address differs')
    if kind=='MASKED_INDEX':
        require(d['type']=='int' and count==64 and 'return '+symbol+'[(n >> 2) & 63];' in c,'masked index bounds not established')
        j=ins.index(b);window=[(i['mnemonic'],i['operands']) for i in ins[j-5:j]]
        require(window==[('lsr.w','#$2, d0'),('and.w','#$3f, d0'),('moveq','#$0, d1'),('move.w','d0, d1'),('asl.l','#$1, d1')], 'decoded unsigned 0..63 index and two-byte stride differ')
        require(by[site]['mnemonic']=='move.w' and by[site]['operands']=='(a0, d1.l), d0' and site==base+6,'word lookup differs')
        domain=list(range(64))
    elif kind=='EXPLICIT_LOOPS':
        require(d['type']=='int' and count==8 and 'for (i = 0; i < 3; i++)' in c and 'for (i = 3; i < 8; i++)' in c and c.count('F_h00_291E('+symbol+'[i],')==2 and re.search(r'for \(i = 0; i < 3; i\+\+\)\s*F_h00_291E\('+re.escape(symbol)+r'\[i\],',c) and re.search(r'for \(i = 3; i < 8; i\+\+\)\s*F_h00_291E\('+re.escape(symbol)+r'\[i\],',c), 'explicit complete 0..7 loop bounds absent')
        require(by[site]['mnemonic']=='move.w' and by[site]['operands']=='(a0, d0.l), -(a7)' and site==base+4,'word loop access differs')
        for n in d['evidence']['additional_sites']:
            require(n in by and by[n]['mnemonic']=='move.w' and by[n]['operands']=='(a0, d0.l), -(a7)','second loop access absent')
        require(len(d['evidence']['additional_sites'])==1,'both loop reads required')
        for j in [ins.index(by[site]),ins.index(by[d['evidence']['additional_sites'][0]])]:
            require(ins[j-2]['mnemonic']=='asl.l' and ins[j-2]['operands']=='#$1, d0','two-byte loop stride differs')
        require(any(i['mnemonic']=='cmpi.w' and i['operands']=='#$3, -$6(a5)' for i in ins) and any(i['mnemonic']=='cmpi.w' and i['operands']=='#$8, -$6(a5)' for i in ins),'decoded loop limits differ')
        domain=list(range(8))
    elif kind=='INPUT_BITS':
        statements=[
            's = ((*(unsigned short *)p1 & 0x80) ^ 0x80) >> 3;',
            's |= (*(unsigned short *)p0 & 0x2) << 2;',
            's |= (*(unsigned short *)p0 & 0x200) >> 7;',
            's |= ((*(unsigned short *)p0 & 0x1) << 1) ^ (*(unsigned short *)p0 & 0x2);',
            's |= ((*(unsigned short *)p0 & 0x200) >> 9) ^ ((*(unsigned short *)p0 & 0x100) >> 8);',
            'e = '+symbol+'[s];']
        require(d['type']=='unsigned char' and count==32 and ' '.join(statements) in ' '.join(c.split()),'input lookup extent is not independently bounded')
        require(by[site]['mnemonic']=='move.b' and by[site]['operands']=='(a0, d0.l), d1' and site==base+8,'byte lookup differs')
        # Exhaust the four contributing p0 bits and the p1 input bit. This
        # proves every index 0..31 without consulting any initializer value.
        domain=sorted({(((q & 0x80)^0x80)>>3)|((v&2)<<2)|((v&0x200)>>7)|(((v&1)<<1)^(v&2))|(((v&0x200)>>9)^((v&0x100)>>8))
                       for q in (0,0x80) for v in [a|(b<<1)|(h<<8)|(j<<9) for a in (0,1) for b in (0,1) for h in (0,1) for j in (0,1)]})
        require(domain==list(range(32)),'input bit-domain differs')
    else:require(False,'unproved aggregate bounds recipe')
    # The type miner is A4-only; the absolute load is evidenced directly above.
    # Interior independently decoded accesses must agree with the element view.
    for g in types['globals']:
        o=g['data_hunk_offset']
        if off<=o<off+count*width:
            require((o-off)%width==0 and all(w==width for w in g['observed_widths_bytes']), 'interior aggregate access conflicts with element type')
    return dict(symbol=symbol,type=d['type'],count=count,bytes=count*width,original_offset=off,
                function=f['id'],access=by[site],base=b,bounds=kind,index_domain=domain,
                evidence_route='CANONICAL_SOURCE_AND_DECODED_ACCESS',historical_extent='UNKNOWN; complete reconstructed provider extent only')


def data_object(raw,terminal_padding=0):
    """Bounded AJ DATA grammar from retained scalar/internal-pointer controls.

    The 0xfd 0x70 0x00 record is ONLY the measured zero-addend reference to
    first local DATA definition. Other reference encodings reject, not guess.
    """
    require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'unsupported AJ header')
    code,data,bss=object_sizes(raw);require(code==bss==0 and data>0,'complete data-only object: CODE/BSS must be zero')
    u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
    begin=u32(24)*4;syms=u16(28)*4;end=u16(30)*4
    require(begin==36 and syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\xc0\0','AJ object boundaries')
    definitions=[];annotated=False;p=syms
    for _ in range(u16(22)):
        require(p+4<=end and raw[p]==3 and raw[p+1] in (0x0a,0x2a),'non-DATA, COMMON, external or unsupported AJ symbol')
        attr=raw[p+1];value=u16(p+2);p+=4
        if attr==0x2a:
            require(not definitions and not annotated and p+2<=end and u16(p)==1,'unsupported local-reference annotation');p+=2;annotated=True
        stop=raw.find(b'\0',p,end);require(stop>=p,'truncated DATA symbol');name=raw[p:stop].decode('ascii');p=stop+1
        require(re.fullmatch(r'_[A-Za-z_]\w*',name) and 0<=value<data,'DATA symbol extent/name')
        definitions.append(dict(name=name,offset=value))
    require(end-p<=3 and raw[p:]==bytes(end-p),'AJ symbol trailer')
    result=bytearray();fixups=[];p=begin;section='CODE'
    while p<syms:
        token=raw[p];p+=1
        if token==0xf5:section='DATA';continue
        if token==0xf4:section='CODE';continue
        if token==0 and syms-p+1<=4 and raw[p-1:syms]==bytes(syms-p+1):p=syms;break
        require(section=='DATA','hidden CODE stream')
        if 0x10<=token<=0x1f:
            n=token-0x10+1;require(p+n<=syms and len(result)+n<=data,'DATA literal overrun');result+=raw[p:p+n];p+=n
        elif token==0xfd:
            require(annotated and not fixups and p+2<=syms and raw[p:p+2]==b'\x70\0' and len(result)+4<=data,'unsupported DATA fixup')
            p+=2;fixups.append(dict(offset=len(result),width=4,type='HUNK_RELOC32',symbol=definitions[0]['name'],addend=0));result+=bytes(4)
        else:require(False,'unknown AJ DATA token')
    require(type(terminal_padding) is int and terminal_padding in (0,1), 'unproved object alignment request')
    require(len(result)+terminal_padding==data and annotated==bool(fixups),'partial object DATA or annotation/fixup mismatch')
    require(not terminal_padding or (not fixups and data%2==0 and len(result)%2==1), 'implicit alignment requires odd relocation-free DATA')
    result+=bytes(terminal_padding)
    require(len({d['name'] for d in definitions})==len(definitions),'duplicate DATA definitions')
    return dict(bytes=bytes(result),definitions=definitions,fixups=fixups,sections=dict(CODE=0,DATA=data,BSS=0,COMMON=0))


def compare_data(original,original_model,fact,obj,linked,map_text):
    if fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
        from data_provider_cells import compare_data as cell_route
        return cell_route(original,original_model,fact,obj,linked,map_text)
    if fact.get('kind')=='BOUNDED_DATA_TABLE':
        from data_provider_tables import compare_data as tables_route
        return tables_route(original,original_model,fact,obj,linked,map_text)
    if fact.get('kind')=='LITERAL_LINE_RECORDS':
        from data_provider_literals import compare_data as literal_compare
        return literal_compare(original,original_model,fact,obj,linked,map_text)
    if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
        from data_provider_pointers import compare_data as external_compare
        return external_compare(original,original_model,fact,obj,linked,map_text)
    """Complete DATA and named RELOC32 identities; no byte masks or search."""
    size=shape(fact); parsed=data_object(obj); require(parsed['sections']==fact['object_sections'],'object section mismatch')
    expected_defs=[dict(name='_'+d['symbol'],offset=d['offset']) for d in fact['definitions']]
    require(parsed['definitions']==expected_defs,'complete object symbol order/extent mismatch')
    lm=parse(linked);sm=symbols(map_text)
    require([(h['number'],h['type']) for h in lm['hunks']]==[(0,'CODE'),(1,'DATA'),(2,'BSS')],'data-only link topology')
    h=lm['hunks'][1];rounded=(size+3)&~3
    require(h['initialized_size']==h['allocated_size']==rounded and h['zero_fill_size']==0,'extra DATA/COMMON allocation')
    require(lm['hunks'][0]['initialized_size']==4 and lm['hunks'][2]['allocated_size']==4,'unexpected dependency CODE/BSS')
    require(linked[lm['hunks'][0]['content_offset']:lm['hunks'][0]['content_offset']+4]==b'\x4e\x75\0\0','independent harness CODE differs')
    require({(hn,n):o for (hn,n),o in sm.items() if hn==1 and n not in ['__H1_org','__H1_end']}=={(1,d['name']):d['offset'] for d in expected_defs},'extra/moved/missing linked DATA symbol')
    require(all(sm.get((1,d['name']))==d['offset'] for d in expected_defs),'linked definition order')
    actual=linked[h['content_offset']:h['content_offset']+size]
    require(linked[h['content_offset']+size:h['content_offset']+rounded]==bytes(rounded-size),'nonzero final hunk padding')
    origin=fact['original'];oh=next(h for h in original_model['hunks'] if h['number']==origin['hunk'])
    require(oh['type']=='DATA' and origin['start']+size<=oh['initialized_size'],'provider outside initialized DATA')
    expected=original[oh['content_offset']+origin['start']:oh['content_offset']+origin['start']+size]
    original_relocs=relocation_profile(original_model,1,origin['start'],size)
    candidate_relocs=relocation_profile(lm,1,0,size)
    wanted=[];original_wanted=[];fixups=[];rebased=bytearray(actual)
    for d in fact['definitions']:
        pos=d['offset'];extent=definition_size(d)
        if d['type'].startswith('struct '):
            payload=bytearray(extent)
            for f,v in zip(struct_layout(d),d['initializer']):
                w=WIDTHS[f['type']];payload[f['offset']:f['offset']+w]=(v & ((1<<(8*w))-1)).to_bytes(w,'big')
            require(parsed['bytes'][pos:pos+extent]==actual[pos:pos+extent]==expected[pos:pos+extent]==payload,'complete struct fields/ABI padding differ')
            continue
        width=WIDTHS[d['type']]
        if d['type']!='int *':
            values=d['initializer'] if d.get('count') is not None else [d['initializer']]
            value_bytes=b''.join((v & ((1<<(width*8))-1)).to_bytes(width,'big') for v in values)
            require(parsed['bytes'][pos:pos+extent]==actual[pos:pos+extent]==expected[pos:pos+extent]==value_bytes,'typed scalar/initializer bytes mismatch')
        else:
            target=next(t for t in fact['definitions'] if t['symbol']==d['target']);c=target['offset'];o=origin['start']+c
            wanted.append(dict(offset=pos,type='HUNK_RELOC32',width=4,target_hunk=1,addend=c))
            original_wanted.append(dict(offset=pos,type='HUNK_RELOC32',width=4,target_hunk=1,addend=o))
            require(actual[pos:pos+4]==c.to_bytes(4,'big') and expected[pos:pos+4]==o.to_bytes(4,'big'),'named target/addend payload differs')
            fixups.append(dict(offset=pos,width=4,type='HUNK_RELOC32',symbol='_'+target['symbol'],addend=0));rebased[pos:pos+4]=o.to_bytes(4,'big')
    require(parsed['fixups']==fixups and candidate_relocs==wanted and original_relocs==original_wanted,'missing/extra/wrong RELOC32 identity')
    require(rebased==expected,'complete provider bytes mismatch')
    require(not [r for r in lm['relocations'] if r['source_hunk']!=1],'unexpected harness relocation')
    return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=fact['id'],original=dict(origin,sha256=sha256(expected)),
                sections=parsed['sections'],symbols=expected_defs,relocation_bindings=fixups,
                original_relocations=original_relocs,candidate_relocations=candidate_relocs,
                actual_sha256=sha256(actual),source_sha256=sha256(source(fact)),object_sha256=sha256(obj),
                historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,
                ambiguity=fact.get('ambiguity'),data_hex=rebased.hex(),zero_fill_credit=0,root_layout_proof=False)


def producer_paths(root,recipe):
    job=recipe['job']
    require(all(Path(n).name==n and '/' not in n and '\\' not in n for n in recipe['artifacts']),'producer artifact pin escapes work directory')
    require(re.fullmatch(r'build/worker-jobs/tu-layout-[a-zA-Z0-9_-]+',job),'producer job escapes approved ignored directory')
    return [job+'/'+n for n in ['request.json','result.json','worker.uae','sys/s/startup-sequence','kick.rom']]+[job+'/sys/work/'+n for n in recipe['artifacts']]


def batch_key(recipe):
    return sha256(json_bytes({k:recipe[k] for k in ['schema_version','members','prefixes','profile','commands','sources','toolchain_inventory_sha256','request_sha256']}))


def producer(root,fact,retained=None):
    """Hash-referenced ignored job. No request/result/artifact bytes in curated evidence."""
    recipe=document(root,fact['producer']['batch'])
    require(any(m['fact'].endswith('/'+fact['id']+'.json') and m['prefix']==fact['producer']['prefix'] and m['fact_sha256']==sha256(json_bytes(fact)) for m in recipe['members']),'provider is not pinned in batch')
    files,result=_audit_job(root,fact['producer']['batch'])
    prefix=fact['producer']['prefix'];require(prefix in recipe['prefixes'] and fact['producer']['profile']=='aztec36','producer selection')
    require(files[prefix+'.c']==source(fact),'source is not strict typed definitions (byte array, filler or different source)')
    return files,result


@shared
def _audit_job(root,batch):
    """Audit one complete producer job: everything that depends only on the
    batch recipe. A job holds a whole batch (up to ~150 providers), so this
    runs once per validation scope instead of once per provider; the scope
    still re-checks every file it read before returning."""
    recipe=document(root,batch);require(recipe['schema_version']==1 and recipe['profile']=='aztec36','batch producer schema/profile')
    require(recipe['cache_key']==batch_key(recipe),'producer cache key changed')
    producer_paths(root,recipe);retained=candidate_path(root,Path(root)/recipe['job'])
    def read_job(path):
        target=candidate_path(root,Path(root)/recipe['job']/path)
        require(target.is_file(),'Missing DATA producer artifact '+str(target)+'. Regenerate with python tools/data_provider_job.py --manifest '+recipe.get('manifest','evidence/data-providers/batch.json')+' --job tu-layout-REGEN --prepare; run WinUAE, collect and refresh hash pins, then reverify. No retained verdict substitutes for the job.')
        return target.read_bytes()
    request_raw=read_job('request.json');result_raw=read_job('result.json')
    require(sha256(request_raw)==recipe['request_sha256'] and sha256(result_raw)==recipe['result_sha256'],'producer request/result hash changed')
    request=json.loads(request_raw);receipt=json.loads(result_raw)
    require(receipt['request']==request and receipt['all_steps_succeeded'] is True,'producer receipt')
    require(len(receipt['artifacts'])==len({a['path'] for a in receipt['artifacts']}) and {a['path']:a['sha256'] for a in receipt['artifacts']}==recipe['artifacts'],'omitted/extra producer artifact pins')
    files={}
    for item in receipt['artifacts']:
        name=item['path'];require(Path(name).name==name and '/' not in name and '\\' not in name,'artifact escapes worker work')
        raw=read_job('sys/work/'+name);require(len(raw)==item['size'] and sha256(raw)==item['sha256'],'producer artifact changed');files[name]=raw
    prefixes=recipe['prefixes'];require(len(prefixes)==len(set(prefixes)) and all(re.fullmatch(r'[a-z][a-z0-9]*',p) for p in prefixes),'invalid producer prefixes')
    controls=recipe.get('controls',[]);require(controls in ([],['structprobe'],['extprobe'],['litprobe'],['tableprobe'],['dataprobe']),'unsupported batch control')
    require(prefixes==[m['prefix'] for m in recipe['members']]+['relprobe']+controls,'one job must contain the entire provider batch and control')
    require(recipe['sources']=={r['path']:r['sha256'] for r in request['source_files']} and recipe['commands']==[r['command'] for r in request['steps']],'curated source/command pins differ')
    require(set(recipe['toolchain_inventory_sha256'])=={'evidence/toolchain/aztec-5.0a.json','evidence/toolchain/aztec-3.6a.json','toolchain/candidate-lock.json'},'incomplete toolchain inventory pins')
    for name,digest in recipe['toolchain_inventory_sha256'].items():
        require(sha256(canonical_path(root,name).read_bytes())==digest,'toolchain inventory changed')
    commands=[]
    for p in prefixes:commands += [f'Old1:bin/cc >{p}-cc.log -a +b {p}.c',f'Old1:bin/as >{p}-as.log -o {p}.o {p}.asm']
    commands += ['Old1:bin/as >h000-as.log -o h000.o h000.asm']
    for p in prefixes:commands += [f'Old1:bin/ln >{p}-ln.log -m -t -o {p}.exe h000.o {p}.o']
    if controls==['extprobe']:
        from data_provider_pointers import commands as external_commands
        commands=external_commands(prefixes)
    if controls==['dataprobe']:
        from data_provider_cells import commands as cell_commands
        commands=cell_commands(prefixes)
    require([s['command'] for s in request['steps']]==commands and receipt['steps']==[dict(s,returncode=0) for s in request['steps']],'changed producing commands/status')
    require(request['source_files']==[dict(path=n,sha256=sha256(files[n])) for n in sorted([p+'.c' for p in prefixes]+['h000.asm']+(['bindptr.asm'] if controls==['extprobe'] else ['binddata.c'] if controls==['dataprobe'] else []))],'source inventory')
    for member in recipe['members']:
        member_fact=document(root,member['fact'])
        require(sha256(json_bytes(member_fact))==member['fact_sha256'],'batch provider fact changed')
        require(files[member['prefix']+'.c']==source(member_fact),'batch source differs from strict typed facts')
    require(files['relprobe.c']==b'int DP_test_target = 7;\nint *DP_test_pointer = &DP_test_target;\n','independently authored relocation control changed')
    require(files['h000.asm']==HARNESSSOURCE and object_sizes(files['h000.o'])==(2,0,0),'independent zero-DATA/BSS harness')
    # Full inventory is independently reconstructed, never a worker-selected subset.
    pins=[]
    for version in ['5.0a','3.6a']:
        inventory=document(root,'evidence/toolchain/aztec-'+version+'.json')
        for disk in inventory['disks']:
            if disk['status']!='VALIDATED':continue
            manifest=disk['filesystem_manifest'] if version=='5.0a' else disk['manifest']
            volume=disk['volume'] if version=='5.0a' else manifest['volume']
            pins += [dict(path='toolchain/installed/aztec-'+version+'/'+volume+'/'+e['path'],sha256=e['sha256']) for e in manifest['entries'] if e['kind']=='file']
    require(request['pinned_inputs']==pins,'incomplete or changed pinned compiler/header inventory')
    for pin in pins: require(sha256(canonical_path(root,pin['path']).read_bytes())==pin['sha256'],'changed compiler/header/OS pin')
    lock=document(root,'toolchain/candidate-lock.json');require(request['archive_sha256']==lock['sha256']==sha256(canonical_path(root,lock['archive']).read_bytes()),'toolchain archive')
    require(request['rom_sha256']==next(m['sha256'] for m in lock['members'] if m['path']=='Kick30.rom'),'ROM identity')
    require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'emulator pin')
    # Validate exact mounts and the independently reconstructed command script.
    config=read_job('worker.uae');startup=read_job('sys/s/startup-sequence')
    require(sha256(read_job('kick.rom'))==request['rom_sha256'],'producer ROM changed')
    require(sha256(config)==request['config_sha256'] and sha256(startup)==request['guest_script_sha256'],'producer config/script hash')
    text=config.decode('utf-8');job=retained.as_posix()
    require(recipe['job'].startswith('build/worker-jobs/tu-layout-'),'unexpected producer job')
    require('filesystem2=rw,DH0:Worker:'+job+'/sys,0' in text.splitlines(),'producer work mount')
    expected_mounts=[f'filesystem2=rw,DH0:Worker:{job}/sys,0']
    for hn,label,vol in [(1,'Tools1','Aztec1'),(2,'Tools2','Aztec2'),(3,'Tools4','Aztec4')]:expected_mounts.append(f'filesystem2=ro,DH{hn}:{label}:{Path(root).as_posix()}/toolchain/installed/aztec-5.0a/{vol},-128')
    expected_mounts += [f'filesystem2=ro,DH4:Old1:{Path(root).as_posix()}/toolchain/installed/aztec-3.6a/SYS1,-128',f'filesystem2=ro,DH5:Old2:{Path(root).as_posix()}/toolchain/installed/aztec-3.6a/SYS2,-128']
    require([l for l in text.splitlines() if l.startswith('filesystem2=')]==expected_mounts,'oracle or changed producer mount')
    settings=['config_description=DuckTales isolated historical build worker','use_gui=no','kickstart_rom_file='+job+'/kick.rom',
        'cpu_model=68020','cpu_speed=max','cpu_compatible=false','cpu_24bit_addressing=true','chipset=aga','chipmem_size=4',
        'fastmem_size=8','bogomem_size=0','sound_output=none','gfx_fullscreen_amiga=false','gfx_width_windowed=640',
        'gfx_height_windowed=256','gfx_framerate=10','win32.start_minimized=yes','win32.inactive_pause=false','win32.minimized_pause=false']
    require(text.splitlines()==settings+expected_mounts,'changed full producer environment recipe')

    beginning=['C:FailAt 100','C:Assign Aztec1: Tools1:','C:Assign Aztec2: Tools2:','C:Assign INCLUDE: Tools1:include','C:Assign LIB: Tools2:lib','C:Path Tools2:bin ADD','C:Stack 65536','C:CD SYS:work','C:Echo booted >booted.txt']
    for i,c in enumerate(commands):beginning += [c,f'C:Echo $RC >step-{i:02d}.rc']
    beginning += ['C:Echo done >done.txt']
    require(startup==('\n'.join(beginning)+'\n').encode('ascii') and files['done.txt'].strip()==b'done' and all(files[f'step-{i:02d}.rc'].strip()==b'0' for i in range(len(commands))),'producer execution/completion graph')
    control=dict(schema_version=1,id='resident_data_0000',source=ROOT_SOURCE+'resident_data_0000.c',original=dict(hunk=1,start=0,size=6),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,object_sections=dict(CODE=0,DATA=6,BSS=0,COMMON=0),definitions=[dict(symbol='DP_test_target',type='int',offset=0,initializer=7,bounds=dict(kind='SCALAR_ABI',bytes=2)),dict(symbol='DP_test_pointer',type='int *',offset=2,target='DP_test_target',bounds=dict(kind='SCALAR_ABI',bytes=4))])
    control_report=compare_data(files['relprobe.exe'],parse(files['relprobe.exe']),control,files['relprobe.o'],files['relprobe.exe'],files['relprobe.sym'].decode('ascii'))
    require(control_report['relocation_bindings']==[dict(offset=2,width=4,type='HUNK_RELOC32',symbol='_DP_test_target',addend=0)],'named relocation positive control differs')
    result=dict(job=recipe['job'],request_sha256=recipe['request_sha256'],result_sha256=recipe['result_sha256'],artifact_sha256=recipe['artifacts'],cache_key=recipe['cache_key'],relocation_control='EXACT_NAMED_INTERNAL_RELOC32; TEST_ONLY_NO_GAME_CREDIT')
    if controls==['structprobe']:
        require(files['structprobe.c']==STRUCT_CONTROL_SOURCE,'struct ABI control source changed')
        padfact=struct_control_fact()
        checked=compare_data(files['structprobe.exe'],parse(files['structprobe.exe']),padfact,files['structprobe.o'],files['structprobe.exe'],files['structprobe.sym'].decode('ascii'))
        result['struct_control']=dict(DATA=checked['sections']['DATA'],padding_offsets=[1,7],game_credit=0)
    if controls==['extprobe']:
        from data_provider_pointers import binder_names,binder_source,binder_object,CONTROL_SOURCE,control_report
        facts=[document(root,m['fact']) for m in recipe['members']]
        require(all(f.get('kind')=='EXTERNAL_CODE_POINTER_TABLE' for f in facts),'external batch member kind')
        names=binder_names(facts)
        require(files['bindptr.asm']==binder_source(names) and files['extprobe.c']==CONTROL_SOURCE,'independent external binder/control recipe changed')
        binder_object(files['bindptr.o'],names)
        result['external_pointer_control']=control_report(files,names)
    if controls==['tableprobe']:
        from data_provider_tables import control_report
        result['table_control']=control_report(files)
    if controls==['dataprobe']:
        from data_provider_cells import binder_names,control_report
        facts=[document(root,m['fact']) for m in recipe['members']]
        require(all(f.get('kind')=='EXTERNAL_DATA_POINTER_CELL' for f in facts),'DATA-cell batch kind')
        result['data_pointer_control']=control_report(files,binder_names(facts))
    if controls==['litprobe']:
        from data_provider_literals import control_report
        require(all(document(root,m['fact']).get('kind')=='LITERAL_LINE_RECORDS' for m in recipe['members']),'literal batch member kind')
        result['literal_control']=control_report(files)
    return files,result

def verify(root,blob,model,analysis,ledger,promotions,fact,source_bytes,retained):
    require(source_bytes==source(fact),'source differs from strict evidence-derived scalar definitions')
    evidence=typed_evidence(root,fact,analysis,ledger,promotions,image=(blob,model))
    files,producer_proof=producer(root,fact,retained);p=fact['producer']['prefix']
    report=compare_data(blob,model,fact,files[p+'.o'],files[p+'.exe'],files[p+'.sym'].decode('ascii'))
    report.update(typed_evidence=evidence,producer=producer_proof,fact_sha256=sha256(json_bytes(fact)),
        verifier_identity={'data_providers.py':sha256(Path(__file__).read_bytes()),
            **{name:sha256(canonical_path(root,'tools/'+name).read_bytes()) for name in ['common.py','repo_paths.py','type_evidence.py','hunk.py','overlay_experiment.py','runtime_natural_members.py']}})
    if any(d['bounds']['kind'] in ('STRUCT_ABI','GUARDED_BYTE','COORDINATES','STATE16') for d in fact['definitions']):
        import data_provider_bounds
        report['verifier_identity']['data_provider_bounds.py']=sha256(Path(data_provider_bounds.__file__).read_bytes())
    if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
        import data_provider_pointers
        report['verifier_identity']['data_provider_pointers.py']=sha256(Path(data_provider_pointers.__file__).read_bytes())
    if fact.get('kind')=='BOUNDED_DATA_TABLE':
        import data_provider_tables
        report['verifier_identity']['data_provider_tables.py']=sha256(Path(data_provider_tables.__file__).read_bytes())
    if fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
        import data_provider_cells
        report['verifier_identity']['data_provider_cells.py']=sha256(Path(data_provider_cells.__file__).read_bytes())
    if fact.get('kind')=='LITERAL_LINE_RECORDS':
        import data_provider_literals
        report['verifier_identity']['data_provider_literals.py']=sha256(Path(data_provider_literals.__file__).read_bytes())
    if fact.get('kind')=='BOUNDED_DATA_TABLE':
        import data_provider_more,data_provider_sequences,data_provider_audio_fields
        for module in (data_provider_more,data_provider_sequences,data_provider_audio_fields):
            if fact.get('route') in module.ROUTES:report['verifier_identity'][Path(module.__file__).name]=sha256(Path(module.__file__).read_bytes())
    if fact.get('route')=='LOCATION_OPTION_ROWS':
        import data_provider_locrows
        report['verifier_identity']['data_provider_locrows.py']=sha256(Path(data_provider_locrows.__file__).read_bytes())
    return report


def load_data_providers(root,blob,model,analysis,ledger,promotions,only=None):
    # ``only`` validates one provider against the complete ledger: typed
    # evidence may legitimately read a neighbouring provider's fact.
    records=[];occupied=set()
    for ident,item in sorted(ledger.get('data_providers',{}).items()):
        if only is not None and ident!=only:continue
        require(item['state']=='DATA_LAYOUT_MATCH','unsupported DATA provider proof level')
        fact=document(root,item['fact']);proof_path=canonical_path(root,item['proof']);proof=document(root,item['proof'])
        require(fact['id']==ident and item['source']==fact['source'],'provider identity/source')
        require(sha256(proof_path.read_bytes())==item['proof_sha256'],'provider proof changed')
        src=canonical_path(root,item['source']).read_bytes();require(sha256(src)==item['source_sha256'],'provider source changed')
        replay=verify(root,blob,model,analysis,ledger,promotions,fact,src,None)
        require(set(proof)=={'fact','comparison','regression'} and proof['regression'].get('passed') is True,
                'provider proof lacks a passing promotion regression receipt')
        # Verifier hashes are provenance only; the complete exact replay is the
        # acceptance check, so verifier edits do not strand canonical proofs.
        facts=lambda c:{k:v for k,v in c.items() if k!='verifier_identity'}
        require(isinstance(proof['comparison'].get('verifier_identity'),dict) and proof['comparison']['verifier_identity'],
                'provider proof lacks verifier provenance')
        require(proof['fact']==fact and facts(proof['comparison'])==facts(json.loads(json_bytes(replay))),
                'provider canonical receipt no longer rederives')
        points={(c['hunk'],p) for c in contributions([replay]) for p in range(c['start'],c['end'])};require(not(points&occupied),'overlapping DATA/literal providers');occupied|=points
        records.append(replay)
    return records


def contributions(records):
    out=[]
    for r in records:
        o=r['original'];rels=[dict(source_offset=o['start']+p['offset'],target_hunk=p['target_hunk'],type=p['type'],width=p['width'],addend_raw=p['addend']) for p in r['original_relocations']]
        out.append(dict(id=r['id'],hunk=o['hunk'],start=o['start'],end=o['start']+o['size'],category='RECOVERED_DATA',bytes=bytes.fromhex(r['data_hex']),relocations=rels))
        for lit in r.get('owned_literals',[]):
            out.append(dict(id=r['id']+':literals',hunk=lit['hunk'],start=lit['start'],end=lit['start']+lit['size'],category='COMPILER_OWNED_DATA',bytes=bytes.fromhex(lit['bytes_hex']),relocations=lit['relocations']))
    return out


def input_identity(root):
    """Snapshot closure: compact facts and their ignored jobs, no cached verdicts."""
    root=Path(root);names={'evidence/data-providers/batch.json','evidence/types.json'};external={}
    facts=[]
    from repo_paths import active_files
    folder=canonical_path(root,'evidence/data-providers')
    for manifest in active_files(folder,'.json') if folder.is_dir() else []:
        if manifest.name=='batch.json' or re.fullmatch(r'batch-[0-9]{4}\.json',manifest.name):
            name=manifest.relative_to(root).as_posix();names.add(name);facts+=document(root,name)['facts']
    ledger=document(root,'recovery/ledger.json') if canonical_path(root,'recovery/ledger.json').is_file() else {}
    for item in ledger.get('data_providers',{}).values():
        names.update([item['source'],item['proof']]);facts.append(item['fact'])
    batches=set()
    for name in facts:
        names.add(name);fact=document(root,name);batch=fact['producer']['batch'];names.add(batch)
        if fact.get('kind')=='EXTERNAL_CODE_POINTER_TABLE':
            from data_provider_pointers import evidence_paths
            names.update(evidence_paths(root,fact))
        if fact.get('kind')=='BOUNDED_DATA_TABLE':
            from data_provider_tables import evidence_paths
            names.update(evidence_paths(root,fact))
        if fact.get('kind')=='EXTERNAL_DATA_POINTER_CELL':
            from data_provider_cells import evidence_paths
            names.update(evidence_paths(root,fact))
        if fact.get('kind')=='LITERAL_LINE_RECORDS':
            from data_provider_literals import evidence_paths
            names.update(evidence_paths(root,fact))
        # Everything below depends only on the batch (one job per batch, up to
        # ~150 providers); it ran once per provider, re-hashing the emulator.
        if batch in batches:continue
        batches.add(batch)
        recipe=document(root,batch);names.update(producer_paths(root,recipe))
        names.update(recipe['toolchain_inventory_sha256'])
        request_path=candidate_path(root,root/recipe['job']/'request.json')
        if request_path.is_file():
            request=json.loads(request_path.read_bytes());names.update(p['path'] for p in request['pinned_inputs'])
            lock=document(root,'toolchain/candidate-lock.json');names.add(lock['archive'])
            emulator=Path(request['emulator']);external[str(emulator)]=sha256(emulator.read_bytes()) if emulator.is_file() else None
    def target(n):return candidate_path(root,root/n) if n.startswith('build/worker-jobs/') else canonical_path(root,n)
    result={}
    for n in sorted(names):
        path=target(n);result[str(path)]=sha256(path.read_bytes()) if path.is_file() else None
    return {**result,**external}
