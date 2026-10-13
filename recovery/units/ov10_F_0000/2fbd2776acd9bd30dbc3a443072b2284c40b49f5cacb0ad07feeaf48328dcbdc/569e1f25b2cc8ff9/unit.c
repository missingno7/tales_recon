/* ov10_F_0000: cave-map load, 8x8 grid state machine, action dispatch. Three unused locals (c1, c2, i1) are kept: the original 134-byte frame and its slot offsets require them. */
struct Rec54 { char b[54]; };
extern char G_h01_5E5E;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern char G_h01_46E0;
extern long G_h01_46E6;
extern short G_h01_4356[64];
extern long G_h01_7998;
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
extern unsigned int G_h01_79A8;
extern short G_h01_799C;
extern char G_h01_79A2;
extern char G_h01_79A4;
extern char G_h01_79A5;
extern char G_h01_79A6;
extern char G_h01_79AA;
extern short G_h01_79AC;
extern short G_h01_79AE;
extern short G_h01_79B0;
extern short G_h01_79B2;
extern char G_h01_79B4;
extern short G_h01_79B6;
extern short G_h01_79B8;
extern short G_h01_79BE;
extern short G_h01_79C0;
extern short G_h01_79EC;
extern short G_h01_79EE;
extern short G_h01_7A22;
extern short G_h01_7A24;
extern short G_h01_7A58;
extern short G_h01_7A5A;
extern short G_h01_7452;
extern short G_h01_7454;
extern short G_h01_741C;
extern short G_h01_741E;
extern short G_h01_74F4;
extern short G_h01_74F6;
extern short G_h01_7746;
extern short G_h01_7748;
extern short G_h01_730E;
extern short G_h01_7310;
extern short G_h01_788A;
extern short G_h01_788C;
extern short G_h01_777C;
extern short G_h01_777E;
extern short G_h01_77B2;
extern short G_h01_77B4;
extern short G_h01_77E8;
extern short G_h01_77EA;
extern short G_h01_781E;
extern short G_h01_7820;
extern short G_h01_7854;
extern short G_h01_7856;
extern short G_h01_7560;
extern short G_h01_7568;
extern short G_h01_756A;
extern short G_h01_7602;
extern short G_h01_7604;
extern short G_h01_7638;
extern short G_h01_763A;
extern short G_h01_766E;
extern short G_h01_7670;
extern short G_h01_76A4;
extern short G_h01_76A6;
extern short G_h01_76DA;
extern short G_h01_76DC;
extern short G_h01_7710;
extern short G_h01_7712;
extern short G_h01_75CC;
extern short G_h01_75CE;
extern short G_h01_75D4;
extern short G_h01_75D6;
extern short G_h01_759E;
extern short G_h01_75A0;
extern short G_h01_7932;
extern short G_h01_7934;
extern short G_h01_7936;
extern short G_h01_792C;
extern short G_h01_792E;
extern short G_h01_78F6;
extern short G_h01_78F8;
extern short G_h01_7596;
extern short G_h01_7598;
extern short G_h01_72AA;
extern short G_h01_72AC;
extern short G_h01_72E0;
extern short G_h01_72E2;
extern short G_h01_7274;
extern short G_h01_7276;
extern short G_h01_7316;
extern short G_h01_7318;
extern short G_h01_734C;
extern short G_h01_734E;
extern short G_h01_7382;
extern short G_h01_7384;
extern short G_h01_73B8;
extern short G_h01_73BA;
extern short G_h01_73EE;
extern short G_h01_73F0;
extern short G_h01_74FC;
extern short G_h01_74FE;
extern short G_h01_7426;
extern short G_h01_7424;
extern short G_h01_745A;
extern short G_h01_745C;
extern short G_h01_7784;
extern short G_h01_7786;
extern short G_h01_77BA;
extern short G_h01_77BC;
extern short G_h01_77F0;
extern short G_h01_77F2;
extern short G_h01_7826;
extern short G_h01_7828;
extern short G_h01_785C;
extern short G_h01_785E;
extern short G_h01_774E;
extern short G_h01_7750;
extern short G_h01_7892;
extern short G_h01_7894;
extern short G_h01_78C8;
extern short G_h01_78CA;
extern short G_h01_78FE;
extern short G_h01_7900;
extern short G_h01_79F4;
extern short G_h01_79F6;
extern short G_h01_7A60;
extern short G_h01_7A62;
extern short G_h01_7A2A;
extern short G_h01_7A2C;
extern char G_h01_16A6[1];
extern char G_h01_1726[1];
extern char G_h01_7236[1];
extern char G_h01_726C[1];
extern char G_h01_727C[1];
extern char G_h01_72A2[1];
extern char G_h01_72B2[1];
extern char G_h01_72D8[1];
extern char G_h01_72E8[1];
extern char G_h01_731E[1];
extern char G_h01_7344[1];
extern char G_h01_7354[1];
extern char G_h01_737A[1];
extern char G_h01_738A[1];
extern char G_h01_73B0[1];
extern char G_h01_73C0[1];
extern char G_h01_73E6[1];
extern char G_h01_73F6[1];
extern char G_h01_742C[1];
extern char G_h01_7462[1];
extern char G_h01_7504[1];
extern char G_h01_7570[1];
extern char G_h01_75A6[1];
extern char G_h01_75DC[1];
extern char G_h01_7756[1];
extern char G_h01_778C[1];
extern char G_h01_77C2[1];
extern char G_h01_77F8[1];
extern char G_h01_782E[1];
extern char G_h01_7864[1];
extern char G_h01_789A[1];
extern char G_h01_78C0[1];
extern char G_h01_78D0[1];
extern char G_h01_7906[1];
extern char G_h01_793C[1];
extern char G_h01_79C6[1];
extern char G_h01_79FC[1];
extern char G_h01_7A32[1];
extern char G_h01_7A68[1];
extern char G_h01_0476[1];
extern char G_h01_04AA[1];
extern char G_h01_04DA[1];
extern char G_h01_050A[1];
extern char G_h01_053E[1];
extern char G_h01_0572[1];
extern char G_h01_059A[1];
extern char G_h01_05D6[1];
extern long G_h01_2A16;
extern long G_h01_2C26;
extern char G_h01_2C2C;
extern long F_h00_0976();
extern int F_h00_0FDE();
extern int F_h00_134C();
extern int F_h00_2816();
extern long F_h00_291E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_3C0E();
extern int F_h00_435E();
extern int F_h00_4376();
extern unsigned int F_h00_463E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_704E();
extern int F_h00_868C();
extern int F_h00_86A8();
extern long F_h00_86DC();
extern int F_h00_8A46();
extern long F_h00_8BC8();
extern int F_h10_2160();
extern int F_h10_25A2();
extern int F_h10_2634();
extern int F_h10_2B8A();
extern int F_h10_2BAC();
extern int F_h10_2BCA();
extern int F_h10_2CF4();
extern int F_h10_2FA0();
extern int F_h10_3288();

recovered(arg)
int arg;
{
    long saved_handle;
    long exp_handle;
    int i;
    int j;
    char *bitmap;
    short *cell;
    long grid_base;
    char *text;
    char c1;
    char line[80];
    int action;
    char c2;
    char kind;
    char kind2;
    char tile;
    unsigned int tick;
    unsigned int phase;
    int last;
    int dx;
    int dy;
    char flag7f;
    char flag80;
    char flag81;
    char flag82;
    int res;
    int i1;

    /* A: state reset and grid clear. */
    flag82 = 0;
    res = 0;
    G_h01_5E5E = 0;
    action = 0;
    tile = 0;
    tick = 0;
    phase = 0;
    last = 0;
    G_h01_79A6 = 0;
    flag7f = 0;
    flag80 = 0;
    saved_handle = G_h01_46DA;
    for (i = 0; i < 64; i++)
        G_h01_4356[i] = 0;

    /* B: open cave map, parse 8 rows of 8 cell words. */
    F_h00_0FDE(2);
    G_h01_46DA = F_h00_86DC("DT2:cavemaps.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    bitmap = F_h00_291E(arg, 0L);
    text = *(char **)(bitmap + 2);
    for (i = 0; i < 64; i += 8) {
        text = (char *)F_h00_0976(text, line);
        F_h00_704E(line, "%d %d %d %d %d %d %d %d",
                   &G_h01_4356[i], &G_h01_4356[i + 1], &G_h01_4356[i + 2], &G_h01_4356[i + 3],
                   &G_h01_4356[i + 4], &G_h01_4356[i + 5], &G_h01_4356[i + 6], &G_h01_4356[i + 7]);
    }
    F_h00_3C0E(bitmap);
    F_h00_868C(G_h01_46DA);

    /* C: open exp.arc, draw static panels, set panel geometry. */
    F_h00_0FDE(2);
    G_h01_46DA = F_h00_86DC("DT2:exp.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    exp_handle = G_h01_46DA;
    F_h00_291E(17, &G_h01_730E);
    G_h01_730E = 82;
    G_h01_7310 = 38;
    if (G_h01_79AA != 0) {
        F_h00_291E(18, G_h01_7344);
        F_h00_291E(19, G_h01_737A);
        F_h00_291E(20, G_h01_73E6);
        F_h00_291E(21, G_h01_73B0);
    }
    F_h00_291E(4, &G_h01_79B6);
    G_h01_79B6 = 220;
    G_h01_79B8 = 40;
    F_h00_291E(5, &G_h01_79EC);
    G_h01_79EC = 0;
    G_h01_79EE = 144;
    F_h00_291E(6, &G_h01_7A22);
    G_h01_7A22 = 240;
    G_h01_7A24 = 122;
    F_h00_291E(3, &G_h01_7A58);
    G_h01_7A58 = 40;
    G_h01_7A5A = 24;
    F_h00_291E(22, &G_h01_7452);
    G_h01_7452 = 71;
    G_h01_7454 = 141;
    F_h00_291E(23, &G_h01_741C);
    G_h01_741C = 176;
    G_h01_741E = 110;
    F_h00_291E(26, &G_h01_74F4);
    G_h01_74F4 = 141;
    G_h01_74F6 = 3;
    F_h00_291E(37, &G_h01_7746);
    G_h01_7746 = 112;
    G_h01_7748 = 137;
    F_h00_291E(38, &G_h01_777C);
    F_h00_291E(39, &G_h01_77B2);
    F_h00_291E(40, &G_h01_77E8);
    F_h00_291E(41, &G_h01_781E);
    F_h00_291E(42, &G_h01_7854);
    F_h00_291E(43, &G_h01_788A);
    G_h01_777C = G_h01_730E + 16;
    G_h01_77B2 = G_h01_730E + 28;
    G_h01_77E8 = G_h01_730E + 53;
    G_h01_781E = G_h01_730E + 99;
    G_h01_7854 = G_h01_730E + 112;
    G_h01_777E = G_h01_7310 + 61;
    G_h01_77B4 = G_h01_7310 + 39;
    G_h01_77EA = G_h01_7310 + 15;
    G_h01_7820 = G_h01_7310 + 41;
    G_h01_7856 = G_h01_7310 + 59;
    G_h01_788A = 160;
    G_h01_788C = 115;
    G_h01_7998 = 0;
    G_h01_7998 = F_h00_291E(47, G_h01_7998);
    F_h00_291E(14, G_h01_726C);
    G_h01_79AC = 14;
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(21);
    G_h01_46DA = exp_handle;
    F_h00_0FDE(2);
    F_h00_2816(G_h01_46DA);
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_34E0(&G_h01_7746);

    /* D: locate the marked start cell (bit 5) and the goal cell (bit 4). */
    grid_base = (long)(cell = G_h01_4356);
    F_h10_2160(cell);
    for (i = 0; i < 64; i++, cell++) {
        if (*cell & 0x20)
            G_h01_79A8 = i;
        else if (*cell & 0x10)
            G_h01_799E = i;
    }
    for (;;) {
        if ((G_h01_79A0 = F_h00_463E() & 63) != G_h01_799E)
            break;
    }
    cell = G_h01_4356 + G_h01_799E;
    G_h01_79B2 = 1;
    kind = 0;
    kind2 = 0;
    G_h01_79A2 = 0;
    G_h01_79A4 = 0;
    G_h01_79A5 = 0;
    switch (G_h01_46E0) {
    case 0:
        flag81 = 20;
        G_h01_79AE = 64;
        break;
    case 1:
        flag81 = 16;
        G_h01_79AE = 48;
        break;
    case 2:
        flag81 = 7;
        G_h01_79AE = 32;
        break;
    }
    G_h01_79B0 = G_h01_79AE >> 2;
    F_h00_57D2(0);
    G_h01_2C26 = 0;
    G_h01_2C2C = 0;
    F_h00_330E();
    F_h00_435E();

    /* E: main input loop. Sentinel actions (-1, -2, -3) leave the loop for section F. */
    for (;;) {
        if (G_h01_799E == G_h01_79A8)
            break;
        G_h01_799C = F_h10_2BCA(G_h01_79A8, G_h01_799E);
        if (G_h01_79B2 != 0) {
            G_h01_79A4++;
            if (G_h01_79A4 == (G_h01_79AE >> 1) && G_h01_79AC == 14) {
                F_h00_3AE4(&G_h01_727C, G_h01_7274, G_h01_7276);
                G_h01_79AC = 15;
                F_h00_0FDE(2);
                F_h00_291E(15, G_h01_72A2);
            } else if (G_h01_79A4 == (G_h01_79AE - G_h01_79B0) && G_h01_79AC == 15) {
                F_h00_3AE4(G_h01_72B2, G_h01_72AA, G_h01_72AC);
                G_h01_79AC = 16;
                F_h00_0FDE(2);
                F_h00_291E(16, G_h01_72D8);
            }
            if ((*cell & 0x40) != 0)
                G_h01_79A6 = 1;
            phase++;
            F_h00_330E();
            F_h00_0FDE(2);
            F_h00_291E(0, G_h01_46CE);
            F_h10_2FA0(cell, 1);
            if (kind == 0 || G_h01_79AA != 0)
                F_h10_2634(&G_h01_730E, 17, 0);
            if (G_h01_79A4 > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0)
                F_h00_34E0(&G_h01_788A);
            F_h00_307C();
            F_h10_2FA0(cell, 0);
            if (kind == 0 || G_h01_79AA != 0)
                F_h10_2634(&G_h01_730E, 17, 0);
            if (G_h01_79A4 > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0)
                F_h00_34E0(&G_h01_788A);
            F_h00_307C();
            G_h01_46D6 = G_h01_16A6;
            F_h00_31AA(G_h01_16A6);
            G_h01_79B2 = 0;
            if (G_h01_79AA != 0) {
                if (G_h01_79A4 > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0) {
                    F_h10_2FA0(cell, 0);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_86A8(50L);
                    G_h01_46E6 += 50;
                    F_h00_57D2(32);
                    F_h00_35DC(132, 128, "$50", 14, 0, 0);
                    F_h00_307C();
                    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                }
            } else {
                if (kind == 1) {
                    F_h00_291E(10, G_h01_7236);
                    F_h10_2CF4(3, 13, G_h01_0476, 10, cell);
                } else if (kind == 2) {
                    F_h00_291E(11, G_h01_7236);
                    F_h10_2CF4(0, 12, G_h01_04DA, 11, cell);
                } else if (kind == 3) {
                    F_h00_291E(12, G_h01_7236);
                    F_h10_2CF4(0, 13, G_h01_053E, 12, cell);
                } else if (kind == 4) {
                    F_h00_291E(13, G_h01_7236);
                    F_h10_2CF4(3, 15, G_h01_059A, 13, cell);
                }
                for (i = 0; i < 2; i++) {
                    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                }
            }
            *cell = *cell | 0x10;
            if ((*cell & 0x40) == 0x40) {
                action = -2;
                break;
            }
            if (G_h01_79A4 >= G_h01_79AE) {
                action = -1;
                break;
            }
            if (G_h01_79AA == 0) {
                F_h00_0FDE(2);
                if (*cell & 1) {
                    F_h00_291E(18, G_h01_7344);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 4) {
                    F_h00_291E(19, G_h01_737A);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 8) {
                    F_h00_291E(20, G_h01_73E6);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 2) {
                    F_h00_291E(21, G_h01_73B0);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                F_h00_57D2(36);
            }
            F_h00_435E();
        }
        action = 0;
        action = F_h00_4376();

        /* Action class from the low five bits decides the feedback draw. */
        if ((action & 31) == 1 || (action & 31) == 2) {
            if (*cell & 8) {
                F_h10_2634(&G_h01_73E6, 17, 5);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    F_h00_57D2(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 3 || (action & 31) == 4) {
            if (*cell & 2) {
                F_h10_2634(&G_h01_73B0, 17, 4);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    F_h00_57D2(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 7 || (action & 31) == 8) {
            if (*cell & 1) {
                F_h10_2634(&G_h01_7344, 17, 2);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    F_h00_57D2(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 5 || (action & 31) == 6) {
            if (*cell & 4) {
                F_h10_2634(&G_h01_737A, 17, 3);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    F_h00_57D2(70);
                    flag82 = 1;
                }
            }
        } else {
            F_h10_2634(&G_h01_730E, 17, 0);
            flag82 = 0;
            if ((F_h00_463E() & 0xff) > 230 && tile == 0) {
                tile = F_h00_463E() % 5;
                if (tile == 0)
                    F_h00_34E0(&G_h01_777C);
                else if (tile == 1)
                    F_h00_34E0(&G_h01_77B2);
                else if (tile == 2)
                    F_h00_34E0(&G_h01_77E8);
                else if (tile == 3)
                    F_h00_34E0(&G_h01_781E);
                else
                    F_h00_34E0(&G_h01_7854);
                tile = 1;
            } else {
                tile = 0;
            }
            if (tick > 14) {
                G_h01_79A4++;
                tick = 0;
                if (G_h01_79A4 == (G_h01_79AE >> 1) && G_h01_79AC == 14) {
                    F_h00_3AE4(&G_h01_727C, G_h01_7274, G_h01_7276);
                    G_h01_79AC = 15;
                    F_h00_0FDE(2);
                    F_h00_291E(15, G_h01_72A2);
                } else if (G_h01_79A4 == (G_h01_79AE - G_h01_79B0) && G_h01_79AC == 15) {
                    F_h00_3AE4(G_h01_72B2, G_h01_72AA, G_h01_72AC);
                    G_h01_79AC = 16;
                    F_h00_0FDE(2);
                    F_h00_291E(16, G_h01_72D8);
                }
                if (G_h01_79A4 >= G_h01_79AE) {
                    action = -1;
                    break;
                }
            }
        }

        flag7f = 0;
        if (phase++ > flag81) {
            if ((G_h01_799E - 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 4))
                || (G_h01_799E - 1 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 2))
                || (G_h01_799E + 1 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 1))
                || (G_h01_799E + 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 8))
                || (G_h01_799E - 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 1))
                || G_h01_79A0 == G_h01_799E) {
            if (G_h01_799E + 1 == G_h01_79A0 || G_h01_79A0 == G_h01_799E)
                G_h01_79A0 = G_h01_799E - 8;
            else if (G_h01_799E + 8 == G_h01_79A0)
                G_h01_79A0 = G_h01_799E - 1;
            G_h01_79A6 = 1;
            action = -3;
            break;
            }
            if ((unsigned int)G_h01_799C <= 6) {
                dx = F_h10_2B8A();
                dy = F_h10_2BAC();
                if (dy == 0) {
                    if (dx < 0)
                        phase = 0;
                    else if (dx > 0)
                        phase = 1;
                } else if (dy < 0) {
                    phase = 2;
                } else if (dy > 0) {
                    phase = 3;
                }
            } else {
                phase = F_h00_463E() & 3;
            }
            switch (phase) {
            case 0:
                if (G_h01_79A0 > 0 && (G_h01_79A0 & 7) != 0 && last + 1 != G_h01_79A0) {
                    if (G_h01_799E + 1 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 1) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0--;
                        flag7f = 1;
                    }
                }
                break;
            case 1:
                if (G_h01_79A0 + 1 <= 63 && (G_h01_79A0 & 7) != 7 && G_h01_79A0 + 1 != last) {
                    if (G_h01_799E == G_h01_79A0 + 1 && (G_h01_4356[G_h01_79A0] & 2) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0++;
                        flag7f = 1;
                    }
                }
                break;
            case 2:
                if (G_h01_79A0 >= 8 && last + 8 != G_h01_79A0) {
                    if (G_h01_799E + 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 8) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0 -= 8;
                        flag7f = 1;
                    }
                }
                break;
            case 3:
                if (G_h01_79A0 + 8 <= 63 && last != G_h01_79A0 + 8) {
                    if (G_h01_799E == G_h01_79A0 + 8 && (G_h01_4356[G_h01_79A0] & 4) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0 += 8;
                        flag7f = 1;
                    }
                }
                break;
            }
            phase = 0;
            if (flag7f != 0) {
                F_h00_57D2(82);
                flag7f = 0;
            }
        }
        if (tick++ > 60000)
            tick = 0;
        F_h00_307C();
        if ((action & 128) && ((action & 31) == 1 || (action & 31) == 2)) {
            if (*cell & 8) {
                F_h00_0FDE(2);
                F_h00_57D2(36);
                F_h10_25A2(cell);
                cell -= 8;
                G_h01_799E -= 8;
                kind = 3;
                G_h01_79B2 = 1;
                phase++;
                if (G_h01_79AA == 0) {
                    F_h00_0FDE(2);
                    F_h00_291E(12, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(0, 10, G_h01_0572, 12, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 5 || (action & 31) == 6)) {
            if (*cell & 4) {
                F_h00_57D2(36);
                F_h10_25A2(cell);
                cell += 8;
                G_h01_799E += 8;
                G_h01_79B2 = 1;
                kind = 2;
                phase++;
                if (G_h01_79AA == 0) {
                    F_h00_0FDE(2);
                    F_h00_291E(11, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(0, 13, G_h01_050A, 11, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 3 || (action & 31) == 4)) {
            if (*cell & 2) {
                F_h00_57D2(36);
                F_h10_25A2(cell);
                cell += 1;
                G_h01_799E += 1;
                G_h01_79B2 = 1;
                kind = 1;
                phase++;
                if (G_h01_79AA == 0) {
                    F_h00_0FDE(2);
                    F_h00_291E(10, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(1, 12, G_h01_04AA, 10, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 7 || (action & 31) == 8)) {
            if (*cell & 1) {
                F_h00_57D2(36);
                F_h10_25A2(cell);
                cell -= 1;
                G_h01_799E -= 1;
                G_h01_79B2 = 1;
                kind = 4;
                phase++;
                if (G_h01_79AA == 0) {
                    F_h00_0FDE(2);
                    F_h00_291E(13, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(2, 13, G_h01_05D6, 13, cell);
                }
            }
        }
        action = 0;
    }

    /* F: action sentinels after the loop. */
    if (action == -1) {
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        F_h10_3288();
        F_h00_3B84(G_h01_7998);
        F_h10_25A2(cell);
    } else if (action == -3) {
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        F_h00_0FDE(2);
        F_h00_291E(46, &G_h01_792C);
        F_h10_2634(&G_h01_730E, 17, 0);
        G_h01_792C = 102;
        G_h01_792E = 200 - G_h01_7932;
        F_h00_291E(29, &G_h01_7596);
        F_h10_2634(&G_h01_730E, 17, 0);
        G_h01_7596 = 76;
        G_h01_7598 = 43;
        F_h00_34E0(&G_h01_792C);
        F_h00_57D2(83);
        F_h00_307C();
        F_h00_291E(30, &G_h01_75CC);
        F_h10_2634(&G_h01_730E, 17, 0);
        G_h01_75CC = 70;
        G_h01_75CE = 43;
        F_h00_34E0(&G_h01_792C);
        F_h00_307C();
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_792C);
        F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        for (i = 0; i < 16; i++) {
            F_h00_8A46(G_h01_46CE, 64L, 5L, G_h01_46D2, 64L, 5L, 176L, 195L, 192L, 255L, 0L);
            F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + (i & 1)));
            F_h00_34E0(&G_h01_792C);
            F_h00_307C();
        }
        F_h00_3AE4(&G_h01_75DC, G_h01_75D4, G_h01_75D6);
        F_h00_3AE4(&G_h01_75A6, G_h01_759E, G_h01_75A0);
        F_h00_3AE4(&G_h01_793C, G_h01_7934, G_h01_7936);
        F_h10_25A2(cell);
        F_h00_3B84(G_h01_7998);
        F_h00_330E();
        while (G_h01_2A16 != 0)
            ;
    } else if (action == -2) {
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        F_h00_0FDE(2);
        F_h00_291E(28, &G_h01_7560);
        for (i = 0; i < 2; i++) {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_7560, 17, 6);
            F_h00_307C();
        }
        F_h00_291E(29, &G_h01_7596);
        G_h01_7596 = 76;
        G_h01_7598 = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(30, &G_h01_75CC);
        G_h01_75CC = 70;
        G_h01_75CE = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(31, &G_h01_7602);
        G_h01_7602 = 88;
        G_h01_7604 = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(32, &G_h01_7638);
        G_h01_7638 = 90;
        G_h01_763A = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(33, &G_h01_766E);
        G_h01_766E = 88;
        G_h01_7670 = 64;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(34, &G_h01_76A4);
        G_h01_76A4 = 70;
        G_h01_76A6 = 73;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_3AE4(&G_h01_7570, G_h01_7568, G_h01_756A);
        F_h00_3B84(G_h01_7998);
        F_h00_291E(35, &G_h01_76DA);
        G_h01_76DA = 61;
        G_h01_76DC = 54;
        F_h00_291E(36, &G_h01_7710);
        G_h01_7710 = 70;
        G_h01_7712 = 42;
        F_h00_57D2(0);
        for (i = 0; i < 2; i++) {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_730E, 17, 0);
            F_h00_307C();
        }
        F_h00_4EC6();
        F_h00_0FDE(2);
        F_h00_4D04(22);
        F_h00_0FDE(2);
        F_h00_2816(G_h01_46DA);
        F_h00_57D2(72);
        for (j = 0; j < 4; j++) {
            for (i = 0; i < 3; i++) {
                if (j == 0)
                    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                else
                    F_h00_8A46(G_h01_46CE, 64L, 40L, G_h01_46D2, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
                F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + i));
                F_h00_307C();
            }
            if (j == 0)
                F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            else
                F_h00_8A46(G_h01_46CE, 64L, 40L, G_h01_46D2, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
            F_h00_34E0(&G_h01_75CC);
            F_h00_307C();
        }
        for (i = 0; i < 3; i++) {
            F_h00_8A46(G_h01_46CE, 64L, 40L, G_h01_46D2, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
            F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + i));
            F_h00_307C();
        }
        F_h00_4EC6();
        F_h00_0FDE(2);
        F_h00_4D04(40);
        F_h00_0FDE(2);
        F_h00_2816(G_h01_46DA);
        F_h00_57D2(71);
        for (i = 3; i < 8; i++) {
            F_h00_8A46(G_h01_46CE, 64L, 10L, G_h01_46D2, 64L, 10L, 176L, 190L, 192L, 255L, 0L);
            F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + i));
            F_h00_307C();
            F_h00_86A8(1L);
        }
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
        for (i = 0; i < 8; i++)
            F_h00_3AE4((char *)((struct Rec54 *)&G_h01_75A6 + i), *(short *)((struct Rec54 *)&G_h01_759E + i),
                       *(short *)((struct Rec54 *)&G_h01_75A0 + i));
        while (G_h01_2A16 != 0)
            ;
    } else {
        G_h01_79A6 = 1;
        F_h10_25A2(cell);
        F_h00_0FDE(2);
        F_h00_291E(44, &G_h01_78C0);
        F_h00_291E(45, &G_h01_78F6);
        G_h01_78F6 = 96;
        G_h01_78F8 = 94;
        F_h00_330E();
        F_h00_291E(0, G_h01_46CE);
        F_h10_2FA0(cell, 0);
        F_h10_2634(&G_h01_730E, 17, 0);
        F_h00_34E0(&G_h01_78F6);
        F_h00_34E0(&G_h01_7452);
        F_h00_307C();
        G_h01_46D6 = G_h01_16A6;
        F_h00_31AA(G_h01_16A6);
        F_h10_2FA0(cell, 0);
        F_h10_2634(&G_h01_730E, 17, 0);
        F_h00_34E0(&G_h01_78F6);
        F_h00_34E0(&G_h01_7452);
        F_h00_307C();
        for (i = 0; i < 3; i++) {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_730E, 17, 0);
            F_h00_34E0(&G_h01_78F6);
            F_h00_34E0(&G_h01_7452);
            F_h00_307C();
        }
        G_h01_79A6 = 2;
        F_h00_4EC6();
        F_h00_0FDE(2);
        F_h00_4D04(24);
        F_h00_0FDE(2);
        F_h00_2816(G_h01_46DA);
        F_h00_57D2(73);
        for (i = 0; i < 10; i++) {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_78C0, 17, 0);
            F_h00_34E0(&G_h01_78F6);
            F_h00_34E0(&G_h01_7452);
            F_h00_307C();
        }
        F_h00_3AE4(&G_h01_78D0, G_h01_78C8, G_h01_78CA);
        F_h00_3AE4(&G_h01_7906, G_h01_78FE, G_h01_7900);
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 1;
        while (G_h01_2A16 != 0)
            ;
        F_h00_4EC6();
        F_h00_3B84(G_h01_7998);
    }

    /* G: teardown, restore the saved map handle, return the result word. */
    F_h00_57D2(0);
    switch (G_h01_79AC) {
    case 14:
        F_h00_3AE4(&G_h01_727C, G_h01_7274, G_h01_7276);
        break;
    case 15:
        F_h00_3AE4(&G_h01_72B2, G_h01_72AA, G_h01_72AC);
        break;
    case 16:
        F_h00_3AE4(&G_h01_72E8, G_h01_72E0, G_h01_72E2);
        break;
    }
    F_h00_3AE4(&G_h01_7462, G_h01_745A, G_h01_745C);
    F_h00_3AE4(&G_h01_742C, G_h01_7424, G_h01_7426);
    F_h00_3AE4(&G_h01_731E, G_h01_7316, G_h01_7318);
    if (G_h01_79AA != 0) {
        F_h00_3AE4(&G_h01_7354, G_h01_734C, G_h01_734E);
        F_h00_3AE4(&G_h01_738A, G_h01_7382, G_h01_7384);
        F_h00_3AE4(&G_h01_73C0, G_h01_73B8, G_h01_73BA);
        F_h00_3AE4(&G_h01_73F6, G_h01_73EE, G_h01_73F0);
    }
    F_h00_3AE4(&G_h01_7504, G_h01_74FC, G_h01_74FE);
    F_h00_3AE4(&G_h01_778C, G_h01_7784, G_h01_7786);
    F_h00_3AE4(&G_h01_77C2, G_h01_77BA, G_h01_77BC);
    F_h00_3AE4(&G_h01_77F8, G_h01_77F0, G_h01_77F2);
    F_h00_3AE4(&G_h01_782E, G_h01_7826, G_h01_7828);
    F_h00_3AE4(&G_h01_7864, G_h01_785C, G_h01_785E);
    F_h00_3AE4(&G_h01_7756, G_h01_774E, G_h01_7750);
    F_h00_3AE4(&G_h01_789A, G_h01_7892, G_h01_7894);
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved_handle;
    F_h00_2816(G_h01_46DA);
    F_h00_330E();
    F_h00_4EC6();
    if (res == 0) {
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
        F_h00_330E();
        F_h00_291E(34, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_35DC(176, 60, "Launchpad McQuack", 1, 0);
        F_h00_35DC(188, 76, "saves the day!", 1, 0);
        F_h00_307C();
        G_h01_46D6 = G_h01_1726;
        F_h00_31AA(G_h01_1726);
        if (F_h00_134C(20) != 0)
            F_h00_57D2(36);
        F_h00_4EC6();
    }
    return res;
}

extern int F_h00_57D2();

F_h10_1F90(a)
int a;
{
    if (a < 2)
        F_h00_57D2(0x51);
    else if (a < 4)
        F_h00_57D2(0x50);
    else if (a < 6)
        F_h00_57D2(0x4f);
    else
        F_h00_57D2(0x4e);
}

struct Flags {
    char pad;
    unsigned char bits;
};
extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8C10();

F_h10_1FDE(x,y,flags,active)
int x,y;
struct Flags *flags;
int active;
{
    char i,j;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
            F_h00_8C10(G_h01_46CA,(long)(x+j),(long)(y+i));
        }
    if (active) {
    *G_h01_5370=3;
    if (flags->bits&8) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x+3),(long)(y-1));
    }
    if (flags->bits&4) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x-1),(long)(y+3));
    }
    if (flags->bits&2) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x+3),(long)(y+3));
    }
    if (flags->bits&1) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x-1),(long)(y-1));
    }
    }
}

struct Cell {
    char pad;
    unsigned char bits;
};
extern char G_h01_46E0;
extern char *G_h01_5370;
extern long G_h01_46D2;
extern int G_h01_7746;
extern int G_h01_7748;
extern int G_h01_774A;
extern int G_h01_774C;
extern char G_h01_774E;
extern int F_h10_1FDE();
extern int F_h00_8A46();

F_h10_2160(p)
struct Cell *p;
{
    unsigned i,x,y;
    int shift;

    shift=3;
    i=0;
    do {
        x=((56-(i&248))>>3)+(i&7);
        y=(i>>3)+(i&7);
        if (!G_h01_46E0 || (p->bits&16)) {
            if ((((unsigned short *)(p-1))[0]&64)==64 &&
                (i&7) && (p->bits&1) ||
                (((unsigned short *)(p+1))[0]&64)==64 &&
                (i&7)!=7 && (p->bits&2) ||
                (((unsigned short *)(p-8))[0]&64)==64 &&
                i>7 && (p->bits&8) ||
                (((unsigned short *)(p+8))[0]&64)==64 &&
                i<56 && (p->bits&4))
                *G_h01_5370=12;
            else
                *G_h01_5370=3;
            F_h10_1FDE(x*4+115,y*4+139,p,1);
        }
        ++i;
        ++p;
    } while (i<64);
    F_h00_8A46(G_h01_46D2,(long)G_h01_7746,(long)G_h01_7748,
        &G_h01_774E,0L,0L,(long)(G_h01_774A<<shift),(long)G_h01_774C,
        192L,255L,0L);
}

struct BoardCell {
    char pad;
    unsigned char bits;
};

extern int F_h00_34E0();
extern int G_h01_7746;
extern char G_h01_46E0;
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A8;
extern unsigned int G_h01_79A0;

F_h10_22E6(p)
struct BoardCell *p;
{
    int unused;
    unsigned x,y;
    int shift;

    shift=3;
    F_h00_34E0(&G_h01_7746);
    if (G_h01_46E0) {
        x=((56-(G_h01_799E&248))>>3)+(G_h01_799E&7);
        y=(G_h01_799E>>3)+(G_h01_799E&7);
        if ((((unsigned short *)(p-1))[0]&64)==64 &&
            (G_h01_799E&7) && (p->bits&1) ||
            (((unsigned short *)(p+1))[0]&64)==64 &&
            (G_h01_799E&7)!=7 && (p->bits&2) ||
            (((unsigned short *)(p-8))[0]&64)==64 &&
            G_h01_799E>7 && (p->bits&8) ||
            (((unsigned short *)(p+8))[0]&64)==64 &&
            G_h01_799E<56 && (p->bits&4))
            *G_h01_5370=12;
        else
            *G_h01_5370=3;
        F_h10_1FDE(x*4+115,y*4+139,p+G_h01_799E,1);
        F_h00_8A46(G_h01_46D2,(long)G_h01_7746,(long)G_h01_7748,
            &G_h01_774E,0L,0L,(long)(G_h01_774A<<shift),(long)G_h01_774C,
            192L,255L,0L);
    }
    x=((56-(G_h01_799E&248))>>3)+(G_h01_799E&7);
    y=(G_h01_799E>>3)+(G_h01_799E&7);
    *G_h01_5370=22;
    F_h10_1FDE(x*4+115,y*4+139,p+G_h01_799E,1);
    if (G_h01_46E0!=2) {
        x=((56-(G_h01_79A8&248))>>3)+(G_h01_79A8&7);
        y=(G_h01_79A8>>3)+(G_h01_79A8&7);
        *G_h01_5370=14;
        F_h10_1FDE(x*4+115,y*4+139,p+G_h01_79A8,1);
    }
    x=((56-(G_h01_79A0&248))>>3)+(G_h01_79A0&7);
    y=(G_h01_79A0>>3)+(G_h01_79A0&7);
    *G_h01_5370=8;
    F_h10_1FDE(x*4+115,y*4+139,p+G_h01_79A0,0);
}

/* Direct reconstruction candidate for ov10_F_25A2. */
struct Flags { char pad; char bits; };
extern char G_h01_79AA;
extern char G_h01_79B4;
extern int G_h01_734C;
extern int G_h01_734E;
extern char G_h01_7354;
extern int G_h01_7382;
extern int G_h01_7384;
extern char G_h01_738A;
extern int G_h01_73B8;
extern int G_h01_73BA;
extern char G_h01_73C0;
extern int G_h01_73EE;
extern int G_h01_73F0;
extern char G_h01_73F6;
extern int F_h00_3AE4();

F_h10_25A2(flags)
struct Flags *flags;
{
    if (!G_h01_79AA && G_h01_79B4) {
        G_h01_79B4 = 0;
        if (flags->bits & 1) F_h00_3AE4(&G_h01_7354, G_h01_734C, G_h01_734E);
        if (flags->bits & 4) F_h00_3AE4(&G_h01_738A, G_h01_7382, G_h01_7384);
        if (flags->bits & 2) F_h00_3AE4(&G_h01_73C0, G_h01_73B8, G_h01_73BA);
        if (flags->bits & 8) F_h00_3AE4(&G_h01_73F6, G_h01_73EE, G_h01_73F0);
    }
}

extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_30F0();
extern int F_h00_34E0();
extern unsigned int F_h00_463E();
extern int F_h00_8A46();
extern int F_h00_8A68();
extern int F_h10_22E6();
extern short G_h01_060A[1];
extern short G_h01_0626[1];
extern short G_h01_0636[1];
extern short G_h01_0646[1];
extern short G_h01_0656[1];
extern char G_h01_4356[1];
extern char *G_h01_5392;
extern short G_h01_726C;
extern short G_h01_726E;
extern short G_h01_72A2;
extern short G_h01_72A4;
extern char G_h01_72D6;
extern short G_h01_72D8;
extern short G_h01_72DA;
extern char G_h01_730C;
extern char G_h01_741C[1];
extern char G_h01_7452[1];
extern char G_h01_74F4[1];
extern long G_h01_7998;
extern char G_h01_79A2;
extern char G_h01_79A3;
extern char G_h01_79A4;
extern char G_h01_79A6;
extern char G_h01_72A0;
extern short G_h01_79AE;
extern short G_h01_79B0;
extern short G_h01_79B2;

void F_h10_2634(obj, kind, frame)
short *obj;
int kind, frame;
{
    short *shape;
    int frame_index, x, y, width, height;

    if (kind == 17) {
        obj[0] = 0x52;
        obj[1] = 0x26;
        if (G_h01_79A6 == 2) {
            obj[0] = 0x53;
            obj[1] = 0x2f;
        }
        if (frame == 6) {
            obj[0] = 0x55;
            obj[1] = 0x30;
        }
        shape = G_h01_060A;
        x = obj[0] - 0x1e;
        y = obj[1] - 0x1e;
        width = 0xb4;
        height = 0xa0;
    } else if (kind == 10) {
        shape = G_h01_0626;
        x = obj[0] - 0x20;
        y = obj[1] - 0x26;
        width = 0xb4;
        height = 0x9e;
    } else if (kind == 11) {
        shape = G_h01_0636;
        x = obj[0];
        y = obj[1] - 0x26;
        width = 0xb4;
        height = 0xb4;
    } else if (kind == 13) {
        shape = G_h01_0656;
        x = obj[0];
        y = obj[1] - 0x28;
        width = 0xb4;
        height = 0xaa;
    } else {
        shape = G_h01_0646;
        x = obj[0] - 0x28;
        y = obj[1] - 0x12;
        width = 0xbe;
        height = 0x9e;
    }

    if (x < 0)
        x = 0;
    else if (x > 0x140)
        x = 0x140;
    if (y < 0)
        y = 0;
    else if (y > 0xc8)
        y = 0xc8;

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);

    frame_index = frame;
    F_h00_8A68(G_h01_7998, 0L, 0L, G_h01_46CA,
               (long)(shape[frame_index * 2] + obj[0] - 0x48),
               (long)(shape[frame_index * 2 + 1] + obj[1] - 0x40),
               0x90L, 0x87L, 0xeeL);

    if (G_h01_79B2 == 0) {
        switch (G_h01_79A2) {
        case 0:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x832;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xb20;
            break;
        case 1:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x842;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xb30;
            break;
        case 2:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x943;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xa30;
            break;
        case 3:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x843;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xa20;
            break;
        }
        F_h00_30F0();
    }

    if ((kind == 17 && frame_index != 5 && frame_index != 6) || kind == 11)
        F_h00_34E0(obj);

    if (G_h01_79A4 < (G_h01_79AE >> 1)) {
        G_h01_72A0 = G_h01_79A2;
        G_h01_726C = shape[frame_index * 2] + obj[0] - 0x0f;
        G_h01_726E = shape[frame_index * 2 + 1] + obj[1] - 0x40;
        if (G_h01_79A6 == 2) {
            G_h01_726C = shape[frame_index * 2] + 0x43;
            G_h01_726E = shape[frame_index * 2 + 1] - 0x1a;
        }
        F_h00_34E0(&G_h01_726C);
    } else if (G_h01_79A4 < G_h01_79AE - G_h01_79B0) {
        G_h01_72D6 = G_h01_79A2;
        G_h01_72A2 = shape[frame_index * 2] + obj[0] - 0x0b;
        G_h01_72A4 = shape[frame_index * 2 + 1] + obj[1] - 0x33;
        if (G_h01_79A6 == 2) {
            G_h01_72A2 = shape[frame_index * 2] + 0x47;
            G_h01_72A4 = shape[frame_index * 2 + 1] - 0x0d;
        }
        F_h00_34E0(&G_h01_72A2);
    } else {
        G_h01_730C = G_h01_79A2;
        G_h01_72D8 = shape[frame_index * 2] + obj[0] - 6;
        G_h01_72DA = shape[frame_index * 2 + 1] + obj[1] - 0x2a;
        if (G_h01_79A6 == 2) {
            G_h01_72D8 = shape[frame_index * 2] + 0x4c;
            G_h01_72DA = shape[frame_index * 2 + 1] - 4;
        }
        F_h00_34E0(&G_h01_72D8);
    }

    if (kind != 11 && (kind != 17 || (kind == 17 && (frame_index == 5 || frame_index == 6))))
        F_h00_34E0(obj);
    F_h00_34E0(G_h01_74F4);
    F_h00_34E0(G_h01_7452);
    F_h00_34E0(G_h01_741C);

    if (kind == 17 && G_h01_79A6 == 0)
        F_h10_22E6(G_h01_4356);

    G_h01_79A2 = F_h00_463E() & 3;
    if (G_h01_79A3 == G_h01_79A2) {
        G_h01_79A2++;
        if (G_h01_79A2 > 3)
            G_h01_79A2 = 0;
    }
    G_h01_79A3 = G_h01_79A2;
}
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
F_h10_2B8A() { int d; d=(G_h01_799E&7)-(G_h01_79A0&7); return d; }

extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
F_h10_2BAC() { int d; d=(G_h01_799E>>3)-(G_h01_79A0>>3); return d; }

#define ABS(x) ((x) < 0 ? -(x) : (x))
F_h10_2BCA(a,b) int a,b;
{
    int rows, columns;
    rows = ABS((a >> 3) - (b >> 3));
    columns = ABS((a & 7) - (b & 7));
    return rows + columns;
}

/* Direct recovery candidate for ov10_F_2CF4 (v2: inverted tail dispatch). */
struct Flags { char pad; char bits; };
extern char G_h01_79AA;
extern char G_h01_726A;
extern int G_h01_7236;
extern int G_h01_7238;
extern int G_h01_723E;
extern int G_h01_7240;
extern char G_h01_7246;
extern short G_h01_730E;
extern char G_h01_788A;
extern int G_h01_7962;
extern int G_h01_7964;
extern char G_h01_7972;
extern int G_h01_796A;
extern int G_h01_796C;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46E6;
extern short G_h01_0476;
extern short G_h01_04AA;
extern short G_h01_04DA;
extern short G_h01_050A;
extern short G_h01_053E;
extern short G_h01_0572;
extern short G_h01_059A;
extern short G_h01_05D6;
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3AE4();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h10_2634();

F_h10_2CF4(start, count, pairs, kind, flags)
int start, count;
short *pairs;
int kind;
struct Flags *flags;
{
    int i, frame;
    char draw;

    if (G_h01_79AA)
        return;
    draw = 0;
    frame = start;
    F_h00_0FDE(2);
    if (pairs == &G_h01_0476 || pairs == &G_h01_05D6) {
        draw = 1;
        F_h00_291E(24, &G_h01_7962);
        G_h01_7962 = 0;
        G_h01_7964 = 0;
    } else if (pairs == &G_h01_04DA || pairs == &G_h01_0572) {
        draw = 1;
        F_h00_291E(25, &G_h01_7962);
        G_h01_7962 = 240;
        G_h01_7964 = 0;
    }
    for (i = 0; i < count; i++, frame++) {
        if (frame > 3)
            frame = 0;
        G_h01_726A = frame;
        G_h01_7236 = pairs[2 * i];
        G_h01_7238 = pairs[2 * i + 1];
        F_h10_2634(&G_h01_7236, kind, frame);
        if (pairs == &G_h01_0476 || pairs == &G_h01_04DA ||
            pairs == &G_h01_053E || pairs == &G_h01_059A) {
            if (!(flags->bits & 0x10) && !(flags->bits & 0x40) && i < 8)
                F_h00_34E0(&G_h01_788A);
        }
        if (draw)
            F_h00_34E0(&G_h01_7962);
        F_h00_307C();
    }
    if (draw)
        F_h00_3AE4(&G_h01_7972, G_h01_796A, G_h01_796C);
    if (pairs != &G_h01_04AA && pairs != &G_h01_050A &&
        pairs != &G_h01_0572 && pairs != &G_h01_05D6) {
        if (!(flags->bits & 0x10) && !(flags->bits & 0x40)) {
            G_h01_46E6 += 50;
            F_h00_57D2(32);
        }
        for (i = 0; i < 4; i++) {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
                0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_730E, 17, 0);
            if (!(flags->bits & 0x10) && !(flags->bits & 0x40))
                F_h00_35DC(132, 128, "$50", 14, 0, 0);
            F_h00_307C();
        }
    } else {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
    }
    F_h00_3AE4(&G_h01_7246, G_h01_723E, G_h01_7240);
}

extern long G_h01_46CE;
extern long G_h01_46D2;
extern unsigned short G_h01_7194;
extern unsigned short G_h01_7196;
extern unsigned short G_h01_719C;
extern unsigned short G_h01_719E;
extern unsigned short G_h01_71A4;
extern unsigned short G_h01_71CA;
extern unsigned short G_h01_71CC;
extern unsigned short G_h01_71D2;
extern unsigned short G_h01_71D4;
extern unsigned short G_h01_71DA;
extern unsigned short G_h01_7200;
extern unsigned short G_h01_7202;
extern unsigned short G_h01_7208;
extern unsigned short G_h01_720A;
extern unsigned short G_h01_7210;
extern unsigned short G_h01_7488;
extern unsigned short G_h01_748A;
extern unsigned short G_h01_7490;
extern unsigned short G_h01_7492;
extern unsigned short G_h01_7498;
extern unsigned short G_h01_74BE;
extern unsigned short G_h01_74C0;
extern unsigned short G_h01_74C6;
extern unsigned short G_h01_74C8;
extern unsigned short G_h01_74CE;
extern unsigned short G_h01_799C;
extern unsigned short G_h01_799E;
extern int F_h00_8A46();
extern int F_h10_320C();
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_34E0();
extern int F_h00_3AE4();
extern int F_h00_57D2();
extern int F_h10_1F90();

void F_h10_2FA0(p, flag)
char *p;
char flag;
{
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h10_320C(p);
    F_h00_0FDE(2);

    if ((*((unsigned short *)p) & 0x40) == 0x40) {
        F_h00_291E(2, &G_h01_74BE);
        G_h01_74BE = 0x1a;
        G_h01_74C0 = 0x5c;
        F_h00_34E0(&G_h01_74BE);
        F_h00_3AE4(&G_h01_74CE, G_h01_74C6, G_h01_74C8);
    }

    if (G_h01_799C < 2) {
        F_h00_291E(9, &G_h01_7200);
        G_h01_7200 = 0x68;
        G_h01_7202 = 0x8;
        F_h00_34E0(&G_h01_7200);
        F_h00_3AE4(&G_h01_7210, G_h01_7208, G_h01_720A);
    } else if (G_h01_799C < 4) {
        F_h00_291E(8, &G_h01_71CA);
        G_h01_71CA = 0x68;
        G_h01_71CC = 0x8;
        F_h00_34E0(&G_h01_71CA);
        F_h00_3AE4(&G_h01_71DA, G_h01_71D2, G_h01_71D4);
    } else if (G_h01_799C < 6) {
        F_h00_291E(7, &G_h01_7194);
        G_h01_7194 = 0x68;
        G_h01_7196 = 0x41;
        F_h00_34E0(&G_h01_7194);
        F_h00_3AE4(&G_h01_71A4, G_h01_719C, G_h01_719E);
    }

    if (((*((unsigned short *)(p - 2)) & 0x40) == 0x40 &&
         ((G_h01_799E & 7) != 0) && ((p[1] & 1) != 0)) ||
        ((*((unsigned short *)(p + 2)) & 0x40) == 0x40 &&
         ((G_h01_799E & 7) != 7) && (p[1] & 2)) ||
        ((*((unsigned short *)(p - 0x10)) & 0x40) == 0x40 &&
         (G_h01_799E > 7) && (p[1] & 8)) ||
        ((*((unsigned short *)(p + 0x10)) & 0x40) == 0x40 &&
         (G_h01_799E < 0x38) && (p[1] & 4))) {
        F_h00_291E(1, &G_h01_7488);
        G_h01_7488 = 0x57;
        G_h01_748A = 0xe;
        F_h00_34E0(&G_h01_7488);
        if (flag != 0)
            F_h00_57D2(0x4d);
        F_h00_3AE4(&G_h01_7498, G_h01_7490, G_h01_7492);
    } else if (flag != 0) {
        F_h10_1F90(G_h01_799C);
    }
    F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
}










/* Direct reconstruction candidate for ov10_F_320C. */
union Flags {
    int value;
    struct { char reserved; char bits; } bytes;
};
extern int F_h00_0FDE();
extern int F_h00_34E0();
extern char G_h01_79B6;
extern char G_h01_79EC;
extern char G_h01_7A22;
extern char G_h01_7A58;

F_h10_320C(flags)
union Flags *flags;
{
    if ((flags->value & 15) == 15)
        return;
    F_h00_0FDE(2);
    if (!(flags->bytes.bits & 8)) F_h00_34E0(&G_h01_79B6);
    if (!(flags->bytes.bits & 4)) F_h00_34E0(&G_h01_79EC);
    if (!(flags->bytes.bits & 2)) F_h00_34E0(&G_h01_7A22);
    if (!(flags->bytes.bits & 1)) F_h00_34E0(&G_h01_7A58);
}

extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern short G_h01_752A;
extern short G_h01_752C;
extern short G_h01_7532;
extern short G_h01_7534;
extern short G_h01_753A;
extern char G_h01_755E;
extern short G_h01_730E;
extern char G_h01_730C;
extern short G_h01_72D8;
extern char G_h01_74F4[1];
extern char G_h01_7452[1];
extern char G_h01_741C[1];

extern void F_h10_2634();
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_34E0();
extern int F_h00_0FDE();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_291E();
extern int F_h00_86A8();
extern int F_h00_57D2();
extern int F_h00_8BC8();
extern int F_h00_330E();
extern int F_h00_3AE4();

void F_h10_3288()
{
    int i;

    for (i = 0; i < 4; i++) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h10_2634(&G_h01_730E, 17, 0);
        F_h00_307C();
    }
    for (i = 0; i < 6; i++) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_730E);
        if ((i & 1) && i < 4)
            G_h01_730C = 3;
        else if (i < 4)
            G_h01_730C = 4;
        else
            G_h01_730C = 4;
        F_h00_34E0(&G_h01_72D8);
        F_h00_34E0(G_h01_74F4);
        F_h00_34E0(G_h01_7452);
        F_h00_34E0(G_h01_741C);
        F_h00_307C();
    }
    F_h00_0FDE(2);
    F_h00_4EC6();
    F_h00_4D04(7);
    F_h00_291E(0x1b, &G_h01_752A);
    G_h01_752A = 0x62;
    G_h01_752C = 0x37;
    G_h01_755E = 4;
    F_h00_34E0(&G_h01_752A);
    F_h00_307C();
    F_h00_86A8(0x32L);
    G_h01_755E = 1;
    F_h00_34E0(&G_h01_752A);
    F_h00_307C();
    F_h00_86A8(5L);
    for (i = 0; i < 6; i++) {
        if (i == 4) {
            F_h00_57D2(0x4b);
        } else {
            F_h00_8BC8(G_h01_46CA, 0L);
            G_h01_755E = i;
            F_h00_34E0(&G_h01_752A);
            F_h00_307C();
            if (i == 1) {
                F_h00_86A8(5L);
            } else {
                if (i & 1)
                    F_h00_86A8(0x32L);
                else
                    F_h00_86A8(0x19L);
                if (i > 1 && i < 6) {
                    G_h01_755E = 1;
                    F_h00_34E0(&G_h01_752A);
                    F_h00_307C();
                    F_h00_86A8(3L);
                }
            }
        }
    }
    G_h01_755E = 0;
    F_h00_34E0(&G_h01_752A);
    F_h00_307C();
    F_h00_86A8(0x96L);
    F_h00_330E();
    F_h00_4EC6();
    F_h00_3AE4(&G_h01_753A, G_h01_7532, G_h01_7534);
}

