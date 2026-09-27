import json,hashlib
from pathlib import Path
D=json.loads(Path('evidence/functions/ledger.json').read_text());by={f['id']:f for f in D['functions']}
ids=['resident_F_8D00','resident_F_8D0A','resident_F_8D14','resident_F_8D1E','resident_F_8D28']
refs=[]
for wid in ids:
 f=by[wid]
 for c in f['callers']:
  cf=by.get(c['id']); site=c['site']; ins=[]
  if cf:
   ix=next((i for i,x in enumerate(cf['instructions']) if x['offset']==site),None)
   if ix is not None: ins=cf['instructions'][max(0,ix-4):ix+1]
  refs.append(dict(target=wid,target_offset=f['start'],caller=c['id'],site=site,basis=c.get('basis'),reference_kind=c.get('reference_kind'),context=[dict(offset=x['offset'],mnemonic=x['mnemonic'],operands=x['operands'],raw=x['raw']) for x in ins]))
arc=Path('toolchain/installed/aztec-3.6a/Library Source/ffp.arc')
manifest=json.loads(Path('evidence/toolchain/aztec-3.6a.json').read_text())
arc_rec=next(x for x in manifest['disks'][2].get('files',[]) if x.get('path')=='ffp.arc') if 'files' in manifest['disks'][2] else None
out=dict(source_evidence={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in [str(arc),'toolchain/installed/aztec-3.6a/SYS1/include/functions.h','toolchain/installed/aztec-3.6a/SYS1/include/clib/macros.h','toolchain/installed/aztec-3.6a/SYS1/lib/c.lib']}, wrappers=[dict(id=wid,hunk=by[wid]['hunk'],start=by[wid]['start'],end=by[wid]['end'],size=by[wid]['size'],extent_status=by[wid]['extent_status'],ownership=by[wid]['ownership'],raw_bytes=by[wid]['raw_bytes'],callers=by[wid]['callers']) for wid in ids],references=refs)
Path('experiments/worker-resident-regabi/references.json').write_text(json.dumps(out,indent=2))
for wid in ids:
 f=by[wid];print(wid,hex(f['start']),hex(f['end']),len(f['callers']),len(set(c['id'] for c in f['callers'])),f['ownership'],f['extent_status'])
print('all refs',len(refs),'unique callers',sorted(set(x['caller'] for x in refs)))
print('hashes',json.dumps(out['source_evidence'],indent=2))
