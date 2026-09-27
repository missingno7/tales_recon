from pathlib import Path
import json, sys
sys.path.insert(0, 'tools')
from compiler_oracle import compile_many
from check_function import validated_function
from function_compare import compare_function

root=Path('.')
out=root/'experiments/worker-ov11-5fb2'
base=(root/'experiments/direct-recovery/ov11_F_5FB2-v1.c').read_text().replace('G_h01_8BEC[];', 'G_h01_8BEC[1];')
variants={
 'stack_calls': base.replace('''#pragma regcall(F_h00_8D1E(d0))\n#pragma regcall(F_h00_8D0A(d0,d1))\n#pragma regcall(F_h00_8D28(d0,d1))\n#pragma regcall(F_h00_8D14(d1))\n#pragma regcall(F_h00_8D00())\n''',''),
 'register_decl': base.replace('''#pragma regcall(F_h00_8D1E(d0))\n#pragma regcall(F_h00_8D0A(d0,d1))\n#pragma regcall(F_h00_8D28(d0,d1))\n#pragma regcall(F_h00_8D14(d1))\n#pragma regcall(F_h00_8D00())\n''','').replace('recovered(a)\nint a;', 'recovered(a)\nregister int a;')
}
for name,src in variants.items():
    (out/(name+'.c')).write_text(src)
trials=[]; names=[]
for name,src in variants.items():
 for profile in ('aztec36','aztec36-x3'):
  trials.append(dict(source=src,profile=profile,target_node=9)); names.append((name,profile,src))
compiled=compile_many(trials)
f,_=validated_function('ov11_F_5FB2')
reports=[]
for (name,profile,src),c in zip(names,compiled):
 r=compare_function(f,c,32766,source_text=src)
 reports.append(dict(hypothesis=name,profile=profile,report=r))
(out/'report.json').write_text(json.dumps(reports,indent=2))
for x in reports:
 r=x['report']
 print(x['hypothesis'],x['profile'],r['verdict'],r['reason'],'len',r.get('actual_length'),'first',r.get('normalized_first_difference'), 'instr',r.get('first_differing_instruction'))
