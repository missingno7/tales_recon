extern int F_h00_3930();
extern short G_h01_0970;
extern long G_h01_542A;

recovered(p, x, y)
char **p;
short x;
short y;
{
    return F_h00_3930(&G_h01_542A, *p, (long)x * y * G_h01_0970);
}
