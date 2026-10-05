"""Refine the guest line limit between 548 (linked) and 563 (failed)."""
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'build/link-limit-exp/src2'
if src.exists(): shutil.rmtree(src)
src.mkdir(parents=True)
G='Old1:'
(src/'compiler-input.txt').write_text('n\n'*20,newline='\n')
names=['t000']+['t000_part%03d'%i for i in range(1,33)]
for i,n in enumerate(names):
    (src/(n+'.c')).write_text('int f%03d() { return %d; }\n'%(i,i),newline='\n')
(src/'h000.c').write_text('extern int f000();\nint (*r)() = f000;\nmain() { return 0; }\n',newline='\n')
cmds=['C:FailAt 1000000']
for n in names[:31]+['h000']:
    cmds+=[f'{G}bin/cc <compiler-input.txt >{n}-cc.log -a {n}.c',f'{G}bin/as <compiler-input.txt >{n}-as.log -o {n}.o {n}.asm']
plan=dict(links={},echo={})
for L in range(544,572):
    out='p%03d'%L
    head=f'{G}bin/ln <compiler-input.txt >{out}-ln.log -m -t -o {out}.exe h000.o +o9 '+' '.join(x+'.o' for x in names[:30])
    tail=' +o0 Old1:lib/c.lib'
    c=head+' '*(L-len(head)-len(tail))+tail; assert len(c)==L
    cmds.append(c); plan['links'][out]=dict(step=len(cmds)-1,length=L)
for L in range(500,600,4):
    head='C:Echo >m%03d.txt '%L
    body=''
    while len(head)+len(body)+10<=L: body+='%09d '%(len(head)+len(body)+10)
    c=(head+body).rstrip(' ')
    c=c+' '+'y'*(L-len(c)-1) if L-len(c)>1 else c
    c=c.ljust(L,'z')[:L]
    cmds.append(c); plan['echo'][L]=dict(step=len(cmds)-1,length=len(c))
plan['commands']=cmds
json.dump(plan,open(ROOT/'build/link-limit-exp/plan2.json','w'),indent=1)
