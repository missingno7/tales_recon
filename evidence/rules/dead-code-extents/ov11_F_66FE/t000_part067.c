struct Record { int field0,value; char tail[48]; };
extern struct Record G_h01_8BEC[1];
F_h11_5F90(n) int n; { struct Record *p; p=&G_h01_8BEC[n]; return p->value; }
