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

recovered()
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
