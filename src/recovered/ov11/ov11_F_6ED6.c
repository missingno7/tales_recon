struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record jg_moving_object_records[36];
recovered(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&jg_moving_object_records[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}
