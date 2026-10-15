"""Versioned stateful stream grammar; batch-0003 remains immutable.

A7 has lexical width one: active state retries at P, inactive state continues
at P+1. Sample commands use the decoded A7 lookahead predicate, never a
length chosen because surrounding bytes happen to parse.
"""
import json,re
from collections import defaultdict
from common import require,sha256,json_bytes,FormatError
from audio_sequence_data import payload,field
from audio_score_commands import integer
from audio_score_grammar import instructions
import audio_region_catalogue as previous
INTERVAL=previous.INTERVAL
SPECS=dict(previous.SPECS,WAIT_SAMPLE=(0xa7,()),RESTART_ENVELOPE=(0xa8,('ticks',)))
BY_OPCODE={op:name for name,(op,_) in SPECS.items()}
SAMPLES={'SAMPLE_TIMED':0x9a,'SAMPLE_WAIT':0x9a,'SAMPLE93_TIMED':0x93,'SAMPLE93_WAIT':0x93}
def doc(root,name):return json.loads((root/name).read_bytes())
def symbol(k,p):return '_audio4_%s_%04X'%(k,p)
def contract(blob,model):
 g=previous.contract(blob,model);code=payload(blob,model,0);ins=instructions(code,0x5bc6,0x5c90)
 expected={0x5bc6:('move.w','d7, d1'),0x5bc8:('lsl.w','#$3, d1'),0x5bca:('lea.l','$2b4e.l, a2'),0x5bd0:('tst.w','(a2, d1.w)'),0x5bd4:('beq.b','$5bf0'),0x5bd6:('clr.l','$4(a0)'),0x5bda:('clr.b','$1e(a0)'),0x5bde:('move.b','#$0, $3b(a0)'),0x5be4:('rts',''),0x5be6:('move.w','d7, d1'),0x5bea:('lea.l','$2b4e.l, a2'),0x5bf0:('movem.l','a3-a4, -(a7)'),0x5c1a:('move.w','(a4)+, (a2, d1.w)'),0x5c2e:('move.l','$3c(a0), d0'),0x5c32:('move.l','d0, $1a(a0)'),0x5c36:('move.b','#$1, $1e(a0)'),0x5c3c:('clr.b','$1f(a0)'),0x5c40:('move.l','a1, d0'),0x5c42:('btst.b','#$0, d0'),0x5c46:('beq.b','$5c4a'),0x5c48:('addq.l','#$1, a1'),0x5c4a:('move.w','(a1)+, d0'),0x5c54:('movem.l','(a7)+, a3-a4'),0x5c58:('move.b','(a1)+, d0'),0x5c5a:('cmp.b','#$a7, d0'),0x5c5e:('beq.b','$5c7c'),0x5c60:('move.b','d0, $8(a0)'),0x5c64:('move.l','a1, $4(a0)'),0x5c68:('rts',''),0x5c6a:('move.w','d7, d3'),0x5c6c:('lsl.w','#$3, d3'),0x5c6e:('lea.l','$2b4e.l, a2'),0x5c74:('adda.w','d3, a2'),0x5c76:('tst.w','(a2)'),0x5c78:('beq.b','$5c8a'),0x5c7a:('subq.l','#$1, a1'),0x5c7c:('subq.l','#$1, a1'),0x5c7e:('move.b','#$1, $8(a0)'),0x5c84:('move.l','a1, $4(a0)'),0x5c88:('rts',''),0x5c8a:('subq.l','#$1, a1'),0x5c8c:('bra.w','$5a76')}
 require(all(ins[p][:2]==v for p,v in expected.items()),'stateful lookahead/rewind instruction changed')
 require(all(next(x for x in g['score']['opcodes'] if x['opcode']==op)['handler']==target for op,target in [(0x93,0x5be6),(0x9a,0x5be6),(0x9b,0x5bc6),(0xa7,0x5c6a),(0xa8,0x5dfe)]),'stateful handler binding changed')
 extra=instructions(code,0x5dfe,0x5e64)
 require([v[:2] for v in list(extra.values())[:6]]==[('move.b','d0, $8(a0)'),('move.l','$3c(a0), d0'),('move.l','d0, $1a(a0)'),('move.b','#$1, $1e(a0)'),('clr.b','$1f(a0)'),('move.l','a1, $4(a0)')] and extra[0x5e62][:2]==('rts',''),'A8 envelope-restart meaning changed')
 require({p for p,(m,o,n) in ins.items() if 'a1' in o}=={0x5c40,0x5c48,0x5c4a,0x5c58,0x5c64,0x5c7a,0x5c7c,0x5c84,0x5c8a},'unmodelled A1 use in stateful handlers')
 # Enumerate all independently decoded state cases. The stream is never
 # parsed at its prefetched lookahead byte while the active branch retries.
 cases=[]
 for parity in (0,1):
  a1=parity+g['score']['dispatch_prefetch'];word=a1+(a1%2)*int(ins[0x5c48][1].split(',')[0].replace('#$',''),16);after=word+{'move.w':2}[ins[0x5c4a][0]]
  cases.extend([dict(opcode=0x9a,parity=parity,lookahead='NOT_A7',word_field=word-parity,length=after+1-parity,next=after+1-parity),dict(opcode=0x9a,parity=parity,lookahead='A7',word_field=word-parity,length=after-parity,next=after-parity),dict(opcode=0xa7,parity=parity,sample_state='ZERO',length=1,saved_cursor=None,next=1),dict(opcode=0xa7,parity=parity,sample_state='NONZERO',length=1,saved_cursor=0,next='RETRY_AFTER_ONE_TICK')])
 g['stateful']=dict(cases=cases+[{**c,'opcode':0x93} for c in cases if c['opcode']==0x9a],descriptor_counter_source=dict(hunk=1,base=0x2b4e,stride=8,width=2),sample_word_alignment='(P+3)&~1',wait_lexical_width=1,wait_fallthrough_proves_counter_zero=True,conditional_9b=dict(handler=0x5bc6,inactive='SAMPLE_FORM',active='STOP_WITHOUT_OPERANDS',admission='REJECT_WITHOUT_INDEPENDENT_ZERO_STATE'),instructions_sha256=sha256(code[0x5bc6:0x5c90]))
 return g

def form(g,op,p):
 if op==0xa7:return dict(length=1,pointer_field=None,flows=['NEXT','YIELD_RETRY'])
 if op==0xa8:
  row=next(x for x in g['score']['opcodes'] if x['opcode']==op);sh=row['forms'][p%2]
  require(sh['length']==2 and sh['flows']==['NEXT'],'A8 consumption changed');return sh
 require(op not in (0x93,0x9a,0x9b),'sample form requires decoded lookahead/state')
 return previous.form(g,op,p)
def stream_form(g,code,p):
 require(type(p) is int and 0<=p<len(code),'partial command position');op=code[p]
 if op in (0x93,0x9a):
  word=(p+3)&~1;look=word+2;require(look<min(INTERVAL[1],len(code)),'partial sample lookahead')
  wait=code[look]==0xa7
  return dict(length=look-p+(0 if wait else 1),pointer_field=None,flows=['NEXT'],word_field=word-p,command=('SAMPLE93_' if op==0x93 else 'SAMPLE_')+('WAIT' if wait else 'TIMED'))
 if op==0x9b:raise FormatError('9B requires independently proved zero sample counter at entry')
 return form(g,op,p)
def read_values(code,p,name,sh):
 if name in SAMPLES:
  q=p+sh['word_field'];require(q==p+2 or code[p+2]==0,'untyped sample alignment byte')
  return [code[p+1],int.from_bytes(code[q:q+2],'big')]+([] if name.endswith('WAIT') else [code[q+2]])
 require((2 if name=='NOTE' else 1+len(SPECS[name][1]))==sh['length'],'wrong grammar length')
 return list(code[p:p+sh['length']]) if name=='NOTE' else list(code[p+1:p+sh['length']])
def command_length(c,g):
 if c['type'] in SAMPLES:return ((c['offset']+3)&~1)+2-c['offset']+(0 if c['type'].endswith('WAIT') else 1)
 return form(g,c['values'][0] if c['type']=='NOTE' else SPECS[c['type']][0],c['offset'])['length']

def envelopes(code,rel,index):
 views=[];roles=defaultdict(set);bindings=[]
 for release in (False,True):
  site=0x5e6c+4*(index+release);r=rel.get(site)
  require(r is not None and r['type']=='HUNK_RELOC32' and r['width']==4 and r['target_hunk']==0,'unproved envelope pointer pair')
  p=r['addend_raw'];entry=p;require(0x5fac<=p<0x615e,'envelope pointer to unproved record')
  bindings.append(dict(field(r),symbol=symbol('e',p)))
  if not release:roles[p].add('INITIAL');p+=1
  steps=[]
  while True:
   require(p+2<=0x615e and p+2-entry<=256,'envelope lacks terminal before cursor/boundary')
   a,b=code[p:p+2]
   if a==0:
    roles[p].add('ZERO');roles[p+1].add('ZERO' if b==0 else 'DELAY');steps.append(dict(offset=p,command='END' if b==0 else 'WAIT'))
   else:roles[p].add('DELTA');roles[p+1].add('TARGET');steps.append(dict(offset=p,command='RAMP_DOWN_END' if a>=128 and b==0 else 'RAMP'))
   p+=2
   if a==b==0 or a>=128 and b==0:break
  views.append(dict(index=index,release=release,entry=entry,end=p,steps=steps))
 return views,roles,bindings
def length(c,g):
 if c['type'] in ('SELECTOR','ENVELOPE_PTR'):return 4
 if c['type']=='ENVELOPE_FIELD':return 1
 if c['type']=='HEADER':return 2
 return command_length(c,g)
def discover(root,blob,model,g):
 code=payload(blob,model,0);rel={r['source_offset']:r for r in model['relocations'] if r['source_hunk']==0};old=doc(root,'evidence/code-data-providers/score.json')
 oldheaders={c['offset'] for c in old['commands'] if c['command']=='HEADER'};triggers=[c for c in old['commands'] if c['command']=='TRIGGER'];highest=max(c['operands']['identifier'] for c in triggers)
 # The accepted root-reached command TRIGGER 175 supplies independent positive
 # indexed-access extent evidence. Each prefix slot additionally needs RELOC32.
 require(highest==175,'independently accessed selector prefix changed')
 rows={};bindings={};roots=[];blocked=[];env_indexes={c['operands']['identifier'] for c in old['commands'] if c['command']=='ENVELOPE'}
 for index in range(highest+1):
  site=0x6200+4*index;r=rel.get(site);local={};lb={};ei=set();entry=None
  try:
   require(r is not None and r['type']=='HUNK_RELOC32' and r['width']==4,'selector field missing relocation')
   entry=r['addend_raw'];require(r['target_hunk']==0,'selector target is unproved H1 data')
   if entry in oldheaders:target='_audio_h_%04X'%entry
   else:
    require(0x64c0<=entry<INTERVAL[1] and code[entry]<4,'unproved selector header')
    local[entry]=dict(offset=entry,type='HEADER',values=[code[entry],code[entry+1]]);todo=[entry+2];seen=set()
    while todo:
     p=todo.pop()
     if p in seen:continue
     seen.add(p);require(0x64c0<=p<INTERVAL[1],'pointer to unproved stream')
     op=code[p];sh=stream_form(g,code,p);z=p+sh['length'];require(z<=INTERVAL[1],'partial stream');name=sh.get('command','NOTE' if op<128 else BY_OPCODE.get(op));targets=[]
     if sh['pointer_field'] is not None:
      q=p+sh['pointer_field'];rr=rel.get(q);require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4 and rr['target_hunk']==0,'unnamed/masked command relocation')
      require(q==p+1 or code[p+1]==0,'untyped command alignment field');t=rr['addend_raw'];values=[symbol('c',t)];targets.append(t);lb[q]=dict(field(rr),symbol=values[0])
     else:
      values=read_values(code,p,name,sh)
     local[p]=dict(offset=p,type=name,values=values)
     if name=='ENVELOPE':envelopes(code,rel,values[0]);ei.add(values[0])
     if 'NEXT' in sh['flows'] or 'CALL' in sh['flows']:targets.append(z)
     todo.extend(targets)
    for p in seen:
     path=set();q=p
     while True:
      require(q in seen and q not in path,'stream has no grammar terminal');path.add(q);sh=stream_form(g,code,q)
      if set(sh['flows']).intersection(('STOP','RETURN','POINTER')):break
      q+=sh['length']
    target=symbol('h',entry)
   for p,c in local.items():require(p not in rows or rows[p]==c,'inconsistent command overlap')
   rows.update(local);bindings.update(lb);env_indexes.update(ei);bindings[site]=dict(field(r),symbol=target);rows[site]=dict(offset=site,type='SELECTOR',values=[target]);roots.append(dict(index=index,site=site,entry=entry,canonical=entry in oldheaders))
  except (FormatError,KeyError) as exc:blocked.append(dict(index=index,site=site,target_hunk=None if r is None else r['target_hunk'],entry=entry,reason=str(exc)))
 envroles=defaultdict(set);views=[]
 for i in sorted(env_indexes):
  v,roles,bs=envelopes(code,rel,i);views.extend(v)
  for p,rs in roles.items():envroles[p].update(rs)
  for b in bs:bindings[b['source_offset']]=b;rows[b['source_offset']]=dict(offset=b['source_offset'],type='ENVELOPE_PTR',values=[b['symbol']])
 for p,rs in envroles.items():rows[p]=dict(offset=p,type='ENVELOPE_FIELD',roles=sorted(rs),values=[code[p]])
 rows=sorted(rows.values(),key=lambda c:c['offset']);covered=set()
 for c in rows:
  points=set(range(c['offset'],c['offset']+length(c,g)));require(not points.intersection(covered),'overlapping typed field/command');covered.update(points)
 touched=[field(r) for r in model['relocations'] if r['source_hunk']==0 and any(p in covered for p in range(r['source_offset'],r['source_offset']+r['width']))]
 require(sorted(touched,key=lambda x:x['source_offset'])==[{k:v for k,v in b.items() if k!='symbol'} for _,b in sorted(bindings.items())],'unnamed/straddling relocation')
 gaps=[]
 for p in range(*INTERVAL):
  if p in covered:continue
  reason=('ENVELOPE_SLOT_NOT_REACHED_BY_PROVED_OPERAND' if p<0x5fac else 'ENVELOPE_BYTE_NOT_REACHED_BY_PROVED_PAIR' if p<0x615e else 'EXECUTABLE_CODE_SEPARATE_INSTRUCTION_ROUTE' if p<0x6200 else next(x['reason'] for x in blocked if x['index']==(p-0x6200)//4) if p<0x64c0 else 'NO_COMPLETE_SUPPORTED_ROOT_CLOSURE')
  if gaps and gaps[-1]['end']==p and gaps[-1]['reason']==reason:gaps[-1]['end']+=1
  else:gaps.append(dict(start=p,end=p+1,reason=reason))
 return dict(rows=rows,bindings=[v for _,v in sorted(bindings.items())],roots=roots,blocked_selectors=blocked,envelope_views=views,selector_extent_basis=[c for c in triggers if c['operands']['identifier']==highest],typed_bytes=len(covered),unproved_intervals=gaps)

def check(c):
 import re
 require(type(c['offset']) is int and isinstance(c['values'],list),'typed field shape');name=c['type'];v=c['values']
 if name in SAMPLES:
  require(set(c)=={'offset','type','values'} and len(v)==(2 if name.endswith('WAIT') else 3),'sample typed fields')
  integer(v[0]);integer(v[1],65535)
  if not name.endswith('WAIT'):integer(v[2]);require(v[2]!=0xa7,'A7 lookahead is a command, not a duration')
  return
 if name in ('SELECTOR','ENVELOPE_PTR') or name in SPECS and SPECS[name][1]==('target',):require(len(v)==1 and type(v[0]) is str and re.fullmatch(r'_(audio4_[ceh]_[0-9A-F]{4}|audio_h_[0-9A-F]{4})',v[0]),'unnamed pointer operand')
 else:
  n=1 if name=='ENVELOPE_FIELD' else 2 if name in ('HEADER','NOTE') else len(SPECS[name][1]) if name in SPECS else -1
  require(len(v)==n,'unknown command or wrong typed field count')
  for x in v:integer(x)
  if name=='HEADER':integer(v[0],3)
  if name=='NOTE':integer(v[0],127)
  if name=='ENVELOPE_FIELD':
   require(set(c)=={'offset','type','values','roles'} and c['roles'] and set(c['roles'])<={'INITIAL','DELTA','TARGET','DELAY','ZERO'},'untyped envelope carrier')
   if 'ZERO' in c['roles']:require(v==[0],'envelope sentinel range')
   if set(c['roles']).intersection(('DELTA','DELAY')):require(v[0]!=0,'envelope nonzero typed range')
 if name!='ENVELOPE_FIELD':require(set(c)=={'offset','type','values'},'raw carrier/extra field')
def row_symbol(c):return '_G_h00_6200' if c['type']=='SELECTOR' and c['offset']==0x6200 else symbol('h' if c['type']=='HEADER' else 'e' if c['type']=='ENVELOPE_FIELD' else 'c',c['offset'])

def plan(layout,g):
 fragments=[]
 for c in layout['rows']:
  if fragments and fragments[-1][-1]['offset']+length(fragments[-1][-1],g)==c['offset']:fragments[-1].append(c)
  else:fragments.append([c])
 # Fragment scheduling changes no field or command; parity is checked for each
 # command. No fillers bridge omitted or blocked fields.
 objects=[];remaining=fragments[:]
 while remaining:
  rows=[];cursor=0
  while True:
   found=next((i for i,fs in enumerate(remaining) if fs[0]['offset']%2==cursor%2),None)
   if found is None:break
   fs=remaining.pop(found);rows+=fs;cursor+=sum(length(c,g) for c in fs)
  require(rows,'odd-root fragment needs typed parity prefix; fillers forbidden')
  prefix='r4%02d'%len(objects);parts=[];q=0
  for c in rows:
   n=length(c,g)
   if parts and parts[-1]['original_end']==c['offset']:parts[-1]['original_end']+=n;parts[-1]['candidate_end']+=n
   else:parts.append(dict(original_start=c['offset'],original_end=c['offset']+n,candidate_start=q,candidate_end=q+n))
   q+=n
  objects.append(dict(id='resident_'+prefix,prefix=prefix,typed_bytes=cursor,CODE=cursor+cursor%2,parts=parts,rows=rows,source='src/recovered/code-data/'+prefix+'.asm',candidate='evidence/rules/audio-stateful-0004/'+prefix+'.asm'))
 return objects

def encode(member,g):
 out=bytearray();definitions=[];fixups=[]
 for c in member['rows']:
  check(c);p=len(out);name=c['type'];v=c['values'];definitions.append(dict(name=row_symbol(c),offset=p))
  if name in SAMPLES:
   out.extend((SAMPLES[name],v[0]))
   if len(out)%2:out.append(0)
   out+=v[1].to_bytes(2,'big')
   if not name.endswith('WAIT'):out.append(v[2])
  elif name in ('SELECTOR','ENVELOPE_PTR'):fixups.append(dict(offset=p,symbol=v[0],type='HUNK_RELOC32',width=4,addend=0));out+=bytes(4)
  elif name in ('HEADER','NOTE','ENVELOPE_FIELD'):out+=bytes(v)
  else:
   op,fields=SPECS[name];out.append(op)
   if fields==('target',):
    if len(out)%2:out.append(0)
    fixups.append(dict(offset=len(out),symbol=v[0],type='HUNK_RELOC32',width=4,addend=0));out+=bytes(4)
   else:out+=bytes(v)
  require(len(out)-p==length(c,g) and p%2==c['offset']%2,'changed pointer grammar parity/length')
 return dict(code=bytes(out),definitions=definitions,fixups=fixups)

def source(member,g,targets):
 targets=targets|{'_G_h00_6200'};sem=encode(member,g);used={f['symbol'] for f in sem['fixups']};local={d['name'] for d in sem['definitions']};names=['_'+member['prefix']+'_begin','_'+member['prefix']+'_end']+sorted(local&targets)+sorted(used-local)
 lines=['; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.']
 macros={'HEADER':['dc.b \\1,\\2'],'NOTE':['dc.b \\1,\\2'],'SELECTOR':['dc.l \\1'],'ENVELOPE_PTR':['dc.l \\1'],'ENV_INITIAL':['dc.b \\1'],'ENV_DELTA':['dc.b \\1'],'ENV_TARGET':['dc.b \\1'],'ENV_DELAY':['dc.b \\1'],'ENV_ZERO':['dc.b 0']}
 for name,(op,fields) in SPECS.items():macros[name]=['dc.b $%02x'%op,'ds 0','dc.l \\1'] if fields==('target',) else ['dc.b '+','.join(['$%02x'%op]+['\\%d'%(i+1) for i in range(len(fields))])]
 for name,op in SAMPLES.items():macros[name]=['dc.b $%02x,\\1'%op,'ds 0','dc.w \\2']+([] if name.endswith('WAIT') else ['dc.b \\3'])
 for name,body in macros.items():lines+=['T4_'+name+' macro']+['\t'+s for s in body]+['\tendm']
 lines+=['\tcseg']+['\tpublic '+n for n in names]+[names[0]+':']
 for c in member['rows']:
  sym=row_symbol(c)
  if sym in targets:lines.append(sym+':')
  name=c['type'];args=c['values']
  if name=='ENVELOPE_FIELD':
   role=next(x for x in ('ZERO','DELTA','DELAY','INITIAL','TARGET') if x in c['roles']);name='ENV_'+role;args=[] if role=='ZERO' else [args[0]-256 if role=='DELTA' and args[0]>=128 else args[0]]
  lines.append('\tT4_'+name+(' '+','.join(map(str,args)) if args else ''))
 return ('\n'.join(lines+[names[1]+':','\tend',''])).encode('ascii')
