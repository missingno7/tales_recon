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
