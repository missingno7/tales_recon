struct Record { char a,b; char reserved[10]; };
extern struct Record G_h01_452E[36];
recovered(a)
char a;
{
 int i;
 i=1; do { if (i!=a && !G_h01_452E[i].a && !G_h01_452E[i].b) break; } while(++i<35);
 return i;
}
