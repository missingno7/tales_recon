struct Record { int pad[23]; int state; int gap; int x,y; char tail[10]; };
extern struct Record jg_actor_records[36];
recovered(n,x,y) int n,*x,*y; {
 struct Record *p;
 p=&jg_actor_records[n];
 if(p->state) { *x=p->x; *y=p->y; }
 return p->state;
}
