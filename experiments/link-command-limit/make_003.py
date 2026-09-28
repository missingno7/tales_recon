"""Bound check: ln -f with 96 trivial objects (argument file ~1.4 KB)."""
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'build/link-limit-exp/src3'
if src.exists(): shutil.rmtree(src)
src.mkdir(parents=True)
G='Old1:'
(src/'compiler-input.txt').write_text('n\n'*20,newline='\n')
names=['t000']+['t000_part%03d'%i for i in range(1,96)]
for i,n in enumerate(names):
    (src/(n+'.c')).write_text('int f%03d() { return %d; }\n'%(i,i),newline='\n')
(src/'h000.c').write_text('extern int f000();\nint (*r)() = f000;\nmain() { return 0; }\n',newline='\n')
cmds=['C:FailAt 1000000']
for n in names+['h000']:
    cmds+=[f'{G}bin/cc <compiler-input.txt >{n}-cc.log -a {n}.c',f'{G}bin/as <compiler-input.txt >{n}-as.log -o {n}.o {n}.asm']
args=['h000.o','+o9']+[x+'.o' for x in names]+['+o0','Old1:lib/c.lib']
(src/'t000-ln.lnk').write_text('\n'.join(args)+'\n',newline='\n')
cmds.append(f'{G}bin/ln <compiler-input.txt >t000-ln.log -m -t -o t000.exe -f t000-ln.lnk')
json.dump(dict(commands=cmds),open(ROOT/'build/link-limit-exp/plan3.json','w'),indent=1)
print(len(cmds),(src/'t000-ln.lnk').stat().st_size)
