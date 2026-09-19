struct Record { int pad[23]; int state; int gap; int x,y; char tail[10]; };
extern struct Record G_h01_9FCE[36];
recovered(n,x,y) int n,*x,*y; {
 struct Record *p;
 p=&G_h01_9FCE[n];
 if(p->state) { *x=p->x; *y=p->y; }
 return p->state;
}
