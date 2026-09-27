import sys,collections
sys.path.insert(0,'tools')
from check_function import validated_function
from recovery_state import recovery
from owned_code_data import expected_string_tail
f,l=validated_function('ov07_F_0F30'); r=recovery()
print('core',f['hunk'],hex(f['start']),hex(f['end']),f['size'],f['extent_status'],f['confidence'],'frame',f['stack_frames'],'returns',f['return_sites'],'indirect',f['indirect_control_flow'],'gaps',f['undecoded_gaps'],'stops',f['boundary_stops'])
print('state',r['functions'].get(f['id'],{}).get('state','DISCOVERED'))
print('calls',f['direct_callees'])
print('pc strings',f['referenced_strings']); print('data refs count',len(f['referenced_data']))
for d in f['referenced_data']:
 print(d)
print('reloc',f['relocations']); print('cfg count',len(f['cfg'])); print('cfg'); [print(x) for x in f['cfg']]
print('branches',f['branch_targets'])
print('register_access',f.get('likely_argument_accesses')); print('save_restore',f.get('register_save_restore'))
try: print('tail',expected_string_tail(f))
except Exception as e: print('tail blocked',type(e).__name__,str(e))
print('instructions sample/branches:')
for i in f['instructions']:
 if i['offset']<180 or i['mnemonic'].startswith(('b','db','rts','jmp','jsr')): print('%04x'%i['offset'],i['mnemonic'],i['operands'])
