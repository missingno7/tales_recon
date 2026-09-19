struct Record { char a,b; char reserved[10]; };
extern struct Record G_h01_452E[36];
recovered(a)
char a;
{
 int i;
 for(i=1;i<35;++i) { if (i==a) continue; if(G_h01_452E[i].a) continue; if(G_h01_452E[i].b) continue; break; }
 return i;
}
