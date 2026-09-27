import json
from pathlib import Path
from tools.compiler_oracle import compile_many
root=Path('.')
src=(root/'experiments/worker-ov11-4b0c-data/probe-one-base.c').read_text()
r=compile_many([dict(source=src,profile='aztec36',target_node=9)])[0]
out={k:r.get(k) for k in ('status','cache_key','cache_hit','error','guest_returncodes')}
c=r.get('contribution',{})
out['contribution']={k:c.get(k) for k in ('code_hex','code_size','data_size','bss_size','hunk','entry_offset','relocations','symbols')}
(root/'experiments/worker-ov11-4b0c-data/probe-one-base.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','cache_key','cache_hit','guest_returncodes')}))
print(json.dumps({k:c.get(k) for k in ('code_hex','code_size','data_size','bss_size','hunk','entry_offset')}))
print('symbols',json.dumps(c.get('symbols')))
print('relocations',json.dumps(c.get('relocations')))
