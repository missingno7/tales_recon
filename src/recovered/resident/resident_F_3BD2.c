extern int F_h00_3AE4();
extern int F_h00_3930();
extern long G_h01_542A;

recovered(p)
char *p;
{
    F_h00_3AE4(p + 16, *(short *)(p + 8), *(short *)(p + 10));
    return F_h00_3930(&G_h01_542A, p, 54L);
}
