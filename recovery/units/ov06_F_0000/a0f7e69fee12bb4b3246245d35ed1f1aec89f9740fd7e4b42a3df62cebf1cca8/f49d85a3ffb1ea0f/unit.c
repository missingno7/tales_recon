struct Rec {
    int f0;
    int f2;
    int f4;
    int f6;
    char rest[46];
};

extern int F_h00_57D2();
extern int F_h00_4EC6();
extern int F_h00_330E();
extern int F_h00_8BC8();
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern int F_h00_291E();
extern int F_h00_435E();
extern int F_h00_134C();
extern int F_h00_3AE4();
extern int F_h00_868C();
extern int F_h06_063A();

extern long G_h01_2A16;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46DA;
extern int G_h01_2F1E;
extern int G_h01_2F20;
extern int G_h01_2F54;
extern int G_h01_2F56;
extern int G_h01_2F8A;
extern int G_h01_2F8C;
extern int G_h01_2FC0;
extern int G_h01_2FC2;
extern int G_h01_2FF6;
extern int G_h01_2FF8;
extern int G_h01_302C;
extern int G_h01_3062;
extern int G_h01_3064;
extern int G_h01_3068;
extern int G_h01_3098;
extern int G_h01_309A;
extern int G_h01_309E;
extern struct Rec G_h01_30CE[6];
extern int G_h01_30D6;
extern int G_h01_30D8;
extern int G_h01_30DE;
extern int G_h01_3104;
extern int G_h01_310C;
extern int G_h01_310E;
extern int G_h01_3114;
extern int G_h01_313A;
extern int G_h01_3142;
extern int G_h01_3144;
extern int G_h01_314A;
extern int G_h01_3170;
extern int G_h01_3178;
extern int G_h01_317A;
extern int G_h01_3180;
extern int G_h01_31A6;
extern int G_h01_31AE;
extern int G_h01_31B0;
extern int G_h01_31B6;
extern int G_h01_31DC;
extern int G_h01_31E4;
extern int G_h01_31E6;
extern int G_h01_31EC;
extern int G_h01_3212;
extern int G_h01_3214;
extern int G_h01_3216;
extern int G_h01_3218;
extern int G_h01_321A;
extern int G_h01_321C;
extern int G_h01_321E;
extern int G_h01_3220;
extern int G_h01_3222;
extern int G_h01_3224;
extern int G_h01_3226;
extern int G_h01_3228;

recovered()
{
    int t0;
    long saved;
    int t1;

    F_h00_57D2(33);
    while (G_h01_2A16)
        ;
    F_h00_4EC6();
    F_h00_330E();
    F_h00_8BC8(G_h01_46CA, 0L);
    saved = G_h01_46DA;
    F_h00_0FDE(2);
    G_h01_46DA = F_h00_86DC("DT2:mac.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    F_h00_291E(0, &G_h01_2F1E);
    F_h00_291E(1, &G_h01_2F54);
    F_h00_291E(2, &G_h01_2F8A);
    F_h00_291E(3, &G_h01_2FC0);
    F_h00_291E(4, &G_h01_2FF6);
    F_h00_291E(5, G_h01_46CE);
    F_h00_291E(6, &G_h01_302C);
    F_h00_291E(7, &G_h01_3062);
    F_h00_291E(8, &G_h01_3098);
    F_h00_291E(9, G_h01_30CE);
    F_h00_291E(10, &G_h01_3104);
    F_h00_291E(11, &G_h01_313A);
    F_h00_291E(12, &G_h01_3170);
    F_h00_291E(13, &G_h01_31A6);
    F_h00_291E(14, &G_h01_31DC);
    F_h00_57D2(0);
    F_h00_435E();
    G_h01_2F1E = 40;
    G_h01_2F20 = 79;
    G_h01_2F54 = 40;
    G_h01_2F56 = 98;
    G_h01_2F8A = 40;
    G_h01_2F8C = 116;
    G_h01_2FC0 = 48;
    G_h01_2FC2 = 79;
    G_h01_2FF6 = 40;
    G_h01_2FF8 = 98;
    G_h01_3212 = 0;
    G_h01_3216 = 79;
    G_h01_3214 = 212;
    G_h01_3218 = 79;
    G_h01_321A = 8;
    G_h01_321E = 44;
    G_h01_321C = 208;
    G_h01_3220 = 116;
    G_h01_3222 = 0;
    G_h01_3226 = 62;
    G_h01_3224 = 208;
    G_h01_3228 = 97;
    G_h01_3062 = 2;
    G_h01_3064 = 200 - G_h01_3068 + 1;
    G_h01_3098 = 238;
    G_h01_309A = 200 - G_h01_309E + 3;
    F_h06_063A();
    F_h00_435E();
    F_h00_134C(40);
    F_h00_3AE4(&G_h01_30DE, G_h01_30D6, G_h01_30D8);
    F_h00_3AE4(&G_h01_3114, G_h01_310C, G_h01_310E);
    F_h00_3AE4(&G_h01_314A, G_h01_3142, G_h01_3144);
    F_h00_3AE4(&G_h01_3180, G_h01_3178, G_h01_317A);
    F_h00_3AE4(&G_h01_31B6, G_h01_31AE, G_h01_31B0);
    F_h00_3AE4(&G_h01_31EC, G_h01_31E4, G_h01_31E6);
    F_h00_868C(G_h01_46DA);
    F_h00_0FDE(1);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

/* Decimal counter animation; names describe observed behavior only. */
extern int F_h00_35DC();
extern int F_h00_307C();
extern int F_h00_86A8();

F_h06_028C(x1, x2, value1, value2, style, color)
int x1;
int x2;
long value1;
long value2;
char style;
char color;
{
    char digits1[11];
    char digits2[11];
    int count1;
    int count2;
    int origin1;
    int origin2;

    origin1 = x1;
    origin2 = x2;
    digits1[10] = 0;
    digits2[10] = 0;
    count1 = 10;
    count2 = 10;

    do {
        if (value1 > 0L || count1 == 10) {
            digits1[--count1] = (value1 % 10L) + 48;
            x1 = origin1 - ((10 - count1) << 3);
        }
        if (value2 > 0L || count2 == 10) {
            digits2[--count2] = (value2 % 10L) + 48;
            x2 = origin2 - ((10 - count2) << 3);
        }
        F_h00_35DC(x1,191,&digits1[count1],style,color);
        F_h00_35DC(x2,179,&digits2[count2],style,color);
        F_h00_307C();
        F_h00_86A8(10L);
        value1 = value1 / 10L;
        value2 = value2 / 10L;
    } while (value1 > 0L || value2 > 0L);

    F_h00_35DC(x1,191,&digits1[count1],style,color);
    F_h00_35DC(x2,179,&digits2[count2],style,color);
    F_h00_307C();
}

struct Rec {
    int f0;
    int f2;
    int f4;
    int f6;
    char rest[46];
};

extern int F_h00_34E0();
extern int G_h01_302C;
extern int G_h01_302E;
extern char G_h01_3096;
extern char G_h01_30CC;
extern struct Rec G_h01_30CE[6];
extern int G_h01_322A;
extern int G_h01_322C;
extern int G_h01_322E;
extern int G_h01_3230;

F_h06_042A(a1, a2, a3, a4, pv, c, n1, n2)
int a1, a2, a3, a4;
long pv;
char c;
int n1, n2;
{
    int i;
    int spare;
    struct Rec *p;
    struct Rec *q;
    int shift;

    shift = 3;
    p = G_h01_30CE;
    q = G_h01_30CE;
    F_h00_34E0(pv);
    G_h01_302C = a1;
    G_h01_302E = a2;
    for (i = 0; i <= n1; i++) {
        p->f0 = ((0x70 - (p->f4 << shift)) >> 1) + G_h01_302C;
        p->f2 = G_h01_302E - p->f6;
        if (i == 0)
            p->f0 = p->f0 + 8;
        else if (i == 1)
            p->f2 = p->f2 - 14;
        else if (i == 3) {
            p->f0 = p->f0 - 8;
            p->f2 = p->f2 - 13;
        } else if (i == 4)
            p->f2 = p->f2 - 27;
        F_h00_34E0(p);
        G_h01_322A = p->f0;
        G_h01_322C = p->f2;
        p++;
    }
    if (n1 > -1)
        p--;
    F_h00_34E0(&G_h01_302C);
    G_h01_302C = a3;
    G_h01_302E = a4;
    for (i = 0; i <= n2; i++) {
        q->f0 = ((0x70 - (q->f4 << shift)) >> 1) + G_h01_302C;
        q->f2 = G_h01_302E - q->f6;
        if (i == 0)
            q->f0 = q->f0 + 8;
        else if (i == 1)
            q->f2 = q->f2 - 14;
        else if (i == 3) {
            q->f0 = q->f0 - 8;
            q->f2 = q->f2 - 13;
        } else if (i == 4)
            q->f2 = q->f2 - 27;
        F_h00_34E0(q);
        G_h01_322E = q->f0;
        G_h01_3230 = q->f2;
        q++;
    }
    F_h00_34E0(&G_h01_302C);
    G_h01_3096 = c;
    G_h01_30CC = c;
}

struct Rec {
    int f0;
    int f2;
    int f4;
    int f6;
    char rest[46];
};

extern int F_h00_0FDE();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3AE4();
extern int F_h00_435E();
extern int F_h00_4376();
extern unsigned int F_h00_463E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_86A8();
extern int F_h00_8A46();
extern int F_h06_028C();
extern int F_h06_042A();

extern char G_h01_1566;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern char G_h01_30CC;
extern char G_h01_3096;
extern struct Rec G_h01_30CE[6];
extern int G_h01_322A;
extern int G_h01_322C;
extern int G_h01_322E;
extern int G_h01_3230;
extern int G_h01_2F1E;
extern int G_h01_2F26;
extern int G_h01_2F28;
extern int G_h01_2F2E;
extern int G_h01_2F54;
extern int G_h01_2F5C;
extern int G_h01_2F5E;
extern int G_h01_2F64;
extern int G_h01_2F8A;
extern int G_h01_2F92;
extern int G_h01_2F94;
extern int G_h01_2F9A;
extern int G_h01_2FC0;
extern int G_h01_2FC8;
extern int G_h01_2FCA;
extern int G_h01_2FD0;
extern int G_h01_2FF6;
extern int G_h01_2FFE;
extern int G_h01_3000;
extern int G_h01_3006;
extern int G_h01_3034;
extern int G_h01_3036;
extern int G_h01_303C;
extern int G_h01_3062;
extern int G_h01_306A;
extern int G_h01_306C;
extern int G_h01_3072;
extern int G_h01_3098;
extern int G_h01_30A0;
extern int G_h01_30A2;
extern int G_h01_30A8;
extern int G_h01_31DC;
extern int G_h01_31DE;
extern char G_h01_3210;
extern int G_h01_3212;
extern int G_h01_3214;
extern int G_h01_3216;
extern int G_h01_3218;
extern int G_h01_321A;
extern int G_h01_321C;
extern int G_h01_321E;
extern int G_h01_3220;
extern int G_h01_3222;
extern int G_h01_3224;
extern int G_h01_3226;
extern int G_h01_3228;

F_h06_063A()
{
    struct Rec *p4;
    struct Rec *p8;
    int wa;
    int wc;
    int ce;
    int kd;
    int y12;
    int x14;
    int m16;
    int r18;
    int d1;
    int i;
    int st;
    int o20;
    int o22;
    int l24;
    int l26;
    int l28;
    int r2a;
    int f2c;
    int sh;

    f2c = 1;
    sh = 3;
    ce = 0;
    kd = 0;
    st = 1;
    l26 = 0;
    l24 = 4;
    o20 = 1;
    o22 = 1;
    x14 = (G_h01_46F2 / 10000L > 4L) ? 4 : G_h01_46F2 / 10000L;
    y12 = (G_h01_46EE / 10000L > 4L) ? 4 : G_h01_46EE / 10000L;
    if (G_h01_46F2 == 0L)
        x14 = -1;
    if (G_h01_46EE == 0L)
        y12 = -1;
    d1 = x14 - y12;
    if (d1 < -2)
        r18 = 0;
    else if (d1 < 0)
        r18 = 1;
    else if (d1 == 0)
        r18 = 2;
    else if (d1 < 3)
        r18 = 3;
    else
        r18 = 4;
    m16 = 2;
    l28 = r18 + 14;
    r2a = l28;
    if (x14 == -1 && y12 == -1)
        l28 = 0;
    i = 0;
    for (; i <= l28; i++) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch (m16) {
        case 0:
            F_h06_042A(G_h01_321A, G_h01_321E, G_h01_321C, G_h01_3220, &G_h01_2F1E, 1, x14, y12);
            break;
        case 1:
            F_h06_042A(G_h01_3222, G_h01_3226, G_h01_3224, G_h01_3228, &G_h01_2F54, 1, x14, y12);
            break;
        case 2:
            F_h06_042A(G_h01_3212, G_h01_3216, G_h01_3214, G_h01_3218, &G_h01_2F8A, 2, x14, y12);
            break;
        case 3:
            F_h06_042A(G_h01_3222, G_h01_3228, G_h01_3224, G_h01_3226, &G_h01_2FF6, 3, x14, y12);
            break;
        case 4:
            F_h06_042A(G_h01_321A, G_h01_3220, G_h01_321C, G_h01_321E, &G_h01_2FC0, 3, x14, y12);
            break;
        default:
            break;
        }
        F_h00_34E0(&G_h01_3062);
        F_h00_34E0(&G_h01_3098);
        F_h00_35DC(106, 179, "$$$$$$$$$$", 1, 4);
        F_h00_35DC(106, 191, "$$$$$$$$$$", 1, 4);
        if (f2c) {
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1566;
            F_h00_31AA(&G_h01_1566);
            f2c = 0;
        } else {
            F_h00_307C();
        }
        if (i < l28) {
            if (i > r2a / 3 && r18 > 0 && r18 < 4 && m16 > 0 && m16 < 4 && o22) {
                o22 = 0;
                l24 = 3;
                l26 = 1;
            }
            m16 = m16 + st;
            if (m16 > l24) {
                m16 = l24 - 1;
                st = -1;
                F_h00_57D2(67);
            } else if (m16 < l26) {
                m16 = l26 + 1;
                st = 1;
                F_h00_57D2(68);
            }
        } else if (i == l28 && o20) {
            i = l28 - 1;
            o20 = 0;
        }
        if (i > r2a / 3 && i <= 2 * (r2a / 3))
            ;
        else
            (i > 2 * (r2a / 3));
    }
    F_h00_35DC(106, 179, "          ", 1, 12);
    F_h00_35DC(106, 191, "          ", 1, 12);
    F_h00_307C();
    F_h00_35DC(106, 179, "          ", 1, 12);
    F_h00_35DC(106, 191, "          ", 1, 12);
    F_h00_307C();
    F_h06_028C(186, 186, G_h01_46F2, G_h01_46EE, 1, 0);
    G_h01_30CC = m16;
    G_h01_3096 = m16;
    F_h00_34E0(&G_h01_3098);
    F_h00_34E0(&G_h01_3062);
    F_h00_307C();
    if (G_h01_3096 == 4) {
        i = 0;
        do {
            G_h01_3096 = 4;
            G_h01_30CC = 5;
            F_h00_34E0(&G_h01_3098);
            F_h00_34E0(&G_h01_3062);
            F_h00_307C();
            G_h01_3096 = 5;
            G_h01_30CC = 5;
            F_h00_34E0(&G_h01_3098);
            F_h00_34E0(&G_h01_3062);
            F_h00_307C();
            i++;
        } while (i < 7);
    }
    F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_307C();
    F_h00_435E();
    F_h00_3AE4(&G_h01_2F2E, G_h01_2F26, G_h01_2F28);
    F_h00_3AE4(&G_h01_2F64, G_h01_2F5C, G_h01_2F5E);
    F_h00_3AE4(&G_h01_2F9A, G_h01_2F92, G_h01_2F94);
    F_h00_3AE4(&G_h01_2FD0, G_h01_2FC8, G_h01_2FCA);
    F_h00_3AE4(&G_h01_3006, G_h01_2FFE, G_h01_3000);
    F_h00_3AE4(&G_h01_303C, G_h01_3034, G_h01_3036);
    F_h00_3AE4(&G_h01_3072, G_h01_306A, G_h01_306C);
    F_h00_3AE4(&G_h01_30A8, G_h01_30A0, G_h01_30A2);
    F_h00_4EC6();
    F_h00_0FDE(2);
    i = F_h00_463E() % 5;
    if (G_h01_46EE > G_h01_46F2) {
        switch (i) {
        case 0:
        case 1:
            F_h00_4D04(26);
            break;
        case 2:
        case 3:
            F_h00_4D04(31);
            break;
        case 4:
        case 5:
            F_h00_4D04(32);
            break;
        }
    } else {
        switch (i) {
        case 0:
            F_h00_4D04(29);
            break;
        case 1:
            F_h00_4D04(33);
            break;
        case 2:
            F_h00_4D04(35);
            break;
        case 3:
            F_h00_4D04(36);
            break;
        case 4:
            F_h00_4D04(37);
            break;
        case 5:
            F_h00_4D04(38);
            break;
        }
    }
    F_h00_57D2(119);
    F_h00_86A8(300L);
    F_h00_4EC6();
    p4 = &G_h01_30CE[x14];
    p8 = &G_h01_30CE[y12];
    for (;;) {
        if (F_h00_4376() & 0x80) {
            F_h00_57D2(36);
            break;
        }
        if (ce > 4) {
            kd = 0;
            ce = 0;
        }
        if (F_h00_463E() % 100 > 50 || ce != 0) {
            if (ce == 0) {
                F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                F_h00_307C();
                F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                F_h00_307C();
                if ((F_h00_463E() & 1) && x14 >= 0) {
                    kd = 1;
                    wc = p4->f6;
                    wa = p4->f4 << sh;
                    wc = F_h00_463E() % wc;
                    if (wc < (p4->f6 >> 1)) {
                        wa = (p4->f4 << sh) >> 1;
                        wa = wa - 5;
                    } else {
                        wa = F_h00_463E() % wa;
                    }
                    if (wa < 14)
                        wa = 14;
                    else if (wa > (p4->f4 << sh) - 16)
                        wa = (p4->f4 << sh) - 16;
                } else if (y12 >= 0) {
                    kd = 2;
                    wc = p8->f6;
                    wa = p8->f4 << 3;
                    wc = F_h00_463E() % wc;
                    if (wc < (p8->f6 >> 1)) {
                        wa = (p8->f4 << sh) >> 1;
                        wa = wa - 5;
                    } else {
                        wa = F_h00_463E() % wa;
                    }
                    if (wa < 14)
                        wa = 14;
                    else if (wa > (p8->f4 << sh) - 16)
                        wa = (p8->f4 << sh) - 16;
                }
            }
            if (kd == 1 && x14 >= 0) {
                G_h01_31DC = G_h01_322A + wa;
                G_h01_31DE = G_h01_322C + wc;
                G_h01_3210 = ce++;
                if (G_h01_31DC < 0)
                    G_h01_31DC = 0;
                F_h00_8A46(G_h01_46CE, (long)(unsigned int)(G_h01_31DC & 0xfff8), (long)G_h01_31DE, G_h01_46D2,
                           (long)(unsigned int)(G_h01_31DC & 0xfff8), (long)G_h01_31DE, 0x20L, 0x12L, 0xc0L, 0xffL, 0L);
                F_h00_34E0(&G_h01_31DC);
            } else if (kd == 2 && y12 >= 0) {
                G_h01_31DC = G_h01_322E + wa;
                G_h01_31DE = G_h01_3230 + wc;
                G_h01_3210 = ce++;
                if (G_h01_31DC < 0)
                    G_h01_31DC = 0;
                F_h00_8A46(G_h01_46CE, (long)(unsigned int)(G_h01_31DC & 0xfff8), (long)G_h01_31DE, G_h01_46D2,
                           (long)(unsigned int)(G_h01_31DC & 0xfff8), (long)G_h01_31DE, 0x20L, 0x12L, 0xc0L, 0xffL, 0L);
                F_h00_34E0(&G_h01_31DC);
            }
            F_h00_307C();
            F_h00_86A8(5L);
        } else {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h00_307C();
            F_h00_86A8(50L);
        }
    }
    F_h00_435E();
}

