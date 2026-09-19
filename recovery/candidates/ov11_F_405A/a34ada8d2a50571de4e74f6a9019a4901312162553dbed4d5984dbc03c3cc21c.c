struct Record { int state; char tail[30]; };
extern struct Record G_h01_A16A[36];
recovered(n) int n; { return G_h01_A16A[n].state==4; }
