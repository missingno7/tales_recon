struct Item { char a,pad[3]; int b,unused,c,d; char e,f; };
recovered(a,b,c,d,e,f,p,count) char a,c,d; int b,e,f; struct Item *p; int *count; { p->a=a; p->b=b; p->e=c; p->f=d; p->c=e; p->d=f; *count=*count+1; }
