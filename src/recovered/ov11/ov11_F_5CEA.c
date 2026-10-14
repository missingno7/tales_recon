struct Record { int fields[15]; int value; char tail[20]; };
extern struct Record G_h01_8BEC[1];
recovered(n) int n; { struct Record *p; p=&G_h01_8BEC[n]; return p->value>0 ? 1 : 0; }
