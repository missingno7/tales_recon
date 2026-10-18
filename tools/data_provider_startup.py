"""Bounded startup callback prefix and envelope CODE-entry table.

Register-ABI entry addresses only. Interior entries bind to an exactly proved
named provider plus an independently decoded instruction offset; no CODE bytes
or additional ASM acceptance are produced here.
"""
from names import to_mechanical
import json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from audio_sequence_data import payload
from overlay_experiment import relocation_profile
from audio_driver_contracts import decode,at

IDS={'resident_data_2B6E':(0x2b6e,6,'AUDIO_ENVELOPE_WORD_FENCE'), 'resident_data_2BC2':(0x2bc2,5,'CALLBACK_INDEX_DOMAIN_PREFIX')}
ENTRY_CONTROL=b'extern void DP_ext_a();\nextern void DP_ext_b();\ntypedef void (*DP_CodeEntry)();\nDP_CodeEntry DP_entry_probe[3] = {(DP_CodeEntry)((char *)DP_ext_a + 2), (DP_CodeEntry)((char *)DP_ext_b + 4), (DP_CodeEntry)((char *)DP_ext_a + 2)};\n'
# Only constants actually emitted by this batch and its independent control.
ADDEND_BYTES={2:b'\x32',4:b'\x34',184:b'\x58\x8b',200:b'\x58\x8c',212:b'\x54\x8d',246:b'\x56\x8f',302:b'\x5e\x92'}


def shape(f):
 require(set(f)==({'selector_writers'} if f.get('id')=='resident_data_2BC2' else set())|{'schema_version','kind','id','source','original','definitions','bindings','object_sections','historical_owner','historical_tu','original_filename','producer'} and f['schema_version']==1 and f['kind']=='EXTERNAL_CODE_POINTER_TABLE' and f['id'] in IDS,'closed startup table identity/schema')
 start,count,route=IDS[f['id']];size=4*count
 require(f['source']=='src/recovered/data/'+f['id']+'.c' and f['original']==dict(hunk=1,start=start,size=size) and f['object_sections']==dict(CODE=0,DATA=size,BSS=0,COMMON=0),'complete bounded startup DATA object')
 require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown historical owner/TU')
 require(isinstance(f['definitions'],list) and len(f['definitions'])==1,'one aggregate per provider')
 d=f['definitions'][0]
 require(set(d)=={'symbol','type','offset','count','targets','bounds','evidence'} and d['symbol']=='G_h01_%04X'%start and d['type']=='CODE_ENTRY_POINTER' and d['offset']==0 and type(d['count']) is int and d['count']==count and d['bounds']==dict(kind=route,bytes=size),'independent startup pointer aggregate extent')
 require(isinstance(d['targets'],list) and len(d['targets'])==count and set(d['targets'])==set(f['bindings']),'complete named entry bindings')
 for name,b in f['bindings'].items():
  require(set(b)=={'hunk','offset','provider','entry','addend'} and b['hunk']==0 and type(b['offset']) is int and type(b['addend']) is int and b['addend']>=0 and name=='_recon_h00_%04X'%b['offset'] and re.fullmatch('_recon_h00_[0-9A-F]{4}',b['entry']),'named CODE provider/entry/offset identity')
  require(b['addend']==0 or b['addend'] in ADDEND_BYTES,'unmeasured symbolic AJ addend rejects')
 if f['id']=='resident_data_2BC2':
  require(set(f['selector_writers'])=={'fact','sha256'} and f['selector_writers']['fact']=='evidence/data-providers/callback-selector-writers.json' and re.fullmatch('[0-9a-f]{64}',f['selector_writers']['sha256']),'pinned complete selector-writer census')
  require(all(b['addend']==0 for b in f['bindings'].values()),'callback prefix uses independently exported direct entries')
 return size


def expressions(f):
 shape(f);return [(f['bindings'][n]['entry'],f['bindings'][n]['addend']) for n in f['definitions'][0]['targets']]


def source(f):
 shape(f);d=f['definitions'][0];es=expressions(f);names=sorted({n for n,a in es})
 prefix='typedef void (*DP_CodeEntry)();\n'+''.join('extern void '+n[1:]+'();\n' for n in names)
 if f['id']=='resident_data_2BC2':return (prefix+'DP_CodeEntry G_h01_2BC2[5] = {'+', '.join(n[1:] for n,a in es)+'};\n').encode('ascii')
 return (prefix+'DP_CodeEntry G_h01_2B6E[6] = {\n'+',\n'.join('  (DP_CodeEntry)((char *)'+n[1:]+' + %d)'%a for n,a in es)+'\n};\n').encode('ascii')


def anchor_ids(f):
 if f['id']=='resident_data_2B6E':return {'resident_driver_544C','resident_frameless_57D2','resident_data_2B86'}
 return {'resident_callback_617C','resident_callback_61A0','resident_data_2C26','resident_F_033E','resident_F_0A44','resident_F_0FDE','resident_F_53E6','resident_F_5428','ov03_F_001C','ov05_F_0000','ov08_F_0000','ov09_F_0000','ov10_F_0000','ov11_F_0000'}


def item(ledger,ident):
 for section in ('reconstructed_asm','functions','data_providers'):
  if ident in ledger.get(section,{}):return ledger[section][ident]
 require(False,'missing independently accepted startup anchor '+ident)


def evidence_paths(root,f):
 from data_providers import document
 l=document(root,'recovery/ledger.json');out={'evidence/types.json'}
 for fid in anchor_ids(f):out.update(item(l,fid)[k] for k in ('source','proof') ) ;out.update([item(l,fid)['fact']] if 'fact' in item(l,fid) else [])
 if f['id']=='resident_data_2BC2':
  import data_provider_selector as selectors
  out.update([selectors.FACT,'evidence/executable/instructions.json','evidence/rules/unreferenced-entries/entries.json',*selectors.source_paths(root)])
 return sorted(out)


def typed_evidence(root,f,blob,model,analysis,ledger):
 from data_providers import document
 from data_provider_pointers import canonical_entries
 from evidence_snapshot import memoized
 shape(f);anchors={}
 for fid in anchor_ids(f):
  x=item(ledger,fid);require(x['state'] in ('FUNCTION_CODE_MATCH','FUNCTION_WITH_DATA_MATCH','DATA_LAYOUT_MATCH'),'exact accepted anchor required')
  require(sha256(to_mechanical(canonical_path(root,x['source']).read_bytes()))==x['source_sha256'] and sha256(canonical_path(root,x['proof']).read_bytes())==x['proof_sha256'],'changed accepted anchor')
  anchors[fid]=dict(source_sha256=x['source_sha256'],proof_sha256=x['proof_sha256'])
 require(f['definitions'][0]['evidence']==anchors,'stale startup consumer/extent evidence')
 cat=canonical_entries(root,blob,model,analysis,ledger)
 if f['id']=='resident_data_2BC2':
  import audio_callback_asm as callbacks
  def callback_entries():
   out={}
   for r in callbacks.rows(root,blob,model,analysis,ledger):
    require(r['acceptance'] and r['source_acceptance'],'callback exact source acceptance')
    fact=document(root,ledger['reconstructed_asm'][r['id']]['fact'])
    for e in fact['exports']:
     if e['original'] is not None:out[e['name']]=dict(hunk=0,offset=e['original'],provider=r['id'])
   return out
  cat={**cat,**memoized(root,'startup-callback-code-entries',sha256(blob)+';'+sha256(json_bytes(ledger['reconstructed_asm'])),callback_entries,strict=True)}
 for name,b in f['bindings'].items():
  base=cat.get(b['entry']);require(base is not None and base['provider']==b['provider'] and base['hunk']==0 and base['offset']+b['addend']==b['offset'],'target must bind to a current exact named provider entry')
  pf=document(root,ledger['reconstructed_asm'][b['provider']]['fact']);o=pf['original'];ins=decode(payload(blob,model,0)[o['start']:o['end']],o['start'])
  require(any(i['offset']==b['offset'] for i in ins),'interior pointer target is not an independently decoded instruction entry')
 if f['id']=='resident_data_2B6E':
  code=payload(blob,model,0);by={i['offset']:i for i in decode(code[0x544c:0x5470],0x544c)}
  for p,m,o in [(0x544c,'tst.b','$1e(a0)'),(0x545e,'move.b','$1e(a0), d0'),(0x5462,'lsl.l','#$2, d0'),(0x5464,'lea.l','$2b6e.l, a2'),(0x546a,'movea.l','(a2, d0.w), a2'),(0x546e,'jsr','(a2)')]:at(by,p,m,o)
  fence={i['offset']:i for i in decode(code[0x57d2:0x57e4],0x57d2)};at(fence,0x57dc,'move.w','d0, $2b86.l')
  ff=document(root,ledger['data_providers']['resident_data_2B86']['fact']);require(ff['original']==dict(hunk=1,start=0x2b86,size=2),'independently typed WORD fence changed')
  require((0x2b86-0x2b6e)//4==6 and (0x2b86-0x2b6e)%4==0,'stride/fence extent')
  extent=dict(kind='AUDIO_ENVELOPE_WORD_FENCE',stride=4,count=6,end=0x2b86,consumer=0x546e,index_field='channel BYTE+0x1E',capacity_claim=False)
 else:
  code=payload(blob,model,0);by={i['offset']:i for i in decode(code[0x617c:0x61a0],0x617c)}
  for p,m,o in [(0x618a,'lea.l','$2bc2.l, a0'),(0x6190,'move.l','$2c26.l, d0'),(0x6196,'lsl.l','#$2, d0'),(0x6198,'movea.l','(a0, d0.w), a0'),(0x619c,'jsr','(a0)')]:at(by,p,m,o)
  for fid in ('ov03_F_001C','ov05_F_0000'):
   text=to_mechanical(canonical_path(root,ledger['functions'][fid]['source']).read_text(encoding='ascii'));text=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
   require('G_h01_2C26 = 0;' in text,'explicit selector-zero witness missing')
   if fid=='ov03_F_001C':require('G_h01_2C26 = 1;' in text,'explicit selector-one witness missing')
  init=document(root,ledger['data_providers']['resident_data_2C26']['fact']);require(init['original']==dict(hunk=1,start=0x2c26,size=4) and init['definitions'][0]['initializer']==0,'independently accepted initial callback index zero')
  # Do not claim that 0/1 are exhaustive: the resident startup writes 4.
  other={i['offset']:i for i in decode(code[0x4cc:0x4d4],0x4cc)};at(other,0x4cc,'move.l','#$4, -$53d8(a4)')
  import data_provider_selector as selectors
  measured=selectors.derive(root,blob,model,analysis,ledger);curated=document(root,selectors.FACT)
  require(curated==measured and sha256(json_bytes(curated))==f['selector_writers']['sha256'],'complete selector-writer census no longer rederives')
  require(curated['index_domain']==[0,1,4] and curated['prefix_count']==f['definitions'][0]['count'] and curated['unreferenced_argument_setter']['excluded_from_game_domain'],'reachable selector domain must bound the complete prefix')
  extent=dict(kind='CALLBACK_INDEX_DOMAIN_PREFIX',stride=4,indices=curated['index_domain'],count=curated['prefix_count'],capacity_claim=False,selector_writers=f['selector_writers'],reachability_exclusion=curated['unreferenced_argument_setter'])
 rels=relocation_profile(model,1,f['original']['start'],f['original']['size']);expected=[dict(offset=4*i,type='HUNK_RELOC32',width=4,target_hunk=0,addend=f['bindings'][n]['offset']) for i,n in enumerate(f['definitions'][0]['targets'])]
 require(rels==expected,'complete original startup pointer relocation identities')
 return [dict(symbol=f['definitions'][0]['symbol'],type='CODE_ENTRY_POINTER',bytes=f['original']['size'],extent=extent,bindings=f['bindings'],historical_owner='UNKNOWN',historical_tu='UNKNOWN',C_calling_convention_claim=False)]


def compare_data(original,model,f,obj,linked,map_text):
 from data_providers import document
 from analysis_support import ROOT
 from data_provider_pointers import binder_names,linked_view
 shape(f);recipe=document(ROOT,f['producer']['batch']);facts=[document(ROOT,m['fact']) for m in recipe['members']];names=binder_names(facts);es=expressions(f);targets=[n for n,a in es];addends=[a for n,a in es];symbol='_'+f['definitions'][0]['symbol']
 parsed,m,actual,sm=linked_view(obj,linked,map_text,symbol,targets,names,addends)
 origin=f['original'];expected=payload(original,model,1)[origin['start']:origin['start']+origin['size']];rebased=b''.join(f['bindings'][n]['offset'].to_bytes(4,'big') for n in f['definitions'][0]['targets'])
 rels=relocation_profile(model,1,origin['start'],origin['size']);wanted=[dict(offset=4*i,type='HUNK_RELOC32',width=4,target_hunk=0,addend=f['bindings'][n]['offset']) for i,n in enumerate(f['definitions'][0]['targets'])]
 require(rebased==expected and rels==wanted,'complete original named target identities; no masks')
 return dict(verdict='EQUAL_CANDIDATE',state='DATA_LAYOUT_MATCH',id=f['id'],original=dict(origin,sha256=sha256(expected)),sections=parsed['sections'],symbols=parsed['definitions'],relocation_bindings=parsed['fixups'],original_relocations=rels,candidate_relocations=relocation_profile(m,1,0,origin['size']),actual_sha256=sha256(actual),source_sha256=sha256(source(f)),object_sha256=sha256(obj),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,ambiguity=None,data_hex=rebased.hex(),zero_fill_credit=0,root_layout_proof=False)
