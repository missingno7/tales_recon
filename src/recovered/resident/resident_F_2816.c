extern long F_h00_8708();
extern long F_h00_2D66();
extern long F_h00_2DBA();
extern long G_h01_A7EE[104];

long recovered(fh)
long fh;
{
    unsigned short n;
    unsigned short i;

    F_h00_8708(fh, 0L, -1L);
    F_h00_2D66(fh, &n);
    if (n > 104) {
        return -1;
    }
    for (i = 0; i < n; i++) {
        F_h00_2DBA(fh, &G_h01_A7EE[i]);
    }
    return 0;
}
