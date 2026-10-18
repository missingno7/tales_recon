/* Map overlay (ov15), in original address order. Readability grouping only;
 * no claim of historical source filenames or original object/TU boundaries.
 * Conflicting Point/PointRef and scalar extern views stay function-local.
 * Overlay-call prototypes are local to avoid unused pinned-linker proxies.
 */

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
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
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44B0;
extern int G_h01_447A;
extern int G_h01_43D8;
extern int G_h01_440E;
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
extern char G_h01_5E5E;
extern char G_h01_46E5;
extern char G_h01_451B;
extern int G_h01_451A;
extern int G_h01_451C;
extern int G_h01_451E;
extern int G_h01_4520;
extern int G_h01_4522;

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
extern int F_h00_7522();
extern int F_h00_330E();
extern int F_h00_86A8();
extern int F_h00_307C();
extern int F_h00_31AA();
extern long F_h00_08FC();
extern int F_h00_8044();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_8C10();
extern long F_h00_86DC();
extern long F_h00_0976();
extern int F_h00_4376();
extern int F_h00_3C0E();
extern int F_h00_868C();

/* Select a map destination, with location details or the office return. */
recovered(p1, flag)
int p1;
char *flag;
{
    extern int F_h13_0942();
    extern int F_h04_1D32();
    extern int F_h04_27FE();
    extern int F_h15_1428();
    extern int F_h15_0C12();
    extern int F_h15_08B0();

    struct Point {
        char pad[32];
        int x;
        int y;
    };
    struct PointRef {
        struct Point *point;
        char reserved[8];
    };
    extern struct PointRef G_h01_4524[36];
    extern int G_h01_44AE;
    extern int G_h01_4478;
    extern int G_h01_43D6;
    extern int G_h01_440C;
    extern int G_h01_44E4;

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
                break;
            if (x >= G_h01_4442 && x <= G_h01_4442 + 0x30 && y >= G_h01_4444 && y <= G_h01_4444 + 0x30) {
                r = 0x23;
                break;
            }
            if (x >= 0x18 && x <= 0x125 && y >= 0x14 && y <= 0x9f) {
                if (p1 == 1)
                    r = F_h15_0C12(G_h01_0666);
                else
                    r = 1;
                if (r == 1) {
                    r = G_h01_0666;
                    break;
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

/* Map overlay (ov15), in original address order. Readability grouping only;
 * no claim of historical source filenames or original object/TU boundaries.
 * Conflicting Point/PointRef and scalar extern views stay function-local.
 * Overlay-call prototypes are local to avoid unused pinned-linker proxies.
 */

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
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
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44B0;
extern int G_h01_447A;
extern int G_h01_43D8;
extern int G_h01_440E;
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
extern char G_h01_5E5E;
extern char G_h01_46E5;
extern char G_h01_451B;
extern int G_h01_451A;
extern int G_h01_451C;
extern int G_h01_451E;
extern int G_h01_4520;
extern int G_h01_4522;

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
extern int F_h00_7522();
extern int F_h00_330E();
extern int F_h00_86A8();
extern int F_h00_307C();
extern int F_h00_31AA();
extern long F_h00_08FC();
extern int F_h00_8044();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_8C10();
extern long F_h00_86DC();
extern long F_h00_0976();
extern int F_h00_4376();
extern int F_h00_3C0E();
extern int F_h00_868C();

/* F_h00_8AA8 a filled map cursor marker and its outline. */
F_h15_08B0(x,y)
int x,y;
{
    char i,j;
    int x0,y0;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
            F_h00_8C10(G_h01_46CA,(long)(x+j),(long)(y+i));
        }
    x0=x-1;
    y0=y-1;
    *G_h01_5370=0;
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x0,(long)y0);
    F_h00_8AA8(G_h01_46CA,(long)(x0+4),(long)y0);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x0,(long)(y0+1));
    F_h00_8AA8(G_h01_46CA,(long)x0,(long)(y0+4));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x0+4),(long)(y0+1));
    F_h00_8AA8(G_h01_46CA,(long)(x0+4),(long)(y0+4));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x0,(long)(y0+4));
    F_h00_8AA8(G_h01_46CA,(long)(x0+4),(long)(y0+4));
}

/* Map overlay (ov15), in original address order. Readability grouping only;
 * no claim of historical source filenames or original object/TU boundaries.
 * Conflicting Point/PointRef and scalar extern views stay function-local.
 * Overlay-call prototypes are local to avoid unused pinned-linker proxies.
 */

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
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
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44B0;
extern int G_h01_447A;
extern int G_h01_43D8;
extern int G_h01_440E;
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
extern char G_h01_5E5E;
extern char G_h01_46E5;
extern char G_h01_451B;
extern int G_h01_451A;
extern int G_h01_451C;
extern int G_h01_451E;
extern int G_h01_4520;
extern int G_h01_4522;

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
extern int F_h00_7522();
extern int F_h00_330E();
extern int F_h00_86A8();
extern int F_h00_307C();
extern int F_h00_31AA();
extern long F_h00_08FC();
extern int F_h00_8044();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_8C10();
extern long F_h00_86DC();
extern long F_h00_0976();
extern int F_h00_4376();
extern int F_h00_3C0E();
extern int F_h00_868C();

/* Outline a map option rectangle. */
F_h15_0A80(p,width,height)
int *p,width,height;
{
    int x,y;

    x=p[0]-1;
    y=p[1]-1;
    *G_h01_5370=1;
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x,(long)y);
    F_h00_8AA8(G_h01_46CA,(long)x,(long)(y+height+1));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x+width+1),(long)y);
    F_h00_8AA8(G_h01_46CA,(long)(x+width+1),(long)(y+height+1));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x,(long)y);
    F_h00_8AA8(G_h01_46CA,(long)(x+width+1),(long)y);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x,(long)(y+height+1));
    F_h00_8AA8(G_h01_46CA,(long)(x+width+1),(long)(y+height+1));
}

/* Map overlay (ov15), in original address order. Readability grouping only;
 * no claim of historical source filenames or original object/TU boundaries.
 * Conflicting Point/PointRef and scalar extern views stay function-local.
 * Overlay-call prototypes are local to avoid unused pinned-linker proxies.
 */

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
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
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44B0;
extern int G_h01_447A;
extern int G_h01_43D8;
extern int G_h01_440E;
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
extern char G_h01_5E5E;
extern char G_h01_46E5;
extern char G_h01_451B;
extern int G_h01_451A;
extern int G_h01_451C;
extern int G_h01_451E;
extern int G_h01_4520;
extern int G_h01_4522;

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
extern int F_h00_7522();
extern int F_h00_330E();
extern int F_h00_86A8();
extern int F_h00_307C();
extern int F_h00_31AA();
extern long F_h00_08FC();
extern int F_h00_8044();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_8C10();
extern long F_h00_86DC();
extern long F_h00_0976();
extern int F_h00_4376();
extern int F_h00_3C0E();
extern int F_h00_868C();

/* Show location and treasure details and choose the travel method. */
F_h15_0C12(n)
int n;
{
    extern int F_h03_154E();
    extern int F_h15_0A80();

    struct Point {
        char pad[30];
        int selected;
    };
    struct PointRef {
        struct Point *point;
        char reserved[8];
    };
    extern char G_h01_43D6;
    extern char G_h01_4478;
    extern char G_h01_44AE;
    extern char G_h01_440C;
    extern char G_h01_44E4;
    extern struct PointRef G_h01_4524[36];


    struct PointRef *p;
    int i, w8, y, x, e;
    char f;
    int g;
    long q, s, t, u1, u2;
    char buf[81];
    long r1, r2, r3, r4;
    int st, k;

    st = 0;
    G_h01_5E5E = 1;
    i = 0;
    do {
        buf[i] = 0;
        i++;
    } while (i <= 80);
    t = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loc.arc", 1005L);
    u1 = G_h01_46DA;
    F_h00_2816(G_h01_46DA);
    p = &G_h01_4524[n];
    q = 0;
    q = F_h00_291E(p->point->selected, q);
    r1 = ((struct Object *)q)->name;
    r1 = F_h00_0976(r1, buf);
    r1 = F_h00_0976(r1, buf);
    r3 = r1;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loot.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    u2 = G_h01_46DA;
    p = &G_h01_4524[n];
    s = 0;
    s = F_h00_291E((*(struct Pair **)p->reserved)->first, s);
    r2 = ((struct Object *)s)->name;
    r2 = F_h00_0976(r2, buf);
    r4 = r2;
    w8 = F_h00_8044(p->point);
    w8 <<= 2;
    f = F_h03_154E(G_h01_46E3, n);
    F_h00_435E();
    i = 0;
    do {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_34E0(&G_h01_43D6);
        F_h00_34E0(&G_h01_440C);
        if (G_h01_46E4)
            F_h00_34E0(&G_h01_44E4);
        F_h00_35DC(160 - w8, 6, p->point, 7, 15);
        r1 = r3;
        r1 = F_h00_0976(r1, buf);
        y = 22;
        F_h00_35DC(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        F_h00_35DC(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        F_h00_35DC(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        F_h00_35DC(32, y, buf, 1, 0);
        if (n != 0) {
            r2 = r4;
            y += 16;
            F_h00_35DC(32, y, "TREASURE: ", 1, 0);
            r2 = F_h00_0976(r2, buf);
            if (F_h00_8044(buf) < 24)
                x = 112;
            else {
                x = 32;
                y += 8;
            }
            F_h00_35DC(x, y, buf, 1, 0);
            y += 16;
            F_h00_35DC(32, y, "TREASURE DESCRIPTION: ", 1, 0);
            r2 = F_h00_0976(r2, buf);
            y += 8;
            F_h00_35DC(32, y, buf, 1, 0);
            r2 = F_h00_0976(r2, buf);
            y += 8;
            F_h00_35DC(32, y, buf, 1, 0);
            y += 16;
            F_h00_35DC(32, y, "TREASURE VALUE: ", 1, 0);
            if (p->reserved[6] || p->reserved[7])
                F_h00_09C0(160, y, 0L, 1, 0, 0L);
            else
                F_h00_09C0(160, y, (long)(*(struct Pair **)p->reserved)->second, 1, 0, 0L);
        }
        y += 16;
        F_h00_35DC(32, y, "TRAVEL TIME:   day", 1, 0);
        if (f != 1)
            F_h00_35DC(176, y, "s", 1, 0);
        F_h00_09C0(136, y, (long)f, 1, 0, 0L);
        F_h00_09C0(176, 175, G_h01_46E6, 1, 9, 1);
        if (G_h01_46E1 < 10)
            F_h00_09C0(18, 182, (long)G_h01_46E1, 7, 1, 0);
        else
            F_h00_09C0(14, 182, (long)G_h01_46E1, 7, 1, 0);
        F_h15_0A80(&G_h01_43D6, 52, 27);
        if (i == 0) {
            F_h00_330E();
            F_h00_307C();
            G_h01_46D6 = &G_h01_14E6;
            F_h00_31AA(&G_h01_14E6);
        } else
            F_h00_307C();
        i++;
    } while (i < 2);
    for (;;) {
        F_h00_435E();
        F_h00_8A46(G_h01_46CE, 0L, 0xa8L, G_h01_46D2, 0L, 0xa8L, 0x140L, 0x20L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_34E0(&G_h01_43D6);
        F_h00_34E0(&G_h01_440C);
        if (G_h01_46E4)
            F_h00_34E0(&G_h01_44E4);
        e = 0;
        e = F_h00_4376();
        k = (e & 0x80) ? 1 : 0;
        if (k == 0) {
            e &= 0x3f;
            if (e == 3) {
                if (st == 2)
                    st = 0;
                else if (st == 1 && !G_h01_46E4)
                    st = 0;
                else
                    st++;
                F_h00_57D2(36);
                F_h00_86A8(5L);
            } else if (e == 7) {
                if (st == 0) {
                    if (G_h01_46E4)
                        st = 2;
                    else
                        st = 1;
                } else
                    st--;
                F_h00_57D2(36);
                F_h00_86A8(5L);
            }
        }
        switch (st) {
        case 0:
            F_h15_0A80(&G_h01_43D6, 52, 27);
            e = 36;
            break;
        case 1:
            G_h01_46E5 = 0;
            F_h15_0A80(&G_h01_440C, 32, 18);
            e = 1;
            break;
        case 2:
            G_h01_46E5 = 1;
            F_h15_0A80(&G_h01_44E4, 37, 27);
            e = 1;
            break;
        }
        F_h00_09C0(176, 175, G_h01_46E6, 1, 9, 1);
        if (G_h01_46E1 < 10)
            F_h00_09C0(18, 182, (long)G_h01_46E1, 7, 1, 0);
        else
            F_h00_09C0(14, 182, (long)G_h01_46E1, 7, 1, 0);
        F_h00_307C();
        if (k != 0)
            break;
        F_h00_86A8(1L);
    }
    F_h00_3C0E(s);
    F_h00_868C(u2);
    F_h00_3C0E(q);
    F_h00_868C(u1);
    G_h01_46DA = t;
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_435E();
    F_h00_86A8(5L);
    return e;
}

/* Map overlay (ov15), in original address order. Readability grouping only;
 * no claim of historical source filenames or original object/TU boundaries.
 * Conflicting Point/PointRef and scalar extern views stay function-local.
 * Overlay-call prototypes are local to avoid unused pinned-linker proxies.
 */

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
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
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44B0;
extern int G_h01_447A;
extern int G_h01_43D8;
extern int G_h01_440E;
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
extern char G_h01_5E5E;
extern char G_h01_46E5;
extern char G_h01_451B;
extern int G_h01_451A;
extern int G_h01_451C;
extern int G_h01_451E;
extern int G_h01_4520;
extern int G_h01_4522;

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
extern int F_h00_7522();
extern int F_h00_330E();
extern int F_h00_86A8();
extern int F_h00_307C();
extern int F_h00_31AA();
extern long F_h00_08FC();
extern int F_h00_8044();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_8C10();
extern long F_h00_86DC();
extern long F_h00_0976();
extern int F_h00_4376();
extern int F_h00_3C0E();
extern int F_h00_868C();

/* F_h00_8B4C and clamp the map cursor using directional input and hold acceleration. */
int F_h15_1428(px, py)
int *px, *py;
{
    G_h01_5E5E = 0;
    G_h01_451A = F_h00_4376();
    if (G_h01_451A & 0x80)
        return 1;
    switch (G_h01_451A & 0x3f) {
    case 1:
        (*py)--;
        G_h01_4522 = -1;
        G_h01_4520 = 0;
        break;
    case 2:
        (*py)--;
        *px += 2;
        G_h01_4522 = -1;
        G_h01_4520 = 1;
        break;
    case 3:
        (*px)++;
        G_h01_4520 = 1;
        G_h01_4522 = 0;
        break;
    case 4:
        (*py)++;
        *px += 2;
        G_h01_4522 = 1;
        G_h01_4520 = 1;
        break;
    case 5:
        (*py)++;
        G_h01_4522 = 1;
        G_h01_4520 = 0;
        break;
    case 6:
        (*py)++;
        *px -= 2;
        G_h01_4522 = 1;
        G_h01_4520 = -1;
        break;
    case 7:
        (*px)--;
        G_h01_4520 = -1;
        G_h01_4522 = 0;
        break;
    case 8:
        (*py)--;
        *px -= 2;
        G_h01_4520 = -1;
        G_h01_4522 = -1;
        break;
    case 0:
    default:
        G_h01_451C = 0;
        G_h01_451A = 0;
        G_h01_4522 = 0;
        G_h01_4520 = 0;
        G_h01_451E = 0;
        break;
    }
    if ((G_h01_451A & 0x3f) != 0 && G_h01_451C < 0x100) {
        if (G_h01_451C != 0) {
            switch (G_h01_451A & 0x3f) {
            case 2:
            case 4:
                G_h01_4520++;
                break;
            case 6:
            case 8:
                G_h01_4520--;
                break;
            }
        }
        G_h01_451C++;
    }
    if (G_h01_451C == 0) {
        G_h01_451C = 1;
        G_h01_451E = 1;
    }
    *px = *px + (G_h01_451C - 1) * G_h01_4520;
    *py = *py + (G_h01_451C - 1) * G_h01_4522;
    if (G_h01_451E) {
        G_h01_451C = 0;
        G_h01_451E = 0;
    }
    if (*px < 0x20)
        *px = 0x20;
    else if (*px > 0x11d)
        *px = 0x11d;
    if (*py < 0x1c)
        *py = 0x1c;
    else if (*py > 0x97)
        *py = 0x97;
    G_h01_A768.first = *px - 8;
    G_h01_A768.second = *py - 8;
    F_h00_34E0(&G_h01_A768);
    F_h00_435E();
    G_h01_5E5E = 1;
    return 0;
}

