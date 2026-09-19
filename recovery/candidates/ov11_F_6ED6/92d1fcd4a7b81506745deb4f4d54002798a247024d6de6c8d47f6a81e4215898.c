struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record G_h01_A554[36];
recovered(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&G_h01_A554[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}
