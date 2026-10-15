extern long F_h00_8708();
extern long F_h00_2DBA();
extern long F_h00_2D66();
extern long G_h01_A7EE[104];
extern long G_h01_A7D6;
extern int G_h01_A7DA;
extern int G_h01_A7DC;
extern int G_h01_A7DE;
extern int G_h01_A7E0;
extern int G_h01_A7E2;
extern int G_h01_A7E4;

recovered(index, fh)
int index;
long fh;
{
    long offset;
    offset = G_h01_A7EE[index];
    F_h00_8708(fh, offset, -1L);
    F_h00_2DBA(fh, &G_h01_A7D6);
    F_h00_2D66(fh, &G_h01_A7DA);
    F_h00_2D66(fh, &G_h01_A7DC);
    F_h00_2D66(fh, &G_h01_A7DE);
    F_h00_2D66(fh, &G_h01_A7E0);
    F_h00_2D66(fh, &G_h01_A7E2);
    F_h00_2D66(fh, &G_h01_A7E4);
    return 0;
}

