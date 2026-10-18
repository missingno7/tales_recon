"""Complete SDK stdio/FFP objects with exhaustive external operand identities.

Private allocator/stdio storage has no independent ownership map here and is
never inferred from role, spacing, repeated accesses, or original bytes.
"""
from names import read_source
import json,re
from pathlib import Path
from common import require,sha256,json_bytes
from repo_paths import canonical_path,candidate_path
from hunk import parse
from overlay_experiment import symbols
import runtime_natural_members as n
import runtime_glue_members as g
RECIPE='evidence/contributions/runtime-stdio-ffp.json'
OUTPUT='evidence/experiments/runtime-members-stdio-ffp.json'
RECIPE_DIGEST='88cebf9671ba113a884992838581b4d87276011877c120c478ea689c0d327a90'
SPECS=[('putchar','_putchar',0x8056,22,22),('isatty','_isatty',0x83e0,88,88),
       ('unlink','_unlink',0x8438,36,36),('chkabort','_Chk_Abort',0x84da,48,48),
       ('write','_write',0x845c,126,126),('ffp','amiga_ffp',0x8d32,112,80)]
CONTRACTS={
 'putchar':{6:dict(kind='A4',symbol='_Cbuffs',addend=22),14:dict(kind='PC',symbol='_aputc')},
 'isatty':{18:dict(kind='A4',symbol='__devtab'),32:dict(kind='A4',symbol='__numdev'),44:dict(kind='A4',symbol='_errno'),64:dict(kind='A4',symbol='__devtab'),72:dict(kind='PC',symbol='__IsInteractive')},
 'unlink':{10:dict(kind='PC',symbol='__DeleteFile'),20:dict(kind='PC',symbol='__IoErr'),24:dict(kind='A4',symbol='_errno')},
 'chkabort':{12:dict(kind='PC',symbol='__SetSignal'),28:dict(kind='A4',symbol='_Enable_Abort'),42:dict(kind='PC',symbol='__abort')},
 'write':{14:dict(kind='PC',symbol='_Chk_Abort'),26:dict(kind='A4',symbol='__devtab'),34:dict(kind='A4',symbol='__numdev'),46:dict(kind='A4',symbol='_errno'),72:dict(kind='A4',symbol='_errno'),94:dict(kind='PC',symbol='__Write'),112:dict(kind='PC',symbol='__IoErr'),116:dict(kind='A4',symbol='_errno')},
 'ffp':{2:dict(kind='A4',symbol='_MathBase'),18:dict(kind='PC',symbol='__OpenLibrary'),24:dict(kind='A4',symbol='_MathBase'),40:dict(kind='PC',symbol='__Output'),46:dict(kind='PC',symbol='__Write'),50:dict(kind='PC',symbol='__abort'),68:dict(kind='A4',symbol='_MathBase')}}

def read(root,path):return (read_source(root, Path(root) / path, scratch=True) if str(path).startswith('src/') else candidate_path(root,Path(root)/path).read_bytes())
def checked(root,r):
 raw=read(root,r['path']);require(sha256(raw)==r['sha256'],'stdio/FFP retained input changed: '+r['path']);return raw

def producer(root,doc,key):
 d=doc[key];request=json.loads(checked(root,d['request']));receipt=json.loads(checked(root,d['receipt']))
 require(receipt['request']==request and [s['command'] for s in receipt['steps']]==d['commands']==[s['command'] for s in request['steps']], 'stdio/FFP producing commands differ')
 require(all(receipt['steps'][i]['returncode']==0 for i in d['required_steps']), 'stdio/FFP required producer failed')
 require(d['work']==d['job']+'/sys/work' and d['job'].startswith('build/worker-jobs/'),'stdio/FFP job path differs')
 for p,k in [('sys/s/startup-sequence','guest_script_sha256'),('worker.uae','config_sha256'),('kick.rom','rom_sha256')]:
  require(sha256(read(root,d['job']+'/'+p))==request[k],'stdio/FFP environment differs')
 require(sha256(Path(request['emulator']).read_bytes())==request['emulator_sha256'],'stdio/FFP emulator differs')
 for path in d['tools']:
  require(any(p['path']==path and p['sha256']==sha256(n.pinned(root,path)) for p in request['pinned_inputs']), 'stdio/FFP pinned tool differs')
 inventory={a['path']:a for a in receipt['artifacts']}
 def artifact(name):
  raw=read(root,d['work']+'/'+name);a=inventory.get(name)
  require(a and a['size']==len(raw) and a['sha256']==sha256(raw),'stdio/FFP producing artifact differs: '+name)
  return raw
 sources={a['path']:a['sha256'] for a in request['source_files']}
 expected={}
 for name,r in d['sdk_sources'].items():
  raw=checked(root,r['archive']);member=r['member'];parts=[]
  for part in raw.split(b'\x0c'):
   lines=part.splitlines(keepends=True)
   if lines and lines[0].strip()==member.encode('ascii'):parts.append(b''.join(lines[1:]).rstrip(b'\x1a'))
  require(len(parts)==1,'stdio/FFP SDK member absent/duplicate');expected[name]=parts[0]
 expected.update({name:text.encode('ascii') for name,text in d['context_sources'].items()})
 require(set(expected)==set(sources),'stdio/FFP source inventory differs')
 for name,raw in expected.items():require(artifact(name)==raw and sources[name]==sha256(raw),'stdio/FFP SDK/context transport differs')
 contexts={}
 for prefix in d['contexts']:
  b=artifact(prefix);m=parse(b);sm=symbols(artifact(prefix+'.sym').decode('ascii'))
  require([(h['number'],h['type']) for h in m['hunks']]==[(0,'CODE'),(1,'DATA'),(2,'BSS')],'stdio/FFP hunk topology differs')
  contexts[prefix]=(b,m,sm)
 if key=='ffp':
  require(n.object_sizes(artifact('ffp.o'))==n.object_sizes(artifact('ffp-source.o'))==(112,0,0),'FFP partial/storage member')
  require(n.pinned(root,'toolchain/installed/aztec-3.6a/SYS1/lib/m.lib').count(artifact('ffp.o'))==1,'FFP object not unique in pinned library')
  for order in ('one','two'):
   require(contexts[order+'-lib']==contexts[order+'-source'],'FFP complete library/SDK source contexts differ')
 else:
  for name,_,_,size,_ in SPECS[:-1]:require(n.object_sizes(artifact(name+'-source.o'))==(size,0,0),'stdio partial/storage object: '+name)
  # All nine complete objects precede dependency resolution, without clipping.
  total=sum(n.object_sizes(artifact('putc-x3.o' if name=='putc' else name+'-source.o'))[0] for name in d['members'])
  require(total==1204,'stdio complete family CODE extent differs')
  for prefix,c in contexts.items():require(n.symbol(c[2],'__abort')==(0,total),'stdio complete family boundary differs')
 return contexts

def access_anchor(root,doc,fid,symbol,coordinate,original):
 """Independent accepted SDK access role; grants no storage ownership/credit."""
 ledger=json.loads(canonical_path(root,'recovery/ledger.json').read_text());group='functions' if fid=='resident_F_8640' else 'mixed_source_objects'
 item=ledger[group].get(fid);require(item is not None,'stdio/FFP independent canonical access absent')
 record=doc['anchors'][fid]
 for k in ('source','proof'):
  require(item[k]==record[k]['path'] and item[k+'_sha256']==record[k]['sha256'],'stdio/FFP canonical access anchor differs')
  checked(root,record[k])
 source=read(root,item['source']).decode('ascii');p=json.loads(read(root,item['proof']))
 require(p['comparison']['verdict']=='EQUAL','stdio/FFP independent access is not exact')
 if fid=='resident_F_8640':
  sdk=read(root,'toolchain/installed/aztec-3.6a/Library Source/sysio.arc').decode('ascii')
  require('errno = EBADF;' in sdk and 'G_h01_B3CC = EBADF;' in source and '#define EBADF 2' in source,'stdio errno error role differs')
  identities=[r.get('identity') for r in p['comparison']['relocation_proof']]
  require(dict(symbol='_G_h01_%04X'%coordinate,hunk=1,offset=coordinate,addend=0) in identities,'stdio typed global access binding absent')
 else:
  require(p.get('kind')=='SDK_DERIVED_MIXED_OBJECT' and p['comparison']['complete_object'],'stdio/FFP mixed access anchor incomplete')
  for r in p['input_graph']:require(sha256(read(root,r['path']))==r['sha256'],'stdio/FFP mixed access proof input changed')
  if fid=='resident_F_8552':
   import resident_mixed
   require(source==resident_mixed.expected_source(root),'FFP canonical SDK MathBase role differs')
   require('if (G_h01_B3D2)' in source and 'F_h00_8788(G_h01_B3D2)' in source,'FFP independent MathBase CloseLibrary role absent')
  else:require('G_h01_B3AE = 1;' in source,'stdio Enable_Abort CLI initializer absent')
  fields=[r for r in p['field_identities'] if r['symbol']=='_G_h01_%04X'%coordinate]
  require(fields and all(r['original_offset']==coordinate for r in fields),'stdio/FFP independent mixed access coordinate differs')
  for r in fields:
   pos=p['original']['start']+r.get('field',r['site']+2)
   require(32766+int.from_bytes(n.extent(*original,0,pos,2),'big',signed=True)==coordinate,'stdio/FFP original independent access changed')
 return dict(original=(1,coordinate),basis='INDEPENDENT_CANONICAL_SDK_ACCESS',ownership='UNKNOWN',accepted_storage_size=0)

def identities(root,doc,original):
 nr=json.loads(canonical_path(root,n.RECIPE).read_text());contexts=n.producer(root,nr)
 rows,env=n.prove_context(root,nr,contexts['natural'],original,contexts['crt'])
 ids={name:dict(original=row['original'],basis=row['basis']) for name,row in env['identities'].items() if name in ('_Cbuffs','_aputc')}
 report=g.verify(root,original=original)
 for row in report['contributions']:
  for e in row['entries']:ids[e['name']]=dict(original=(0,row['original']['offset']+e['offset']),basis='INDEPENDENT_COMPLETE_PINNED_GLUE')
 tail,_=n.prove_tail_context(root,nr,contexts['tail_natural'],original,contexts['crt'])
 abort=next(r for r in tail if r['member']=='abort');ids['__abort']=dict(original=(0,abort['original']['offset']),basis='INDEPENDENT_COMPLETE_NATURAL_ABORT')
 for name,coordinate,fid in [('__devtab',0xb3a6,'resident_F_8640'),('__numdev',0x2eb0,'resident_F_8640'),('_errno',0xb3cc,'resident_F_8640'),('_Enable_Abort',0xb3ae,'resident_F_766C'),('_MathBase',0xb3d2,'resident_F_8552')]:
  ids[name]=access_anchor(root,doc,fid,name,coordinate,original)
 return ids

def compare(candidate,original,spec,base_ids,*,object_size=None,contract=None):
 name,entry,start,size,code_size=spec
 require(spec in SPECS and object_size==size,'stdio/FFP partial or unsupported complete member')
 fields=CONTRACTS[name] if contract is None else contract
 require(fields==CONTRACTS[name],'stdio/FFP external contract changed/masked')
 ids={}
 for symbol,row in base_ids.items():
  matches=[(h,o) for (h,s),o in candidate[2].items() if s==symbol]
  if len(matches)==1:ids[symbol]=dict(row,candidate=(0 if matches[0][0]==0 else 1,matches[0][1]))
 hn,off=n.symbol(candidate[2],entry);require(hn==0,'stdio/FFP member entry outside root')
 entries=sorted((s,o-off) for (h,s),o in candidate[2].items() if h==0 and off<=o<off+size and not s.startswith('__H'))
 require(entries==[(entry,0)],'stdio/FFP complete exports differ')
 proof=n.compare_member(candidate,original,start,off,size,code_size,fields,ids)
 return dict(member=name,members=[name],profile='aztec36',provider='PINNED_LIBRARY_OBJECT' if name=='ffp' else 'PINNED_SDK_SOURCE',original=dict(hunk=0,offset=start,size=size),entries=[dict(name=entry,offset=0)],owned_data_size=0,owned_bss_size=0,relocation_identity=[],**proof)

def verify(root,*,document=None,original=None):
 if document is None:document=json.loads(canonical_path(root,RECIPE).read_text())
 require(sha256(json_bytes(document))==RECIPE_DIGEST,'stdio/FFP curated recipe changed')
 if original is None:
  from analysis_support import game
  from census import advisory_image
  with advisory_image():original=game()[:2]
 require(sha256(original[0])==document['game_sha256'],'stdio/FFP oracle differs')
 for r in document['headers'].values():require(checked(root,r)==n.pinned(root,r['path']),'stdio pinned header changed')
 contexts={k:producer(root,document,k) for k in ('stdio','ffp')};ids=identities(root,document,original);rows=[]
 for spec in SPECS:
  key='ffp' if spec[0]=='ffp' else 'stdio';prefixes=['one-lib','two-lib'] if key=='ffp' else ['stdio-one','stdio-two'];variants=[]
  for prefix in prefixes:
   c=contexts[key][prefix];local=dict(ids)
   if spec[0]=='write':local['_Chk_Abort']=dict(original=(0,0x84da),basis='COMPLETE_CHKABORT_PROVED_ABOVE')
   variants.append(compare(c,original,spec,local,object_size=spec[3]))
  a,z=variants
  require((a['original'],a['entries'],a['code_sha256'])==(z['original'],z['entries'],z['code_sha256']),'stdio/FFP independent contexts differ')
  a.update(recipe_sha256=RECIPE_DIGEST,object_sha256s={spec[0]:sha256(read(root,document[key]['work']+('/ffp.o' if key=='ffp' else '/'+spec[0]+'-source.o')))})
  rows.append(a)
 return dict(schema_version=1,status='COMPLETE_RUNTIME_CODE_MATCH',game_sha256=document['game_sha256'],recipe=RECIPE,recipe_sha256=RECIPE_DIGEST,contributions=rows,reconstructed_game_functions=0,exact_compiler_release_selected=False,limitations=['No private storage ownership, BSS credit, historical TU or complete root layout.','FFP complete object is 112 bytes; two following zero bytes remain unowned.'])

def input_identity(root):
 path=canonical_path(root,RECIPE)
 if not path.exists():return {str(path):None}
 doc=json.loads(path.read_text());paths={RECIPE,OUTPUT,'tools/runtime_stdio_ffp_members.py'}
 paths.update(r['path'] for r in doc['headers'].values())
 for d in (doc['stdio'],doc['ffp']):
  paths.update([d['request']['path'],d['receipt']['path'],*d['tools']]);paths.update(r['archive']['path'] for r in d['sdk_sources'].values())
  rec=json.loads(read(root,d['receipt']['path']));paths.update(d['work']+'/'+a['path'] for a in rec['artifacts'])
  paths.update(d['job']+'/'+p for p in ('sys/s/startup-sequence','worker.uae','kick.rom'))
 for a in doc['anchors'].values():paths.update(r['path'] for r in a.values())
 return {str(Path(root)/p):sha256(read(root,p)) if Path(root,p).exists() else None for p in paths}
