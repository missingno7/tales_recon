"""Complete direct selector-writer census across original CODE and active source.

Unreferenced argument setters remain visible but may be excluded from the game
domain by a closed static-reference census. Limit: no computed-address reference
to the entry exists in recovered code; no claim about external/dynamic callers.
"""
from names import to_mechanical
import re
from collections import Counter,defaultdict
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import active_files,canonical_path
from audio_sequence_data import payload
from analysis_support import decoder,K

GLOBAL='G_h01_2C26';OFFSET=0x2c26
FACT='evidence/data-providers/callback-selector-writers.json'


def clean(text):
 return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:'\n'*m.group(0).count('\n'),text,flags=re.S)


def literal(text):
 text=text.strip()
 return int(text.rstrip('Ll'),0) if re.fullmatch(r'(?:0|[1-9][0-9]*|0[xX][0-9a-fA-F]+)[Ll]?',text) else None


def assignments(text):
 text=clean(text);out=[]
 for m in re.finditer(r'\b'+GLOBAL+r'\s*(\+\+|--|[+*/|&^-]?=(?!=))\s*([^;]*);',text):
  op,value=m.group(1),m.group(2).strip();out.append(dict(line=text[:m.start()].count('\n')+1,operator=op,expression=value,value=literal(value) if op=='=' else None))
 return out


def reachable_domain(initializer,writers,excluded):
 require(type(initializer) is int and initializer>=0,'nonnegative selector initializer required')
 live=[w for w in writers if w['function'] not in excluded]
 require(all(type(w['value']) is int and w['value']>=0 for w in live),'reachable selector writer has an unbounded/negative domain')
 domain=sorted({initializer}|{w['value'] for w in live})
 return domain,max(domain)+1


def source_paths(root):return [p.relative_to(root).as_posix() for p in active_files(Path(root)/'src') if p.suffix in ('.c','.asm','.h')]


def derive(root,blob,model,analysis,ledger):
 from data_providers import document
 index=document(root,'evidence/executable/instructions.json');require(index['analysis_current'] and analysis['game_sha256']==sha256(blob),'current original instruction census required')
 code={h['number']:payload(blob,model,h['number']) for h in model['hunks'] if h['type']=='CODE'};bias=analysis['a4']['bias'];rows=index['instructions'];md=decoder();refs=defaultdict(list)
 for r in model['relocations']:
  if r['target_hunk']==1 and OFFSET-3<=r['addend_raw']<OFFSET+4:refs[r['source_hunk']].append(r)
 writers=[];reads=[];escapes=[];incoming=[];computed_candidates=[];word_owners={};setter_lo,setter_hi=0x5428,0x544c
 for row in rows:
  h,p,n=row['hunk'],row['offset'],row['length']
  if h not in code:continue
  raw=code[h];ins=next(md.disasm(raw[p:p+24],p,count=1),None)
  require(ins is not None and ins.size==n and bytes(ins.bytes).hex()==row['raw'],'stale original instruction boundary')
  text=ins.op_str;mn=ins.mnemonic;stem=mn.split('.')[0];width={'b':1,'w':2,'l':4}.get(mn.rsplit('.',1)[-1],0);operands=list(ins.operands);sites=set()
  for oi,op in enumerate(operands):
   if op.type==K.M68K_OP_MEM and op.mem.base_reg==K.M68K_REG_A4:
    addr=bias+op.mem.disp
    if addr<OFFSET+4 and OFFSET<addr+max(width,1):sites.add(oi)
  contained=[r for r in refs.get(h,[]) if p<=r['source_offset']<p+n]
  if contained:
   require(len(contained)==1,'ambiguous selector relocation operand')
   for oi,op in enumerate(operands):
    if op.type==K.M68K_OP_MEM and op.mem.base_reg==0:sites.add(oi)
  if sites:
   require(len(row['function_candidates'])==1,'selector access requires one original owner');fid=row['function_candidates'][0]
   record=dict(function=fid,hunk=h,offset=p,size=n,mnemonic=mn,operands=text)
   for oi in sites:
    write=(stem=='clr' or stem=='move' and oi==len(operands)-1)
    read=(stem in ('cmp','cmpi','tst','btst') or stem=='move' and oi!=len(operands)-1)
    if write:
     require(width==4,'partial selector write requires a new domain analysis')
     if stem=='clr':record.update(value=0,expression='0')
     elif operands[0].type==K.M68K_OP_IMM:record.update(value=operands[0].imm,expression=str(operands[0].imm))
     else:record.update(value=None,expression='p',unbounded='LONG_ARGUMENT_8_A5');require(text=='$8(a5), $2c26.l','unknown computed selector writer')
     writers.append(record)
    elif read:reads.append(record)
    else:escapes.append(record)
   for q in range(p,p+n,2):word_owners[(h,q)]=record
  if any(op.type==K.M68K_OP_IMM and setter_lo<=op.imm<setter_hi for op in operands):computed_candidates.append(dict(hunk=h,offset=p,mnemonic=mn,operands=text))
  # Any direct/static reference into the unreferenced setter defeats exclusion.
  if h==0 and not(setter_lo<=p<setter_hi) and (stem in ('jmp','jsr','bra','bsr') or stem.startswith('db') or stem in ('bhi','bls','bcc','bcs','bne','beq','bvc','bvs','bpl','bmi','bge','blt','bgt','ble')):
   for match in re.finditer(r'\$([0-9a-f]+)(?![0-9a-f])',text):
    address=int(match.group(1),16)
    if h==0 and setter_lo<=address<setter_hi:incoming.append(dict(hunk=h,offset=p,mnemonic=mn,operands=text,target=address))
 # Every displacement that could overlap this LONG is accounted for, even
 # outside the decoded instruction inventory and across every overlay hunk.
 displacement_words={((OFFSET+j-bias)&65535).to_bytes(2,'big') for j in range(-3,4)};raw_sites=[]
 for h,raw in code.items():
  for p in range(0,len(raw)-1,2):
   if raw[p:p+2] in displacement_words:
    require((h,p) in word_owners,'unclassified possible selector displacement outside the instruction census')
    raw_sites.append(dict(hunk=h,offset=p,writer_offset=word_owners[(h,p)]['offset']))
 for h,rs in refs.items():
  for r in rs:require(any(h==x['hunk'] and x['offset']<=r['source_offset']<x['offset']+x['size'] for x in writers+reads+escapes),'unclassified/escaped selector relocation')
 incoming_relocs=[{k:r[k] for k in ('source_hunk','source_offset','target_hunk','addend_raw','type','width')} for r in model['relocations'] if r['target_hunk']==0 and setter_lo<=r['addend_raw']<setter_hi]
 pred=next(f for f in analysis['functions'] if f['hunk']==0 and f['end']==setter_lo);require(pred['instructions'][-1]['mnemonic']=='rts','setter has incoming fallthrough')
 setter=next(f for f in analysis['functions'] if f['id']=='resident_F_5428');require(not setter['callers'] and all(e['kind'].startswith('CURATED_UNREFERENCED') for e in setter['entry_evidence']),'setter has a real entry/caller')
 require(not incoming and not incoming_relocs and not computed_candidates,'argument setter acquired a static/computed incoming reference')
 owners={}
 for section in ('functions','reconstructed_asm','data_providers'):
  for fid,x in ledger.get(section,{}).items():owners.setdefault(x['source'],[]).append((fid,x))
 src_writes=[];asm_writes=[];mentioned=[];initializer=None;source_references=[]
 for name in source_paths(root):
  text=to_mechanical(canonical_path(root,name).read_text(encoding='utf8'));stripped=clean(text)
  if re.search(r'(?:\b_?(?:resident_F_5428|recon_h00_5428|F_5428)\b|\b0[xX]5428\b|\b21544\b|\$5428\b)',stripped,re.I):source_references.append(name)
  if not re.search(r'\b_?'+GLOBAL+r'\b',stripped):continue
  require(not re.search(r'&\s*'+GLOBAL+r'\b',stripped),'selector address escaped through source')
  require(name in owners and len(owners[name])==1,'selector source is not one exact accepted owner');fid,entry=owners[name][0]
  require(entry['state'] in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH','DATA_LAYOUT_MATCH'),'selector source lacks exact acceptance')
  require(sha256(to_mechanical(canonical_path(root,entry['source']).read_bytes()))==entry['source_sha256'] and sha256(canonical_path(root,entry['proof']).read_bytes())==entry['proof_sha256'],'stale selector source/proof')
  mentioned.append(dict(function=fid,source=name,source_sha256=entry['source_sha256'],proof_sha256=entry['proof_sha256']))
  if name.endswith('.asm'):
   for no,line in enumerate(stripped.splitlines(),1):
    line=line.strip()
    if GLOBAL not in line or line.startswith('public '):continue
    require(',' in line and line.split(',')[-1].strip()!='_'+GLOBAL,'assembly selector write needs a new classification')
  else:
   for row in assignments(text):
    row=dict(row,function=fid,source=name)
    if fid=='resident_data_2C26':require(row['value']==0,'accepted selector initializer changed');initializer=row
    else:src_writes.append(row)
 require(initializer is not None,'accepted selector initializer missing')
 require(Counter((x['function'],x['expression'],x['value']) for x in writers)==Counter((x['function'],x['expression'],x['value']) for x in src_writes),'C/original writer inventories disagree')
 unknown=[x for x in writers if x['value'] is None];require(len(unknown)==1 and unknown[0]['function']=='resident_F_5428','new unbounded selector writer requires review')
 require(not escapes,'selector address/access escape prevents a closed direct-writer domain')
 require(not source_references,'argument setter acquired a recovered-source reference')
 domain,prefix_count=reachable_domain(initializer['value'],writers,{'resident_F_5428'})
 return dict(schema_version=1,kind='CALLBACK_SELECTOR_WRITERS',global_symbol=GLOBAL,original=dict(hunk=1,offset=OFFSET,width=4),writers=sorted(writers,key=lambda x:(x['hunk'],x['offset'])),source_writers=sorted(src_writes,key=lambda x:(x['function'],x['line'])),assembly_writers=asm_writes,readers=sorted(reads,key=lambda x:(x['hunk'],x['offset'])),initializer=initializer,sources=sorted(mentioned,key=lambda x:x['source']),address_escapes=escapes,all_code_hunks=sorted(code),raw_displacement_sites=raw_sites,unreferenced_argument_setter=dict(function='resident_F_5428',writer=unknown[0],direct_or_pc_references=incoming,incoming_relocations=incoming_relocs,preceding_function=pred['id'],preceding_terminal=pred['instructions'][-1]['offset'],callers=setter['callers'],entry_evidence=setter['entry_evidence'],source_references=source_references,immediate_address_candidates=computed_candidates,excluded_from_game_domain=True,kind='RECOVERED_CODE_REACHABILITY_EXCLUSION',limits='No computed-address reference to this entry exists in the recovered code; excludes external callers, dynamically synthesized code and arbitrary memory corruption'),concrete_values=domain,index_domain=domain,prefix_count=prefix_count,capacity_claim=False,limits='Direct named selector writes in all original CODE hunks and all active C/ASM sources; arbitrary memory corruption/external calls are outside this domain.')
