"""Closed story-record provider: C literal semantics, decoded fields and domains.

CODE is compiler-owned string data only. No instructions, opaque carriers,
guessed extents, source padding or historical object ownership are admitted.
"""
from names import to_mechanical
import json,re
from common import require,sha256
from audio_sequence_data import payload
from overlay_experiment import symbols,relocation_profile
from hunk import parse
from runtime_natural_members import object_sizes
KIND='LITERAL_LINE_RECORDS'
FIELDS=[dict(name='x',type='short',offset=0),dict(name='y',type='short',offset=2),dict(name='text',type='char *',offset=4)]
CONTROL_SOURCE=b'struct DP_Line { short x, y; char *text; };\nstruct DP_Line DP_one[2] = {{1, 2, "A"}, {-3, 4, "BC"}};\nstruct DP_Line DP_two[1] = {{5, -6, "A"}};\n'
CONSUMERS=['ov04_F_0926','ov04_F_0B50','ov04_F_0E44','resident_F_35DC','ov09_F_298E','resident_F_01BA']

def shape(f):
 require(set(f)=={'schema_version','kind','id','source','original','literal_original','definitions','evidence','object_sections','historical_owner','historical_tu','original_filename','producer'},'literal fact fields; no carriers, filler or masks')
 require(f['schema_version']==1 and f['kind']==KIND and f['id']=='resident_data_0320' and f['source']=='src/recovered/data/resident_data_0320.c','closed story identity')
 require(f['original']==dict(hunk=1,start=0x320,size=328) and f['literal_original']==dict(hunk=0,start=0x18,size=418),'two independently bounded arrays and literal bundle; root header excluded')
 require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'story historical provenance unknown')
 require(f['object_sections']==dict(CODE=418,DATA=328,BSS=0,COMMON=0),'complete literal provider sections')
 require(len(f['definitions'])==2 and set(f['evidence'])==set(CONSUMERS),'complete story definitions/consumers')
 for d,(base,count,fid) in zip(f['definitions'],[(0x320,15,'ov04_F_0926'),(0x398,26,'ov04_F_0B50')]):
  require(set(d)=={'symbol','type','offset','count','fields','initializer','bounds','evidence'} and d['symbol']=='G_h01_%04X'%base and d['type']=='LITERAL_LINE_RECORD' and d['offset']==base-0x320 and type(d['count']) is int and d['count']==count,'strict struct array/count/definition order; no byte carrier or guessed extent')
  require(d['fields']==FIELDS and d['bounds']==dict(kind='STORY_CALL_DOMAIN',bytes=count*8) and d['evidence']==dict(function=fid),'decoded ABI/field order/domain')
  require(isinstance(d['initializer'],list) and len(d['initializer'])==count,'complete typed record initializers')
  for row in d['initializer']:
   require(set(row)=={'x','y','text'} and all(type(row[k]) is int and -32768<=row[k]<=32767 for k in ['x','y']),'typed short fields only')
   require(isinstance(row['text'],str) and row['text'] and all(32<=ord(c)<127 for c in row['text']),'string literal characters plus implicit NUL only')
 require(len(semantic(f['definitions'])['code'])==418,'literal extents/pool alignment differ')
 return 328

def source(f):
 shape(f);lines=['struct DP_Line { short x, y; char *text; };\n']
 for d in f['definitions']:
  lines+=['struct DP_Line '+d['symbol']+'['+str(d['count'])+'] = {\n']
  lines+=['  {%d, %d, %s},\n'%(v['x'],v['y'],json.dumps(v['text'])) for v in d['initializer']];lines+=['};\n']
 return ''.join(lines).encode('ascii')

def semantic(definitions):
 code=bytearray();data=bytearray();fixups=[];pools=[];names=[];literal_names=[]
 for k,d in enumerate(definitions):
  start=len(code);pool=bytearray();names.append(dict(name='_'+d['symbol'],offset=len(data)))
  for i,row in enumerate(d['initializer']):
   target=len(code)+len(pool);name='_literal_'+d['symbol']+'_%02d'%i
   data+=int(row['x']).to_bytes(2,'big',signed=True)+int(row['y']).to_bytes(2,'big',signed=True)
   fixups.append(dict(offset=len(data),width=4,type='HUNK_RELOC32',symbol=name,pool=k,addend=len(pool),target=target))
   data+=target.to_bytes(4,'big');raw=row['text'].encode('ascii')+b'\0';literal_names.append(dict(name=name,offset=target,size=len(raw)));pool+=raw
  padding=len(pool)%2;code+=pool+bytes(padding);pools.append(dict(offset=start,size=len(pool),padding=padding,references=len(d['initializer'])))
 return dict(code=bytes(code),data=bytes(data),fixups=fixups,pools=pools,definitions=names,literals=literal_names)

def evidence_paths(root,fact):
 from data_providers import document
 l=document(root,'recovery/ledger.json');return sorted({l['functions'][fid][k] for fid in CONSUMERS for k in ['source','proof']})

def typed_evidence(root,fact,blob,model,analysis,ledger,promotions):
 from data_providers import document
 from repo_paths import canonical_path
 shape(fact);accepted={p['id'] for p in promotions};by={f['id']:f for f in analysis['functions']};texts={};proofs={};ev=[]
 for fid in CONSUMERS:
  require(fid in accepted and fid in ledger['functions'],'story consumer not currently canonical')
  item=ledger['functions'][fid];src=to_mechanical(canonical_path(root,item['source']).read_bytes());pr=canonical_path(root,item['proof']).read_bytes()
  require(sha256(src)==item['source_sha256'] and sha256(pr)==item['proof_sha256'],'canonical story consumer changed')
  require(fact['evidence'][fid]==dict(source_sha256=item['source_sha256'],proof_sha256=item['proof_sha256']),'stale story consumer pins')
  texts[fid]=' '.join(src.decode('ascii').split());proofs[fid]=json.loads(pr)
  ev.append(dict(function=fid,source=item['source'],source_sha256=item['source_sha256'],proof=item['proof'],proof_sha256=item['proof_sha256']))
 require(ledger['functions']['resident_F_01BA']['evidence_extent']['hunk']==0 and ledger['functions']['resident_F_01BA']['evidence_extent']['start']==0x1ba,'independent next CODE definition boundary absent')
 renderer=texts['resident_F_35DC'];require('char *text;' in renderer and 'F_h00_8BEA(G_h01_46CA, text, (long)F_h00_8044(text));' in renderer,'canonical renderer character pointer and string length ABI absent')
 caller=texts['ov04_F_0E44'];domains={}
 for d in fact['definitions']:
  fid=d['evidence']['function'];name='F_h04_'+fid.rsplit('_',1)[-1];var='i' if fid=='ov04_F_0926' else 'row';base=0x320+d['offset'];c=texts[fid]
  require('for ('+var+' = first - 1; '+var+' < last; ++'+var+')' in c,'decoded loop/source domain absent')
  calls=[tuple(map(int,m)) for m in re.findall(name+r'\((\d+), (\d+), (\d+)\);',caller)]
  domain=sorted({n for first,last,rounds in calls for n in range(first-1,last) if rounds>0})
  require(domain==list(range(d['count'])) and all(1<=x<=y<=d['count'] for x,y,z in calls),'independent complete caller domain differs')
  # Accepted source plus decoded original operations establish stride and widths.
  ins=by[fid]['instructions'];tri=[(i['mnemonic'],i['operands']) for i in ins]
  require(tri.count(('asl.l','#$3, d0'))==6,'decoded eight-byte stride differs')
  for field,width,opcode in [(0,2,'move.w'),(2,2,'move.w'),(4,4,'move.l')]:
   off=base+field;disp=off-32766;raw='41ec'+disp.to_bytes(2,'big',signed=True).hex();sites=[j for j,i in enumerate(ins) if i['raw']==raw]
   require(len(sites)==2 and all(ins[j+1]['mnemonic']==opcode and ins[j+1]['operands']=='(a0, d0.l), -(a7)' for j in sites),'decoded record base/field width differs')
   bindings=proofs[fid]['comparison']['relocation_proof']
   for j in sites:
    require(any(b.get('kind')=='A4_D16_SYMBOL' and b.get('offset')==ins[j]['offset']+2-by[fid]['start'] and b.get('expected')==[1,off] and b.get('identity')==dict(symbol='_G_h01_%04X'%off,hunk=1,offset=off,addend=0) for b in bindings),'accepted named record field binding absent')
  domains[d['symbol']]=dict(indices=domain,calls=calls,field_offsets=[0,2,4],widths=[2,2,4],stride=8)
 # The second independently addressed definition bounds the first; the separate
 # mask-array base bounds the second. No mask payload or guessed array is claimed.
 require('extern char G_h01_0468[16];' in texts['ov09_F_298E'],'independent next-definition base absent')
 require(any(b.get('kind')=='A4_D16_SYMBOL' and b.get('expected')==[1,0x468] and b.get('identity',{}).get('symbol')=='_G_h01_0468' for b in proofs['ov09_F_298E']['comparison']['relocation_proof']),'next definition lacks canonical operand identity')
 sem=semantic(fact['definitions']);o=fact['literal_original'];require(sem['code']==payload(blob,model,0)[o['start']:o['start']+o['size']],'complete semantic literal bundle differs')
 # No CODE relocation/instruction is hidden in a literal section.
 require(not relocation_profile(model,0,o['start'],o['size']),'literal section contains relocation/instruction obligation')
 require(not any(f['hunk']==0 and f['start']<o['start']+o['size'] and o['start']<f['end'] for f in analysis['functions'] if f['id'] in accepted),'literal bundle intersects canonical function')
 return [dict(kind='CANONICAL_STORY_FIELDS_AND_CALL_DOMAINS',consumers=ev,domains=domains,literals=sem['literals'],literal_semantics='C string-literal initializer; characters plus NUL; one pool per complete array; independently compiled word alignment',neighbours=[0x398,0x468],no_root_header_credit=True)]

def constant(n):
 require(type(n) is int and 0<=n<=276,'unmeasured AJ literal addend')
 return bytes([0x30+n]) if n<16 else bytes([0x50+(n&15),0x80+(n>>4)])

def object_data(raw,definitions):
 """Measured full AJ two-array grammar, including anonymous literal pools.

 FD21 is local CODE pool plus a typed literal offset. 02/A0 records carry
 pool offsets/refcounts. Every section byte, symbol, fixup and trailer is checked.
 """
 sem=semantic(definitions);code=sem['code'];data=sem['data'];require(object_sizes(raw)==(len(code),len(data),0),'complete literal AJ sections/BSS')
 require(raw[:10]==b'AJ'+bytes(8) and raw[34:36]==b'\xc0\0','literal AJ header')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big');syms=u16(28)*4;locals_=u16(30)*4;end=u16(32)*4
 require(u16(24)==len(definitions) and u16(26)*4==36 and u16(22)==len(definitions) and end==len(raw),'complete literal AJ structure')
 stream=bytearray();cursor=0
 for k,d in enumerate(definitions):
  stream.append(0xf5)
  for row in d['initializer']:
   f=sem['fixups'][cursor];cursor+=1
   stream+=b'\x13'+int(row['x']).to_bytes(2,'big',signed=True)+int(row['y']).to_bytes(2,'big',signed=True)
   stream+=b'\xfd\x21'+bytes([0x60+k,0])+constant(f['addend'])
  stream.append(0xf4);p=sem['pools'][k];pool=code[p['offset']:p['offset']+p['size']+p['padding']]
  for j in range(0,len(pool),16):chunk=pool[j:j+16];stream+=bytes([15+len(chunk)])+chunk
 stream.append(0xf5);stream+=bytes(4-(len(stream)%4))
 require(syms==36+len(stream) and raw[36:syms]==stream,'complete typed DATA/literal AJ stream, named offsets, implicit padding or trailer differ')
 named=b''.join(b'\x03\x0a'+d['offset'].to_bytes(2,'big')+d['name'].encode()+b'\0' for d in sem['definitions']);named+=bytes((-len(named))%4)
 require(locals_==syms+len(named) and raw[syms:locals_]==named,'DATA symbol order or hidden definition/COMMON')
 anon=b''.join(b'\x02\xa0'+p['offset'].to_bytes(2,'big')+p['references'].to_bytes(2,'big') for p in sem['pools'])
 require(raw[locals_:]==anon,'complete anonymous CODE pool order/reference counts')
 return dict(sections=dict(CODE=len(code),DATA=len(data),BSS=0,COMMON=0),definitions=sem['definitions'],fixups=sem['fixups'],pools=sem['pools'])

def linked_view(obj,linked,map_text,definitions):
 sem=semantic(definitions);parsed=object_data(obj,definitions);lm=parse(linked);sm=symbols(map_text);nc=len(sem['code']);nd=len(sem['data']);rc=(nc+2+3)&~3;rd=(nd+3)&~3
 require([(h['number'],h['type'],h['initialized_size'],h['allocated_size']) for h in lm['hunks']]==[(0,'CODE',rc,rc),(1,'DATA',rd,rd),(2,'BSS',0,4)],'complete literal link topology, BSS/COMMON allocation')
 require(payload(linked,lm,0)==b'\x4e\x75'+sem['code']+bytes(rc-nc-2),'entire linked CODE is independent harness plus literal pools/alignment')
 expected_symbols={(0,'.begin'):0,(0,'__H0_org'):0,(0,'__H0_end'):rc,(1,'__H1_org'):0,(1,'__H1_end'):rd,(2,'__H2_org'):rd,(2,'__H2_end'):rd};expected_symbols.update({(1,d['name']):d['offset'] for d in sem['definitions']})
 require(sm==expected_symbols,'whole linked symbol order/section obligations')
 expected=bytearray(sem['data']);rels=[]
 for f in sem['fixups']:
  value=2+f['target'];expected[f['offset']:f['offset']+4]=value.to_bytes(4,'big');rels.append(dict(offset=f['offset'],type='HUNK_RELOC32',width=4,target_hunk=0,addend=value))
 require(payload(linked,lm,1)==expected+bytes(rd-nd),'whole linked DATA and named literal pointers')
 require(relocation_profile(lm,1,0,nd)==rels and len(lm['relocations'])==len(rels),'entire named DATA-to-literal RELOC32 inventory')
 return parsed,lm,sem,bytes(expected)

def compare_data(original,model,fact,obj,linked,map_text):
 shape(fact);parsed,lm,sem,actual=linked_view(obj,linked,map_text,fact['definitions']);origin=fact['original'];lit=fact['literal_original'];expected=payload(original,model,1)[origin['start']:origin['start']+origin['size']];mapped=bytearray(actual);rels=[];bindings=[]
 for f in sem['fixups']:
  target=lit['start']+f['target'];mapped[f['offset']:f['offset']+4]=target.to_bytes(4,'big');rels.append(dict(offset=f['offset'],type='HUNK_RELOC32',width=4,target_hunk=0,addend=target));bindings.append(dict(offset=f['offset'],width=4,type='HUNK_RELOC32',symbol=f['symbol'],candidate_pool=f['pool'],pool_addend=f['addend'],candidate_target=2+f['target'],original_target=target))
 require(bytes(mapped)==expected and relocation_profile(model,1,origin['start'],origin['size'])==rels,'entire original DATA and all41 named literal relocations')
 require(payload(original,model,0)[lit['start']:lit['start']+lit['size']]==sem['code'] and not relocation_profile(model,0,lit['start'],lit['size']),'complete original compiler literal section')
 return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=fact['id'],original=dict(origin,sha256=sha256(expected)),sections=parsed['sections'],symbols=parsed['definitions'],relocation_bindings=bindings,original_relocations=rels,candidate_relocations=relocation_profile(lm,1,0,origin['size']),actual_sha256=sha256(actual),source_sha256=sha256(source(fact)),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=bytes(mapped).hex(),owned_literals=[dict(lit,sha256=sha256(sem['code']),bytes_hex=sem['code'].hex(),category='COMPILER_OWNED_DATA',literal_definitions=sem['literals'],pools=sem['pools'],relocations=[])],zero_fill_credit=0,root_layout_proof=False)

def control_report(files):
 defs=[dict(symbol='DP_one',initializer=[dict(x=1,y=2,text='A'),dict(x=-3,y=4,text='BC')]),dict(symbol='DP_two',initializer=[dict(x=5,y=-6,text='A')])]
 require(files['litprobe.c']==CONTROL_SOURCE,'literal control source differs')
 p,m,s,a=linked_view(files['litprobe.o'],files['litprobe.exe'],files['litprobe.sym'].decode('ascii'),defs)
 require(p['pools']==[dict(offset=0,size=5,padding=1,references=2),dict(offset=6,size=2,padding=0,references=1)],'independent literal order/alignment/duplicate semantics')
 return dict(sections=p['sections'],pools=p['pools'],named_relocations=3,game_credit=0)
