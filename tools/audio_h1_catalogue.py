"""Rooted H1 score closure with a complete selector prefix and typed envelopes.

H0 score/callback proofs remain immutable. Header roots are supplied by decoded
selector fields; every reached command must terminate under the existing grammar.
"""
from names import read_source
from collections import defaultdict
from common import require,sha256,json_bytes
from audio_sequence_data import payload,field
import audio_stateful_catalogue as old
from audio_score_commands import integer

ROOT_INDEX=6
STOP_INDEX=0x21
SPECS=old.SPECS

def doc(root,name):
 from code_data_providers import document
 return document(root,name)

def symbol(h,kind,p):return '_audio5_%s_h%02d_%04X'%(kind,h,p)

def row_symbol(c):
 h,p,k=c['hunk'],c['offset'],c['type']
 return '_G_h00_6200_complete' if k=='SELECTOR' and p==0x6200 else symbol(h,'h' if k=='HEADER' else 'e' if k=='ENVELOPE_FIELD' else 'c',p)

def check(c):
 require(type(c['hunk']) is int and c['hunk'] in (0,1) and type(c['offset']) is int and c['offset']>=0,'typed hunk/position')
 d={k:v for k,v in c.items() if k!='hunk'}
 if c['type']=='ENVELOPE_FIELD':old.check(d);return
 require(set(d)=={'offset','type','values'} and isinstance(d['values'],list),'closed typed command fields')
 if c['type'] in ('SELECTOR','ENVELOPE_PTR') or c['type'] in SPECS and SPECS[c['type']][1]==('target',):
  require(len(c['values'])==1 and isinstance(c['values'][0],str),'one symbolic target')
  import re
  require(re.fullmatch(r'_(?:audio5_[ceh]_h0[01]_[0-9A-F]{4}|audio4_[ch]_[0-9A-F]{4}|audio_h_[0-9A-F]{4})',c['values'][0]),'independently named pointer target')
 else:old.check(d)

def length(c,g):return old.length({k:v for k,v in c.items() if k!='hunk'},g)

def score_closure(blob,model,g,index):
 """Follow triggers, jumps and calls from one independent selector operand.

 No next-symbol bounds, physical container limit is only a rejection fence.
 Each linear path must end at the first END/RETURN/JUMP, as in the H0 route.
 """
 raw={h:payload(blob,model,h) for h in (0,1)}
 rel={(r['source_hunk'],r['source_offset']):r for r in model['relocations']}
 roots=[];rows={};bindings={};todo=[index];seen_roots=set();streams=[]
 while todo:
  n=todo.pop()
  if n in seen_roots:continue
  seen_roots.add(n);site=0x6200+4*n;r=rel.get((0,site))
  require(r is not None and r['type']=='HUNK_RELOC32' and r['width']==4 and r['target_hunk'] in raw,'unproved sound selector')
  h,p=r['target_hunk'],r['addend_raw'];code=raw[h];entry=p
  require(0<=p<p+2<len(code) and code[p]<4,'unproved score header')
  header=dict(hunk=h,offset=p,type='HEADER',values=list(code[p:p+2]));check(header)
  require((h,p) not in rows or rows[h,p]==header,'overlapping headers');rows[h,p]=header
  roots.append(dict(index=n,selector=field(r),hunk=h,entry=p,channel=code[p],priority=code[p+1]))
  entries={p+2};pending=[p+2];seen=set()
  while pending:
   q=pending.pop()
   if q in seen:continue
   seen.add(q);require(0<=q<len(code),'score edge outside hunk')
   op=code[q];sh=old.stream_form(g,code,q);z=q+sh['length'];require(z<=len(code),'partial score command')
   name=sh.get('command','NOTE' if op<128 else old.BY_OPCODE.get(op));targets=[]
   if sh['pointer_field'] is not None:
    ptr=q+sh['pointer_field'];rr=rel.get((h,ptr))
    require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4 and rr['target_hunk']==h,'unproved/cross-hunk pattern pointer')
    require(int.from_bytes(code[ptr:ptr+4],'big')==rr['addend_raw'] and (ptr==q+1 or code[q+1]==0),'pointer payload/alignment')
    target=rr['addend_raw'];values=[symbol(h,'c',target)];targets.append(target);entries.add(target);bindings[h,ptr]=dict(field(rr),symbol=values[0])
   else:values=old.read_values(code,q,name,sh)
   c=dict(hunk=h,offset=q,type=name,values=values);check(c)
   require((h,q) not in rows or rows[h,q]==c,'inconsistent score command overlap');rows[h,q]=c
   if name=='TRIGGER':todo.append(values[0])
   if 'NEXT' in sh['flows'] or 'CALL' in sh['flows']:targets.append(z)
   pending.extend(targets)
  for q in sorted(entries):
   path=[];p=q
   while True:
    require(p in seen and p not in path,'score lacks a grammar-terminal extent');path.append(p);c=rows[h,p];sh=old.stream_form(g,code,p)
    if c['type'] in ('END','RETURN','JUMP'):break
    p+=sh['length']
   streams.append(dict(hunk=h,entry=q,terminal=p,end=p+sh['length'],commands=len(path)))
 return dict(roots=sorted(roots,key=lambda x:x['index']),rows=sorted(rows.values(),key=lambda c:(c['hunk'],c['offset'])),bindings=sorted(bindings.values(),key=lambda b:(b['source_hunk'],b['source_offset'])),streams=streams)

def discover(root,blob,model,g):
 h1=score_closure(blob,model,g,ROOT_INDEX);stops=score_closure(blob,model,g,STOP_INDEX)
 require(all(r['hunk']==1 for r in h1['roots']) and all(r['hunk']==0 for r in stops['roots']),'rooted hunk domain changed')
 # Literal call witnesses establish both command operands independently.
 from storage_plan import clean
 ledger=doc(root,'recovery/ledger.json');witnesses={}
 for fid,index in [('ov13_F_02BE',STOP_INDEX),('ov13_F_02BE',ROOT_INDEX)]:
  item=ledger['functions'][fid];src=read_source(root, root / item['source'], names_root=None);proof=(root/item['proof']).read_bytes()
  require(sha256(src)==item['source_sha256'] and sha256(proof)==item['proof_sha256'],'changed canonical sound caller')
  text=clean(src.decode('ascii'));import re
  require(any(int(x,0)==index for x in re.findall(r'F_h00_57D2\(\s*(0x[0-9a-fA-F]+|[0-9]+)\s*\)',text)),'literal sound-command witness absent')
  witnesses[fid]={k:item[k] for k in ('source_sha256','proof_sha256')}
 oldscore=doc(root,'evidence/code-data-providers/score.json');highest=max(c['operands']['identifier'] for c in oldscore['commands'] if c['command']=='TRIGGER')
 prior=doc(root,'evidence/code-data-providers/stateful-0004.json');old_rows=[c for o in prior['objects'] for c in o['rows']];selectors={c['offset']:c for c in old_rows if c['type']=='SELECTOR'}
 h1_roots={r['index']:r for r in h1['roots']};rows={(c['hunk'],c['offset']):c for c in h1['rows']+stops['rows']};bindings={(b['source_hunk'],b['source_offset']):b for b in h1['bindings']+stops['bindings']};rel={(r['source_hunk'],r['source_offset']):r for r in model['relocations']};selector_roots=[]
 for index in range(highest+1):
  site=0x6200+4*index;rr=rel.get((0,site));require(rr is not None and rr['type']=='HUNK_RELOC32' and rr['width']==4,'complete selector prefix relocation')
  if index in h1_roots:
   x=h1_roots[index];require((rr['target_hunk'],rr['addend_raw'])==(x['hunk'],x['entry']),'H1 selector/header binding');target=symbol(1,'h',x['entry'])
  else:
   require(rr['target_hunk']==0 and site in selectors,'unreached/unsupported selector prefix cell');target=selectors[site]['values'][0]
  rows[0,site]=dict(hunk=0,offset=site,type='SELECTOR',values=[target]);bindings[0,site]=dict(field(rr),symbol=target);selector_roots.append(dict(index=index,target_hunk=rr['target_hunk'],entry=rr['addend_raw'],symbol=target))
 env_indices=sorted({c['values'][0] for c in h1['rows'] if c['type']=='ENVELOPE'});roles=defaultdict(set);views=[];code=payload(blob,model,0);h0rel={r['source_offset']:r for r in model['relocations'] if r['source_hunk']==0}
 for index in env_indices:
  v,rs,bs=old.envelopes(code,h0rel,index);views.extend(v)
  for p,kinds in rs.items():roles[p].update(kinds)
  for b in bs:
   b=dict(b,symbol=symbol(0,'e',b['addend_raw']));bindings[0,b['source_offset']]=b;rows[0,b['source_offset']]=dict(hunk=0,offset=b['source_offset'],type='ENVELOPE_PTR',values=[b['symbol']])
 for p,rs in roles.items():rows[0,p]=dict(hunk=0,offset=p,type='ENVELOPE_FIELD',roles=sorted(rs),values=[code[p]])
 rows=sorted(rows.values(),key=lambda c:(c['hunk'],c['offset']));covered=set()
 for c in rows:
  points={(c['hunk'],p) for p in range(c['offset'],c['offset']+length(c,g))};require(not points&covered,'overlapping typed command/header');covered|=points
 touched=[field(r) for r in model['relocations'] if any((r['source_hunk'],p) in covered for p in range(r['source_offset'],r['source_offset']+r['width']))]
 require(sorted(touched,key=lambda r:(r['source_hunk'],r['source_offset']))==[{k:v for k,v in b.items() if k!='symbol'} for _,b in sorted(bindings.items())],'unbound or straddling relocation')
 return dict(rows=rows,bindings=[b for _,b in sorted(bindings.items())],roots=h1['roots'],streams=h1['streams'],stop_roots=stops['roots'],stop_streams=stops['streams'],selector_prefix=selector_roots,selector_max_witness=highest,envelope_indices=env_indices,envelope_views=views,caller_witnesses=witnesses)

def plan(layout,g):
 objects=[]
 for h in (0,1):
  fragments=[]
  for c in [c for c in layout['rows'] if c['hunk']==h]:
   if fragments and fragments[-1][-1]['offset']+length(fragments[-1][-1],g)==c['offset']:fragments[-1].append(c)
   else:fragments.append([c])
  # Selectors begin at zero, giving a complete contiguous 176-slot interface.
  if h==0:fragments.sort(key=lambda f:(f[0]['type']!='SELECTOR',f[0]['offset']))
  ordered=[];cursor=0
  while fragments:
   found=next((i for i,f in enumerate(fragments) if f[0]['offset']%2==cursor%2),None);require(found is not None,'typed parity requires another independent fragment; no filler')
   fs=fragments.pop(found);ordered+=fs;cursor+=sum(length(c,g) for c in fs)
  parts=[];at=0
  for c in ordered:
   n=length(c,g)
   if parts and parts[-1]['original_end']==c['offset']:parts[-1]['original_end']+=n;parts[-1]['candidate_end']+=n
   else:parts.append(dict(original_start=c['offset'],original_end=c['offset']+n,candidate_start=at,candidate_end=at+n))
   at+=n
  objects.append(dict(hunk=h,section='CODE' if h==0 else 'DATA',typed_bytes=cursor,allocated_bytes=cursor+cursor%2,parts=parts,rows=ordered))
 return objects

def encode(objects,g):
 sections={};definitions=[];fixups=[]
 for o in objects:
  out=bytearray();h=o['hunk']
  for c in o['rows']:
   check(c);p=len(out);name=c['type'];v=c['values'];definitions.append(dict(name=row_symbol(c),hunk=h,offset=p))
   if name in ('SELECTOR','ENVELOPE_PTR'):fixups.append(dict(hunk=h,offset=p,symbol=v[0],type='HUNK_RELOC32',width=4,addend=0));out+=bytes(4)
   elif name in ('HEADER','NOTE','ENVELOPE_FIELD'):out+=bytes(v)
   elif name in old.SAMPLES:
    out.extend((old.SAMPLES[name],v[0]));out+=bytes(len(out)%2);out+=v[1].to_bytes(2,'big')
    if not name.endswith('WAIT'):out.append(v[2])
   else:
    op,fields=SPECS[name];out.append(op)
    if fields==('target',):
     out+=bytes(len(out)%2);fixups.append(dict(hunk=h,offset=len(out),symbol=v[0],type='HUNK_RELOC32',width=4,addend=0));out+=bytes(4)
    else:out+=bytes(v)
   require(len(out)-p==length(c,g) and p%2==c['offset']%2,'changed grammar parity/length')
  require(len(out)==o['typed_bytes'],'complete typed section');sections[h]=bytes(out)+bytes(len(out)%2)
 return dict(sections=sections,definitions=definitions,fixups=fixups)

def source(objects,g):
 sem=encode(objects,g);targets={b['symbol'] for b in sem['fixups']};local={d['name'] for d in sem['definitions']};names=sorted(local&targets)
 # Export the complete selector base plus every independently rooted H1 header.
 exports=set(names)|{'_G_h00_6200_complete'}|{row_symbol(c) for o in objects for c in o['rows'] if c['type']=='HEADER' and c['hunk']==1}
 external=sorted(targets-local);data_exports=[row_symbol(c) for o in objects for c in o['rows'] if c['hunk']==1 and c['type']=='HEADER'];lines=['; Typed score/selector/envelope DATA. Historical source/TU/owner UNKNOWN.','\tcseg']+['\tpublic '+n for n in data_exports]
 macros={'HEADER':['dc.b \\1,\\2'],'NOTE':['dc.b \\1,\\2'],'SELECTOR':['dc.l \\1'],'ENVELOPE_PTR':['dc.l \\1'],'ENV_INITIAL':['dc.b \\1'],'ENV_DELTA':['dc.b \\1'],'ENV_TARGET':['dc.b \\1'],'ENV_DELAY':['dc.b \\1'],'ENV_ZERO':['dc.b 0']}
 for name,(op,fields) in SPECS.items():macros[name]=['dc.b $%02x'%op,'ds 0','dc.l \\1'] if fields==('target',) else ['dc.b '+','.join(['$%02x'%op]+['\\%d'%(i+1) for i in range(len(fields))])]
 for name,op in old.SAMPLES.items():macros[name]=['dc.b $%02x,\\1'%op,'ds 0','dc.w \\2']+([] if name.endswith('WAIT') else ['dc.b \\3'])
 for name,body in macros.items():lines+=['T5_'+name+' macro']+['\t'+s for s in body]+['\tendm']
 for h in (0,1):
  lines+=['\tcseg' if h==0 else '\tdseg','\tpublic _audio5_%s_begin'%h,'\tpublic _audio5_%s_end'%h]
  lines+=['\tpublic '+d['name'] for d in sem['definitions'] if d['hunk']==h and d['name'] in exports and (h==0 or d['name'] not in data_exports)]
  if h==0:lines+=['\tpublic '+n for n in external]
  lines+=['_audio5_%s_begin:'%h]
  for c in next(o for o in objects if o['hunk']==h)['rows']:
   sym=row_symbol(c)
   if sym in exports:lines.append(sym+':')
   name,args=c['type'],c['values']
   if name=='ENVELOPE_FIELD':
    role=next(k for k in ('ZERO','DELTA','DELAY','INITIAL','TARGET') if k in c['roles']);name='ENV_'+role;args=[] if role=='ZERO' else [args[0]-256 if role=='DELTA' and args[0]>=128 else args[0]]
   lines.append('\tT5_'+name+(' '+','.join(map(str,args)) if args else ''))
  lines+=['_audio5_%s_end:'%h]
 return ('\n'.join(lines+['\tend',''])).encode('ascii')
