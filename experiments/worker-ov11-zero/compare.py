import json, pathlib, sys
root=pathlib.Path.cwd(); sys.path.insert(0,str(root/'tools'))
from compiler_oracle import compile_many
from check_function import validated_function
from function_compare import compare_function
from recovery_state import evidence
fid='ov11_F_3B92'; f,_=validated_function(fid); ledger=evidence()
base=(root/'experiments/direct-recovery/ov11_F_3B92-v4.c').read_text()
variants={'direct':base,'int_cast':base.replace('= event->valueD;', '= (int)event->valueD;'),'unsigned_int_cast':base.replace('= event->valueD;', '= (unsigned int)event->valueD;'),
'int_temp':base.replace('            case 18:\n', '            case 18: {\n                int promoted_byte;\n                promoted_byte = event->valueD;\n').replace('G_h01_9F66->value34 = event->valueD;', 'G_h01_9F66->value34 = promoted_byte;').replace('                break;\n            case 17:', '                break;\n            }\n            case 17: {\n                int promoted_byte;\n                promoted_byte = event->valueD;').replace('G_h01_9F8A->value34 = event->valueD;', 'G_h01_9F8A->value34 = promoted_byte;').replace('                break;\n            }\n            }', '                break;\n            }\n            }')}
profiles=('aztec36','aztec36-x3','aztec50','aztec50-short')
trials=[dict(source=s,profile=p,target_node=9) for s in variants.values() for p in profiles]
for (name,p),c in zip([(n,p) for n in variants for p in profiles],compile_many(trials)):
    if c['status']!='COMPILED': print(name,p,c['status']); continue
    report=compare_function(f,c,ledger['a4']['bias'],source_text=variants[name])
    print(name,p,'len',len(bytes.fromhex(c['contribution']['code_hex'])),'verdict',report.get('verdict'),'reason',report.get('reason'),'first',report.get('raw_first_difference') or report.get('normalized_first_difference'))
