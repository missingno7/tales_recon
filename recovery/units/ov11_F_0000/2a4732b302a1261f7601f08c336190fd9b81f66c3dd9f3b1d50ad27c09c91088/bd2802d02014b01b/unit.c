/* Plain structured transcription of ov11_F_0000 (worker haiku-fn-ov11_F_0000). */
struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };

extern int G_h01_12FE;
extern long G_h01_2C26;
extern char G_h01_2C2C;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern int G_h01_7A94;
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern int G_h01_8A42;
extern struct Record G_h01_8A66[1];
extern int G_h01_8B1C[41][4];
extern short G_h01_940C[1];
extern int G_h01_94AC;
extern int G_h01_94AE;
extern int G_h01_94B8;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94E6;
extern long G_h01_9FA6;
extern char G_h01_16E6[1];

extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_435E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_868C();
extern int F_h00_86A8();
extern int F_h00_8A46();
extern int F_h00_8BC8();

recovered(arg)
int arg;
{
    int i;
    int aux;
    int j;
    int lim;
    struct Record *p;
    int flag;
    char scratch[200];

    flag = 1;
    G_h01_7A94 = arg;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h11_15C8(1);
    F_h11_2A3A();
    F_h11_4EC6();
    F_h11_69A4();
    F_h11_3A24();
    F_h11_21F8();
    F_h11_68B0();
    F_h11_6FFE();
    F_h11_14BA(1);
    G_h01_2C26 = 0;
    G_h01_2C2C = 0;
    F_h00_330E();
    G_h01_12FE = 0;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xC8L, 0xC0L, 0xFFL, 0L);
    F_h11_62B4(1);
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(8);
    F_h00_57D2(0x5C);
    G_h01_940C[G_h01_8B1C[G_h01_94BA][G_h01_94BC]] = 0;
    G_h01_94B8 = 0;
    F_h00_435E();

    while (G_h01_12FE == 0) {
        if (G_h01_8A3C == 0) {
            F_h11_13DC();
        }
        G_h01_94E6 = 0;
        F_h11_063A();
        F_h11_0BB6();
        if (G_h01_12FE != 0) continue;
        if (G_h01_94AE == 7) {
            F_h00_57D2(0);
            F_h00_86A8(0x32L);
            F_h00_330E();
            if (G_h01_94AC < 3) {
                G_h01_8A3C = 3;
                flag = 1;
                F_h11_49CE();
                F_h11_15C8(0);
                F_h11_14BA(0);
                F_h11_2A3A();
                F_h11_62B4(0);
                F_h11_3A24();
                F_h11_21F8();
                F_h00_86A8(0x64L);
                G_h01_94B8 = 0;
                F_h00_57D2(0x5C);
            } else {
                break;
            }
        }
        F_h11_0558();
        if (G_h01_8A42) {
            G_h01_8A3C = 3;
        }
        j = G_h01_8A3E / 104;
        lim = (G_h01_8A42 ? 4 : 3) + j;

        for (i = j; i < lim; i++) {
            p = &G_h01_8A66[i];
            if (p->ignored) {
                F_h11_5D14(p->ignored);
            }
            if (p->value1) {
                F_h11_51C0(p->value1);
            }
            if (p->value2) {
                F_h11_6CFE(p->value2);
                if (p->value3) {
                    F_h11_6CFE(p->value3);
                }
            }
            if (p->value5) {
                F_h11_2EEA(p->value5);
            }
            if (p->value5) {
                F_h11_3532(p->value5);
            }
            if (p->value4) {
                F_h11_6486(p->value4);
                F_h11_6582(p->value4);
            }
            if (p->value6) {
                F_h11_70DC(p->value6);
            }
        }

        F_h11_3D9A();
        F_h11_2272();
        F_h11_0B4C();
        F_h11_0D8E();
        if (G_h01_8A3C > 1) {
            F_h11_4848();
        }
        if (G_h01_8A3C > 0) {
            F_h11_487E(G_h01_8A3E, 0, 0x140, G_h01_8A3C == 1);
            G_h01_8A3C--;
        } else {
            F_h11_4790();
        }

        for (i = j; i < lim; i++) {
            p = &G_h01_8A66[i];
            if (p->ignored) {
                F_h11_5C1A(p->ignored);
            }
            if (p->value5) {
                F_h11_2DBA(p->value5);
            }
        }

        F_h11_3B92();

        for (i = j; i < lim; i++) {
            p = &G_h01_8A66[i];
            if (p->value1) {
                F_h11_519C(p->value1);
            }
            if (p->value5) {
                F_h11_36F8(p->value5);
                F_h11_37E4(p->value5);
            }
            if (p->value2) {
                F_h11_6C3A(p->value2);
                if (p->value3) {
                    F_h11_6C3A(p->value3);
                }
            }
            if (p->value4 && G_h01_94AE == 45) {
                F_h11_645E(p->value4);
            }
            if (p->value6) {
                F_h11_706C(p->value6);
            }
        }

        F_h11_1372();
        F_h11_23F4();
        F_h11_27CC();
        if (flag) {
            F_h00_330E();
            F_h00_307C();
            G_h01_46D6 = G_h01_16E6;
            F_h00_31AA(G_h01_16E6);
            flag = 0;
            F_h00_435E();
        } else {
            F_h00_307C();
        }
    }

    F_h11_049C();
    F_h11_4A92();
    F_h00_330E();
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = G_h01_9FA6;
    F_h00_2816(G_h01_46DA);
    F_h00_57D2(0);
    F_h00_4EC6();
    return G_h01_12FE;
}

/* Direct reconstruction candidate for ov11_F_049C. */
extern long G_h01_9F4E;
extern long G_h01_9F52;
extern long G_h01_9F56;
extern long G_h01_9F5E;
extern long G_h01_9F62;
extern long G_h01_9F66;
extern long G_h01_9F6A;
extern long G_h01_9F6E;
extern long G_h01_9F76;
extern long G_h01_9F7E;
extern long G_h01_9F82;
extern long G_h01_9F8A;
extern long G_h01_9F8E;
extern long G_h01_9F92;
extern long G_h01_9F96;
extern long G_h01_9F9A;
extern long G_h01_9F9E;
extern long G_h01_9FA2;
extern int F_h00_3BD2();

F_h11_049C()
{
    F_h00_3BD2(G_h01_9F8E);
    F_h00_3BD2(G_h01_9F4E);
    F_h00_3BD2(G_h01_9F52);
    F_h00_3BD2(G_h01_9F56);
    F_h00_3BD2(G_h01_9F5E);
    F_h00_3BD2(G_h01_9F62);
    F_h00_3BD2(G_h01_9F66);
    F_h00_3BD2(G_h01_9F6A);
    F_h00_3BD2(G_h01_9F82);
    F_h00_3BD2(G_h01_9F7E);
    F_h00_3BD2(G_h01_9F6E);
    F_h00_3BD2(G_h01_9F76);
    F_h00_3BD2(G_h01_9F8A);
    F_h00_3BD2(G_h01_9F92);
    F_h00_3BD2(G_h01_9F96);
    F_h00_3BD2(G_h01_9F9A);
    F_h00_3BD2(G_h01_9F9E);
    F_h00_3BD2(G_h01_9FA2);
}

/* Direct reconstruction candidate for ov11_F_0558. */
extern int G_h01_8A42;
extern int G_h01_8A44;
extern int G_h01_8A48;
extern int G_h01_8A3E;
extern int G_h01_8A4A;
extern int G_h01_94BE;
extern int G_h01_94AE;
extern int G_h01_1300[16];

F_h11_0558()
{
    if (G_h01_8A42) {
        if (G_h01_8A48 == 1) {
            G_h01_8A3E += 8;
            if (G_h01_8A3E >= G_h01_8A4A) {
                G_h01_8A3E = G_h01_8A4A;
                G_h01_8A42 = 0;
                G_h01_8A44 = 1;
            }
        } else {
            G_h01_8A3E -= 8;
            if (G_h01_8A3E <= G_h01_8A4A) {
                G_h01_8A3E = G_h01_8A4A;
                G_h01_8A42 = 0;
                G_h01_8A44 = 1;
            }
        }
    } else if (G_h01_94BE >= G_h01_8A3E + 240 && G_h01_8A3E < 856) {
        G_h01_8A42 = 1;
        G_h01_8A4A = G_h01_1300[G_h01_94BE / 104 - 1];
        G_h01_8A48 = 1;
    } else if (G_h01_94BE < G_h01_8A3E + 72 && G_h01_94AE != 8 && G_h01_94AE != 6 && G_h01_8A3E > 0) {
        G_h01_8A42 = 1;
        G_h01_8A4A = G_h01_1300[G_h01_94BE / 104 - 1];
        G_h01_8A48 = 0;
    }
}

struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_8B1C[41][4];
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_945C[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94B8;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D6;
extern int G_h01_94D8;
extern int G_h01_7A90;
extern int G_h01_34D8[16];
extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h11_4B0C();
extern int F_h11_5A12();
extern int F_h11_5A62();
extern int F_h11_5AB0();
extern int F_h11_5EC0();
extern int F_h11_3F90();
extern int F_h11_6F78();

void F_h11_063A()
{
    unsigned int key;
    int found;
    int animated;
    int old_state;
    int old_direction;
    struct ClusterRecord *record;

    animated = 0;
    old_state = G_h01_94AE;
    old_direction = G_h01_94B0;
    record = &G_h01_8BEC[G_h01_94D6];
    key = F_h00_4376();
    G_h01_7A90 = key;

    if (key & 0x80)
        key |= 0x80;
    if (G_h01_34D8[7] > 0) {
        --G_h01_34D8[7];
        return;
    }

    if (G_h01_94AE == 5) {
        switch (key) {
        case 3:
            G_h01_94AE = 1;
            if (G_h01_94B0 == 0)
                G_h01_94B0 = 1;
            if ((8 >> G_h01_94B0) + G_h01_94BE + 20 >
                F_h11_5A12(0, G_h01_94BA)) {
                if (G_h01_94B4) {
                    G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                    F_h11_5EC0(G_h01_94D6);
                } else if (!G_h01_94B6 &&
                           !G_h01_8B1C[G_h01_94BA + 1][G_h01_94BC]) {
                    if (F_h11_5AB0(1, 3, &found) ||
                        (G_h01_94BC == 2 &&
                         F_h11_3F90((8 >> G_h01_94B0) +
                                    G_h01_94BE + 16) > 0))
                        G_h01_94AE = 4;
                }
            }
            break;

        case 7:
            if (G_h01_94BE - 16 <= 0) {
                G_h01_94AE = 5;
                break;
            } else {
                G_h01_94AE = 1;
                if (G_h01_94B0 == 1)
                    G_h01_94B0 = 0;
                if ((8 >> G_h01_94B0) + G_h01_94BE - 18 <
                    F_h11_5A62(0, G_h01_94BA)) {
                    if (G_h01_94B4 &&
                        G_h01_8B1C[G_h01_94BA + 1][((int *)record)[1]]) {
                        G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                        F_h11_5EC0(G_h01_94D6);
                    } else if (!G_h01_94B6 &&
                               !G_h01_8B1C[G_h01_94BA - 1][G_h01_94BC]) {
                        if (F_h11_5AB0(0, 3, &found) ||
                            (G_h01_94BC == 2 &&
                             F_h11_3F90((8 >> G_h01_94B0) +
                                        G_h01_94BE - 16) > 0))
                            G_h01_94AE = 4;
                    }
                }
            }
            break;

        case 128:
            G_h01_94AE = 18;
            break;

        case 1:
            if (G_h01_94B4 && G_h01_94B0 == 1) {
                G_h01_94AE = 3;
            } else if (F_h11_5AB0(2, 2, &found)) {
                if (G_h01_94B6) {
                    G_h01_94B6 = 0;
                    G_h01_94C0 = 0x82;
                    G_h01_94BC = (G_h01_94C0 - 16) >> 5;
                    G_h01_94AE = 12;
                } else
                    G_h01_94AE = 20;
            } else {
                if (G_h01_945C[G_h01_94BA]) {
                    if (G_h01_94B6) {
                        G_h01_94AE = 19;
                    } else if (G_h01_94B0 == 1 &&
                               G_h01_945C[G_h01_94BA + 1]) {
                        G_h01_94AE = 17;
                    } else if (G_h01_94B0 == 0 &&
                               G_h01_945C[G_h01_94BA - 1]) {
                        G_h01_94AE = 16;
                    } else {
                        G_h01_94AE = 19;
                    }
                } else {
                    G_h01_94AE = 19;
                }
            }
            break;

        case 5:
            if (G_h01_94B6)
                G_h01_94AE = 10;
            else if (((G_h01_94C0 + 14) >> 5) >= 2) {
                if (G_h01_94B4) {
                    G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                    F_h11_5EC0(G_h01_94D6);
                }
                G_h01_94AE = 13;
            } else
                G_h01_94AE = 21;
            break;

        default:
            ++G_h01_94B8;
            break;
        }
    } else if (G_h01_94AE == 8) {
        G_h01_34D8[7] = 2;
        switch (key) {
        case 5:
            ++G_h01_94BC;
            G_h01_94C0 = G_h01_94BC * 32 + 16;
            G_h01_94D8 = 0;
            if (G_h01_94C0 + 16 > 0x70)
                G_h01_94AE = 2;
            else
                G_h01_94AE = 5;
            break;

        case 3:
            if (F_h11_6F78(G_h01_94D8 + 1,
                           (8 >> G_h01_94B0) + G_h01_94BE,
                           G_h01_94C0 + 16, 0x100)) {
                ++G_h01_94D8;
                animated = 1;
            } else {
                ++G_h01_94BC;
                G_h01_94C0 = G_h01_94BC * 32 + 16;
                if (G_h01_94C0 + 16 > 0x70)
                    G_h01_94AE = 2;
                else
                    G_h01_94AE = 5;
                G_h01_94D8 = 0;
            }
            break;

        case 7:
            if (F_h11_6F78(G_h01_94D8 - 1,
                           (8 >> G_h01_94B0) + G_h01_94BE,
                           G_h01_94C0 + 16, 0x100)) {
                --G_h01_94D8;
                animated = 1;
            } else {
                ++G_h01_94BC;
                G_h01_94C0 = G_h01_94BC * 32 + 16;
                G_h01_94D8 = 0;
                if (G_h01_94C0 + 16 > 0x70)
                    G_h01_94AE = 2;
                else
                    G_h01_94AE = 5;
            }
            break;

        default:
            G_h01_34D8[7] = 0;
            break;
        }
    }

    if (!animated &&
        (G_h01_94AE != old_state || G_h01_94B0 != old_direction))
        F_h11_4B0C(G_h01_94AE);
    G_h01_94BA = ((8 >> G_h01_94B0) + G_h01_94BE) / 53;
    G_h01_94BC = (G_h01_94C0 - 16) >> 5;
    F_h00_435E();
}

extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int F_h11_5FB2();
extern int F_h11_405A();
extern int F_h11_4B0C();
extern int F_h11_415A();
extern int F_h11_40E0();

F_h11_0B4C()
{
    if (G_h01_94B4) {
        F_h11_5FB2(G_h01_94D6, &G_h01_94C0);
    } else if (G_h01_94B6) {
        if (F_h11_405A(G_h01_94D4)) {
            G_h01_94AE = 2;
            F_h11_4B0C(2);
            G_h01_94B6 = 0;
        } else {
            F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            F_h11_40E0(G_h01_94D4, 10);
        }
    }
}

extern short G_h01_94AE;
extern short G_h01_94B0;
extern short G_h01_94B4;
extern short G_h01_94BA;
extern short G_h01_94BC;
extern short G_h01_94BE;
extern short G_h01_94C0;
extern short G_h01_8A3C;
extern short G_h01_8B1C[40][4];
extern short G_h01_940C[1];
extern long G_h01_46E6;
extern int F_h11_25D6();
extern int F_h00_57D2();
extern int F_h11_5A12();
extern int F_h11_5A62();
extern int F_h11_4B0C();

F_h11_0BB6()
{
    int tile, xpos, offset, ypos;

    offset = (8 >> G_h01_94B0) + G_h01_94BE;
    if (((G_h01_94C0 + 14) >> 5) < 3) {
        if ((tile = G_h01_8B1C[G_h01_94BA][((G_h01_94C0 + 14) >> 5)]) != 0 &&
            G_h01_940C[tile] != 0) {
            xpos = G_h01_94BA * 53;
            ypos = (((G_h01_94C0 + 14) >> 5) << 5) + 0x30;
            if (F_h11_25D6(xpos + 0x0f, offset, xpos + 0x21) &&
                F_h11_25D6(ypos - 0x0f, G_h01_94C0 + 0x12, ypos)) {
                F_h00_57D2(0x20);
                G_h01_940C[tile] = 0;
                G_h01_46E6 += 0x32;
                G_h01_8A3C = 3;
            }
        }
    }

    switch (G_h01_94AE) {
    case 1:
    case 5:
        do {
            if (G_h01_94B4 != 0) {
                break;
            }
            if (G_h01_8B1C[G_h01_94BA][((G_h01_94C0 + 14) >> 5)] == 0 &&
                G_h01_94BC < 3) {
                if (G_h01_8B1C[G_h01_94BA - 1][((G_h01_94C0 + 14) >> 5)] != 0 &&
                    offset + 1 < F_h11_5A12(0, G_h01_94BA - 1)) {
                    break;
                }
                if (G_h01_8B1C[G_h01_94BA + 1][((G_h01_94C0 + 14) >> 5)] != 0 &&
                    offset + 4 > F_h11_5A62(0, G_h01_94BA + 1)) {
                    break;
                }
                G_h01_94AE = 2;
                F_h11_4B0C(2);
            }
        } while (0);
        break;
    }
}

struct ClusterRecord { char pad0[8]; int value8; int value10; char pad12[2]; int value14; int value16; char pad18[12]; int state30; int value32; char pad34[6]; int state40; int value42; int value2c; int value2e; char tail[4]; };
extern int G_h01_94AE;
extern int G_h01_94B0;
extern char G_h01_94B3;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int G_h01_94D8;
extern char *G_h01_94DA;
extern int G_h01_94DE;
extern int G_h01_94E0;
extern int G_h01_94E6;
extern int G_h01_945C[1];
extern int G_h01_8B1C[41][4];
extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h00_57D2();
extern int F_h11_3F90();
extern int F_h11_40AE();
extern int F_h11_415A();
extern int F_h11_4AA4();
extern int F_h11_4B0C();
extern int F_h11_5EC0();
extern int F_h11_6ED6();
extern int F_h11_6F78();

F_h11_0D8E()
{
    int r2;
    int r4;
    int t6;
    int t8;
    int done;
    int prev;
    int tick;
    char *cursor;

    done = 0;
    prev = G_h01_94AE;
    tick = (G_h01_94DE + 1 >= G_h01_94E0);
    cursor = (char *)G_h01_8BEC + ((long)G_h01_94D6 * 52);
    if (G_h01_94E6 > 0)
        return;
    G_h01_94BA = ((8 >> G_h01_94B0) + G_h01_94BE) / 53;
    G_h01_94BC = (G_h01_94C0 - 16) >> 5;

    switch (G_h01_94AE) {
    case 19:
        if (tick) {
            G_h01_94C0 += 8;
            G_h01_94AE = 5;
        }
        break;
    case 18:
        if (tick) {
            G_h01_94AE = 5;
            G_h01_94BE += G_h01_94B0 == 0 ? 14 : -14;
        }
        break;
    case 17:
        if (tick) {
            if ((t8 = G_h01_945C[G_h01_94BA]) != 0 && F_h11_6F78(t8, G_h01_94BE + 15, G_h01_94C0 + 24, 0x144)) {
                G_h01_94D8 = t8;
                G_h01_94AE = 8;
            } else {
                G_h01_94AE = 2;
            }
        }
        break;
    case 16:
        if (tick) {
            if ((t8 = G_h01_945C[G_h01_94BA]) != 0 && F_h11_6F78(t8, G_h01_94BE + 4, G_h01_94C0 + 8, 0x144)) {
                G_h01_94D8 = t8;
                G_h01_94AE = 8;
            } else {
                G_h01_94AE = 2;
            }
        }
        break;
    case 14:
        if (tick)
            G_h01_94AE = 2;
        break;
    case 12:
        if (tick) {
            G_h01_94C0 = ((G_h01_94C0 >> 5) << 5) + 16;
            G_h01_94AE = 5;
        }
        break;
    case 20:
        if (tick) {
            G_h01_94C0 += 7;
            G_h01_94AE = 5;
        }
        break;
    case 21:
        if (tick) {
            G_h01_94C0 += 6;
            G_h01_94AE = 5;
        } else if (G_h01_94DE == 5) {
            if (G_h01_8B1C[G_h01_94BA][G_h01_94BC + 1] == 0)
                G_h01_94AE = 2;
        }
        break;
    case 13:
        if (tick) {
            G_h01_94C0 += 5;
            if ((t6 = F_h11_3F90(G_h01_94BE)) >= 0) {
                G_h01_94D4 = t6;
                F_h11_40AE(G_h01_94D4);
                G_h01_94B6 = 1;
                G_h01_94AE = 5;
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            } else {
                G_h01_94AE = 2;
            }
        }
        break;
    case 10:
        if (tick)
            G_h01_94AE = 5;
        break;
    case 3:
        if (G_h01_94DE == 1) {
            F_h11_5EC0(G_h01_94D6);
        } else if (G_h01_94DE == 6) {
            t8 = G_h01_8B1C[G_h01_94BA][(G_h01_94C0 + 14) >> 5];
            if (t8 == 0 || (G_h01_94B4 && t8 == G_h01_94D6)) {
                G_h01_94AE = 2;
                break;
            }
        } else if (tick) {
            G_h01_94C0 = ((((G_h01_94C0 + 14) >> 5)) << 5) + 16;
            G_h01_94AE = 5;
            F_h00_57D2(0x77);
        }
        if ((t8 = G_h01_945C[G_h01_94BA]) != 0 && F_h11_6F78(t8, (8 >> G_h01_94B0) + G_h01_94BE, G_h01_94C0 + 16, 0x400)) {
            G_h01_94D8 = t8;
            G_h01_94AE = 8;
        }
        break;
    case 4:
        if (G_h01_94DE == 4 && ((G_h01_94C0 + 14) >> 5) > 2) {
            G_h01_94C0 += 8;
        } else if (tick) {
            if (G_h01_94BC >= 3) {
                if ((t6 = F_h11_3F90((8 >> G_h01_94B0) + G_h01_94BE)) >= 0) {
                    G_h01_94D4 = t6;
                    F_h11_40AE(G_h01_94D4);
                    F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                    F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                    G_h01_94B6 = 1;
                } else {
                    G_h01_94AE = 6;
                }
            }
            G_h01_94AE = 5;
            F_h00_57D2(0x77);
        }
        break;
    case 1:
        if (tick) {
            F_h00_57D2(10);
            G_h01_94B3 ^= 1;
            G_h01_94AE = 5;
        }
        break;
    case 2:
        if (G_h01_94C0 + 40 >= 154) {
            if ((t6 = F_h11_3F90((8 >> G_h01_94B0) + G_h01_94BE)) >= 0) {
                G_h01_94D4 = t6;
                F_h11_40AE(G_h01_94D4);
                G_h01_94B6 = 1;
                G_h01_94AE = 5;
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            } else {
                G_h01_94AE = 6;
            }
        } else {
            G_h01_94C0 += 16;
            done = 1;
        }
        break;
    case 8:
        F_h11_6ED6(G_h01_94D8, &r2, &r4, &G_h01_94BE, &G_h01_94C0);
        if (G_h01_94BE < r2) {
            G_h01_94DA[52] = G_h01_94B0 == 1 ? 0x1c : 0x1e;
            if (G_h01_94B0 == 0) {
                G_h01_94BE -= 20;
                G_h01_94C0 -= 13;
            } else {
                G_h01_94BE -= 9;
                G_h01_94C0 -= 12;
            }
        } else if (G_h01_94BE > r2) {
            G_h01_94DA[52] = G_h01_94B0 == 1 ? 0x1d : 0x1f;
            if (G_h01_94B0 == 0) {
                G_h01_94BE -= 6;
                G_h01_94C0 -= 12;
            } else {
                G_h01_94BE += 4;
                G_h01_94C0 -= 10;
            }
        } else {
            G_h01_94DA[52] = G_h01_94B0 == 1 ? 0x17 : 0x1b;
            if (G_h01_94B0 == 0) {
                G_h01_94BE -= 12;
                G_h01_94C0 -= 1;
            } else {
                G_h01_94BE -= 5;
                G_h01_94C0 += 0;
            }
        }
        done = 1;
        break;
    case 6:
        if (tick)
            G_h01_94AE = 7;
        break;
    default:
        done = 1;
        break;
    }

    if (!done) {
        if (prev != G_h01_94AE)
            F_h11_4B0C(G_h01_94AE);
        else
            F_h11_4AA4();
    }
    G_h01_94BA = ((8 >> G_h01_94B0) + G_h01_94BE) / 53;
    G_h01_94BC = (G_h01_94C0 - 16) >> 5;
}

/* Direct reconstruction candidate for ov11_F_1372. */
struct Target { int x; int y; };
extern int G_h01_94C2;
extern int G_h01_94C4;
extern int G_h01_94C6;
extern int G_h01_94C8;
extern long G_h01_94CA;
extern long G_h01_94CE;
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Target *G_h01_94DA;
extern int G_h01_94AE;
extern int G_h01_8A3E;
extern int F_h00_34E0();

F_h11_1372()
{
    long unused;

    G_h01_94C2 = G_h01_94C6;
    G_h01_94C4 = G_h01_94C8;
    G_h01_94CE = G_h01_94CA;
    G_h01_94C6 = G_h01_94BE - (G_h01_94B0 ? 16 : 0);
    G_h01_94C8 = G_h01_94C0;
    G_h01_94CA = G_h01_94DA;
    G_h01_94DA->x = G_h01_94C6 - G_h01_8A3E;
    G_h01_94DA->y = G_h01_94C0 + 1;
    if (G_h01_94AE != 45)
        F_h00_34E0(G_h01_94DA);
}

extern int G_h01_94C2;
extern int G_h01_94C4;
struct Object;
extern struct Object *G_h01_94CE;
extern struct Object *G_h01_9F4E;
extern struct Object *G_h01_9F52;
extern struct Object *G_h01_9F56;
extern struct Object *G_h01_9F8E;
extern int F_h11_4696();
extern int F_h11_583A();

F_h11_13DC()
{
    if (G_h01_94CE == G_h01_9F4E ||
        G_h01_94CE == G_h01_9F56) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 0x28, 0x21, 0x16);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 0x28, 0x21, 0x0a);
    } else if (G_h01_94CE == G_h01_9F52) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 0x30, 0x29, 0x16);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 0x30, 0x29, 0x0a);
    } else if (G_h01_94CE == G_h01_9F8E) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 0x58, 0x22, 0x16);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 0x58, 0x22, 0x0a);
    }
}

extern int G_h01_1708;
extern int G_h01_170A;
extern int G_h01_170C;
extern int G_h01_170E;
extern int G_h01_94AC;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B2;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94C2;
extern int G_h01_94C4;
extern int G_h01_94C6;
extern int G_h01_94C8;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int G_h01_94D8;
extern int F_h00_30F0();
extern int F_h11_5BC4();
extern int F_h11_4B0C();

F_h11_14BA(flag)
int flag;
{
    int selector;
    if (flag)
        G_h01_94AC = 1;
    else
        G_h01_94AC++;

    selector = 3 - G_h01_94AC + 1;
    switch (selector) {
    case 3:
        G_h01_1708 = 0x62;
        G_h01_170A = 0x82;
        G_h01_170C = 0xb3;
        G_h01_170E = 0x4d8;
        break;
    case 2:
        G_h01_1708 = 5;
        G_h01_170A = 8;
        G_h01_170C = 0x11c;
        G_h01_170E = 0x44d;
        break;
    case 1:
        G_h01_1708 = 0x500;
        G_h01_170A = 0x800;
        G_h01_170C = 0xc00;
        G_h01_170E = 0xd44;
        break;
    }

    F_h00_30F0(0);
    G_h01_94AE = 5;
    G_h01_94B0 = 1;
    G_h01_94B2 = 0;
    G_h01_94B6 = 0;
    G_h01_94B4 = 0;
    G_h01_94D4 = 0;
    G_h01_94D6 = 0;
    G_h01_94D8 = 0;
    F_h11_5BC4(&G_h01_94BA, &G_h01_94BC);
    G_h01_94BE = G_h01_94BA * 53 + 8;
    G_h01_94C0 = (G_h01_94BC << 5) + 16;
    G_h01_94C2 = G_h01_94C6 = G_h01_94BE - (G_h01_94B0 ? 16 : 0);
    G_h01_94C8 = G_h01_94C0;
    G_h01_94C4 = G_h01_94C0;
    F_h11_4B0C(G_h01_94AE);
}





/* ov11_F_15C8 candidate (worker v9; unread struct spans renamed neutrally). */
struct Descriptor { long object; int word4; int type; int word8; int word10; int dy; int dx; };
struct Controller { int x; int y; char f4[48]; char state; };
struct Object { char f0[52]; char state; };
struct Header { int count; char *data; };
extern int G_h01_12FE;
extern int G_h01_7A94;
extern struct Header *G_h01_7A96;
extern char G_h01_7A9A[1];
extern int G_h01_8A3A; extern int G_h01_8A3C; extern int G_h01_8A3E; extern int G_h01_8A40; extern int G_h01_8A42;
extern long G_h01_46CE; extern long G_h01_46DA; extern long G_h01_9FA6;
extern long G_h01_9F4E; extern long G_h01_9F52; extern long G_h01_9F56;
extern long G_h01_9F5E; extern long G_h01_9F62; extern long G_h01_9F6A; extern long G_h01_9F82; extern long G_h01_9F7E;
extern long G_h01_9F6E; extern long G_h01_9F66; extern long G_h01_9F76; extern long G_h01_9F8A; extern long G_h01_9F9E;
extern long G_h01_9FA2; extern long G_h01_9F92; extern long G_h01_9F96; extern long G_h01_9F9A;
extern long G_h01_9F8E; extern long G_h01_9F5A;
extern struct Descriptor G_h01_94EC[10]; extern struct Descriptor G_h01_958C[10]; extern struct Descriptor G_h01_962C[8];
extern struct Descriptor G_h01_96AC[8]; extern struct Descriptor G_h01_972C[3]; extern struct Descriptor G_h01_975C[3];
extern struct Descriptor G_h01_978C[7]; extern struct Descriptor G_h01_97FC[7]; extern struct Descriptor G_h01_986C[5];
extern struct Descriptor G_h01_98BC[9]; extern struct Descriptor G_h01_99DC[2]; extern struct Descriptor G_h01_99FC[2];
extern struct Descriptor G_h01_9A1C[5]; extern struct Descriptor G_h01_9A6C[5]; extern struct Descriptor G_h01_9ABC[3];
extern struct Descriptor G_h01_9AEC[1]; extern struct Descriptor G_h01_9AFC[5]; extern struct Descriptor G_h01_9B4C[7];
extern struct Descriptor G_h01_9BBC[7]; extern struct Descriptor G_h01_9C2C[6];
extern long F_h00_0FDE(); extern long F_h00_86DC(); extern int F_h00_2816(); extern long F_h00_291E();
extern int F_h00_3674(); extern int F_h00_3C0E(); extern int F_h00_3BD2();
extern int F_h11_20F2(); extern int F_h11_6080(); extern int F_h11_506A(); extern int F_h11_67B0();
extern int F_h11_6A44(); extern int F_h11_2C96(); extern int F_h11_7194(); extern int F_h11_3926(); extern int F_h11_49EA();

F_h11_15C8(arg)
int arg;
{
    int i;

    G_h01_8A3E = 0;
    G_h01_8A40 = 0;
    G_h01_8A42 = 0;
    G_h01_8A3C = 3;
    G_h01_12FE = 0;
    if (arg) {
        G_h01_9FA6 = G_h01_46DA;
        F_h00_0FDE(2);
        G_h01_46DA = F_h00_86DC("DT2:jg.arc", 1005L);
        F_h00_2816(G_h01_46DA);
        if (G_h01_7A94 == 0)
            G_h01_7A96 = (struct Header *)F_h00_291E(1, 0L);
        else if (G_h01_7A94 == 1)
            G_h01_7A96 = (struct Header *)F_h00_291E(2, 0L);
        else
            G_h01_7A96 = (struct Header *)F_h00_291E(3, 0L);
        G_h01_8A3A = G_h01_7A96->count;
        if (G_h01_8A3A > 4000)
            F_h00_3674(0x8A4);
        for (i = 0; i < G_h01_8A3A; i++)
            G_h01_7A9A[i] = G_h01_7A96->data[i];
        F_h00_3C0E(G_h01_7A96);
        F_h11_20F2(G_h01_7A9A);
        F_h11_6080(G_h01_7A9A);
        F_h11_506A(G_h01_7A9A);
        F_h11_67B0(G_h01_7A9A);
        F_h11_6A44(G_h01_7A9A);
        F_h11_2C96(G_h01_7A9A);
        F_h11_7194(G_h01_7A9A);
        F_h11_3926(G_h01_7A9A);
        F_h00_291E(4, G_h01_46CE);
        G_h01_9F5A = F_h00_291E(7, 0L);
        F_h11_49EA();
        F_h00_3BD2(G_h01_9F5A);
        G_h01_9F8E = F_h00_291E(0, 0L);
        G_h01_9F4E = F_h00_291E(5, 0L);
        G_h01_9F52 = F_h00_291E(6, 0L);
        G_h01_9F56 = F_h00_291E(17, 0L);
        G_h01_9F5E = F_h00_291E(8, 0L);
        G_h01_9F62 = F_h00_291E(9, 0L);
        G_h01_9F6A = F_h00_291E(11, 0L);
        G_h01_9F82 = F_h00_291E(12, 0L);
        G_h01_9F7E = F_h00_291E(13, 0L);
        G_h01_9F6E = F_h00_291E(14, 0L);
        G_h01_9F66 = F_h00_291E(10, 0L);
        G_h01_9F76 = F_h00_291E(15, 0L);
        G_h01_9F8A = F_h00_291E(16, 0L);
        G_h01_9F9E = F_h00_291E(18, 0L);
        G_h01_9FA2 = F_h00_291E(19, 0L);
        ((struct Object *)G_h01_9FA2)->state = 0;
        G_h01_9F92 = F_h00_291E(20, 0L);
        G_h01_9F96 = F_h00_291E(21, 0L);
        G_h01_9F9A = F_h00_291E(22, 0L);
        *(int *)G_h01_9F96 = 8;
        *((int *)G_h01_9F96 + 1) = 0xb2;
        ((struct Object *)G_h01_9F96)->state = 0;
        *(int *)G_h01_9F9A = 0x28;
        *((int *)G_h01_9F9A + 1) = 0xb1;
        ((struct Object *)G_h01_9F9A)->state = 0;
        for (i = 0; i < 5; i++) {
            G_h01_986C[i].object = G_h01_9F4E;
        }
        G_h01_986C[0].word4 = 0x14;
        G_h01_986C[1].word4 = 0x18;
        for (i = 0; i < 10; i++) {
            G_h01_94EC[i].object = G_h01_9F4E;
        }
        G_h01_94EC[0].object = G_h01_9F4E;
        G_h01_94EC[0].word4 = 0;
        G_h01_94EC[0].dy = 0x10;
        G_h01_94EC[1].word4 = 0x1;
        G_h01_94EC[2].word4 = 0x2;
        G_h01_94EC[3].word4 = 0x3;
        G_h01_94EC[4].word4 = 0x4;
        G_h01_94EC[5].word4 = 0x5;
        G_h01_94EC[5].dy = 0x10;
        G_h01_94EC[6].word4 = 0x6;
        G_h01_94EC[7].word4 = 0x7;
        G_h01_94EC[8].word4 = 0x8;
        G_h01_94EC[9].word4 = 0x9;
        for (i = 0; i < 10; i++) {
            G_h01_958C[i].object = G_h01_9F4E;
        }
        G_h01_958C[0].object = G_h01_9F4E;
        G_h01_958C[0].word4 = 0xa;
        G_h01_958C[0].dy = 0xfff0;
        G_h01_958C[1].word4 = 0xb;
        G_h01_958C[2].word4 = 0xc;
        G_h01_958C[3].word4 = 0xd;
        G_h01_958C[4].word4 = 0xe;
        G_h01_958C[5].word4 = 0xf;
        G_h01_958C[5].dy = 0xfff0;
        G_h01_958C[6].word4 = 0x10;
        G_h01_958C[7].word4 = 0x11;
        G_h01_958C[8].word4 = 0x12;
        G_h01_958C[9].word4 = 0x13;
        for (i = 0; i < 8; i++) {
            G_h01_962C[i].object = G_h01_9F4E;
        }
        G_h01_962C[0].word4 = 0x15;
        G_h01_962C[0].dy = 0xa;
        G_h01_962C[0].dx = 0;
        G_h01_962C[1].word4 = 0x14;
        G_h01_962C[1].dy = 0x2;
        G_h01_962C[1].dx = 0xfff4;
        G_h01_962C[2].word4 = 0x7;
        G_h01_962C[2].dy = 0x2;
        G_h01_962C[2].dx = 0xc;
        G_h01_962C[2].object = G_h01_9F56;
        G_h01_962C[3].word4 = 0x7;
        G_h01_962C[3].dy = 0x2;
        G_h01_962C[3].dx = 0x8;
        G_h01_962C[3].object = G_h01_9F56;
        G_h01_962C[4].word4 = 0x7;
        G_h01_962C[4].dy = 0x2;
        G_h01_962C[4].dx = 0xa;
        G_h01_962C[4].object = G_h01_9F56;
        G_h01_962C[5].word4 = 0x7;
        G_h01_962C[5].dy = 0x2;
        G_h01_962C[5].dx = 0xe;
        G_h01_962C[5].object = G_h01_9F56;
        G_h01_962C[6].word4 = 0x15;
        G_h01_962C[6].dy = 0xa;
        G_h01_962C[6].dx = 0;
        G_h01_962C[7].word4 = 0x14;
        G_h01_962C[7].dy = 0xfff6;
        G_h01_962C[7].dx = 0;
        for (i = 0; i < 8; i++) {
            G_h01_96AC[i].object = G_h01_9F4E;
        }
        G_h01_96AC[0].word4 = 0x19;
        G_h01_96AC[0].dy = 0xfff6;
        G_h01_96AC[0].dx = 0;
        G_h01_96AC[1].word4 = 0x18;
        G_h01_96AC[1].dy = 0xfffe;
        G_h01_96AC[1].dx = 0xfff4;
        G_h01_96AC[2].word4 = 0x3;
        G_h01_96AC[2].dy = 0xfffe;
        G_h01_96AC[2].dx = 0xc;
        G_h01_96AC[2].object = G_h01_9F56;
        G_h01_96AC[3].word4 = 0x3;
        G_h01_96AC[3].dy = 0xfffe;
        G_h01_96AC[3].dx = 0x8;
        G_h01_96AC[3].object = G_h01_9F56;
        G_h01_96AC[4].word4 = 0x3;
        G_h01_96AC[4].dy = 0xfffe;
        G_h01_96AC[4].dx = 0xa;
        G_h01_96AC[4].object = G_h01_9F56;
        G_h01_96AC[5].word4 = 0x3;
        G_h01_96AC[5].dy = 0xfffe;
        G_h01_96AC[5].dx = 0xe;
        G_h01_96AC[5].object = G_h01_9F56;
        G_h01_96AC[6].word4 = 0x19;
        G_h01_96AC[6].dy = 0xfff6;
        G_h01_96AC[6].dx = 0;
        G_h01_96AC[7].word4 = 0x18;
        G_h01_96AC[7].dy = 0xa;
        G_h01_96AC[7].dx = 0;
        for (i = 0; i < 3; i++) {
            G_h01_972C[i].object = G_h01_9F4E;
            G_h01_975C[i].object = G_h01_9F4E;
        }
        G_h01_972C[0].word4 = 0x15;
        G_h01_972C[0].dy = 0x10;
        G_h01_972C[1].word4 = 0x16;
        G_h01_972C[1].dy = 0;
        G_h01_972C[1].type = 0x7;
        G_h01_972C[2].word4 = 0x14;
        G_h01_972C[2].dy = 0xfff0;
        G_h01_975C[0].word4 = 0x19;
        G_h01_975C[0].dy = 0xfff0;
        G_h01_975C[1].word4 = 0x1a;
        G_h01_975C[1].dy = 0;
        G_h01_975C[1].type = 0x7;
        G_h01_975C[2].word4 = 0x18;
        G_h01_975C[2].dy = 0x10;
        for (i = 0; i < 7; i++) {
            G_h01_978C[i].object = G_h01_9F52;
        }
        G_h01_978C[0].word4 = 0x4;
        G_h01_978C[0].dx = 0xfff8;
        G_h01_978C[1].word4 = 0x5;
        G_h01_978C[1].dx = 0xfff4;
        G_h01_978C[2].word4 = 0x6;
        G_h01_978C[2].dx = 0xfff8;
        G_h01_978C[3].word4 = 0x7;
        G_h01_978C[3].dx = 0xfffa;
        G_h01_978C[4].word4 = 0x8;
        G_h01_978C[4].dx = 0;
        G_h01_978C[5].word4 = 0x7;
        G_h01_978C[5].dx = 0;
        G_h01_978C[6].word4 = 0x4;
        G_h01_978C[6].dx = 0xffeb;
        for (i = 0; i < 7; i++) {
            G_h01_97FC[i].object = G_h01_9F52;
        }
        G_h01_97FC[0].word4 = 0x4;
        G_h01_97FC[0].dx = 0x3;
        G_h01_97FC[1].word4 = 0x7;
        G_h01_97FC[1].dx = 0xe;
        G_h01_97FC[2].word4 = 0x8;
        G_h01_97FC[2].dx = 0;
        G_h01_97FC[3].word4 = 0x7;
        G_h01_97FC[3].dx = 0;
        G_h01_97FC[4].word4 = 0x6;
        G_h01_97FC[4].dx = 0x6;
        G_h01_97FC[5].word4 = 0x5;
        G_h01_97FC[5].dx = 0xa;
        G_h01_97FC[6].word4 = 0x4;
        G_h01_97FC[6].dx = 0x6;
        for (i = 0; i < 7; i++) {
            G_h01_9B4C[i].object = G_h01_9F52;
        }
        G_h01_9B4C[0].word4 = 0x4;
        G_h01_9B4C[0].dx = 0xfff9;
        G_h01_9B4C[1].word4 = 0x5;
        G_h01_9B4C[1].dx = 0x3;
        G_h01_9B4C[2].word4 = 0x6;
        G_h01_9B4C[2].dx = 0xfff9;
        G_h01_9B4C[3].word4 = 0x7;
        G_h01_9B4C[3].dx = 0xfffa;
        G_h01_9B4C[4].word4 = 0x8;
        G_h01_9B4C[4].dx = 0;
        G_h01_9B4C[5].word4 = 0x7;
        G_h01_9B4C[5].dx = 0;
        G_h01_9B4C[6].word4 = 0x4;
        G_h01_9B4C[6].dx = 0xffea;
        for (i = 0; i < 7; i++) {
            G_h01_9BBC[i].object = G_h01_9F52;
        }
        G_h01_9BBC[0].word4 = 0x4;
        G_h01_9BBC[0].dx = 0xfff9;
        G_h01_9BBC[1].word4 = 0x7;
        G_h01_9BBC[1].dx = 0x17;
        G_h01_9BBC[2].word4 = 0x8;
        G_h01_9BBC[2].dx = 0;
        G_h01_9BBC[3].word4 = 0x7;
        G_h01_9BBC[3].dx = 0;
        G_h01_9BBC[4].word4 = 0x6;
        G_h01_9BBC[4].dx = 0x6;
        G_h01_9BBC[5].word4 = 0x5;
        G_h01_9BBC[5].dx = 0x8;
        G_h01_9BBC[6].word4 = 0x4;
        G_h01_9BBC[6].dx = 0xfffc;
        for (i = 0; i < 9; i++) {
            G_h01_98BC[i].object = G_h01_9F56;
        }
        G_h01_98BC[0].word4 = 0x4;
        G_h01_98BC[1].word4 = 0x5;
        G_h01_98BC[2].word4 = 0;
        G_h01_98BC[2].object = G_h01_9F52;
        G_h01_98BC[2].dy = 0x5;
        G_h01_98BC[2].dx = 0xfff2;
        G_h01_98BC[3].word4 = 0;
        G_h01_98BC[3].object = G_h01_9F52;
        G_h01_98BC[3].dy = 0x5;
        G_h01_98BC[3].dx = 0xfff4;
        G_h01_98BC[4].word4 = 0;
        G_h01_98BC[4].object = G_h01_9F52;
        G_h01_98BC[4].dy = 0x5;
        G_h01_98BC[4].dx = 0xfff6;
        G_h01_98BC[5].word4 = 0x7;
        G_h01_98BC[5].dy = 0x5;
        G_h01_98BC[5].dx = 0xfff8;
        G_h01_98BC[6].word4 = 0x7;
        G_h01_98BC[6].dy = 0x5;
        G_h01_98BC[6].dx = 0x2;
        G_h01_98BC[7].word4 = 0x6;
        G_h01_98BC[7].dy = 0xd;
        G_h01_98BC[7].dx = 0x3;
        G_h01_98BC[8].word4 = 0x14;
        G_h01_98BC[8].object = G_h01_9F4E;
        G_h01_98BC[8].dy = 0xfff6;
        G_h01_98BC[8].dx = 0x4;
        G_h01_9AEC[0].object = G_h01_9F52;
        G_h01_9AEC[0].word4 = 0x9;
        G_h01_9AEC[0].type = 0x5;
        G_h01_99DC[0].object = G_h01_9F56;
        G_h01_99DC[0].word4 = 0x5;
        G_h01_99DC[1].object = G_h01_9F52;
        G_h01_99DC[1].word4 = 0;
        G_h01_99DC[1].dy = 0x4;
        G_h01_99DC[1].dx = 0xfff9;
        G_h01_99FC[0].object = G_h01_9F56;
        G_h01_99FC[0].word4 = 0x1;
        G_h01_99FC[1].object = G_h01_9F52;
        G_h01_99FC[1].word4 = 0x2;
        G_h01_99FC[1].dy = 0xfffc;
        G_h01_99FC[1].dx = 0xfff9;
        for (i = 0; i < 5; i++) {
            G_h01_9A6C[i].object = G_h01_9F4E;
        }
        G_h01_9A6C[0].word4 = 0x15;
        G_h01_9A6C[0].dy = 0xe;
        G_h01_9A6C[1].word4 = 0x4;
        G_h01_9A6C[1].dy = 0xfff8;
        G_h01_9A6C[1].object = G_h01_9F56;
        G_h01_9A6C[2].word4 = 0x7;
        G_h01_9A6C[2].type = 0x8;
        G_h01_9A6C[2].dx = 0xffe8;
        G_h01_9A6C[2].dy = 0xfff8;
        G_h01_9A6C[2].object = G_h01_9F56;
        G_h01_9A6C[3].word4 = 0x4;
        G_h01_9A6C[3].dy = 0x8;
        G_h01_9A6C[3].dx = 0x18;
        G_h01_9A6C[3].object = G_h01_9F56;
        G_h01_9A6C[4].word4 = 0x15;
        G_h01_9A6C[4].dy = 0x8;
        for (i = 0; i < 5; i++) {
            G_h01_9A1C[i].object = G_h01_9F4E;
        }
        G_h01_9A1C[0].word4 = 0x19;
        G_h01_9A1C[0].dy = 0xfff2;
        G_h01_9A1C[1].word4 = 0;
        G_h01_9A1C[1].dy = 0x8;
        G_h01_9A1C[1].object = G_h01_9F56;
        G_h01_9A1C[2].word4 = 0x3;
        G_h01_9A1C[2].type = 0x8;
        G_h01_9A1C[2].dx = 0xffe8;
        G_h01_9A1C[2].dy = 0x6;
        G_h01_9A1C[2].object = G_h01_9F56;
        G_h01_9A1C[3].word4 = 0;
        G_h01_9A1C[3].dy = 0xfffa;
        G_h01_9A1C[3].dx = 0x18;
        G_h01_9A1C[3].object = G_h01_9F56;
        G_h01_9A1C[4].word4 = 0x19;
        G_h01_9A1C[4].dy = 0xfff8;
        for (i = 0; i < 3; i++) {
            G_h01_9ABC[i].object = G_h01_9F52;
        }
        G_h01_9ABC[0].word4 = 0x4;
        G_h01_9ABC[0].dx = 0xfff8;
        G_h01_9ABC[1].word4 = 0x5;
        G_h01_9ABC[2].word4 = 0x4;
        for (i = 0; i < 5; i++) {
            G_h01_9AFC[i].object = G_h01_9F8E;
            G_h01_9AFC[i].type = 3;
        }
        G_h01_9AFC[0].word4 = 0;
        G_h01_9AFC[0].dy = 0xffe9;
        G_h01_9AFC[1].word4 = 0x1;
        G_h01_9AFC[2].word4 = 0x2;
        G_h01_9AFC[3].word4 = 0x3;
        G_h01_9AFC[4].word4 = 0x4;
        for (i = 0; i < 6; i++) {
            G_h01_9C2C[i].object = G_h01_9F62;
            G_h01_9C2C[i].dx = -6;
        }
        G_h01_9C2C[0].word4 = 0;
        G_h01_9C2C[0].word8 = 0;
        G_h01_9C2C[0].type = 0x1;
        G_h01_9C2C[1].word4 = 0x1;
        G_h01_9C2C[1].word8 = 0xa;
        G_h01_9C2C[1].type = 0x1;
        G_h01_9C2C[2].word4 = 0x2;
        G_h01_9C2C[2].type = 0x4;
        G_h01_9C2C[2].word8 = 0x17;
        G_h01_9C2C[3].word4 = 0x1;
        G_h01_9C2C[3].type = 0x1;
        G_h01_9C2C[3].word8 = 0xa;
        G_h01_9C2C[4].word4 = 0;
        G_h01_9C2C[4].word8 = 0;
        G_h01_9C2C[4].type = 0x1;
        G_h01_9C2C[5].word4 = 0x3;
        G_h01_9C2C[5].type = 0x3;
        G_h01_9C2C[5].word8 = 0xfffc;
    }
}

/* Ownership probe for ov11_F_20F2: parse L header and seven-word rows. */
struct Record {
    int ignored;
    int value1;
    int value2;
    int value3;
    int value4;
    int value5;
    int value6;
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_8A66[1];

F_h11_20F2(text)
char *text;
{
    char *line;
    int rows;
    struct Record *record;

    line = F_h00_75D8(text, 'L');
    if (F_h00_704E(line, "L %d", &rows) < 1)
        F_h00_3674(55);
    line = F_h00_75D8(line, '\n') + 1;
    for (record = G_h01_8A66; record - G_h01_8A66 < rows; record++) {
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d\n",
                &record->ignored, &record->value1, &record->value2,
                &record->value3, &record->value4, &record->value5,
                &record->value6) != 7)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(67);
next_record:
        ;
    }
}

struct LongSlot { long value; long pad[3]; };

extern struct LongSlot G_h01_9F0C[4];
extern long G_h01_9F9E;
extern int G_h01_9F10;
extern int G_h01_9F20;
extern int G_h01_9F30;
extern int G_h01_9F40;
extern int G_h01_9F4C;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FCC;
extern char G_h01_46E0;

F_h11_21F8()
{
    int i;

    for (i = 0; i < 4; i++)
        G_h01_9F0C[i].value = G_h01_9F9E;
    G_h01_9F10 = 0;
    G_h01_9F20 = 1;
    G_h01_9F30 = 2;
    G_h01_9F40 = 1;
    G_h01_9FCC = 0;
    G_h01_9FC0 = 0;
    G_h01_9FC2 = 0;
    switch (G_h01_46E0) {
    case 0: G_h01_9F4C = 350; break;
    case 1: G_h01_9F4C = 200; break;
    case 2: G_h01_9F4C = 100; break;
    }
}

extern int G_h01_8A3E;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94B8;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_9F4C;
extern int G_h01_9FAA;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FC4;
extern int G_h01_9FC6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int G_h01_9FCC;
extern int F_h11_262E();
extern int F_h11_2430();
extern int F_h11_407C();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_4B0C();

F_h11_2272()
{
    int x;
    int y;

    switch (G_h01_9FCC) {
    case 0:
        if (G_h01_94B8 > G_h01_9F4C) {
            G_h01_9FCC = 1;
            G_h01_9FC0 = G_h01_8A3E + 318;
            G_h01_9FC2 = G_h01_94C0 + 12;
            G_h01_9FC4 = G_h01_9FC0;
            G_h01_9FC6 = G_h01_9FC2;
            G_h01_9FC8 = G_h01_9FC4;
            G_h01_9FCA = G_h01_9FC6;
            F_h11_2430(12);
            F_h11_41F6(33, &G_h01_9FAA, G_h01_9FCC,
                G_h01_9FC0, G_h01_9FC2);
        }
        break;

    case 1:
        x = (8 >> G_h01_94B0) + G_h01_94BE;
        y = G_h01_94C0 + 16;
        switch (G_h01_94AE) {
        case 19:
            y += 8;
            break;
        case 6:
            x += 16;
            y += 8;
            break;
        }

        if (F_h11_262E(x - 4, y - 6, x + 4, y + 6,
                G_h01_9FC0 + 8, G_h01_9FC2 + 8,
                G_h01_9FC0 + 18, G_h01_9FC2 + 20) &&
            G_h01_94AE != 2 && G_h01_94AE != 45) {
            if (G_h01_94B6) {
                F_h11_407C(G_h01_94D4);
                G_h01_94B6 = 0;
            }
            G_h01_94AE = 2;
            F_h11_4B0C(2);
        }

        if (G_h01_9FC0 + 32 < G_h01_8A3E) {
            G_h01_9FCC = 0;
            G_h01_94B8 = 0;
        } else {
            G_h01_9FC0 -= 4;
            F_h11_4474(33, &G_h01_9FAA);
        }
        F_h11_2430(12);
        break;
    }
}


/* Direct reconstruction candidate for ov11_F_23F4. */
extern int G_h01_9FCC;
extern int G_h01_9FAA;
extern int G_h01_9FAC;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FC4;
extern int G_h01_9FC6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int F_h11_4610();

F_h11_23F4()
{
    if (G_h01_9FCC) {
        G_h01_9FAA = G_h01_9FC0;
        G_h01_9FAC = G_h01_9FC2;
        F_h11_4610(&G_h01_9FAA);
    }
    G_h01_9FC8 = G_h01_9FC4;
    G_h01_9FCA = G_h01_9FC6;
    G_h01_9FC4 = G_h01_9FC0;
    G_h01_9FC6 = G_h01_9FC2;
}
extern int G_h01_9FB6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int F_h11_4696();
extern int F_h11_247C();

F_h11_2430(a)
int a;
{
    G_h01_9FB6 = 2;
    if (a == 12)
        F_h11_4696(G_h01_9FC8, G_h01_9FCA, 40, 32, 33);
    F_h11_247C(12, G_h01_9FC8, G_h01_9FCA, 40, 32);
}

struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
extern struct Record G_h01_8A66[1];
extern int F_h11_5C42();
extern int F_h11_54F8();
extern int F_h11_2E26();
extern int F_h11_66FE();
extern int F_h11_717A();

F_h11_247C(a,b,c)
int a,c;
long b;
{
    struct Record *p,*last;

    if (((int *)&b)[0]<0) ((int *)&b)[0]=0;
    p=&G_h01_8A66[((int *)&b)[0]/104];
    last=&G_h01_8A66[(((int *)&b)[0]+c)/104];
    for (;p<=last;p++) {
        if (p->ignored) F_h11_5C42(p->ignored,a);
        if (p->value1) F_h11_54F8(p->value1,a);
        if (p->value5) F_h11_2E26(p->value5,a);
        if (p->value4) F_h11_66FE(p->value4,a);
        if (p->value6) F_h11_717A(p->value6,a);
    }
}

long F_h11_2562(x1,y1,x2,y2)
int x1,y1,x2,y2;
{
    long dx,dy;

    dx=(x1-x2<0)?-(x1-x2):x1-x2;
    dy=(y1-y2<0)?-(y1-y2):y1-y2;
    return dx*dx+dy*dy;
}

F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

extern int F_h11_25D6();
F_h11_25F8(a,b,c,d,e,f) int a,b,c,d,e,f; { return F_h11_25D6(a,c,e) && F_h11_25D6(b,d,f); }

F_h11_262E(a,b,c,d,e,f,g,h) int a,b,c,d,e,f,g,h; { return g>=a && e<=c && h>=b && f<=d; }

struct DrawRecord {
    int x;
    int y;
    char unused[48];
    char pen;
};

extern long G_h01_46CA;
extern char G_h01_46E1;
extern long G_h01_46E6;
extern char *G_h01_5370;
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94AC;
extern int G_h01_94C0;
extern long G_h01_9F92;
extern long G_h01_9F96;
extern long G_h01_9F9A;
extern int F_h00_09C0();
extern int F_h00_34E0();
extern int F_h00_8AA8();
extern int F_h00_8B4C();
extern void F_h00_8B76();
extern int F_h00_8B88();
extern int F_h11_25D6();

void F_h11_27CC()
{
    char saved;
    int i;
    int bottom;
    int redraw;

    bottom = 0xb0;
    redraw = 0;
    saved = *G_h01_5370;
    if (G_h01_94AE == 6 ||
        F_h11_25D6(bottom, G_h01_94C0 + 0x20, 0xb0))
        redraw = 1;

    if (redraw || G_h01_8A3C) {
        *G_h01_5370 = 0;
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B76(G_h01_46CA, 0L, (long)bottom, 0x13fL, 0xc7L);
        *G_h01_5370 = 0x11;
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, 0x13fL, (long)bottom);
        F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, 0L, 0xc7L);
        F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, 0L, (long)bottom);
        F_h00_8AA8(G_h01_46CA, 0L, 0xc7L);

        F_h00_34E0(G_h01_9F96);
        F_h00_34E0(G_h01_9F9A);
        ((struct DrawRecord *)G_h01_9F92)->pen = 2;
        ((struct DrawRecord *)G_h01_9F92)->x = 0xd8;
        ((struct DrawRecord *)G_h01_9F92)->y = 0xba;
        i = 0;
        for (; i <= 3 - G_h01_94AC; ++i) {
            F_h00_34E0(G_h01_9F92);
            ((struct DrawRecord *)G_h01_9F92)->pen--;
            ((struct DrawRecord *)G_h01_9F92)->x += 0x20;
        }
        F_h00_09C0(0xae, 0xb5, G_h01_46E6, 1, 0, 1);
        if (G_h01_46E1 < 10)
            F_h00_09C0(0x12, 0xb9, (long)G_h01_46E1, 0, 0, 0);
        else
            F_h00_09C0(0xe, 0xb9, (long)G_h01_46E1, 0, 0, 0);
    }

    *G_h01_5370 = 0x11;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, (long)bottom);
    F_h00_8AA8(G_h01_46CA, 0x13fL, (long)bottom);
    *G_h01_5370 = saved;
}

struct Record {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};

struct Slot { long value; char unused[12]; };

extern char G_h01_46E0;
extern char G_h01_9D2C[1];
extern char G_h01_9D4C[1];
extern char G_h01_9D6C[1];
extern char G_h01_9D9C[1];
extern char G_h01_9E5C[1];
extern long G_h01_9F6A;
extern struct Record G_h01_9FCE[1];
extern int G_h01_1300[16];
extern int G_h01_34D8[16];

extern int G_h01_9D30;
extern int G_h01_9D40;
extern int G_h01_9D4A;
extern int G_h01_9D50;
extern int G_h01_9D5A;
extern int G_h01_9D60;
extern int G_h01_9D6A;
extern int G_h01_9D70;
extern int G_h01_9D72;
extern int G_h01_9D80;
extern int G_h01_9D82;
extern int G_h01_9D90;
extern int G_h01_9DA0;
extern int G_h01_9DB0;
extern int G_h01_9DB2;
extern int G_h01_9DC0;
extern int G_h01_9DD0;
extern int G_h01_9DD2;
extern int G_h01_9DE0;
extern int G_h01_9DF0;
extern int G_h01_9DF2;
extern int G_h01_9E00;
extern int G_h01_9E10;
extern int G_h01_9E12;
extern int G_h01_9E20;
extern int G_h01_9E30;
extern int G_h01_9E32;
extern int G_h01_9E40;
extern int G_h01_9E50;
extern int G_h01_9E52;
extern int G_h01_9E60;
extern int G_h01_9E62;
extern int G_h01_9E70;
extern int G_h01_9E72;
extern int G_h01_9E80;
extern int G_h01_9E82;
extern int G_h01_9E90;
extern int G_h01_9E92;
extern int G_h01_9EA0;
extern int G_h01_9EA2;

extern int F_h11_2E26();
extern int F_h11_41F6();

F_h11_2A3A()
{
    int i;
    struct Record *record;

    for (i = 0; i < 2; i++) {
        ((struct Slot *)G_h01_9D4C)[i].value = G_h01_9F6A;
        ((struct Slot *)G_h01_9D2C)[i].value = G_h01_9F6A;
    }

    G_h01_9D50 = 0;
    G_h01_9D5A = 0;
    G_h01_9D60 = 1;
    G_h01_9D6A = 12;
    G_h01_9D30 = 0;
    G_h01_9D40 = 1;
    G_h01_9D4A = 12;

    for (i = 0; i < 3; i++)
        ((struct Slot *)G_h01_9D6C)[i].value = G_h01_9F6A;

    G_h01_9D70 = 2;
    G_h01_9D72 = 5;
    G_h01_9D80 = 3;
    G_h01_9D82 = 128;
    G_h01_9D90 = 1;

    for (i = 0; i < 12; i++)
        ((struct Slot *)G_h01_9D9C)[i].value = G_h01_9F6A;

    G_h01_9DA0 = 4;
    G_h01_9DB0 = 5;
    G_h01_9DB2 = 2;
    G_h01_9DC0 = 4;
    G_h01_9DD0 = 5;
    G_h01_9DD2 = 2;
    G_h01_9DE0 = 4;
    G_h01_9DF0 = 5;
    G_h01_9DF2 = 2;
    G_h01_9E00 = 4;
    G_h01_9E10 = 5;
    G_h01_9E12 = 2;
    G_h01_9E20 = 4;
    G_h01_9E30 = 5;
    G_h01_9E32 = 2;
    G_h01_9E40 = 4;
    G_h01_9E50 = 5;
    G_h01_9E52 = 2;

    for (i = 0; i < 5; i++)
        ((struct Slot *)G_h01_9E5C)[i].value = G_h01_9F6A;

    G_h01_9E60 = 6;
    G_h01_9E62 = 3;
    G_h01_9E70 = 7;
    G_h01_9E72 = 0;
    G_h01_9E80 = 7;
    G_h01_9E82 = 0;
    G_h01_9E90 = 7;
    G_h01_9E92 = 64;
    G_h01_9EA0 = 6;
    G_h01_9EA2 = 3;

    switch (G_h01_46E0) {
    case 0:
        G_h01_34D8[8] = 6;
        break;
    case 1:
        G_h01_1300[13] = 50;
        G_h01_1300[14] = 75;
        G_h01_1300[15] = 75;
        G_h01_34D8[8] = 3;
        break;
    case 2:
        G_h01_1300[13] = 75;
        G_h01_1300[14] = 75;
        G_h01_1300[15] = 85;
        G_h01_34D8[8] = 2;
        break;
    }

    for (i = 0; i < 6; i++) {
        record = &G_h01_9FCE[i];
        record->field30 = record->field34;
        *(int *)((char *)record + 44) = 14;
        *(int *)((char *)record + 46) = 0;
        *(int *)((char *)record + 62) = G_h01_34D8[8];
        F_h11_2E26(i, 7);
        F_h11_41F6(2, (char *)record + 2, 14,
                   *(int *)((char *)record + 30),
                   *(int *)((char *)record + 32));
    }
}

/* Parse M records into 64-byte resident records. */
struct Record {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_9FCE[1];

F_h11_2C96(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'M');
    F_h00_704E(line, "M %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, "%d ", &index) < 1) {
            F_h00_3674(901);
            goto next_record;
        }
        record = &G_h01_9FCE[index];
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d\n",
                         &record->field24, &record->field26,
                         &record->field28, &record->field30,
                         &record->field32, &record->field0) != 6)
            goto bad_record;
        record->field34 = record->field30;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(902);
next_record:
        ;
    }
}

struct MotionRecord {
    char pad0[2];
    char motion[28];
    short v30;
    short v32;
    short pad34;
    short v36;
    short v38;
    short v40;
    short v42;
    short state;
    char remainder[18];
};

extern struct MotionRecord G_h01_9FCE[1];
extern int F_h11_4610();

F_h11_2DBA(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_9FCE[n];
    if (record->state != 14)
        F_h11_4610(record->motion);
    record->v38 = record->v36;
    record->v42 = record->v40;
    record->v40 = record->v32;
    record->v36 = record->v30;
}

struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
extern struct Record G_h01_9FCE[1];
extern int F_h11_4696();
extern int F_h11_5962();

F_h11_2E26(index, state)
int index;
int state;
{
    struct Record *record;

    record = &G_h01_9FCE[index];
    *(int *)((char *)record + 14) = 2;

    if (*(int *)((char *)record + 16) == 0 || state == 7)
        *(int *)((char *)record + 16) = state;

    if (state == 7) {
        F_h11_4696(*(int *)((char *)record + 38),
                   *(int *)((char *)record + 42), 64, 74, index + 1);
        if (*(int *)((char *)record + 24))
            F_h11_5962(*(int *)((char *)record + 24), 7);
        if (*(int *)((char *)record + 26))
            F_h11_5962(*(int *)((char *)record + 26), 7);
        if (*(int *)((char *)record + 28))
            F_h11_5962(*(int *)((char *)record + 28), 7);
    }
}


struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
struct Row { int field0; int field2; int field4; };
extern struct Record G_h01_9FCE[1];
extern int G_h01_1300[16];
extern struct Row G_h01_12C0[32];
extern int G_h01_34D8[16];
extern int G_h01_7A92;
extern int G_h01_8A3C;
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_A14E;
extern unsigned int F_h00_463E();
extern int F_h00_57D2();
extern int F_h11_25D6();
extern int F_h11_2E26();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_45EC();

F_h11_2EEA(index)
int index;
{
    int *object;
    int changed;
    int redraw;
    int near;
    object = (int *)&G_h01_9FCE[index];
    changed = 0;
    redraw = 0;
    near = F_h11_45EC(object + 1);
    object[31]--;
    changed = 1;
    switch (object[22]) {
    case 14:
        if (object[31] == 0) {
            if (object[15] > G_h01_94BE && object[0] != 0 &&
                (int)F_h00_463E() % 100 < 75) {
                object[22] = 12; changed = 1; redraw = 1;
            } else if (object[15] > ((8 >> G_h01_94B0) + G_h01_94BE - 32) &&
                       (int)F_h00_463E() % 100 < 75) {
                object[22] = 16; object[16] = 8;
                G_h01_34D8[9] = (G_h01_94BE - object[15] + 12) % 64;
                object[15] = object[17] + G_h01_34D8[9];
                changed = 1; redraw = 1;
            }
        }
        break;
    case 16:
        if (object[15] < ((8 >> G_h01_94B0) + G_h01_94BE - 64)) {
            object[22] = 14; object[15] = object[17];
            changed = 1; redraw = 1;
        } else if (object[23] == 0 &&
                   (int)F_h00_463E() % 100 < G_h01_1300[15]) {
            object[22] = 17; G_h01_7A92 = index;
            object[23] = 1; object[24] = 3;
            object[25] = object[28] = object[27] = object[15] + 8;
            object[26] = object[30] = object[29] = object[16] + 28;
            changed = 1; redraw = 1;
        }
        break;
    case 17:
        if (object[31] == 0)
            goto state17_body;
        goto state17_done;
state17_body:
        if (near) {
            object[22] = 14; changed = 1; redraw = 1;
        } else {
            if (object[4] == 2) F_h00_57D2(96);
            F_h11_4474(2, object + 1);
        }
state17_done:
        break;
    case 12:
        if (object[31] == 0)
            goto state12_body;
        goto state12_done;
state12_body:
        if (near) {
                object[16] += 12;
                if (object[16] > 80) {
                    object[22] = 13;
                    changed = 1;
                    redraw = 1;
                } else if (object[16] + 28 < G_h01_94C0 + 32) {
                    changed = 1;
                    redraw = 1;
                } else {
                    object[22] = 13;
                    changed = 1;
                    redraw = 1;
                }
            } else {
                F_h11_4474(2, object + 1);
            }
state12_done:
        break;

    case 11:
        if (object[31] == 0)
            goto state11_body;
        goto state11_done;
state11_body:
        if (near) {
                object[16] -= 12;
                if (object[16] < 16) {
                    object[22] = 14;
                    changed = 1;
                    redraw = 1;
                } else if (object[16] + 32 > G_h01_94C0 + 32 || object[15] < G_h01_94BE) {
                    changed = 1;
                    redraw = 1;
                } else {
                    object[22] = 13;
                    changed = 1;
                    redraw = 1;
                }
            } else {
                F_h11_4474(2, object + 1);
            }
state11_done:
        break;

    case 13:
        if (object[31] <= 0) {
            if ((int)F_h00_463E() % 100 < G_h01_1300[13]) {
                if (object[23] == 0 &&
                    ((8 >> G_h01_94B0) + G_h01_94BE) <= object[15]) {
                    object[22] = 15; G_h01_12C0[16].field0 = 1;
                    changed = 1; redraw = 1; G_h01_7A92 = index;
                    G_h01_A14E = 0; object[23] = 1; object[24] = 0;
                    object[25] = object[28] = object[27] = object[15] + 44;
                    object[26] = object[30] = object[29] = object[16] + 22;
                }
            } else if ((int)F_h00_463E() % 100 < G_h01_1300[14]) {
                if (F_h11_25D6(object[15] - 32,
                               (8 >> G_h01_94B0) + G_h01_94BE,
                               object[15] + 32) != 0 || object[15] < G_h01_94BE) {
                    object[22] = 11; changed = 1; redraw = 1;
                } else if (object[16] + 20 < G_h01_94C0 && object[16] < 80) {
                    object[22] = 12; changed = 1; redraw = 1;
                } else if (object[16] + 20 > G_h01_94C0 + 32) {
                    object[22] = 11; changed = 1; redraw = 1;
                }
            }
        }
        break;
    case 15:
        if (near) {
            object[22] = 13; changed = 1; redraw = 1;
        } else {
            if (object[4] == 1 && G_h01_12C0[16].field0 != 0) {
                F_h00_57D2(96); G_h01_12C0[16].field0 = 0;
                F_h11_4474(2, object + 1);
            } else {
                F_h11_4474(2, object + 1);
            }
        }
        break;
    case 18:
        if (near) { object[22] = 13; changed = 1; redraw = 1; }
        else F_h11_4474(2, object + 1);
        break;
    }
    if (G_h01_8A3C != 0 || changed) F_h11_2E26(index, 7);
    if (redraw) F_h11_41F6(2, object + 1, object[22], object[15], object[16]);
    if (object[31] <= 0) object[31] = G_h01_34D8[8];
}

struct Record {
    int field0;
    char gap2[6];
    int field8;
    char gap10[14];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char gap36[8];
    int field44;
    int field46;
    int field48;
    int field50;
    int field52;
    char gap54[2];
    int field56;
    int field58;
    int field60;
    int field62;
};

struct TableCell {
    int value;
    char unused[12];
};

extern struct Record G_h01_9FCE[1];
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern struct TableCell G_h01_8A68[1];
extern int G_h01_A14E;
extern int F_h11_41F6();
extern int F_h11_4696();
extern int F_h11_583A();
extern int F_h11_54F8();

F_h11_3532(index)
int index;
{
    struct Record *record;
    int row;

    record = &G_h01_9FCE[index];
    if (record->field46 != 1)
        goto exit;
    if (record->field8 == 0)
        goto state_update;
    if (record->field48 != 0)
        goto state_update;
    if (record->field50 > G_h01_8A3E - 16)
        goto upper;

    record->field44 = 13;
    record->field46 = 0;
    G_h01_7A92 = 0;
    F_h11_41F6(2, (char *)record + 2, 13,
               record->field30, record->field32);
    goto position_join;

upper:
    if (record->field50 < G_h01_8A3E + 320)
        goto adjust;
    record->field46 = 0;
    goto position_join;

adjust:
    if (G_h01_A14E)
        goto subtract_eight;
    G_h01_A14E = 1;
    record->field50 -= 32;
    goto position_join;

subtract_eight:
    record->field50 -= 8;
position_join:
    goto draw;

state_update:
    if (record->field48 != 3)
        goto draw;
    if (record->field8 <= 2)
        goto draw;
    record->field52 += 8;
    if (record->field52 < 169)
        goto draw;
    record->field44 = 16;
    record->field46 = 0;
    F_h11_41F6(2, (char *)record + 2, 16,
               record->field30, record->field32);

draw:
    F_h11_4696(record->field56, record->field60, 24, 16,
               index + 12);
    F_h11_583A(record->field56, record->field60, 24, 16, 11);
    row = record->field56 / 104;
    if (G_h01_8A68[row].value)
        F_h11_54F8(G_h01_8A68[row].value, 11);
exit:
    ;
}

/* Direct reconstruction candidate for ov11_F_36F8. */
struct Object {
    char pad0[46];
    int active;
    int pad1;
    int x;
    int y;
    int old_x;
    int previous_x;
    int old_y;
    int previous_y;
    char pad2[2];
};

struct Controller {
    int x;
    int y;
    char pad[48];
    char state;
};

extern struct Object G_h01_9FCE[16];
extern struct Controller *G_h01_9F6E;
extern int G_h01_8A3E;
extern int F_h00_34E0();

F_h11_36F8(index)
int index;
{
    struct Object *object;

    object = &G_h01_9FCE[index];
    if (object->active) {
        G_h01_9F6E->x = object->x - G_h01_8A3E;
        G_h01_9F6E->y = object->y;
        G_h01_9F6E->state = 0;
        if (G_h01_9F6E->x > 0)
            if (G_h01_9F6E->y < 154)
                F_h00_34E0(G_h01_9F6E);
        object->previous_x = object->old_x;
        object->previous_y = object->old_y;
        object->old_x = G_h01_9F6E->x + G_h01_8A3E;
        object->old_y = G_h01_9F6E->y;
    }
}

struct Record { int pad[23]; int state; int gap; int x,y; char tail[10]; };
extern struct Record G_h01_9FCE[36];
F_h11_37A0(n,x,y) int n,*x,*y; {
 struct Record *p;
 p=&G_h01_9FCE[n];
 if(p->state) { *x=p->x; *y=p->y; }
 return p->state;
}

struct Object {
    char pad00[0x1e];
    int value1e;
    int value20;
    char pad24[10];
    int state2c;
    int gate2e;
    int state30;
    int y32;
    int x34;
    char pad36[2];
    int value38;
    char pad3a[2];
    int value3c;
    char pad3e[2];
};

extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern struct Object G_h01_9FCE[1];
extern int F_h11_262E();
extern int F_h11_41F6();
extern int F_h11_4B0C();
extern int F_h11_4696();
extern int F_h11_407C();

F_h11_37E4(index)
int index;
{
    int left;
    int top;
    struct Object *object;
    int hit;

    left = (8 >> G_h01_94B0) + G_h01_94BE;
    top = G_h01_94C0 + 16;
    object = &G_h01_9FCE[index];
    hit = 0;
    if (object->gate2e != 0) {
        hit = F_h11_262E(left - 4, top - 6, left + 4, top + 6,
                         object->y32 + 4, object->x34 + 2,
                         object->y32 + 8, object->x34 + 12);
    }
    if (hit != 0) {
        if (object->state30 == 0) {
            object->state2c = 0x12;
            F_h11_41F6(2, (char *)object + 2, 0x12,
                       object->value1e, object->value20);
        } else if (G_h01_94B6 != 0) {
            F_h11_407C(G_h01_94D4);
            G_h01_94B6 = 0;
        }
        G_h01_94AE = 2;
        F_h11_4B0C(2);
        object->gate2e = 0;
        F_h11_4696(object->value38, object->value3c, 0x18, 0x10,
                   index + 12);
    }
    return hit;
}
/* Ownership probe for ov11_F_3926: parse F header and indexed records. */
struct Record {
    char unused0[4];
    int value1;
    int value2;
    char unused1[10];
    int value3;
    char unused2[12];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern int G_h01_A152;
extern struct Record G_h01_A15E[1];

F_h11_3926(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'F');
    F_h00_704E(line, "F %d", &rows);
    G_h01_A152 = rows;
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(1021);
            goto next_record;
        }
        record = &G_h01_A15E[index];
        if (F_h00_704E(line, "%*d %d %d %d\n",
                &record->value2, &record->value1, &record->value3) != 3)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(1032);
next_record:
        ;
    }
}

struct Event {
    char pad0[2];
    int value2;
    char pad4[2];
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad18[6];
    int value18;
    int value1a;
    char rest[4];
};

extern long F_h00_463E();
extern void F_h00_3674();
extern int F_h11_40E0();
extern struct Event G_h01_A15E[1];
extern int G_h01_A152;
extern int G_h01_A150;
extern int G_h01_A158;
extern int G_h01_A15A;
extern char G_h01_46E0;

F_h11_3A24()
{
    int i;
    struct Event *event;

    for (i = 0; i < G_h01_A152; ++i) {
        event = &G_h01_A15E[i];
        switch (event->kind) {
        case 18:
            event->value14 = 4;
            event->value10 = 32;
            event->value8 = 80;
            break;
        case 17:
            event->value14 = 3;
            event->value10 == 20;
            event->value8 = 80;
            break;
        default:
            F_h00_3674(4555);
            break;
        }
        event->value2 = 154 - event->value10 / 4 - 1;
        event->value18 = event->value2;
        event->value1a = event->value18;
        if ((unsigned)F_h00_463E() % 10 < 5) {
            event->value12 = 0;
            event->value16 = 3;
        } else {
            event->value12 = event->value14 - 1;
            event->value16 = 2;
        }
        F_h11_40E0(i, 6);
    }
    G_h01_A15A = 2;
    G_h01_A158 = (unsigned)F_h00_463E() % G_h01_A152;
    switch (G_h01_46E0) {
    case 0:
        G_h01_A150 = 1;
        break;
    case 1:
        G_h01_A150 = 2;
        break;
    case 2:
        G_h01_A150 = 3;
        break;
    }
}
struct Event {
    char pad0[2];
    int value2;
    int value4;
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad12[2];
    int work14;
    int work16;
    int work18;
    int work1a;
    int count1c;
    int value1e;
};
struct Sprite { int x,y; char pad4[48]; char value34; };
extern int F_h11_37A0();
extern int F_h11_25F8();
extern int F_h11_40E0();
extern void F_h00_34E0();
extern struct Event G_h01_A15E[1];
extern struct Sprite *G_h01_9F66;
extern struct Sprite *G_h01_9F8A;
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;

F_h11_3B92()
{
    int quotient;
    int base;
    int i;
    int x;
    int y;
    struct Event *event;
    int screen_x;
    int screen_y;

    quotient = G_h01_8A3E / 128;
    base = (G_h01_A158 + quotient) % G_h01_A152;
    for (i = 0; i < 4; ++i) {
        event = &G_h01_A15E[(base + i) % G_h01_A152];
        if (event->value4 == 1) {
            screen_x = (quotient + i - 1) * 128 + G_h01_A154;
            screen_y = event->value2;
            if (G_h01_7A92 && F_h11_37A0(G_h01_7A92, &x, &y) &&
                F_h11_25F8(screen_x, screen_y - event->value10, x, y,
                            event->value8 + screen_x, event->value10 + screen_y))
                F_h11_40E0((base + i) % G_h01_A152, 7);
        if (event->count1c > 0 && event->value12 < event->value14) {
            switch (event->kind) {
            case 18:
                G_h01_9F66->value34 = ((unsigned char *)&event->value12)[1] + 0;
                G_h01_9F66->x = screen_x - G_h01_8A3E;
                G_h01_9F66->y = screen_y;
                if (G_h01_9F66->x < 320)
                    F_h00_34E0(G_h01_9F66);
                break;
            case 17:
                G_h01_9F8A->value34 = ((unsigned char *)&event->value12)[1] + 0;
                G_h01_9F8A->x = screen_x - G_h01_8A3E;
                G_h01_9F8A->y = screen_y;
                if (G_h01_9F8A->x < 320)
                    F_h00_34E0(G_h01_9F8A);
                break;
            }
            --event->count1c;
            if (event->count1c == 0)
                event->value1e = 0;
        }
        event->work16 = event->work14;
        event->work1a = event->work18;
        event->work14 = screen_x;
        event->work18 = screen_y;
        }
    }
}
struct Event {
    char pad0[2];
    int value2;
    int value4;
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    int value18;
    int value1a;
    char rest[10];
};

extern int F_h00_463E();
extern int F_h11_40E0();
extern struct Event G_h01_A15E[1];
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern int G_h01_8A42;
extern int G_h01_94C0;
extern int G_h01_A150;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;
extern int G_h01_A15A;

F_h11_3D9A()
{
    int quotient;
    int base;
    struct Event *event;
    int i;
    int index;

    if (G_h01_8A42)
        G_h01_A15A = 3;
    else if (G_h01_A15A <= 0)
        G_h01_A15A = 2;
    --G_h01_A15A;
    quotient = G_h01_8A3E / 128;
    base = (G_h01_A158 + quotient) % G_h01_A152;
    for (i = 0; i < 5; ++i) {
        event = &G_h01_A15E[(base + i) % G_h01_A152];
        index = (base + i) % G_h01_A152;
        if (G_h01_A15A == 0) {
            if (event->value4 && event->value1a + event->value8 > 1168) {
                if (event->value12 < event->value14)
                    ++event->value12;
            } else if (event->value4 == 1 && (unsigned)(F_h00_463E() & 15) < (unsigned)event->value18) {
                if (event->value16 == 2) {
                    if (event->value12 <= 0 &&
                        (unsigned)(F_h00_463E() & 15) < (unsigned)G_h01_A150)
                        event->value16 = 3;
                    else if (event->value12 > 0)
                        --event->value12;
                } else if (event->value16 == 3) {
                    if (event->value12 >= event->value14 &&
                        (unsigned)(F_h00_463E() & 15) < (unsigned)G_h01_A150)
                        event->value16 = 2;
                    else if (event->value12 < event->value14)
                        ++event->value12;
                }
            }
            F_h11_40E0(index, 6);
        }
        if ((G_h01_94C0 + 16) >> 5 >= 3)
            F_h11_40E0(index, 10);
        else if (G_h01_8A3C)
            F_h11_40E0(index, 6);
    }
    if (G_h01_A15A == 0) {
        G_h01_A154 += 4;
        if (G_h01_A154 >= 128) {
            G_h01_A154 = 0;
            --G_h01_A158;
            if (G_h01_A158 < 0)
                G_h01_A158 = G_h01_A152 - 1;
        }
    }
}
/* Direct reconstruction candidate for ov11_F_3F90. */
struct Event {
    char pad0[4];
    int value4;
    char pad6[2];
    int value8;
    char padA[2];
    int valueC;
    int valueE;
    char tail[16];
};

extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;
extern struct Event G_h01_A15E[1];
extern int F_h11_25D6();

int F_h11_3F90(a)
int a;
{
    struct Event *event;
    int page;
    int index;
    int screen_x;
    int result;

    result=-1;
    page=a/128+1;
    if (a%128<G_h01_A154)
        --page;
    screen_x=(page-1)*128+G_h01_A154;
    index=(G_h01_A158+page)%G_h01_A152;
    event=&G_h01_A15E[index];
    if (event->value4==1 && event->valueC<event->valueE)
        if (F_h11_25D6(event->valueC+screen_x+10,
                        (8>>G_h01_94B0)+G_h01_94BE,
                        event->value8+screen_x))
            result=index;
    return result;
}

struct Record { int state; char tail[30]; };
extern struct Record G_h01_A16A[36];
F_h11_405A(n) int n; { return G_h01_A16A[n].state==4; }

/* Direct reconstruction candidate for ov11_F_407C. */
struct Record {
    char pad0[12];
    int value12;
    int value14;
    char pad2[6];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};

extern struct Record G_h01_A15E[1];
extern int F_h11_40E0();

F_h11_407C(index)
int index;
{
    G_h01_A15E[index].value12 = G_h01_A15E[index].value14;
    F_h11_40E0(index, 6);
}
/* Direct reconstruction candidate for ov11_F_40AE. */
struct Event {
    char pad0[2];
    int value2;
    char pad4[2];
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad18[6];
    int value18;
    int value1a;
    char rest[4];
};

extern short G_h01_A156;
extern struct Event G_h01_A15E[1];
extern int F_h00_57D2();
extern int F_h00_86A8();

F_h11_40AE(index)
int index;
{
    struct Event *record;

    record = &G_h01_A15E[index];
    G_h01_A156 = 0;
    F_h00_86A8(5L);
    F_h00_57D2(91);
}

/* Direct reconstruction candidate for ov11_F_40E0. */
struct Record {
    char pad0[22];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};

extern struct Record G_h01_A15E[1];
extern int F_h11_4696();

F_h11_40E0(index, mode)
int index;
int mode;
{
    struct Record *record;

    record = &G_h01_A15E[index];
    record->state = 2;
    if (record->value30 == 0 || mode == 6)
        record->value30 = mode;
    if (mode == 6)
        F_h11_4696(record->value22, record->value26, 88, 30,
                   index % 4 + 18);
}
struct Row {
	short word0;
	short word2;
	short unused4[4];
	short word12;
	short word14;
	short unused16[8];
};

extern short G_h01_94AE;
extern short G_h01_94B6;
extern short G_h01_94C0;
extern short G_h01_94D4;
extern short G_h01_A156;
extern short G_h01_A15A;
extern short G_h01_A15E[1];

void F_h11_415A(index, cursor, output)
short index;
short *cursor;
short *output;
{
	struct Row *row;
	short next;

	row = (struct Row *)((char *)G_h01_A15E + (long)index * 32L);
	if (row->word12 >= row->word14 || F_h11_3F90(*cursor) < 0) {
		G_h01_94B6 = 0;
		G_h01_94D4 = 0;
		G_h01_94AE = 6;
		F_h11_4B0C(6);
    } else if (G_h01_A15A == 0) {

	*cursor += 4;
	next = row->word12 * 2 + row->word2 - 26;
	if (G_h01_A156 == 0)
		G_h01_A156 = G_h01_94C0;
	*output += next - G_h01_A156;
	G_h01_A156 = next;
	}
}
struct State {
    int value0;
    int value2;
    int unused4;
    int value6;
    int value8;
    int code;
    int unusedc;
    int unusede;
    char *address;
    int value14;
};

struct Target {
    char padding[6];
    int value6;
};

extern char G_h01_9F0C[1];
extern char G_h01_9C2C[1];
extern char G_h01_9CBC[1];
extern char G_h01_9CFC[1];
extern char G_h01_9CEC[1];
extern char G_h01_9EBC[1];
extern char G_h01_9EAC[1];
extern char G_h01_9D9C[1];
extern char G_h01_9E5C[1];
extern char G_h01_9D6C[1];
extern char G_h01_9D3C[1];
extern char G_h01_9D4C[1];
extern char G_h01_9D2C[1];
extern int F_h00_57D2();
extern int F_h00_86A8();

F_h11_41F6(mode, state, kind, value0, value2)
int mode;
struct State *state;
int kind;
int value0;
int value2;
{
    state->value6 = 0;
    state->value14 = kind;
    state->value0 = value0;
    state->value2 = value2;

    switch (mode) {
    case 33:
        state->address = G_h01_9F0C;
        state->code = 4;
        F_h00_57D2(89);
        break;
    case 24:
        switch (kind) {
        case 1:
            state->code = 1;
            state->address = G_h01_9C2C;
            break;
        case 3:
            state->code = 6;
            state->address = G_h01_9C2C;
            break;
        }
        break;
    case 11:
        switch (kind) {
        case 14:
            state->code = 0;
            state->address = G_h01_9CEC;
            break;
        case 18:
            state->code = 0;
            state->address = G_h01_9CFC;
            break;
        case 19:
            state->code = 3;
            state->address = G_h01_9CBC;
            break;
        }
        break;
    case 8:
        switch (kind) {
        case 20:
            state->code = 1;
            state->address = G_h01_9EAC;
            break;
        case 45:
            state->code = 5;
            state->address = G_h01_9EBC;
            break;
        }
        break;
    case 2:
        switch (kind) {
        case 12:
            state->code = 2;
            state->address = G_h01_9D4C;
            break;
        case 11:
            state->code = 2;
            state->address = G_h01_9D2C;
            break;
        case 15:
            state->code = 3;
            state->address = G_h01_9D6C;
            break;
        case 13:
            state->code = 0;
            state->address = G_h01_9D3C;
            break;
        case 18:
            state->code = 12;
            state->address = G_h01_9D9C;
            F_h00_57D2(0);
            F_h00_86A8((long)5);
            F_h00_57D2(97);
            break;
        case 17:
            state->code = 5;
            state->address = G_h01_9E5C;
            break;
        case 16:
            state->code = 0;
            state->address = G_h01_9E5C;
            break;
        }
        break;
    }
    state->value8 = ((struct Target *)state->address)->value6;
}
struct Counter {
    char pad[6];
    int value;
};

struct State {
    char pad0[6];
    int index;
    int countdown;
    int limit;
    char pad1[4];
    char *counter;
    int action;
};

extern char G_h01_9F0C;
extern char G_h01_9C2C;
extern int F_h00_57D2();

F_h11_4474(action,state)
int action;
struct State *state;
{
    if (state->countdown > 0)
        state->countdown--;
    else {
        state->index++;
        if (state->index < state->limit && state->counter)
            state->counter += 16;
        switch (action) {
        case 33:
            if (state->action && state->index >= state->limit) {
                state->index = 0;
                state->limit = 4;
                state->counter = &G_h01_9F0C;
            }
            break;
        case 24:
            switch (state->action) {
            case 1:
                if (state->index >= state->limit) {
                    state->index = 0;
                    state->limit = 1;
                    state->counter = &G_h01_9C2C;
                }
                break;
            case 3:
                if (state->index >= state->limit) {
                    state->index = 0;
                    state->limit = 6;
                    state->counter = &G_h01_9C2C;
                    F_h00_57D2(94);
                } else if (state->index == 3)
                    F_h00_57D2(87);
                break;
            }
            break;
        }
        if (state->index < state->limit && state->counter)
            state->countdown = ((struct Counter *)state->counter)->value;
    }
}

F_h11_45EC(p) int *p; { return p[3]>=p[5]-1; }

/* Direct reconstruction candidate for ov11_F_4610. */
struct Target {
    int x;
    int y;
    char pad[48];
    char state;
};

struct Holder {
    struct Target *target;
    char pad0;
    char state;
    char pad1[6];
    int x;
    int y;
};

struct Motion {
    int x;
    int y;
    char pad[8];
    int remaining;
    int active;
    struct Holder *holder;
};

extern int G_h01_8A3E;
extern int F_h00_34E0();

F_h11_4610(motion)
struct Motion *motion;
{
    struct Holder *holder;
    struct Target *target;

    holder = motion->holder;
    target = holder->target;
    if (motion->remaining > 0) {
        target->x = motion->x + holder->x - G_h01_8A3E;
        target->y = motion->y + holder->y;
        target->state = holder->state;
        F_h00_34E0(target);
        motion->remaining--;
        if (motion->remaining == 0)
            motion->active = 0;
    }
}

/* Direct reconstruction candidate for ov11_F_4696. */
struct Rect {
    int kind;
    int x;
    int y;
    int width;
    int height;
    int index;
    char pad[2];
};

extern struct Rect G_h01_34EC[40];
extern int G_h01_8A3C;
extern int G_h01_8A3E;

F_h11_4696(x, y, width, height, index)
int x;
int y;
int width;
int height;
int index;
{
    struct Rect *rect;

    rect = &G_h01_34EC[index];
    if (G_h01_8A3C < 2) {
        x -= G_h01_8A3E;
        if (x < 0) {
            width += x;
            if (width <= 0)
                return;
            x = 0;
        } else {
            if (x >= 320)
                return;
            if (x + width > 320)
                width = 320 - x + 8;
        }
        if (y < 0) {
            height += y;
            if (height <= 0)
                return;
            y = 0;
        } else {
            if (y > 176)
                return;
            if (y + height > 176)
                height = 176 - y;
        }
        if (height <= 0)
            return;
        if (width <= 0)
            return;
        rect->kind = 2;
        rect->x = x;
        rect->y = y;
        rect->width = width;
        rect->height = height;
        rect->index = index;
    }
}

/* Direct reconstruction candidate for ov11_F_4790. */
struct Rect {
    int kind;
    int x;
    int y;
    int width;
    int height;
    int index;
    char pad[2];
};

extern struct Rect G_h01_34EC[40];
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();

F_h11_4790()
{
    struct Rect *rect;

    for (rect = G_h01_34EC; rect - G_h01_34EC < 40; rect++)
        if (rect->kind) {
            rect->kind--;
            if (rect->width > 0)
                if (rect->height > 0)
                    F_h00_8A46(G_h01_46CE, (long)rect->x,
                        (long)rect->y, G_h01_46D2, (long)rect->x,
                        (long)rect->y, (long)rect->width,
                        (long)rect->height, (long)192, (long)255, 0L);
        }
}

struct Record {
    int value;
    char rest[12];
};

extern struct Record G_h01_34EC[40];

F_h11_4848()
{
    struct Record *p;

    for (p = G_h01_34EC; p - G_h01_34EC < 40; p++)
        p->value = 0;
}

extern int F_h00_8A46();
extern int F_h11_55B8();
extern int F_h11_645E();
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_A460;
extern int G_h01_8A6E[1];
extern int G_h01_8A3E;
extern int G_h01_94AE;
extern int G_h01_A45E;

F_h11_487E(x,y,width,height)
int x,y,width,height;
{
    int last,column,step,local_y,progress,spare;

    local_y=y;
    progress=0;
    last=(x+48)%104;
    while (progress<width) {
        step=(104-last<width-progress)?(104-last):(width-progress);
        F_h00_8A46((long)G_h01_A460,(long)last,(long)0,
            (long)G_h01_46D2,(long)local_y,(long)0,(long)step,
            (long)176,(long)192,(long)255,(long)0);
        progress+=step;
        local_y+=step;
        last=0;
    }
    F_h11_55B8();

    last=x/104;
    column=(x+320)/104;
    for (;last<=column;last++) {
        if (*((int *)((char *)G_h01_8A6E+((long)last*14))) && G_h01_94AE!=45)
            F_h11_645E(*((int *)((char *)G_h01_8A6E+((long)last*14))));
    }
    if (height) {
        F_h00_8A46((long)G_h01_46D2,(long)y,(long)0,
            (long)G_h01_46CE,(long)y,(long)0,(long)width,
            (long)200,(long)192,(long)255,(long)0);
        G_h01_A45E=G_h01_8A3E;
    }
}

extern int G_h01_8A3E;
extern int G_h01_A45E;
F_h11_49CE() { G_h01_8A3E=0; G_h01_A45E%=320; }

/* Direct reconstruction candidate for ov11_F_49EA. */
struct Controller { int x; int y; char pad[48]; char state; };
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern struct Controller *G_h01_9F5A;
extern long G_h01_A460;
extern int G_h01_A45E;
extern int G_h01_8A3E;
extern int F_h00_8BC8();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern long F_h00_3B16();

F_h11_49EA()
{
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 176L, 192L, 255L, 0L);
    G_h01_9F5A->x = 48;
    G_h01_9F5A->y = 0;
    G_h01_9F5A->state = 1;
    F_h00_34E0(G_h01_9F5A);
    G_h01_A460 = F_h00_3B16(128, 176);
    F_h00_8A46(G_h01_46D2, 56L, 0L, G_h01_A460,
        0L, 0L, 104L, 176L, 192L, 255L, 0L);
    G_h01_A45E = 0;
    G_h01_8A3E = 0;
}

extern long G_h01_A460;
extern int F_h00_3B84();

int F_h11_4A92() {
    return F_h00_3B84(G_h01_A460);
}

struct Destination { char pad[52]; char value; };
struct Source {
    struct Destination *destination;
    char pad0;
    char value;
    int delay;
    char pad1[4];
    int x;
    int y;
};

extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Destination *G_h01_94DA;
extern int G_h01_94DE;
extern int G_h01_94E0;
extern int G_h01_94E4;
extern struct Source *G_h01_94E8;

F_h11_4AA4()
{
    if (G_h01_94E4 > 0) {
        G_h01_94E4--;
    } else {
        G_h01_94DE++;
        if (G_h01_94DE < G_h01_94E0)
            if (G_h01_94E8 != 0) {
                G_h01_94E8++;
                G_h01_94BE += G_h01_94E8->x;
                G_h01_94C0 += G_h01_94E8->y;
                G_h01_94DA = G_h01_94E8->destination;
                G_h01_94DA->value = G_h01_94E8->value;
                G_h01_94E4 = G_h01_94E8->delay;
            }
    }
}

/* Isolated source-shape probe for ov11_F_4B0C; no source ownership claimed. */
struct Descriptor { long object; char pad4; char state; int type; char pad8[4]; int dy; int dx; };
struct Object { char pad[52]; char state; };
extern int G_h01_94B0; extern int G_h01_94B0; extern int G_h01_94B2; extern int G_h01_94B4; extern int G_h01_94B6;
extern int G_h01_94BE; extern int G_h01_94C0; extern int G_h01_94C0; extern int G_h01_94D8;
extern struct Object *G_h01_94DA; extern int G_h01_94DE; extern int G_h01_94E0; extern int G_h01_94E0;
extern int G_h01_94E4; extern int G_h01_94E6; extern struct Descriptor *G_h01_94E8;
extern struct Object *G_h01_9F4E; extern struct Object *G_h01_9F52;
extern struct Descriptor G_h01_94EC[1]; extern struct Descriptor G_h01_958C[1];
extern struct Descriptor G_h01_962C[1]; extern struct Descriptor G_h01_96AC[1];
extern struct Descriptor G_h01_972C[1]; extern struct Descriptor G_h01_978C[1];
extern struct Descriptor G_h01_975C[1]; extern struct Descriptor G_h01_97FC[1];
extern struct Descriptor G_h01_986C[1]; extern struct Descriptor G_h01_987C[1];
extern struct Descriptor G_h01_98BC[1]; extern struct Descriptor G_h01_994C[1];
extern struct Descriptor G_h01_99DC[1]; extern struct Descriptor G_h01_99FC[1];
extern struct Descriptor G_h01_9A1C[1]; extern struct Descriptor G_h01_9A6C[1];
extern struct Descriptor G_h01_9ABC[1]; extern struct Descriptor G_h01_9AEC[1];
extern struct Descriptor G_h01_9AFC[1]; extern struct Descriptor G_h01_9B4C[1];
extern struct Descriptor G_h01_9BBC[1]; extern struct Object *G_h01_9F52; extern struct Object *G_h01_9F4E;
extern int F_h00_57D2(); extern int F_h11_6ED6();

F_h11_4B0C(mode)
int mode;
{
    int x;
    int y;
    G_h01_94DE = 0;
    G_h01_94E4 = 0;
    G_h01_94E6 = 1;
    G_h01_94E8 = 0;
    switch (mode) {
    case 20: G_h01_94E0 = 7; G_h01_94E8 = G_h01_9B4C; break;
    case 21: G_h01_94E0 = 7; G_h01_94E8 = G_h01_9BBC; break;
    case 6: F_h00_57D2(0x58); G_h01_94C0 = 0x8e; G_h01_94E0 = 5; G_h01_94E8 = G_h01_9AFC; break;
    case 19: G_h01_94E0 = 3; G_h01_94E8 = G_h01_9ABC; break;
    case 18: G_h01_94E0 = 5; G_h01_94E8 = (G_h01_94B0 == 0) ? G_h01_9A1C : G_h01_9A6C; F_h00_57D2(0x64); break;
    case 17: G_h01_94E0 = 2; G_h01_94E8 = G_h01_99DC; break;
    case 16: G_h01_94E0 = 2; G_h01_94E8 = G_h01_99FC; break;
    case 14: G_h01_94E0 = 1; G_h01_94E8 = G_h01_9AEC; break;
    case 45: G_h01_94E0 = 0; break;    case 12: G_h01_94E0 = 7; G_h01_94E8 = G_h01_978C; break;
    case 13: G_h01_94E0 = 7; G_h01_94E8 = G_h01_97FC; break;
    case 3: G_h01_94E0 = 9; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_98BC : G_h01_994C; break;
    case 10: G_h01_94E0 = 3; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_972C : G_h01_975C; break;
    case 4: G_h01_94E0 = 8; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_962C : G_h01_96AC; break;
    case 5: G_h01_94E0 = 0; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_986C : G_h01_987C; break;
    case 1:
        if (G_h01_94B2 != 0) { G_h01_94DE = 0; G_h01_94E0 = 5; }
        else { G_h01_94DE = 5; G_h01_94E0 = 10; }
        if (G_h01_94B0 == 1) G_h01_94E8 = &G_h01_94EC[G_h01_94DE];
        else G_h01_94E8 = &G_h01_958C[G_h01_94DE];
        break;
    case 2:
        G_h01_94B6 = 0; G_h01_94B4 = 0; G_h01_94E0 = 0; G_h01_94DA = G_h01_9F52;
        if (G_h01_94B0 == 1) G_h01_94DA->state = 1; else G_h01_94DA->state = 3;
        F_h00_57D2(0xf); break;
    case 8:
        G_h01_94E0 = 1; G_h01_94DA = G_h01_9F4E;
        F_h11_6ED6(G_h01_94D8, &x, &y, &G_h01_94BE, &G_h01_94C0);
        if (G_h01_94BE < x) {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x1c : 0x1e;
            if (G_h01_94B0 == 0) { G_h01_94BE -= 12; G_h01_94C0 += 8; }
            else { G_h01_94BE -= 3; G_h01_94C0 += 9; }
        } else if (G_h01_94BE > x) {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x1d : 0x1f;
            if (G_h01_94B0 == 0) { G_h01_94BE += 0; G_h01_94C0 += 10; }
            else { G_h01_94BE += 10; G_h01_94C0 += 17; }
        } else {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x17 : 0x1b;
            if (G_h01_94B0 == 0) { G_h01_94BE -= 6; G_h01_94C0 += 22; }
            else { G_h01_94BE += 1; G_h01_94C0 += 22; }
        }
        G_h01_94BE -= 6; G_h01_94C0 -= 21; break;

    }
    if (G_h01_94E8 != 0) {
        G_h01_94DA = G_h01_94E8->object;
        G_h01_94BE += G_h01_94E8->dy;
        G_h01_94C0 += G_h01_94E8->dx;
        G_h01_94DA->state = G_h01_94E8->state;
        G_h01_94E4 = G_h01_94E8->type;
    }
}

struct AnimRecord {
    char prefix[22];
    int animation;
    int flags;
    int x;
    int y;
    int row;
    int column;
    int value;
    int extra;
    int tail;
};

extern struct AnimRecord G_h01_3724[1];
extern long G_h01_9F82;
extern char G_h01_9C8C[1];
extern char G_h01_9CBC[1];
extern char G_h01_9C92[1];
extern char G_h01_9CC2[1];
extern int G_h01_9C90;
extern int G_h01_9CA0;
extern int G_h01_9CB0;
extern int G_h01_9CC0;
extern int G_h01_9CD0;
extern int G_h01_9CE0;
extern char G_h01_9CEC[1];
extern int G_h01_9CF0;
extern int G_h01_9D00;
extern int G_h01_9D10;
extern int G_h01_9D20;
extern int G_h01_371C;
extern int G_h01_371E;
extern int G_h01_3720;
extern int G_h01_3722;
extern char G_h01_46E0;
extern int F_h11_54F8();
extern int F_h11_41F6();

F_h11_4EC6()
{
    struct AnimRecord *record;
    int i;

    for (i=0;i<3;i++) {
        *((long *)(G_h01_9C8C+((long)i*16)))=G_h01_9F82;
        *((long *)(G_h01_9CBC+((long)i*16)))=G_h01_9F82;
        *((int *)(G_h01_9C92+((long)i*16)))=1;
        *((int *)(G_h01_9CC2+((long)i*16)))=1;
    }
    G_h01_9C90=6;
    G_h01_9CA0=7;
    G_h01_9CB0=6;
    G_h01_9CC0=2;
    G_h01_9CD0=3;
    G_h01_9CE0=2;
    for (i=0;i<4;i++)
        *((long *)(G_h01_9CEC+((long)i*16)))=G_h01_9F82;
    G_h01_9CF0=0;
    G_h01_9D00=1;
    G_h01_9D10=4;
    G_h01_9D20=5;
    for (i=0;i<5;i++) {
        record=&G_h01_3724[i];
        record->x=record->row*53;
        record->y=record->column*32+32;
        record->animation=14;
        F_h11_54F8(i,5);
        F_h11_41F6(11,record,14,record->x,record->y);
    }
    switch (G_h01_46E0) {
    case 0:
        G_h01_371C=80;
        G_h01_371E=75;
        G_h01_3720=20;
        break;
    case 1:
        G_h01_371C=70;
        G_h01_371E=85;
        G_h01_3720=20;
        break;
    case 2:
        G_h01_371C=60;
        G_h01_371E=90;
        G_h01_3720=10;
        break;
    }
    G_h01_3722=G_h01_3720*3;
}

/* Ownership probe for ov11_F_506A: parse P header and 40-byte records. */
struct Record {
    char unused[24];
    int value24;
    int value26;
    int value28;
    int value30;
    int value32;
    int value34;
    int value36;
    int value38;
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_3724[1];

F_h11_506A(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'P');
    F_h00_704E(line, "P %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(435);
            goto next_record;
        }
        record = &G_h01_3724[index];
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d %d\n",
                &record->value34, &record->value36, &record->value38,
                &record->value26, &record->value28, &record->value30,
                &record->value32, &record->value24) != 8)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(444);
next_record:
        ;
    }
}

/* Direct recovery candidate for a 40-byte motion record dispatch. */
struct MotionRecord {
    char bytes[40];
};

extern struct MotionRecord G_h01_3724[1];
extern int F_h11_4610();

F_h11_519C(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_3724[n];
    F_h11_4610(record);
}

struct ScreenRecord {
    char prefix[12];
    int slot0c;
    char reserved0e[8];
    int mode;
    int frame;
    int x;
    int y;
    int row;
    int column;
    int id;
    int flags;
    int tail;
};

extern struct ScreenRecord G_h01_3724[1];
extern int G_h01_00A8;
extern int G_h01_00CC;
extern int G_h01_371C;
extern int G_h01_371E;
extern int G_h01_3720;
extern int G_h01_3722;
extern int G_h01_8A3E;
extern int G_h01_8A6A[1];
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B2;
extern int G_h01_94B8;
extern int G_h01_94C2;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_9F5E[1];
extern int F_h11_54F8();
extern int F_h11_25F8();
extern int F_h11_4B0C();
extern int F_h11_45EC();
extern int F_h11_4474();
extern long F_h11_2562();
extern int F_h11_41F6();
extern int F_h00_463E();
extern int F_h00_57D2();

F_h11_51C0(index)
int index;
{
    struct ScreenRecord *record;
    int changed,step,row_index;

    record=&G_h01_3724[index];
    changed=0;
    step=0;
    if (G_h01_8A3C) G_h01_3722=G_h01_3720;
    else G_h01_3722--;
    switch (record->mode) {
    case 14:
        if (G_h01_3722==0) {
            record->mode=18;
            changed=1;
            step=1;
        }
        break;
    case 18:
        if (record->row==G_h01_94BA &&
            record->column==((G_h01_94C0+14)>>5) &&
            (G_h01_94AE==5 || G_h01_94AE==1 || G_h01_94AE==12)) {
            G_h01_94AE=14;
            F_h11_4B0C(14);
        }
        if (G_h01_3722!=0) goto shared_tail;
        {
                if ((F_h00_463E()%100)<G_h01_371C) {
                    record->mode=14;
                    G_h01_3722=G_h01_3720*3;
                    changed=1;
                    step=1;
                } else if ((F_h00_463E()%100)<G_h01_371E) {
                    if (F_h11_25F8(record->x+6,record->y+12,
                        G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16,
                        record->x+58,record->y+64) && G_h01_94AE!=8) {
                        record->mode=19;
                        changed=1;
                        step=1;
                        F_h00_57D2(99);
                    }
                }
        }
        break;
    case 19:
        if (G_h01_94AE!=10) {
            if (F_h11_25F8(record->x,record->y,
                G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16,
                record->x+64,record->y+48)) {
                G_h01_94C0-=24;
                if (G_h01_94B6) G_h01_94B6=0;
                G_h01_94AE=2;
                F_h11_4B0C(2);
            }
        }
        if (F_h11_45EC(record)) {
            record->mode=18;
            changed=1;
            step=1;
        } else {
            changed=1;
            F_h11_4474(11,record);
        }
        break;
    }
shared_tail:
    if (G_h01_8A3C) {
        F_h11_54F8(index,0);
    } else {
        if (changed || F_h11_2562(record->x+32,record->y+24,
            G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16)<10000) {
            F_h11_54F8(index,5);
        } else {
            row_index=record->x/104;
            if (*((int *)((char *)G_h01_8A6A+((long)row_index*14))) ||
                *((int *)((char *)G_h01_8A6A+((long)(row_index-1)*14))))
                record->slot0c++;
        }
    }
    if (step)
        F_h11_41F6(11,record,record->mode,record->x,record->y);
    if (G_h01_3722<=0)
        G_h01_3722=G_h01_3720;
}

struct Record {
	char pad0[12];
	int state;
	int value;
	char pad10[10];
	int x;
	int y;
	char gap[4];
	int first;
	int second;
	int third;
};

extern struct Record G_h01_3724[1];
extern int F_h11_4696();
extern int F_h11_5962();

F_h11_54F8(index,mode)
int index,mode;
{
	struct Record *record;
	record=&G_h01_3724[index];
	record->state=2;
	if (record->value==0 || mode==5) record->value=mode;
	if (mode==5) {
		F_h11_4696(record->x,record->y,64,48,11);
		if (record->first) F_h11_5962(record->first,5);
		if (record->second) F_h11_5962(record->second,5);
		if (record->third) F_h11_5962(record->third,5);
	}
}
struct GridRecord {
    char prefix[8];
    int code;
    int state;
    char pad12[0x1c];
    int duration;
    int counter;
    int vertical;
    int horizontal;
    char tail[4];
};

extern int G_h01_37F2;
extern int G_h01_8A3E;
extern int G_h01_8A3C;
extern int G_h01_8B1C[41][4];
extern int G_h01_8BEC[1];
extern int G_h01_940C[1];
extern int *G_h01_9F5E;
extern int *G_h01_9FA2;
extern int F_h11_5962();
extern int F_h00_34E0();

F_h11_55B8()
{
    int row,column,base,tile,vertical,horizontal;
    struct GridRecord *object;

    if (G_h01_37F2) {
        G_h01_37F2=0;
        for (row=0;row<24;row++) {
            vertical=row*53+(!((row&1)^1)?-4:-24);
            for (column=2;column>=0;column--) {
                tile=G_h01_8B1C[row][column];
                if (tile) {
                    object=(struct GridRecord *)((char *)G_h01_8BEC+((long)tile*52));
                    if (!object->code) {
                        horizontal=column*32+48;
                        object->vertical=vertical;
                        object->horizontal=horizontal;
                    }
                }
            }
        }
    }
    base=(G_h01_8A3E-12)/53;
    base=(base<0)?0:base;
    for (row=6;row>=0;row--) {
        for (column=2;column>=0;column--) {
            tile=G_h01_8B1C[base+row][column];
            if (tile) {
                object=(struct GridRecord *)((char *)G_h01_8BEC+((long)tile*52));
                if (G_h01_8A3C) F_h11_5962(tile,2);
                if (object->duration>0 && !object->code) {
                    G_h01_9F5E[0]=object->vertical-G_h01_8A3E;
                    G_h01_9F5E[1]=object->horizontal;
                    *((char *)G_h01_9F5E+0x34)=object->prefix[7];
                    F_h00_34E0(G_h01_9F5E);
                    object->duration--;
                    if (!object->duration) object->counter=0;
                }
            }
        }
    }
    for (row=6;row>=0;row--) {
        vertical=(row+base)*53-G_h01_8A3E;
        for (column=2;column>=0;column--) {
            tile=G_h01_8B1C[base+row][column];
            if (tile) {
                object=(struct GridRecord *)((char *)G_h01_8BEC+((long)tile*52));
                if (object->duration>0) {
                    horizontal=column*32+48;
                    if (G_h01_940C[tile]>0 && !object->state) {
                        G_h01_9FA2[0]=vertical+16;
                        G_h01_9FA2[1]=horizontal-13;
                        F_h00_34E0(G_h01_9FA2);
                    }
                }
            }
        }
    }
}

/* Provisional source for normal ov11 layout evidence; never canonical by itself. */
extern int G_h01_8B1C[41][4];
extern void F_h11_5962();

F_h11_583A(x,y,width,height,mode)
int x,y,width,height,mode;
{
    int tile,i,j,x_end,y_end;
    if (mode==10) {
        x_end=x+width;
        y_end=y+height;
        x=(x-24)/53;
        y=(y-48)>>5;
        x_end=(x_end+24)/53;
        y_end=(y_end-16)>>5;
    } else {
        x_end=x+width;
        y_end=y+height;
        x=x/53;
        y=(y-48)>>5;
        x_end=x_end/53;
        y_end=(y_end-48)>>5;
    }
    if (x<0) x=0;
    if (y<0) y=0;
    for (i=x;i<=x_end;i++)
        for (j=y;j<=y_end;j++) {
            tile=G_h01_8B1C[i][j];
            if (tile) F_h11_5962(tile,mode);
        }
}

struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h11_5C42();
extern int F_h11_66FE();

F_h11_5962(index,mode)
int index;
int mode;
{
    struct ClusterRecord *record;

    record=&G_h01_8BEC[index];
    record->state40=2;
    if (record->value42==0 || mode==2) record->value42=mode;
    if (mode!=3 && record->value8) F_h11_5C42(index,2);
    if (mode!=8 && record->value10) F_h11_66FE(record->value10,2);
}

extern int G_h01_37F4[40];

F_h11_5A12(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        for (i = 0; i < 40; i++)
            G_h01_37F4[i] = (i + 1) * 53 + 2;
    } else
        return G_h01_37F4[index];
}

extern int G_h01_3844[40];

F_h11_5A62(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        for (i = 0; i < 40; i++)
            G_h01_3844[i] = i * 53 - 2;
    } else
        return G_h01_3844[index];
}

/* Direct reconstruction candidate for ov11_F_5AB0. */
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_8B1C[41][4];

F_h11_5AB0(direction, kind, result)
int direction;
int kind;
int *result;
{
    int found;
    int row;
    int column;

    found = 0;
    row = G_h01_94BA;
    if (direction == 1)
        row++;
    else if (direction == 0)
        row--;
    if (row < 0)
        goto invalid_row;
    if (row <= 40)
        goto select;
invalid_row:
    goto done;

select:
    if (direction == 0 || direction == 1) {
        if (kind == 2) {
            if ((column = G_h01_94BC - 1) >= 0)
                if (G_h01_8B1C[row][column]) {
                    *result = column;
                    found = 1;
                }
        } else if (kind == 3) {
            if ((column = G_h01_94BC + 1) < 3)
                if (G_h01_8B1C[row][column]) {
                    *result = column;
                    found = 1;
                }
            }
    } else if (direction == 2) {
        if (G_h01_94BC > 0) {
            if (G_h01_8B1C[row][G_h01_94BC - 1]) {
                *result = G_h01_94BC - 1;
                found = 1;
            }
        }
    }
done:
    return found;
}

extern int G_h01_8B1C[6][4];

F_h11_5BC4(row, column)
int *row, *column;
{
    int i, j;

    for (i = 0; i < 6; i++)
        for (j = 0; j < 3; j++)
            if (G_h01_8B1C[i][j]) {
                *row = i;
                *column = j;
                return;
            }
}

struct MotionRecord {
    char pad[18];
    char motion;
    char remainder[33];
};

extern struct MotionRecord G_h01_8BEC[1];
extern int F_h11_4610();

F_h11_5C1A(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_8BEC[n];
    F_h11_4610(&record->motion);
}

struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h11_4696();
extern int F_h11_5962();

F_h11_5C42(index,mode)
int index;
int mode;
{
    struct ClusterRecord *record;

    record=&G_h01_8BEC[index];
    record->state30=2;
    if (record->value32==0 || mode==3) record->value32=mode;
    if (mode==3) {
        F_h11_4696(record->value2c,record->value2e-6,72,32,24);
        if (record->value14) F_h11_5962(record->value14,2);
        if (record->value16) F_h11_5962(record->value16,2);
    }
}

struct ClusterRecord {
    int value0;
    int value2;
    char pad4[14];
    char pad18[26];
    int value2c;
    int value2e;
    int state30;
    int value32;
};

extern int G_h01_7A92;
extern int G_h01_8A3C;
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94C0;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_25F8();
extern int F_h11_37A0();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_5C42();

F_h11_5D14(index)
int index;
{
    struct ClusterRecord *record;
    int x, y, update, state;

    record = &G_h01_8BEC[index];
    update = 0;
    state = record->state30;

    switch (record->state30) {
    case 1:
        if (((G_h01_94C0 + 14) >> 5) == ((int *)record)[1] &&
            ((int *)record)[0] == G_h01_94BA) {
            G_h01_94B4 = 1;
            G_h01_94D6 = index;
            state = 3;
            update = 1;
        }
        break;
    case 3:
        if ((((int *)record)[0] != G_h01_94BA && G_h01_94AE != 18) ||
            G_h01_94B6) {
            state = 1;
            G_h01_94B4 = 0;
            G_h01_94D6 = 0;
            G_h01_37F0 = 0;
            G_h01_37EE = 0;
            update = 1;
        } else {
            update = 1;
            F_h11_4474(24, &record->pad18[0]);
        }
        break;
    default:
        break;
    }

    if (record->state30 != state) {
        record->state30 = state;
        F_h11_41F6(24, &record->pad18[0], state,
                   record->value2c, record->value2e);
    }

    if (G_h01_8A3C) {
        F_h11_5C42(index, 0);
    } else if (update) {
        F_h11_5C42(index, 3);
    } else if (G_h01_7A92 &&
               F_h11_37A0(G_h01_7A92, &x, &y) &&
               F_h11_25F8(record->value2c, record->value2e - 6,
                          x, y, record->value2c + 64,
                          record->value2e + 32)) {
        F_h11_5C42(index, 3);
    }
}

struct InitRecord { char prefix[0x2c]; int value2c; int value2e; int value30; int value32; };
extern struct InitRecord G_h01_8BEC[1];
extern int G_h01_94B4;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_5C42();
extern int F_h11_41F6();

F_h11_5EC0(index)
int index;
{
    struct InitRecord *record;

    record=&G_h01_8BEC[index];
    record->value30=1;
    G_h01_94B4=0;
    G_h01_94D6=0;
    G_h01_37F0=0;
    G_h01_37EE=0;
    F_h11_5C42(index,3);
    F_h11_41F6(24,&record->prefix[0x12],1,record->value2c,record->value2e);
}

/* ov11_F_5FB2: per-record scroll delta from float position math (m.lib FFP). */
struct ClusterRecord {
    char f0[8];
    int value8;
    int value10;
    char f12[2];
    int value14;
    int value16;
    char f18[12];
    int state30;
    int value32;
    int *ref34;
    char f38[2];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37EE;
extern int G_h01_37F0;
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;

F_h11_5FB2(index)
int index;
{
    struct ClusterRecord *record;
    int delta;
    int shift;

    record = &G_h01_8BEC[index];
    delta = (int)(((float)G_h01_94BE - (float)record->value2c)
                  * (float)record->ref34[4] / 104.0);
    shift = 0;
    if (record->ref34[2] == 2) {
        if ((8 >> G_h01_94B0) + G_h01_94BE - G_h01_37F0 - record->value2c > 45) {
            delta += 5;
            shift = -5;
        }
    }
    G_h01_94C0 += delta - G_h01_37EE;
    G_h01_94BE += shift - G_h01_37F0;
    G_h01_37EE = delta;
    G_h01_37F0 = shift;
}

struct ARecord { int value0; int value2; int value4; int value6; };
struct BRecord {
    int value0; int value2; int value4; int value6; int value8;
    int value10; int value12; int value14; int value16;
    char padding[26]; int value44; int value46; int unused48; int unused50;
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct ARecord G_h01_8B1C[1];
extern struct BRecord G_h01_8BEC[1];
extern int G_h01_37EC;

F_h11_6080(text)
char *text;
{
    char *line;
    int rows;
    struct BRecord *record;
    int i;

    line = F_h00_75D8(text, 'A');
    if (F_h00_704E(line, "A %d", &rows) < 1)
        F_h00_3674(231);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; ++i) {
        if (F_h00_704E(line, "%*d %d %d %d %d\n",
                &G_h01_8B1C[i].value0, &G_h01_8B1C[i].value2,
                &G_h01_8B1C[i].value4, &G_h01_8B1C[i].value6) == 4)
            line = F_h00_75D8(line, '\n') + 1;
        else
            F_h00_3674(241);
    }
    line = F_h00_75D8(text, 'B');
    if (F_h00_704E(line, "B %d", &rows) < 1)
        F_h00_3674(88);
    G_h01_37EC = rows;
    if (G_h01_37EC > 40)
        F_h00_3674(89);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0, record = G_h01_8BEC; i < rows; ++i, ++record) {
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d %d %d %d %d\n",
                &record->value0, &record->value2, &record->value44,
                &record->value46, &record->value4, &record->value6,
                &record->value8, &record->value10, &record->value12,
                &record->value14, &record->value16) == 11)
            line = F_h00_75D8(line, '\n') + 1;
        else
            F_h00_3674(89);
    }
}

struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37EC;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int G_h01_37F2;
extern char G_h01_46E0[3];
extern struct ClusterRecord G_h01_8BEC[1];
extern short G_h01_940C[1];
extern int F_h11_5962();
extern int F_h11_5A12();
extern int F_h11_5A62();
extern int F_h11_5C42();
extern int F_h11_41F6();
extern unsigned int F_h00_463E();

F_h11_62B4(mode)
int mode;
{
    int i, selected, result;

    G_h01_37F2 = 1;
    switch (G_h01_46E0[0]) {
    case 0:
        selected = 35;
        break;
    case 1:
        selected = 25;
        break;
    case 2:
        selected = 15;
        break;
    }

    for (i = 1; i < G_h01_37EC; i++) {
        F_h11_5962(i, 2);
        if (G_h01_8BEC[i].value8 != 0) {
            ((int *)&G_h01_8BEC[i])[24] = 1;
            G_h01_8BEC[i].value2c =
                ((int *)&G_h01_8BEC[i])[0] * 53 +
                ((((((int *)&G_h01_8BEC[i])[0] & 1) ^ 1) == 0) ? 4 : -8) - 1;
            G_h01_8BEC[i].value2e = ((int *)&G_h01_8BEC[i])[1] * 32 + 48;
            F_h11_5C42(i, 3);
            F_h11_41F6(24, G_h01_8BEC[i].pad18, 1,
                       G_h01_8BEC[i].value2c,
                       G_h01_8BEC[i].value2e);
        }
        else if (mode && F_h00_463E() % 100 < 25)
            G_h01_940C[i] = 1;
    }

    G_h01_37F0 = 0;
    G_h01_37EE = 0;
    if (mode) {
        result = F_h11_5A62(1, 0);
        result = F_h11_5A12(1, 0);
    }
}

struct MotionRecord {
    char pad[10];
    char motion;
    char remainder[29];
};

extern struct MotionRecord G_h01_A464[1];
extern int F_h11_4610();

F_h11_645E(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_A464[n];
    F_h11_4610(&record->motion);
}

struct MotionRecord {
    char prefix[32];
    int field20;
    int field22;
    int field24;
    int field26;
};
extern struct MotionRecord G_h01_A464[1];
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int F_h11_45EC();
extern int F_h11_66FE();
extern int F_h11_41F6();
extern int F_h11_4B0C();
extern int F_h11_4474();

F_h11_6486(index)
int index;
{
    struct MotionRecord *state;
    state = &G_h01_A464[index];
    state->field26--;
    switch (state->field20) {
    case 20:
        break;
    case 45:
        G_h01_8A3C = 3;
        if (F_h11_45EC((char *)state + 10)) {
            state->field20 = 20;
            F_h11_66FE(index, 8);
            F_h11_41F6(8, (char *)state + 10, 20, state->field22, state->field24);
            G_h01_94AE = 2;
            F_h11_4B0C(2);
        } else {
            F_h11_66FE(index, 8);
            F_h11_4474(8, (char *)state + 10);
        }
        break;
    }
    if (G_h01_8A3C != 0)
        F_h11_66FE(index, 8);
    if (state->field26 <= 0)
        state->field26 = 20;
}

struct Item {
    int value0;
    int value2;
    char pad4[6];
    int value10;
    char pad12[20];
    int state;
    int value34;
    int value36;
    char pad38[2];
};

extern struct Item G_h01_A464[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_8A3C;
extern int F_h11_25F8();
extern int F_h11_4B0C();
extern int F_h11_41F6();
extern int F_h00_57D2();

F_h11_6582(index)
int index;
{
    struct Item *item;
    int result;
    int y;
    int x;

    item = G_h01_A464 + index;
    result = 0;
    y = (8 >> G_h01_94B0) + G_h01_94BE;
    x = G_h01_94C0 + 16;
    if (G_h01_94AE == 19)
        x += 8;
    else if (G_h01_94AE == 18)
        y -= 16;

    if (item->state != 45 && G_h01_94AE != 2 &&
        G_h01_94AE != 6 && G_h01_94AE != 7) {
        if (F_h11_25F8(item->value34 + 16,
                       item->value36,
                       y,
                       x,
                       item->value34 + 48,
                       item->value36 + 56) != 0) {
            if (G_h01_94B6 != 0) {
                G_h01_94B6 = 0;
                G_h01_94D4 = 0;
            }
            G_h01_94AE = 45;
            F_h11_4B0C(G_h01_94AE);
            item->state = 45;
            F_h11_41F6(8, &item->value10, 45,
                       item->value34, item->value36);
            F_h00_57D2(98);
            G_h01_8A3C = 3;
            result = 1;
        } else if (item->value0 == G_h01_94BA &&
                   ((G_h01_94C0 + 14) >> 5) == item->value2 &&
                   (G_h01_94AE == 12 || G_h01_94AE == 1 || G_h01_94AE == 5)) {
            G_h01_94AE = 14;
            F_h11_4B0C(14);
        }
    }
    return result;
}
struct Record { int padding[11],state,value; char tail[14]; };
extern struct Record G_h01_A464[36];
F_h11_66FE(a,b) int a,b; { struct Record *p; p=&G_h01_A464[a]; p->state=2; if(!p->value || b==8)p->value=b; }

struct Record {
    int field0;
    int field2;
    char unused[30];
    int field34;
    int field36;
    char unused2[2];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_A464[1];

F_h11_67B0(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'S');
    F_h00_704E(line, "S %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(521);
            goto next_record;
        }
        record = &G_h01_A464[index];
        if (F_h00_704E(line, "%*d %d %d %d %d\n",
                         &record->field0, &record->field2,
                         &record->field34, &record->field36) != 4)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(523);
next_record:
        ;
    }
}

struct Display {
    long value0;
    int value4;
    int value6;
    char padding[8];
};

struct Record {
    int input0;
    int input2;
    char padding0[28];
    int value20;
    int value22;
    int value24;
    int value26;
};

extern char G_h01_9EAC[1];
extern int G_h01_9EB0;
extern int G_h01_9EC0;
extern int G_h01_9EC2;
extern int G_h01_9ED0;
extern int G_h01_9ED2;
extern int G_h01_9EE0;
extern int G_h01_9EE2;
extern int G_h01_9EF0;
extern int G_h01_9EF2;
extern int G_h01_9F00;
extern int G_h01_9F02;
extern long G_h01_9F7E;
extern struct Record G_h01_A464[6];
extern int F_h11_41F6();

F_h11_68B0()
{
    struct Record *record;
    int i;

    i = 0;
    do {
        ((struct Display *)G_h01_9EAC)[i].value0 = G_h01_9F7E;
        ++i;
    } while (i < 6);

    G_h01_9EB0 = 0;
    G_h01_9EC0 = 1;
    G_h01_9EC2 = 1;
    G_h01_9ED0 = 2;
    G_h01_9ED2 = 1;
    G_h01_9EE0 = 3;
    G_h01_9EE2 = 4;
    G_h01_9EF0 = 2;
    G_h01_9EF2 = 1;
    G_h01_9F00 = 1;
    G_h01_9F02 = 1;

    i = 1;
    do {
        record = &G_h01_A464[i];
        record->value22 = record->input0 * 53;
        record->value24 = record->input2 * 32 + 33;
        record->value20 = 20;
        record->value26 = 20;
        F_h11_41F6(8, (char *)record + 10, 20,
                    record->value22, record->value24);
        ++i;
    } while (i < 6);
}

struct Record {
    int unused0, unused2;
    int left, right, top, bottom;
    int initial_x, initial_y, offset_y;
    int x, y, flags;
    int unused24, unused26, unused28;
    int step, active;
};
extern struct Record G_h01_A554[10];
F_h11_69A4()
{
    struct Record *p;
    int i;
    i = 0;
    do {
        p = &G_h01_A554[i];
        p->x = p->initial_x;
        p->y = p->initial_y + p->offset_y;
        p->left = p->right = p->x;
        p->top = p->bottom = p->y;
        p->flags = 192;
        p->step = 8;
        p->active = 1;
        ++i;
    } while (i < 10);
}

/* Parse adjacent V and J sections. */
struct VRecord {
    int field0;
    int field2;
    char unused0[8];
    int field12;
    int field14;
    int field16;
    char unused1[6];
    int field24;
    int field26;
    int field28;
    char unused2[4];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct VRecord G_h01_A554[1];
extern int G_h01_945C[1];

F_h11_6A44(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct VRecord *record;

    line = F_h00_75D8(text, 'V');
    F_h00_704E(line, "V %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, "%d", &index) < 1) {
            F_h00_3674(888);
            goto next_v;
        }
        record = &G_h01_A554[index];
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d %d\n",
                         &record->field12, &record->field14,
                         &record->field16, &record->field24,
                         &record->field26, &record->field28,
                         &record->field0, &record->field2) != 8)
            goto bad_v;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_v;
bad_v:
        F_h00_3674(890);
next_v:
        ;
    }

    line = F_h00_75D8(text, 'J');
    F_h00_704E(line, "J %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, "%d", &index) < 1) {
            F_h00_3674(988);
            goto next_j;
        }
        if (F_h00_704E(line, "%*d %d \n", &G_h01_945C[index]) != 1)
            goto bad_j;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_j;
bad_j:
        F_h00_3674(990);
next_j:
        ;
    }
}

/* Direct reconstruction candidate for ov11_F_6C3A. */
struct Record {
    char pad0[4];
    int first;
    int first_old;
    int second;
    int second_old;
    int x;
    int y;
    int pad_between;
    int x2;
    int y2;
    char pad1[9];
    char state;
    char pad2[2];
};
extern struct Record G_h01_A554[16];
extern char *G_h01_5370;
extern long G_h01_46CA;
extern int G_h01_8A3E;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();

F_h11_6C3A(index)
int index;
{
    struct Record *record;

    record = &G_h01_A554[index];
    *G_h01_5370 = record->state;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, (long)(record->x - G_h01_8A3E), (long)record->y);
    F_h00_8AA8(G_h01_46CA, (long)(record->x2 - G_h01_8A3E), (long)record->y2);
    record->first_old = record->first;
    record->first = record->x2;
    record->second_old = record->second;
    record->second = record->y2;
}

struct Record { int unused0, unused2; int left, right, top, bottom; int initial_x, initial_y, offset_y; int x, y, flags; int unused24, unused26, unused28; int step, active; };
extern int G_h01_94AE;
extern int G_h01_94D8;
extern struct Record G_h01_A554[10];
extern int F_h00_57D2();
extern int F_h11_4696();
extern int F_h11_5962();
extern int F_h11_727A();
extern int F_h11_729C();

F_h11_6CFE(index)
int index;
{
    struct Record *record;
    int dx;
    int dy;

    record = &G_h01_A554[index];
    record->flags += record->unused28;
    if (record->flags > record->unused26) {
        record->unused28 *= -1;
        if (G_h01_94AE == 8 && index == G_h01_94D8)
            F_h00_57D2(0x5a);
    } else {
        if (record->flags < record->unused24) {
            record->unused28 *= -1;
            if (G_h01_94AE == 8 && index == G_h01_94D8)
                F_h00_57D2(0x5d);
        }
    }

    record->x = record->initial_x +
        (F_h11_729C(record->flags - 0x80) * record->offset_y) / 0x100;
    record->y = record->initial_y +
        (F_h11_727A(record->flags - 0x80) * record->offset_y) / 0x100;

    if (record->initial_x <= record->right) {
        dx = record->right - record->initial_x;
        record->right = record->initial_x;
    } else {
        dx = record->initial_x - record->right;
    }
    dx += 0x10;
    dy = record->bottom - record->initial_y + 1;
    F_h11_4696(record->right, record->initial_y, dx, dy, index + 0x1c);

    if (record->unused0)
        F_h11_5962(record->unused0, 4);
    if (record->unused2)
        F_h11_5962(record->unused2, 4);
}

struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record G_h01_A554[36];
F_h11_6ED6(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&G_h01_A554[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}

/* Fingerprint-derived direct reconstruction candidate for ov11_F_6F78. */
struct DistanceRecord {
    char pad0[18];
    int value18;
    int value20;
    char tail[12];
};

extern char G_h01_46E0;
extern struct DistanceRecord G_h01_A554[1];
extern long F_h11_2562();

int F_h11_6F78(index,x,y,scale)
int index;
int x;
int y;
int scale;
{
    struct DistanceRecord *record;

    record=&G_h01_A554[index];
    switch (G_h01_46E0) {
    case 0:
        scale*=3;
        break;
    case 1:
        scale*=2;
        break;
    case 2:
        break;
    }
    return index>0 && (long)scale>F_h11_2562(x,y,record->value18,record->value20);
}

/* Direct reconstruction candidate for ov11_F_6FFE. */
struct InitRecord { int value0; int value2; int value4; int value6; int pad8; };
struct Target { char pad0[52]; char value52; };
extern struct InitRecord G_h01_A6A8[1];
extern struct Target *G_h01_9F76;
extern int F_h11_717A();
F_h11_6FFE()
{
    struct InitRecord *record;
    int i;
    for (i = 1, record = G_h01_A6A8; i < 3; i++, record++) {
        record->value4 = record->value0 * 53 + 12;
        record->value6 = (record->value2 << 5) + 21;
        F_h11_717A(i, 9);
    }
    G_h01_9F76->value52 = 0;
}
struct Record {
    int unused0;
    int unused1;
    int first;
    int second;
    int count;
};
struct Output {
    int first;
    int second;
};

extern struct Record G_h01_A6A8[1];
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern struct Output *G_h01_9F76;
extern int F_h00_34E0();

F_h11_706C(n)
int n;
{
    struct Record *record;

    record=&G_h01_A6A8[n];
    if (G_h01_8A3C>0 || record->count>0) {
        G_h01_9F76->first=record->first-G_h01_8A3E;
        G_h01_9F76->second=record->second;
        F_h00_34E0(G_h01_9F76);
        record->count=G_h01_8A3C ? 2 : record->count-1;
    }
}

/* Direct reconstruction candidate for ov11_F_70DC. */
struct Record {
    int value;
    int value2;
    int value4;
    int value6;
    char tail[2];
};

extern int G_h01_12FE;
extern int G_h01_94B0;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Record G_h01_A6A8[1];
extern int F_h11_25D6();
extern int F_h11_25F8();
extern int F_h11_717A();

F_h11_70DC(a)
int a;
{
    struct Record *record;

    record = &G_h01_A6A8[a];
    if (F_h11_25D6(record->value - 2, G_h01_94BA,
                    record->value + 1)) {
        F_h11_717A(a, 9);
        if (F_h11_25F8(record->value4, record->value6,
                        (8 >> G_h01_94B0) + G_h01_94BE,
                        G_h01_94C0 + 16, record->value4 + 48,
                        record->value6 + 30))
            G_h01_12FE = 1;
    }
}

struct Record { int value; char tail[8]; };
extern struct Record G_h01_A6B0[36];
F_h11_717A(a) int a; { G_h01_A6B0[a].value=2; }

/* Parse X records into the observed ten-byte resident records. */
struct Record {
    int field0;
    int field2;
    char unused[6];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_A6A8[1];

F_h11_7194(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'X');
    F_h00_704E(line, "X %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, "%d ", &index) < 1) {
            F_h00_3674(914);
            goto next_record;
        }
        record = &G_h01_A6A8[index];
        if (F_h00_704E(line, "%*d %d %d\n",
                         &record->field0, &record->field2) != 2)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(917);
next_record:
        ;
    }
}

extern int G_h01_1322[64];

unsigned F_h11_727A(n)
unsigned n;
{
    return G_h01_1322[(n >> 2) & 63];
}

extern int G_h01_13A2[64];

unsigned F_h11_729C(n)
unsigned n;
{
    return G_h01_13A2[(n >> 2) & 63];
}

