"""Strict external CODE-entry pointer DATA, independently named and bounded.

Address-only function designators model register-ABI code addresses. They grant
no ordinary C calling convention, CODE credit, owner or original TU identity.
"""
from names import to_mechanical
import re,json
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from audio_sequence_data import payload
from overlay_experiment import symbols,relocation_profile
from hunk import parse

KIND='EXTERNAL_CODE_POINTER_TABLE'
CONTROL_SOURCE=b'extern void DP_ext_a();\nextern void DP_ext_b();\ntypedef void (*DP_CodeEntry)();\nDP_CodeEntry DP_ext_probe[3] = {DP_ext_a, DP_ext_b, DP_ext_a};\n'
CONTROL_NAMES=['_DP_ext_a','_DP_ext_b']


def shape(f):
 if f.get('id') in ('resident_data_2B6E','resident_data_2BC2'):
  from data_provider_startup import shape as startup
  return startup(f)
 require(set(f)=={'schema_version','kind','id','source','original','definitions','bindings','object_sections','historical_owner','historical_tu','original_filename','producer'},'external pointer fact fields; opaque carriers/masks reject')
 require(f['schema_version']==1 and f['kind']==KIND and f['id']=='resident_data_292E' and f['source']=='src/recovered/data/resident_data_292E.c','closed external pointer provider identity')
 require(f['original']==dict(hunk=1,start=0x292e,size=176),'exact44 pointer extent; never fabricate45th period-data alias')
 require(f['object_sections']==dict(CODE=0,DATA=176,BSS=0,COMMON=0),'whole pointer provider sections')
 require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown pointer provider provenance')
 require(len(f['definitions'])==1,'one complete independently bounded table')
 d=f['definitions'][0]
 require(set(d)=={'symbol','type','offset','count','targets','bounds','evidence'} and d['symbol']=='G_h01_292E' and d['type']=='CODE_ENTRY_POINTER' and d['offset']==0 and type(d['count']) is int and d['count']==44,'typed44 code-entry pointers required')
 require(d['bounds']==dict(kind='AUDIO_DISPATCH44_PERIOD_FENCE',bytes=176),'independent pointer bounds recipe')
 require(isinstance(d['targets'],list) and len(d['targets'])==44 and set(d['targets'])==set(f['bindings']),'complete named targets; no integer pointers or unreferenced bindings')
 for n,b in f['bindings'].items():
  require(re.fullmatch(r'_recon_h00_[0-9A-F]{4}',n) and set(b)=={'hunk','offset','provider'} and b['hunk']==0 and type(b['offset']) is int and n=='_recon_h00_%04X'%b['offset'],'named canonical CODE entry, zero addend only')
 return 176


def source(f):
 if f.get('id') in ('resident_data_2B6E','resident_data_2BC2'):
  from data_provider_startup import source as startup
  return startup(f)
 shape(f)
 lines=['typedef void (*DP_CodeEntry)();\n']+['extern void '+n[1:]+'();\n' for n in sorted(f['bindings'])]
 lines+=['DP_CodeEntry G_h01_292E[44] = {\n  '+',\n  '.join(n[1:] for n in f['definitions'][0]['targets'])+'\n};\n']
 return ''.join(lines).encode('ascii')


def binder_source(names):
 require(names==sorted(set(names)) and all(re.fullmatch(r'_[A-Za-z_]\w*',n) for n in names),'complete unique binder labels')
 return ('\n'.join(x for n in names for x in ['\tpublic '+n,n,'\trts'])+'\tend\n').encode('ascii')


def binder_names(facts):return sorted(set(CONTROL_NAMES)|{b.get('entry',n) for f in facts for n,b in f['bindings'].items()})


def commands(prefixes):
 result=[]
 for p in prefixes:result += [f'Old1:bin/cc >{p}-cc.log -a +b {p}.c',f'Old1:bin/as >{p}-as.log -o {p}.o {p}.asm']
 result+=['Old1:bin/as >h000-as.log -o h000.o h000.asm','Old1:bin/as >bindptr-as.log -o bindptr.o bindptr.asm']
 for p in prefixes:result += [f'Old1:bin/ln >{p}-ln.log -m -t -o {p}.exe h000.o {p}.o'+('' if p=='relprobe' else ' bindptr.o')]
 return result


def evidence_paths(root,fact):
 if fact.get('id') in ('resident_data_2B6E','resident_data_2BC2'):
  from data_provider_startup import evidence_paths as startup
  return startup(root,fact)
 from data_providers import document
 ledger=document(root,'recovery/ledger.json');names=set()
 ids={b['provider'] for b in fact['bindings'].values()}|{'resident_driver_5A50','resident_driver_5CC6','resident_asm_59A4'}
 for fid in ids:
  item=ledger['reconstructed_asm'][fid];names.update(item[k] for k in ['source','proof','fact'])
 return sorted(names)


def canonical_entries(root,blob,model,analysis,ledger):
 from audio_driver_asm import rows
 from evidence_snapshot import memoized
 identity=sha256(json_bytes(ledger.get('reconstructed_asm',{})))+';'+sha256(blob)
 def derive():
  reports=rows(root,blob,model,analysis,ledger);out={}
  from data_providers import document
  for r in reports:
   require(r['acceptance'] and r['source_acceptance'],'canonical driver source acceptance')
   fid=r['id'];item=ledger['reconstructed_asm'][fid];fact=document(root,item['fact'])
   for e in fact['exports']:
    if e['original'] is None:continue
    require(e['original']==fact['original']['start']+e['offset'] and e['offset']<fact['original']['size'],'entry outside complete object')
    out[e['name']]=dict(hunk=0,offset=e['original'],provider=fid)
  return out
 return memoized(root,'data-provider-canonical-code-entries',identity,derive,strict=True)


def typed_evidence(root,fact,blob,model,analysis,ledger):
 if fact.get('id') in ('resident_data_2B6E','resident_data_2BC2'):
  from data_provider_startup import typed_evidence as startup
  return startup(root,fact,blob,model,analysis,ledger)
 shape(fact);cat=canonical_entries(root,blob,model,analysis,ledger)
 require(all(cat.get(n)==b for n,b in fact['bindings'].items()),'unproved/interior/private/incorrect canonical named target')
 from data_providers import document
 d=fact['definitions'][0];e=d['evidence'];consumer=ledger['reconstructed_asm']['resident_driver_5A50']
 require(e==dict(function='resident_driver_5A50',source_sha256=consumer['source_sha256'],proof_sha256=consumer['proof_sha256']),'stale canonical pointer consumer')
 from audio_driver_contracts import decode
 code=payload(blob,model,0);by={i['offset']:i for i in decode(code[0x5a72:0x5a9c],0x5a72)}
 expected=[(0x5a80,'cmp.b','#$2c, d0'),(0x5a84,'ble.b','$5a8a'),(0x5a8a,'lsl.w','#$2, d0'),(0x5a8c,'lea.l','$292e.l, a2'),(0x5a92,'movea.l','(a2, d0.w), a2'),(0x5a9a,'jmp','(a2)')]
 for p,m,o in expected:require((by[p]['mnemonic'],by[p]['operands'])==(m,o),'decoded pointer dispatch/stride changed')
 # The inclusive44 comparison does not make45 pointers. The next field is
 # independently accessed as WORD period data by the accepted note member.
 note=ledger['reconstructed_asm']['resident_asm_59A4'];src=to_mechanical(canonical_path(root,note['source']).read_bytes());pr=canonical_path(root,note['proof']).read_bytes()
 require(sha256(src)==note['source_sha256'] and sha256(pr)==note['proof_sha256'] and b'lea _G_h01_29DE,a2\n\tmove.w 0(a2,d1.w),d1' in src,'independent period WORD fence missing')
 require(any(r['source_hunk']==0 and r['source_offset']==0x5a1e and r['target_hunk']==1 and r['addend_raw']==0x29de for r in model['relocations']),'period-data base relocation missing')
 rs=relocation_profile(model,1,0x292e,176)
 wanted=[dict(offset=4*i,type='HUNK_RELOC32',width=4,target_hunk=0,addend=fact['bindings'][n]['offset']) for i,n in enumerate(d['targets'])]
 require(rs==wanted and not any(r['source_hunk']==1 and r['source_offset']==0x29de for r in model['relocations']),'all44 original named CODE relocations; no45th')
 return [dict(symbol=d['symbol'],type=d['type'],count=44,bytes=176,original_offset=0x292e,function='resident_driver_5A50',bounds='AUDIO_DISPATCH44_PERIOD_FENCE',code_entries=fact['bindings'],index_limit_inclusive=44,valid_pointer_indices=[0,43],index44=dict(offset=0x29de,classification='PERIOD_WORD_DATA_ALIAS',pointer=False,unproved_execution=True),historical_extent='Reconstructed complete provider only; historical TU unknown')]


def object_data(raw,symbol,targets,addends=None):
 """Measured external-CODE pointer AJ grammar; packed index is not an addend.

 The batch/control prove07/28 CODE-external records, reference counts and packed
 symbol indices1..36. Unknown records, bytes, sections, COMMON or trailers fail.
 """
 require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'pointer AJ header')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
 addends=[0]*len(targets) if addends is None else addends
 require(len(addends)==len(targets) and all(type(a) is int and a>=0 for a in addends),'complete nonnegative symbolic addends')
 size=4*len(targets);externs=list(dict.fromkeys(targets));count=1+len(externs)
 require((u32(10),u32(14),u32(18))==(0,size,0),'whole data-only pointer object')
 begin=u32(24)*4;syms=u16(28)*4;end=u16(30)*4
 require(begin==36 and syms<=end==u16(32)*4==len(raw) and u16(22)==count and raw[34:36]==b'\xc0\0','pointer AJ object structure')
 symbols_=[];p=syms
 for n,name in enumerate([symbol]+externs):
  require(p+4<=end and raw[p:p+2]==(b'\x03\x0a' if n==0 else b'\x07\x28') and u16(p+2)==0,'pointer symbol type/offset; hidden COMMON/section rejects');p+=4
  references=0
  if n:
   require(p+2<=end and u16(p)==targets.count(name),'pointer external reference count');references=u16(p);p+=2
  z=raw.find(b'\0',p,end);require(z>p and raw[p:z].decode('ascii')==name,'complete pointer symbol inventory/order');p=z+1
  symbols_.append(dict(name=name,kind='DATA_DEFINITION' if n==0 else 'EXTERNAL_CODE',offset=0,references=references))
 require(end-p<=3 and raw[p:]==bytes(end-p),'pointer symbol trailer')
 p=begin;require(raw[p]==0xf5,'pointer DATA segment');p+=1;refs=[]
 for i,name in enumerate(targets):
  require(p<syms and raw[p]==0xfd,'only external long pointer records');p+=1
  if addends[i]:
   from data_provider_startup import ADDEND_BYTES
   require(addends[i] in ADDEND_BYTES and p<syms and raw[p]==0x21,'only measured symbolic-addition AJ expression');p+=1
  require(p+2<=syms and 0x70<=raw[p]<=0x7f and raw[p+1]<=2,'measured packed external CODE symbol')
  index=raw[p]-0x70+16*raw[p+1];p+=2
  require(1<=index<count and index<=36 and symbols_[index]['name']==name,'pointer fixup named index/identity')
  if addends[i]:
   encoded=ADDEND_BYTES[addends[i]];require(raw[p:p+len(encoded)]==encoded,'symbolic addend encoding differs');p+=len(encoded)
  refs.append(dict(offset=i*4,type='HUNK_RELOC32',width=4,symbol=name,addend=addends[i]))
 require(raw[p:p+2]==b'\xf4\xf5','pointer empty CODE/DATA end transition');p+=2
 require(syms==((p+4)//4)*4 and raw[p:syms]==bytes(syms-p),'pointer whole DATA stream/trailer')
 return dict(bytes=b''.join(a.to_bytes(4,'big') for a in addends),definitions=[dict(name=symbol,offset=0)],fixups=refs,symbols=symbols_,sections=dict(CODE=0,DATA=size,BSS=0,COMMON=0),object_sha256=sha256(raw))


def binder_object(raw,names):
 size=2*len(names);require(len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'binder AJ header')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
 require((u32(10),u32(14),u32(18))==(size,0,0),'independent binder complete sections')
 syms=u16(28)*4;end=u16(30)*4;require(u32(24)*4==36 and u16(22)==len(names) and syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\xc0\0','binder object boundaries')
 p=syms
 for i,n in enumerate(names):
  require(raw[p:p+2]==b'\x02\x08' and u16(p+2)==2*i,'binder CODE symbol order/offset');p+=4;z=raw.find(b'\0',p,end);require(z>p and raw[p:z].decode()==n,'binder named entry');p=z+1
 require(end-p<=3 and raw[p:]==bytes(end-p),'binder symbol trailer')
 p=36;code=bytearray()
 while len(code)<size:
  token=raw[p];p+=1;require(0x10<=token<=0x1f,'binder literal-only independent RTS code');n=token-15;require(p+n<=syms and len(code)+n<=size,'binder CODE bound');code+=raw[p:p+n];p+=n
 require(syms==((p+4)//4)*4 and raw[p:syms]==bytes(syms-p) and code==b'\x4e\x75'*len(names),'complete independent binder CODE/trailer')
 return dict(CODE=size,DATA=0,BSS=0,COMMON=0)


def linked_view(obj,linked,map_text,symbol,targets,names,addends=None):
 addends=[0]*len(targets) if addends is None else addends
 parsed=object_data(obj,symbol,targets,addends);m=parse(linked);sm=symbols(map_text);size=4*len(targets);round4=lambda n:(n+3)&~3;bc=2+2*len(names);rcode=round4(bc);rdata=round4(size)
 require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in m['hunks']]==[(0,'CODE',rcode,rcode),(1,'DATA',rdata,rdata),(2,'BSS',4,0)],'complete external-pointer link topology/allocations')
 require(payload(linked,m,0)==b'\x4e\x75'*(1+len(names))+bytes(rcode-bc),'independent harness/binder CODE and padding')
 expected={(0,'__H0_org'):0,(0,'.begin'):0,(0,'__H0_end'):rcode,(1,'__H1_org'):0,(1,symbol):0,(1,'__H1_end'):rdata,(2,'__H2_org'):rdata,(2,'__H2_end'):rdata}
 expected.update({(0,n):2+2*i for i,n in enumerate(names)});require(sm==expected,'complete pointer link symbol order/positions')
 actual=payload(linked,m,1);require(actual[size:]==bytes(rdata-size),'pointer final hunk padding')
 wanted=[dict(source_hunk=1,source_offset=4*i,target_hunk=0,addend_raw=sm[(0,n)]+addends[i],width=4,type='HUNK_RELOC32') for i,n in enumerate(targets)]
 actual_rels=[{k:r[k] for k in ['source_hunk','source_offset','target_hunk','addend_raw','width','type']} for r in m['relocations']]
 require(actual_rels==wanted,'complete external named relocation inventory')
 for i,n in enumerate(targets):require(actual[i*4:i*4+4]==(sm[(0,n)]+addends[i]).to_bytes(4,'big'),'named linked pointer payload')
 return parsed,m,actual[:size],sm


def compare_data(original,model,fact,obj,linked,map_text):
 if fact.get('id') in ('resident_data_2B6E','resident_data_2BC2'):
  from data_provider_startup import compare_data as startup
  return startup(original,model,fact,obj,linked,map_text)
 size=shape(fact);d=fact['definitions'][0];names=binder_names([fact]);targets=d['targets'];parsed,m,actual,sm=linked_view(obj,linked,map_text,'_'+d['symbol'],targets,names)
 origin=fact['original'];expected=payload(original,model,1)[origin['start']:origin['start']+size];rebased=bytearray(actual);original_wanted=[]
 for i,n in enumerate(targets):
  t=fact['bindings'][n];require(t['hunk']==0,'only independently named CODE targets');value=t['offset'].to_bytes(4,'big');require(expected[4*i:4*i+4]==value,'original pointer differs from independent target');rebased[4*i:4*i+4]=value
  original_wanted.append(dict(offset=4*i,type='HUNK_RELOC32',width=4,target_hunk=0,addend=t['offset']))
 original_rels=relocation_profile(model,1,origin['start'],size);candidate_rels=relocation_profile(m,1,0,size)
 require(original_rels==original_wanted and bytes(rebased)==expected,'whole pointer DATA/relocation identities; no masks')
 return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=fact['id'],original=dict(origin,sha256=sha256(expected)),sections=parsed['sections'],symbols=parsed['definitions'],relocation_bindings=parsed['fixups'],original_relocations=original_rels,candidate_relocations=candidate_rels,actual_sha256=sha256(actual),source_sha256=sha256(source(fact)),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=bytes(rebased).hex(),zero_fill_credit=0,root_layout_proof=False)


def control_report(files,names):
 targets=['_DP_ext_a','_DP_ext_b','_DP_ext_a']
 parsed,m,actual,sm=linked_view(files['extprobe.o'],files['extprobe.exe'],files['extprobe.sym'].decode(),'_DP_ext_probe',targets,names)
 return dict(DATA=12,relocations=3,unique_named_targets=2,source_sha256=sha256(CONTROL_SOURCE),object_sha256=parsed['object_sha256'],game_credit=0)
