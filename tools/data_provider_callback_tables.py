"""Typed callback records and the independently consumed WORD prefixes.

The complete selector-writer proof bounds a record prefix, not historical
capacity. The callback's cursor and DBRA access bound the cursor domain plus n+1 source WORDs;
repeated words beyond that bound remain raw. No CODE is produced or credited.
"""
from names import read_source
import re,json
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from audio_sequence_data import payload
from overlay_experiment import relocation_profile,symbols
from hunk import parse
from validation_memo import shared
import data_provider_cells as cells

ROUTES={'CALLBACK_CYCLE_RECORDS','CALLBACK_CYCLE_WORDS'}
HEADER='struct DP_Cycle { unsigned short *words; unsigned short last; unsigned short destination; };\n'
CONTROL_SOURCE=('extern unsigned short DP_a, DP_b;\n'+HEADER+
 'struct DP_Cycle DP_cycles[3] = {{&DP_a, 1, 2}, {0, 0, 0}, {&DP_b, 3, 4}};\n').encode('ascii')


def shape(f):
 require(set(f)=={'schema_version','kind','id','source','original','definitions','route','anchors','object_sections','historical_owner','historical_tu','original_filename','producer'},'closed callback table fact fields')
 o=f['original'];require(f['schema_version']==1 and f['kind']=='BOUNDED_DATA_TABLE' and f['route'] in ROUTES and set(o)=={'hunk','start','size'} and o['hunk']==1 and type(o['start']) is int and o['start']>=0x320 and o['start']%2==0 and type(o['size']) is int,'aligned initialized callback DATA')
 require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','callback provider identity')
 require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown historical provenance')
 require(isinstance(f['anchors'],dict) and set(f['anchors'])=={'resident_callback_61A0'},'exact independently accepted callback anchor')
 require(isinstance(f['definitions'],list) and len(f['definitions'])==1,'one complete aggregate')
 d=f['definitions'][0];require(set(d)=={'symbol','type','offset','dimensions','initializer','bounds'} and d['symbol']=='G_h01_%04X'%o['start'] and d['offset']==0,'named complete callback aggregate')
 vals=d['initializer'];dims=d['dimensions'];require(isinstance(dims,list) and len(dims)==1 and type(dims[0]) is int and 0<dims[0]<=256 and isinstance(vals,list) and len(vals)==dims[0],'finite independently bounded array')
 if f['route']=='CALLBACK_CYCLE_RECORDS':
  require(d['type']=='struct DP_Cycle' and o['start']==0x2bfe,'typed pointer/WORD/WORD records')
  for row in vals:
   require(isinstance(row,dict) and set(row)=={'words','last','destination'} and all(type(row[k]) is int and 0<=row[k]<=65535 for k in ('last','destination')),'complete strict callback fields')
   require(row['words'] is None or isinstance(row['words'],str) and re.fullmatch('G_h01_[0-9A-F]{4}',row['words']),'null or independently named source words; no integer pointers')
  size=8*dims[0]
 else:
  require(d['type']=='unsigned short' and all(type(v) is int and 0<=v<=65535 for v in vals),'typed source WORDs only')
  size=2*dims[0]
 require(o['size']==size and d['bounds']==dict(kind=f['route'],bytes=size) and f['object_sections']==dict(CODE=0,DATA=size,BSS=0,COMMON=0),'whole typed callback object; no padding fillers')
 return size


def source(f):
 shape(f);d=f['definitions'][0];vals=d['initializer']
 if f['route']=='CALLBACK_CYCLE_WORDS':return ('unsigned short '+d['symbol']+'[%d] = {'%len(vals)+', '.join(map(str,vals))+'};\n').encode('ascii')
 names=sorted({row['words'] for row in vals if row['words'] is not None})
 return (HEADER+''.join('extern unsigned short '+n+'[];\n' for n in names)+
  'struct DP_Cycle '+d['symbol']+'[%d] = {'%len(vals)+', '.join('{'+(row['words'] or '0')+', '+str(row['last'])+', '+str(row['destination'])+'}' for row in vals)+'};\n').encode('ascii')


def semantic(f):
 shape(f);d=f['definitions'][0]
 if f['route']=='CALLBACK_CYCLE_WORDS':return b''.join(v.to_bytes(2,'big') for v in d['initializer'])
 return b''.join(bytes(4)+r['last'].to_bytes(2,'big')+r['destination'].to_bytes(2,'big') for r in d['initializer'])


def evidence_paths(root,f):
 from data_providers import document,producer_paths
 from data_provider_sequences import evidence_paths as anchor_paths
 l=document(root,'recovery/ledger.json');names=set(anchor_paths(root,f))
 for ident in ('resident_data_2BC2','resident_data_2C2B'):
  item=l['data_providers'][ident];names.update(item[k] for k in ('source','proof','fact'))
 names.add('evidence/data-providers/callback-selector-writers.json')
 names.update(l['functions']['resident_F_5428'][k] for k in ('source','proof'))
 if f['route']=='CALLBACK_CYCLE_RECORDS':
  for row in f['definitions'][0]['initializer']:
   if row['words'] is None:continue
   path='evidence/data-providers/resident_data_'+row['words'][-4:]+'.json';target=document(root,path)
   names.update([path,target['producer']['batch'],*producer_paths(root,document(root,target['producer']['batch']))])
 return sorted(names)


def consumed_words(last,global_last):
 require(type(last) is int and type(global_last) is int and 0<=last<=global_last<128,'word cursor must not wrap its masked byte offset')
 # A selector change preserves the cursor: the previous record may have a
 # larger reset value. Include that incoming state, not only a local cycle.
 starts={last if cursor==0 else cursor-1 for cursor in range(global_last+1)}
 reads={cursor+j for cursor in starts for j in range(last+1)}
 count=max(max(starts)+last+1,1)
 require(reads==set(range(count)),'callback cursor/DBRA prefix domain')
 return count


@shared
def plan(root,blob,model,analysis,ledger,promotions):
 from data_providers import document,load_data_providers
 from data_provider_sequences import anchors
 from data_provider_tables import fragments
 from audio_driver_contracts import decode,at
 # Re-prove the accepted selector-domain and initialized cursor objects.
 selector=load_data_providers(root,blob,model,analysis,ledger,promotions,only='resident_data_2BC2')[0]
 extent=selector['typed_evidence'][0]['extent'];count=extent['count']
 require(extent['kind']=='CALLBACK_INDEX_DOMAIN_PREFIX' and count>0,'current complete selector-prefix bound')
 cursor=load_data_providers(root,blob,model,analysis,ledger,promotions,only='resident_data_2C2B')[0]
 require(cursor['data_hex']=='00' and cursor['original']['size']==1,'independently typed initial cursor zero')
 item=ledger['reconstructed_asm']['resident_callback_61A0'];a=anchors(root,dict(anchors={'resident_callback_61A0':{k:item[k] for k in ('source_sha256','proof_sha256')}}),analysis,ledger,promotions)
 fragments(a['resident_callback_61A0'][0],'lea.l _G_h01_2BFE,a2','move.l _G_h01_2C26,d0','lsl.l #$3,d0','adda.l d0,a2','move.b _G_h01_2C2B,d0','subq.l #$1,d0','move.w $4(a2),d0','move.b d0,_G_h01_2C2B','lsl.w #$1,d0','movea.l (a2),a0','and.l #$ff,d0','adda.l d0,a0','move.w $6(a2),d0','lsl.l #$2,d0','move.w $4(a2),d7','move.w (a0)+,(a1)+','addq.l #$2,a1','dbra d7,_recon_h00_61F6')
 code=payload(blob,model,0);by={i['offset']:i for i in decode(code[0x61b0:0x6200],0x61b0)}
 for p,m,o in [(0x61b8,'lea.l','$2bfe.l, a2'),(0x61be,'move.l','$2c26.l, d0'),(0x61c4,'lsl.l','#$3, d0'),(0x61c6,'adda.l','d0, a2'),(0x61d4,'move.w','$4(a2), d0'),(0x61d8,'move.b','d0, $2c2b.l'),(0x61de,'lsl.w','#$1, d0'),(0x61e0,'movea.l','(a2), a0'),(0x61e2,'and.l','#$ff, d0'),(0x61e8,'adda.l','d0, a0'),(0x61ea,'move.w','$6(a2), d0'),(0x61ee,'lsl.l','#$2, d0'),(0x61f2,'move.w','$4(a2), d7'),(0x61f6,'move.w','(a0)+, (a1)+'),(0x61fa,'dbra','d7, $61f6')]:at(by,p,m,o)
 # The original absolute references close the cursor writer set; the A4
 # evidence is checked independently as well, rather than ignored.
 sites=[r['source_offset'] for r in model['relocations'] if r['target_hunk']==1 and r['addend_raw']==0x2c2b]
 require(sites==[0x542e,0x61cc,0x61da],'unmodelled absolute cursor reference')
 setter=ledger['functions']['resident_F_5428'];src=read_source(root, setter['source'], names_root=None);proof=canonical_path(root,setter['proof']).read_bytes()
 require(sha256(src)==setter['source_sha256'] and sha256(proof)==setter['proof_sha256'],'changed canonical cursor reset')
 fragments(src.decode('ascii'),'G_h01_2C2B=0;')
 at({i['offset']:i for i in decode(code[0x5428:0x544c],0x5428)},0x542c,'clr.b','$2c2b.l')
 types=document(root,'evidence/types.json')
 for g in types['globals']:
  if g['data_hunk_offset']==0x2c2b:require(not g['address_taken'] and all(a['function'] in ('resident_callback_61A0','resident_F_5428') for a in g['accesses']),'unmodelled A4 cursor writer/address escape')
 data=payload(blob,model,1);rows=[];colors={};start=0x2bfe
 rels=relocation_profile(model,1,start,8*count);wanted=[]
 global_last=max(int.from_bytes(data[start+8*i+4:start+8*i+6],'big') for i in range(count))
 for i in range(count):
  p=start+8*i;target=int.from_bytes(data[p:p+4],'big');last=int.from_bytes(data[p+4:p+6],'big');dest=int.from_bytes(data[p+6:p+8],'big');n=consumed_words(last,global_last)
  if target:
   require(target%2==0 and target+2*n<=len(data),'partial/unaligned callback WORD target')
   wanted.append(dict(offset=8*i,type='HUNK_RELOC32',width=4,target_hunk=1,addend=target))
   require(target not in colors or colors[target]==n,'conflicting callback source extents')
   colors[target]=n
  rows.append(dict(words=None if target==0 else 'G_h01_%04X'%target,last=last,destination=dest))
 require(rels==wanted,'all callback record pointer relocations must bind the typed targets')
 return dict(count=count,rows=rows,colors={str(k):v for k,v in sorted(colors.items())},selector_extent=extent,cursor_initializer='00',source_word_prefix_rule='max(last, global_max_last-1)+last+1; includes incoming cursor across selector changes')


def typed_evidence(root,f,analysis,ledger,promotions):
 from data_providers import document,verify
 from data_provider_sequences import anchors
 from census import advisory_image
 from game_image import game
 from evidence_snapshot import memoized
 shape(f);anchors(root,f,analysis,ledger,promotions)
 with advisory_image():blob,model,_=game()
 p=plan(root,blob,model,analysis,ledger,promotions);d=f['definitions'][0];o=f['original']
 if f['route']=='CALLBACK_CYCLE_WORDS':
  require(str(o['start']) in p['colors'] and d['dimensions']==[p['colors'][str(o['start'])]],'source WORDs exceed the independently consumed prefix')
  details=dict(prefix_words=d['dimensions'][0],rule=p['source_word_prefix_rule'],capacity_claim=False)
 else:
  require(d['dimensions']==[p['count']] and d['initializer']==p['rows'],'complete callback prefix fields/targets differ from their typed original view')
  proofs=[]
  for target in p['colors']:
   name='evidence/data-providers/resident_data_%04X.json'%int(target);tf=document(root,name)
   require(tf['route']=='CALLBACK_CYCLE_WORDS' and tf['original']['start']==int(target),'missing independently typed named callback target')
   identity=sha256(json_bytes(tf))+';'+sha256(blob)+';'+sha256(json_bytes(ledger))
   report=memoized(root,'callback-word-target',identity,lambda:verify(root,blob,model,analysis,ledger,promotions,tf,source(tf),None),strict=True)
   require(report['state']=='DATA_LAYOUT_MATCH','typed callback target did not verify')
   proofs.append(dict(fact=name,fact_sha256=sha256(json_bytes(tf)),object_sha256=report['object_sha256']))
  details=dict(prefix_count=p['count'],selector_extent=p['selector_extent'],target_proofs=proofs,record_stride=8,field_widths=[4,2,2],capacity_claim=False)
 return [dict(kind=f['route'],anchors=f['anchors'],details=details,historical_extent='UNKNOWN; complete reconstructed access prefix only')]


def binder_names(facts):return sorted(set(cells.CONTROL_NAMES)|{'_'+r['words'] for f in facts for r in f['definitions'][0]['initializer'] if r['words'] is not None})


def object_records(raw,symbol,rows):
 """Measured mixed external DATA fixups and literal WORD fields; no addends."""
 size=8*len(rows);targets=[('_'+r['words']) for r in rows if r['words'] is not None];externs=list(dict.fromkeys(targets))
 require(1<=len(externs)<=14 and len(raw)>=36 and raw[:10]==b'AJ'+bytes(8),'bounded callback DATA AJ header/extern inventory')
 u16=lambda p:int.from_bytes(raw[p:p+2],'big');u32=lambda p:int.from_bytes(raw[p:p+4],'big')
 require((u32(10),u32(14),u32(18))==(0,size,0),'complete callback DATA-only object')
 syms=u16(28)*4;end=u16(30)*4
 require(u32(24)*4==36 and u16(22)==1+len(externs) and syms<=end==u16(32)*4==len(raw) and raw[34:36]==b'\xc0\0','whole callback AJ boundaries')
 p=syms
 for i,n in enumerate([symbol]+externs):
  require(raw[p:p+2]==(b'\x03\x0a' if i==0 else b'\x07\x2a') and u16(p+2)==0,'callback DATA definition/external class/value');p+=4
  if i:require(u16(p)==targets.count(n),'external callback DATA reference count');p+=2
  z=raw.find(b'\0',p,end);require(z>p and raw[p:z].decode('ascii')==n,'complete callback symbol inventory/order');p=z+1
 require(end-p<=3 and raw[p:]==bytes(end-p),'callback symbol trailer')
 p=36;require(raw[p]==0xf5,'callback DATA stream');p+=1;out=bytearray();fixups=[]
 while len(out)<size:
  token=raw[p];p+=1
  if 0x10<=token<=0x1f:
   n=token-15;require(p+n<=syms and len(out)+n<=size,'callback literal overrun');out+=raw[p:p+n];p+=n
  else:
   require(token==0xfd and p+2<=syms and raw[p+1]==0,'only measured named external DATA fixups')
   index=raw[p]-0x70;require(1<=index<=len(externs),'callback external index');p+=2
   fixups.append(dict(offset=len(out),width=4,type='HUNK_RELOC32',symbol=externs[index-1],addend=0));out+=bytes(4)
 require(raw[p:p+2]==b'\xf4\xf5','callback DATA end transition');p+=2
 require(syms==((p+4)//4)*4 and raw[p:syms]==bytes(syms-p),'complete callback stream/trailer')
 expected=b''.join(bytes(4)+r['last'].to_bytes(2,'big')+r['destination'].to_bytes(2,'big') for r in rows)
 wanted=[dict(offset=8*i,width=4,type='HUNK_RELOC32',symbol='_'+r['words'],addend=0) for i,r in enumerate(rows) if r['words'] is not None]
 require(bytes(out)==expected and fixups==wanted,'every callback literal field and named relocation must match')
 return dict(bytes=bytes(out),definitions=[dict(name=symbol,offset=0)],fixups=fixups,sections=dict(CODE=0,DATA=size,BSS=0,COMMON=0))


def linked_records(obj,linked,map_text,symbol,rows,names):
 parsed=object_records(obj,symbol,rows);lm=parse(linked);sm=symbols(map_text);size=len(parsed['bytes']);binder=b''.join((i+1).to_bytes(2,'big') for i in range(len(names)));rounded=(size+len(binder)+3)&~3
 require([(h['number'],h['type'],h['allocated_size'],h['initialized_size']) for h in lm['hunks']]==[(0,'CODE',4,4),(1,'DATA',rounded,rounded),(2,'BSS',4,0)],'complete callback link topology')
 require(payload(linked,lm,0)==b'\x4e\x75\0\0','independent callback link harness')
 expected={(0,'__H0_org'):0,(0,'.begin'):0,(0,'__H0_end'):4,(1,'__H1_org'):0,(1,symbol):0,(1,'__H1_end'):rounded,(2,'__H2_org'):rounded,(2,'__H2_end'):rounded};expected.update({(1,n):size+2*i for i,n in enumerate(names)})
 require(sm==expected,'complete callback/binder symbol inventory')
 want=bytearray(parsed['bytes']);rels=[]
 for f in parsed['fixups']:
  value=sm[1,f['symbol']];want[f['offset']:f['offset']+4]=value.to_bytes(4,'big');rels.append(dict(offset=f['offset'],type='HUNK_RELOC32',width=4,target_hunk=1,addend=value))
 require(payload(linked,lm,1)==bytes(want)+binder+bytes(rounded-size-len(binder)),'whole callback/binder linked DATA and alignment')
 require(relocation_profile(lm,1,0,size)==rels and len(lm['relocations'])==len(rels),'entire callback link relocation inventory')
 return parsed,lm,bytes(want)


def compare_data(original,model,f,obj,linked,map_text):
 from data_provider_tables import numeric_compare
 from data_providers import document
 from analysis_support import ROOT
 if f['route']=='CALLBACK_CYCLE_WORDS':return numeric_compare(original,model,f,obj,linked,map_text,shape(f),semantic(f),source(f))
 shape(f);recipe=document(ROOT,f['producer']['batch']);facts=[document(ROOT,m['fact']) for m in recipe['members']];d=f['definitions'][0];rows=d['initializer'];parsed,lm,actual=linked_records(obj,linked,map_text,'_'+d['symbol'],rows,binder_names(facts))
 expected=payload(original,model,1)[f['original']['start']:f['original']['start']+f['original']['size']];mapped=bytearray(parsed['bytes']);rels=[]
 for i,r in enumerate(rows):
  if r['words'] is None:continue
  target=int(r['words'][-4:],16);mapped[8*i:8*i+4]=target.to_bytes(4,'big');rels.append(dict(offset=8*i,type='HUNK_RELOC32',width=4,target_hunk=1,addend=target))
 require(bytes(mapped)==expected and relocation_profile(model,1,f['original']['start'],len(mapped))==rels,'all original callback fields and independently named targets')
 return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=f['id'],original=dict(f['original'],sha256=sha256(expected)),sections=parsed['sections'],symbols=parsed['definitions'],relocation_bindings=parsed['fixups'],original_relocations=rels,candidate_relocations=relocation_profile(lm,1,0,len(mapped)),actual_sha256=sha256(actual),source_sha256=sha256(source(f)),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=expected.hex(),zero_fill_credit=0,root_layout_proof=False)


def control_report(files,names):
 from data_providers import data_object
 require(files['cycleprobe.c']==CONTROL_SOURCE and files['binddata.c']==cells.binder_source(names),'independent callback record/binder controls')
 binder=data_object(files['binddata.o']);require(binder['bytes']==b''.join((i+1).to_bytes(2,'big') for i in range(len(names))) and binder['definitions']==[dict(name=n,offset=2*i) for i,n in enumerate(names)] and not binder['fixups'] and binder['sections']==dict(CODE=0,DATA=2*len(names),BSS=0,COMMON=0),'whole synthetic callback DATA binder')
 rows=[dict(words='DP_a',last=1,destination=2),dict(words=None,last=0,destination=0),dict(words='DP_b',last=3,destination=4)]
 parsed,lm,actual=linked_records(files['cycleprobe.o'],files['cycleprobe.exe'],files['cycleprobe.sym'].decode('ascii'),'_DP_cycles',rows,names)
 return dict(DATA=24,records=3,relocations=2,null_pointers=1,field_widths=[4,2,2],object_sha256=sha256(files['cycleprobe.o']),game_credit=0)
