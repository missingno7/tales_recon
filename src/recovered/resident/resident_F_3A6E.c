extern long F_h00_3870();
extern int F_h00_3674();
extern long G_h01_542A;
extern int G_h01_0970;

recovered(p, c, e)
long *p;
unsigned int c;
unsigned int e;
{
    int i;
    long r;

    r = F_h00_3870(&G_h01_542A, (long)(unsigned int)(c * e * G_h01_0970));
    if (r == 0)
        F_h00_3674(6000);
    for (i = 0; i < G_h01_0970; i++)
        p[i] = r + (unsigned int)(i * c * e);
}
