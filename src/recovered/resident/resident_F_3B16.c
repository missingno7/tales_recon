/* resident_F_3B16: allocates a 40-byte bitmap header (error 7000) and its planes through 3A6E. u1..u3 are unused: the original 12-byte frame leaves 6 bytes between r and x. */
extern long F_h00_3870();
extern int F_h00_3674();
extern int F_h00_3A6E();
extern long G_h01_542A;
extern char G_h01_0971;

recovered(c, e)
unsigned int c;
unsigned int e;
{
    char *r;
    unsigned int u1;
    unsigned int u2;
    unsigned int u3;
    unsigned int x;

    r = F_h00_3870(&G_h01_542A, 40L);
    if (r == 0)
        F_h00_3674(7000);
    x = c >> 3;
    F_h00_3A6E(r + 8, x, e);
    *(unsigned int *)r = x;
    *(unsigned int *)(r + 2) = e;
    *(char *)(r + 5) = G_h01_0971;
    return r;
}
