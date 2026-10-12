extern int G_h01_4D8A;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h00_35DC();
extern int F_h00_7A96();
extern int F_h07_0E7C();
extern int F_h07_0E06();
char *F_h07_2050();

recovered(idx, x, y)
int idx;
long x;
long y;
{
    char buf[34];
    char *p;

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h07_0E7C(y);
    F_h07_0E06(x);
    F_h00_35DC(96, 8, "NEWS INFORMATION", 1, 15);
    buf[0] = 0;
    p = F_h07_2050((long)*(int *)((char *)&G_h01_4D8A + (long)idx * 46));
    F_h00_7A96(buf, "NEWS BULLETIN FROM DAY ");
    F_h00_7A96(buf, p);
    F_h00_35DC(56, 23, buf, 14, 0);
}
