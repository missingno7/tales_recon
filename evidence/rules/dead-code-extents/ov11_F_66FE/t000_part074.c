struct Record { int head[2],field4,field6,middle[7],state,value,extra[3],field32,x,y,last; };
extern struct Record G_h01_A464[1];
extern int F_h11_4696();
extern int F_h11_5962();
F_h11_66FE(a,b) int a,b; { struct Record *p;
 p=&G_h01_A464[a];p->state=2;if(!p->value||b==8)p->value=b;
 return;
 if(b==8) {
  if(p->field32==45) F_h11_4696(p->x,p->y,48,56,8);
  if(p->field4) F_h11_5962(p->field4,8);
  if(p->field6) F_h11_5962(p->field6,8);
 }

}
