"""Strict retained mixed-object dependencies; never import their inline ASM as C.

The one supported complete object is canonical exit (8552). Its retained CJ
object is linked byte-for-byte, outside the ordinary C unit contribution. A
mechanical entry rename prevents collision with that object's _recovered.
"""
from names import to_mechanical
import copy,json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path
from analysis_support import ROOT
import runtime_natural_members as n
FIELD='mixed_object_dependencies'
ID='resident_F_8552'
NAME='F_h00_8552'
ENTRY='unit_entry'

def recipe(root=ROOT,ledger=None):
 import resident_mixed as m
 root=Path(root);ledger=ledger or json.loads(canonical_path(root,'recovery/ledger.json').read_text())
 item=ledger.get('mixed_source_objects',{}).get(ID)
 require(item is not None,'mixed dependency is not canonical')
 require(item['source']==m.SOURCE and item['proof']==m.PROOF and item['state']=='FUNCTION_CODE_MATCH','unsupported mixed dependency')
 source=to_mechanical(canonical_path(root,item['source']).read_bytes());proof_raw=canonical_path(root,item['proof']).read_bytes();p=json.loads(proof_raw)
 require(source==m.expected_source(root).encode('ascii') and sha256(source)==item['source_sha256'] and sha256(proof_raw)==item['proof_sha256'],'mixed dependency canonical source/proof changed')
 require(p['kind']=='SDK_DERIVED_MIXED_OBJECT' and p['comparison']['verdict']=='EQUAL' and p['comparison']['complete_object'] and p['size']==238 and p['original']==dict(hunk=0,start=0x8552,end=0x8640) and p['comparison']['owned_data']==p['comparison']['owned_bss']==0,'mixed dependency complete contract differs')
 for r in p['input_graph']:
  data=canonical_path(root,r['path']).read_bytes()
  require(sha256(to_mechanical(data) if r['path'].startswith('src/') else data)==r['sha256'],'mixed dependency proof input changed')
 fact=json.loads(canonical_path(root,m.FACT).read_text());directory=fact['mechanical_directory']
 raw,_,_,_=m.control(root,directory,source.decode('ascii'))
 require(sha256(raw)==p['comparison']['actual_sha256'],'mixed dependency complete producer changed')
 path=directory+'/candidate.o';obj=canonical_path(root,path).read_bytes()
 require(n.object_sizes(obj)==(238,0,0),'mixed dependency partial/storage object')
 return dict(id=ID,name=NAME,symbol='_recovered',object=dict(path=path,sha256=sha256(obj)),proof=dict(path=item['proof'],sha256=sha256(proof_raw)),source=dict(path=item['source'],sha256=sha256(source)),original=p['original'],size=238,profile='aztec36-x3',storage_credit=0)

def derive(members,root=ROOT,ledger=None):
 calls=[c for m in members for c in m.get('direct_callees',()) if c.get('id')==ID]
 if not calls:return []
 require(all(c.get('hunk')==0 and c.get('offset')==0x8552 and c.get('basis')=='PC_RELATIVE' for c in calls),'mixed dependency requires exact PC entry')
 return [recipe(root,ledger)]

def header(root=ROOT):
 import resident_mixed as m
 source=to_mechanical(canonical_path(root,m.SOURCE).read_text());return source[:source.index('recovered(code)')]

def configure(trial,recipes,root=ROOT):
 if not recipes:return
 require(recipes==[recipe(root)],'mixed dependency recipe does not rederive')
 require(trial.get('target_node')==0 and trial['profile'] in ('aztec36','aztec36-x3') and trial.get('objects') and not trial.get('object_profiles') and not trial.get('object_groups'),'mixed dependency requires separate compatible root C objects')
 require(not re.search(r'\bunit_entry\b',trial['source']),'mixed dependency entry name collision')
 # Only the candidate entry is renamed. The mixed object's input is untouched.
 trial['source']=re.sub(r'\brecovered\b',ENTRY,trial['source'])+'\n'+header(root)
 for obj in trial['objects']:
  obj['source']='#define '+NAME+' recovered\n'+re.sub(r'\brecovered\b',ENTRY,obj['source'])
 trial['entry_function']=ENTRY
 trial['local_functions']=[*trial.get('local_functions',()),NAME,'recovered']
 trial[FIELD]=recipes

def plan(trial,base_plan,root=ROOT):
 recipes=trial.get(FIELD)
 if not recipes:return base_plan(trial)
 require(recipes==[recipe(root)],'mixed dependency plan is stale')
 key,meta,h,objects=base_plan(trial);meta=dict(meta)
 meta[FIELD]=recipes;meta['mixed_dependency_runner_sha256']=sha256(Path(__file__).read_bytes())
 # The transformed member sources and header participate in the ordinary key;
 # this additional key pins the exact separately linked retained object.
 meta['mixed_dependency_base_key']=key
 from compiler_oracle import overlay_proxies
 from link_line import identity_field
 labels=[o['label'] for o in objects]+['mixed8552']
 field=identity_field(labels,overlay_proxies(trial['source'],0),0,meta)
 if field is not None:meta['link_argument_file']=field
 else:meta.pop('link_argument_file',None)
 return sha256(json_bytes(meta)),meta,h,objects

def stage(trial,source_dir,prefix,root=ROOT):
 recipes=trial.get(FIELD,[])
 if not recipes:return []
 require(recipes==[recipe(root)],'mixed dependency staging is stale')
 raw=canonical_path(root,recipes[0]['object']['path']).read_bytes()
 require(sha256(raw)==recipes[0]['object']['sha256'],'mixed dependency object changed')
 name=prefix+'_mixed8552';(source_dir/(name+'.o')).write_bytes(raw);return [name]

def validate_linked(compiled,root=ROOT,original=None):
 recipes=compiled['identity'].get(FIELD)
 if not recipes:return compiled
 require(recipes==[recipe(root)],'mixed dependency linked recipe is stale')
 require(compiled['identity'].get('entry_function')==ENTRY,'mixed dependency entry collision')
 if original is None:
  from analysis_support import game
  original=game()[:2]
 directory=Path(compiled['directory']);prefix=compiled['prefix'];r=recipes[0]
 require(sha256((directory/(prefix+'_mixed8552.o')).read_bytes())==r['object']['sha256'],'mixed dependency linked object was modified')
 b=(directory/(prefix+'.exe')).read_bytes();model=n.parse(b)
 from overlay_experiment import symbols
 sm=symbols((directory/(prefix+'.sym')).read_text());hn,start=n.symbol(sm,'_recovered')
 require(hn==0 and n.symbol(sm,'_'+ENTRY)[1]!=start,'mixed dependency CODE/entry identity differs')
 c=compiled['contribution'];require(start==c['resident_bounds']['end'],'mixed dependency must follow the complete ordinary C objects')
 raw=n.extent(b,model,0,start,238);expected=n.extent(*original,0,0x8552,238)
 require(not n.relocations(model,0,start,238) and not n.relocations(original[1],0,0x8552,238),'mixed dependency unexpected relocation')
 p=json.loads(canonical_path(root,r['proof']['path']).read_text());seen=set()
 for field in p['field_identities']:
  site=field['site'];pos=site+2;name=field['symbol'];coord=field['original_offset']
  require(pos+2<=238 and not seen.intersection([pos,pos+1]),'mixed dependency field overlap/extent')
  seen.update([pos,pos+1]);ch,actual=n.symbol(sm,name)
  cd=int.from_bytes(raw[pos:pos+2],'big',signed=True);od=int.from_bytes(expected[pos:pos+2],'big',signed=True)
  if name.startswith('_F_h00_'):
   require(ch==0 and start+pos+cd==actual and 0x8552+pos+od==coord,'mixed dependency callee binding changed')
  else:require(ch in (1,2) and 32766+cd==actual and 32766+od==coord,'mixed dependency global binding changed')
 require(len(seen)==58 and all(a==z for i,(a,z) in enumerate(zip(raw,expected)) if i not in seen),'mixed dependency complete ordinary bytes differ')
 # Analysis aliases only. Neither object bytes nor the cached linked artifact is rewritten.
 out=copy.deepcopy(compiled);symbols=out['contribution']['symbols']
 for s in symbols:
  if s['name']=='_recovered':s['name']='_'+NAME
  elif s['name']=='_'+ENTRY:s['name']='_recovered'
 return out
