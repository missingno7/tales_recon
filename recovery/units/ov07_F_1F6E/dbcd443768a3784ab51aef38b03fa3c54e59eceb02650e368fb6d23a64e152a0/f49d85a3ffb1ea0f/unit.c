struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern char G_h01_46E1;

F_h07_0E06(p)
struct Header *p;
{
    int unused1;
    int unused2;

    p->first = 8;
    p->second = 175;
    F_h00_34E0(p);
    if (G_h01_46E1 < 10)
        F_h00_09C0(18, 182, (long)G_h01_46E1, 7, 1, 0);
    else
        F_h00_09C0(14, 182, (long)G_h01_46E1, 7, 1, 0);
}

struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern long G_h01_46E6;

F_h07_0E7C(p)
struct Header *p;
{
    p->first = 40;
    p->second = 172;
    F_h00_34E0(p);
    F_h00_09C0(176, 175, G_h01_46E6, 1, 9, 1);
}

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

extern char G_h01_33E3[10];
extern char G_h01_33ED;

char *F_h07_2050(n)
long n;
{
    int i;

    G_h01_33ED = 0;
    i = 10;
    do {
        G_h01_33E3[--i] = n % 10 + '0';
    } while ((n = n / 10) > 0);
    return G_h01_33E3 + i;
}

