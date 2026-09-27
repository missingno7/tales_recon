from pathlib import Path
import json
root=Path.cwd(); out=root/'experiments/worker-ov11-5fb2-ffp'
base='''struct Child { char pad0[4]; int kind; char pad1[2]; int value; };
struct State { char pad0[34]; struct Child *child; char pad1[6]; int value; char pad2[6]; };
extern struct State G_h01_8BEC[1];
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_37EE;
extern int G_h01_37F0;
recovered(a)
int a;
{
 struct State *p; int x,y;
 p=G_h01_8BEC+a;
'''
tail=''' y=0;
 if(p->child->kind==2)
  if((8 >> G_h01_94B0)+G_h01_94BE-G_h01_37F0-p->value>45) { x+=5; y=-5; }
 G_h01_94C0+=x-G_h01_37EE;
 G_h01_94BE+=y-G_h01_37F0;
 G_h01_37EE=x;
 G_h01_37F0=y;
}
'''
forms={
 'cast_each_104':' x=((float)G_h01_94BE-(float)p->value)*(float)p->child->value/104.0;\n',
 'cast_after_integer_sub':' x=(float)(G_h01_94BE-p->value)*(float)p->child->value/104.0;\n',
 'named_float_temporaries_104':' { float left,right,factor; left=(float)G_h01_94BE; right=(float)p->value; factor=(float)p->child->value; x=(left-right)*factor/104.0; }\n'
}
requests=[]
for name,expr in forms.items():
 src=base+expr+tail; p=out/(name+'.c');p.write_text(src,encoding='ascii');requests.append(dict(id='ov11_F_5FB2',source=str(p),profiles=['aztec36']))
(out/'batch-104.json').write_text(json.dumps(requests,indent=2),encoding='ascii')
