struct Record { int padding[11],state,value; char tail[14]; };
extern struct Record G_h01_A464[36];
recovered(a,b) int a,b; { struct Record *p; p=&G_h01_A464[a]; p->state=2; if(!p->value || b==8)p->value=b; }
