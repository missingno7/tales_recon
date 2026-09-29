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

void recovered()
{
    int key;
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

    if (key & 0x80) {
        key |= 0x80;
        if (G_h01_34D8[7] > 0) {
            --G_h01_34D8[7];
            return;
        }
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
            if (G_h01_94BE - 16 > 0) {
                G_h01_94AE = 1;
                if (G_h01_94B0 == 1)
                    G_h01_94B0 = 0;
                if ((8 >> G_h01_94B0) + G_h01_94BE - 18 <
                    F_h11_5A62(0, G_h01_94BA)) {
                    if (G_h01_94B4) {
                        if (G_h01_8B1C[G_h01_94BA + 1][G_h01_94BC]) {
                            G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                            F_h11_5EC0(G_h01_94D6);
                        }
                    } else if (!G_h01_94B6 &&
                               !G_h01_8B1C[G_h01_94BA - 1][G_h01_94BC]) {
                        if (F_h11_5AB0(0, 3, &found) ||
                            (G_h01_94BC == 2 &&
                             F_h11_3F90((8 >> G_h01_94B0) +
                                        G_h01_94BE - 16) > 0))
                            G_h01_94AE = 4;
                    }
                }
            } else
                G_h01_94AE = 5;
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
                G_h01_94AE = 19;
                if (G_h01_945C[G_h01_94BA] && !G_h01_94B8) {
                    if (G_h01_94B0 == 1) {
                        if (G_h01_945C[G_h01_94BA + 1])
                            G_h01_94AE = 17;
                    } else if (G_h01_94B0 == 0) {
                        if (G_h01_945C[G_h01_94BA - 1])
                            G_h01_94AE = 16;
                    }
                }
            }
            break;

        case 5:
            if (G_h01_94B6)
                G_h01_94AE = 10;
            else if (((G_h01_94C0 + 14) >> 5) < 2 || !G_h01_94B4)
                G_h01_94AE = 21;
            else {
                G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                F_h11_5EC0(G_h01_94D6);
                G_h01_94AE = 13;
            }
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
                if (G_h01_94C0 + 16 > 0x70)
                    G_h01_94AE = 2;
                else
                    G_h01_94AE = 5;
                G_h01_94D8 = 0;
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
