/* Candidate h3 for ov15_F_0000: h3 with k stored and reloaded before the shift (one-factor change). */
struct Point {
    char pad[32];
    int x;
    int y;
};

struct PointRef {
    struct Point *point;
    char reserved[8];
};

struct Pair {
    int first;
    int second;
};

extern long G_h01_2A16;
extern char G_h01_14E6;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern long G_h01_4700;
extern char G_h01_46E1;
extern char G_h01_46E3;
extern char G_h01_46E4;
extern long G_h01_46E6;
extern char G_h01_4705;
extern char *G_h01_5370;
extern struct PointRef G_h01_4524[36];
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44AE;
extern int G_h01_44B0;
extern int G_h01_4478;
extern int G_h01_447A;
extern int G_h01_43D6;
extern int G_h01_43D8;
extern int G_h01_440C;
extern int G_h01_440E;
extern int G_h01_44E4;
extern int G_h01_44E6;
extern int G_h01_4480;
extern int G_h01_4482;
extern int G_h01_4488;
extern int G_h01_44B6;
extern int G_h01_44B8;
extern int G_h01_44BE;
extern int G_h01_444A;
extern int G_h01_444C;
extern int G_h01_4452;
extern int G_h01_43DE;
extern int G_h01_43E0;
extern int G_h01_43E6;
extern int G_h01_4414;
extern int G_h01_4416;
extern int G_h01_441C;
extern int G_h01_A770;
extern int G_h01_A772;
extern int G_h01_A778;
extern int G_h01_44EC;
extern int G_h01_44EE;
extern int G_h01_44F4;

extern int F_h00_435E();
extern int F_h00_57D2();
extern int F_h00_8BC8();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_2816();
extern long F_h00_291E();
extern int F_h00_8A46();
extern int F_h00_35DC();
extern int F_h00_34E0();
extern int F_h00_09C0();
extern int F_h13_0942();
extern int F_h00_7522();
extern int F_h00_330E();
extern int F_h04_1D32();
extern int F_h04_27FE();
extern int F_h00_86A8();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h15_1428();
extern int F_h15_0C12();
extern int F_h15_08B0();
extern long F_h00_08FC();
extern int F_h00_8044();
extern int F_h00_3AE4();
extern int F_h00_3B84();

recovered(p1, flag)
int p1;
char *flag;
{
    struct PointRef *ent;
    int x, y, xs, ys, i, k;
    long t1, t2;
    int r;
    long h;

    h = 0;
    ent = 0;
    F_h00_435E();
    F_h00_57D2(0x21);
    while (G_h01_2A16 != 0)
        ;
    F_h00_57D2(0);
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(1);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    if (p1 == 1)
        F_h00_291E(0x14, G_h01_46CE);
    else
        F_h00_291E(0x15, G_h01_46CE);
    h = F_h00_291E(0x16, h);
    F_h00_291E(0x18, &G_h01_4442);
    G_h01_4442 = 0x16;
    G_h01_4444 = 0x73;
    F_h00_291E(0x17, &G_h01_44AE);
    G_h01_44AE = 0x28;
    G_h01_44B0 = 0xac;
    F_h00_291E(0x19, &G_h01_4478);
    G_h01_4478 = 8;
    G_h01_447A = 0xaf;
    F_h00_291E(0x1a, &G_h01_43D6);
    G_h01_43D6 = 0xc0;
    G_h01_43D8 = 0xaa;
    F_h00_291E(0x1b, &G_h01_440C);
    G_h01_440C = 0xf8;
    G_h01_440E = 0xae;
    F_h00_291E(0x1c, &G_h01_A768);
    if (G_h01_46E4 && p1) {
        F_h00_291E(0x1d, &G_h01_44E4);
        G_h01_44E4 = 0x119;
        G_h01_44E6 = 0xaa;
    }
    if (G_h01_46E3 == 0x23) {
        x = 0x2e;
        xs = 0x2e;
        y = 0x8b;
        ys = 0x8b;
    } else {
        x = G_h01_4524[G_h01_46E3].point->x;
        xs = x;
        y = G_h01_4524[G_h01_46E3].point->y;
        ys = y;
    }
    if (*flag) {
        *flag = 0;
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_35DC(0x64, 6, "Security System", 1, 0xf);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_09C0(0xb0, 0xaf, G_h01_46E6, 1, 9, 1);
        if (G_h01_46E1 < 10)
            F_h00_09C0(0x12, 0xb6, (long)G_h01_46E1, 7, 1, 0);
        else
            F_h00_09C0(0xe, 0xb6, (long)G_h01_46E1, 7, 1, 0);
        if (F_h13_0942() == 0) {
            F_h00_7522(F_h13_0942);
            F_h00_330E();
            G_h01_46DA = G_h01_4700;
            F_h00_2816(G_h01_46DA);
            F_h04_1D32();
            F_h04_27FE("Beagle-Boy");
        }
        F_h00_291E(0x14, G_h01_46CE);
        F_h00_57D2(0x21);
        while (G_h01_2A16 != 0)
            ;
        F_h00_330E();
    }
    F_h00_57D2(0);
    F_h00_86A8(5L);
    F_h00_57D2(0x1f);
    F_h00_8A46(h, 0L, 0L, G_h01_46D2, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    ent = G_h01_4524;
    for (i = 0; i < 35 && ent->point != 0; i++, ent++) {
        if (ent->reserved[6] != 0)
            *G_h01_5370 = 0xe;
        else if (ent->reserved[7] != 0)
            *G_h01_5370 = 9;
        else
            *G_h01_5370 = 0xc;
        F_h15_08B0(ent->point->x, ent->point->y);
    }
    F_h00_8A46(G_h01_46D2, 0x18L, 0x14L, h, 0L, 0L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_8A46(h, 0L, 0L, G_h01_46D2, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    F_h00_34E0(&G_h01_4478);
    F_h00_34E0(&G_h01_44AE);
    F_h00_34E0(&G_h01_4442);
    F_h00_86A8(0x19L);
    F_h00_435E();
    F_h00_330E();
    F_h00_307C();
    G_h01_46D6 = &G_h01_14E6;
    F_h00_31AA(&G_h01_14E6);
    for (;;) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_8A46(h, 0L, 0L, G_h01_46D2, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_34E0(&G_h01_4442);
        if ((r = F_h15_1428(&x, &y)) != 0) {
            if (r == 0x25)
                goto tail;
            if (x >= G_h01_4442 && x <= G_h01_4442 + 0x30 && y >= G_h01_4444 && y <= G_h01_4444 + 0x30) {
                r = 0x23;
                goto tail;
            }
            if (x >= 0x18 && x <= 0x125 && y >= 0x14 && y <= 0x9f) {
                if (p1 == 1)
                    r = F_h15_0C12(G_h01_0666);
                else
                    r = 1;
                if (r == 1) {
                    r = G_h01_0666;
                    goto tail;
                }
                if (r == 0x24) {
                    x = xs;
                    y = ys;
                    F_h00_86A8(10L);
                    F_h00_435E();
                }
            }
        }
        if (x >= G_h01_4442 && x <= G_h01_4442 + 0x30 && y >= G_h01_4444 && y <= G_h01_4444 + 0x30) {
            F_h00_35DC(0x88, 6, "OFFICE", 1, 0xf);
        } else if (x >= 0x18 && x <= 0x125 && y >= 0x14 && y <= 0x9f) {
            G_h01_0666 = 0;
            ent = G_h01_4524;
            t1 = F_h00_08FC(x, ent->point->x, y, ent->point->y);
            for (i = 0; i < 35 && ent->point != 0; i++, ent++) {
                t2 = F_h00_08FC(x, ent->point->x, y, ent->point->y);
                if (t2 < t1) {
                    G_h01_0666 = i;
                    t1 = t2;
                }
            }
            ent = &G_h01_4524[G_h01_0666];
            k = F_h00_8044(ent->point);
            k = k << 2;
            if (G_h01_4705 == G_h01_0666)
                F_h00_35DC(0xa0 - k, 6, ent->point, 7, 0xf);
            else
                F_h00_35DC(0xa0 - k, 6, ent->point, 1, 0xf);
            *G_h01_5370 = 8;
            F_h15_08B0(ent->point->x, ent->point->y);
        }
        F_h00_09C0(0xb0, 0xaf, G_h01_46E6, 1, 9, 1);
        if (G_h01_46E1 < 10)
            F_h00_09C0(0x12, 0xb6, (long)G_h01_46E1, 7, 1, 0);
        else
            F_h00_09C0(0xe, 0xb6, (long)G_h01_46E1, 7, 1, 0);
        F_h00_307C();
        F_h00_86A8(2L);
    }
tail:
    F_h00_3AE4(&G_h01_4488, G_h01_4480, G_h01_4482);
    F_h00_3AE4(&G_h01_44BE, G_h01_44B6, G_h01_44B8);
    F_h00_3AE4(&G_h01_4452, G_h01_444A, G_h01_444C);
    F_h00_3AE4(&G_h01_43E6, G_h01_43DE, G_h01_43E0);
    F_h00_3AE4(&G_h01_441C, G_h01_4414, G_h01_4416);
    F_h00_3AE4(&G_h01_A778, G_h01_A770, G_h01_A772);
    if (G_h01_46E4 && p1)
        F_h00_3AE4(&G_h01_44F4, G_h01_44EC, G_h01_44EE);
    F_h00_3B84(h);
    F_h00_330E();
    return r;
}
