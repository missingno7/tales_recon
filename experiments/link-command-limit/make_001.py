"""Link-line limit experiment: trivial independent objects only (no game bytes)."""
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'build/link-limit-exp/src'
if src.exists(): shutil.rmtree(src)
src.mkdir(parents=True)
G='Old1:'
(src/'compiler-input.txt').write_text('n\n'*20,newline='\n')
names=['t000']+['t000_part%03d'%i for i in range(1,33)]
for i,n in enumerate(names):
    (src/(n+'.c')).write_text('int f%03d() { return %d; }\n'%(i,i),newline='\n')
(src/'h000.c').write_text('extern int f000();\nint (*r)() = f000;\nmain() { return 0; }\n',newline='\n')
cmds=['C:FailAt 1000000']
echo={}
for L in (200,255,256,257,300,400,500,510,511,512,513,514,520,580,1000):
    head='C:Echo "';tail='" >e%04d.txt'%L
    cmds.append(head+'x'*(L-len(head)-len(tail))+tail); assert len(cmds[-1])==L; echo[L]=len(cmds)-1
for n in names+['h000']:
    cmds+=[f'{G}bin/cc <compiler-input.txt >{n}-cc.log -a {n}.c',f'{G}bin/as <compiler-input.txt >{n}-as.log -o {n}.o {n}.asm']
def direct(out,k):
    return f'{G}bin/ln <compiler-input.txt >{out}-ln.log -m -t -o {out}.exe h000.o +o9 '+' '.join(x+'.o' for x in names[:k])+'  +o0 Old1:lib/c.lib'
links={}
for k in range(1,34):
    c=direct('d%02d'%k,k); cmds.append(c); links['d%02d'%k]=dict(step=len(cmds)-1,objects=k,length=len(c))
# argument files: one-line and one-per-line, for 7 and 33 objects
for k in (7,33):
    args=['h000.o','+o9']+[x+'.o' for x in names[:k]]+['+o0','Old1:lib/c.lib']
    (src/('a%02d-line.lnk'%k)).write_text(' '.join(args)+'\n',newline='\n')
    (src/('a%02d-multi.lnk'%k)).write_text('\n'.join(args)+'\n',newline='\n')
    for style in ('line','multi'):
        out='f%02d%s'%(k,style[0])
        c=f'{G}bin/ln <compiler-input.txt >{out}-ln.log -m -t -o {out}.exe -f a{k:02d}-{style}.lnk'
        cmds.append(c); links[out]=dict(step=len(cmds)-1,objects=k,length=len(c),argfile='a%02d-%s.lnk'%(k,style))
json.dump(dict(commands=cmds,echo=echo,links=links),open(ROOT/'build/link-limit-exp/plan.json','w'),indent=1)
print(len(cmds))
