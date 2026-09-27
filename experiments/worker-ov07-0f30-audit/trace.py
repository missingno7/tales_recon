import sys
sys.path.insert(0,'tools')
from check_function import validated_function
f,_=validated_function('ov07_F_0F30');s=f['start']
for i in f['instructions']:
 o=i['offset']-s
 if i['mnemonic'].startswith(('cmp','b','move','clr','jsr','bra','ext','add','sub','tst','rts','unlk','link')):
  print('%03x %-7s %s'%(o,i['mnemonic'],i['operands']))
