from pathlib import Path
for p in [Path('toolchain/installed/aztec-3.6a/SYS1/lib/c.lib'),Path('toolchain/installed/aztec-3.6a/SYS1/lib/m.lib')]:
 b=p.read_bytes();print('\n',p,len(b))
 for term in [b'amiga_ffp',b'_Fflt',b'.Fflt',b'_Ffix',b'_MathBase',b'mathffp.library',b'_LVOSPFlt']:
  print(term, [i for i in range(len(b)) if b.startswith(term,i)][:8])
