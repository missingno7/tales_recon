struct Entry { unsigned char kind; char active; char rest[4]; };
struct Slot { int x; int y; int t; char pad[46]; char st; char tail; };
struct Sprite { int x; int y; int t; int u; int w; int h; long p; char data[36]; char st; char tail; };
extern char *G_h01_6EB0;
extern struct Entry *G_h01_6F3C;
extern char *G_h01_6EB4;
extern char G_h01_6EB8[54];
extern char G_h01_6EEE[54];
extern char G_h01_6EFE[1];
extern int G_h01_6EF6;
extern int G_h01_6EF8;
extern int G_h01_6EC0;
extern int G_h01_6EC2;
extern char G_h01_6EC8[1];
extern char G_h01_0AA2[32];
extern char G_h01_0AC4[1];
extern char G_h01_0CD2[1];
extern char G_h01_0EE0[1];
extern char G_h01_10F2[1];
extern char G_h01_1188[1];
extern char G_h01_121E[1];
extern char G_h01_15E6[1];
extern int G_h01_1608;
extern int G_h01_160A;
extern int G_h01_160C;
extern int G_h01_160E;
extern char G_h01_2C2C;
extern long G_h01_2C26;
extern char G_h01_12BB;
extern char G_h01_34CE;
extern int G_h01_349A;
extern int G_h01_349C;
extern int G_h01_345A;
extern int G_h01_3424;
extern int G_h01_33EE;
extern int G_h01_34D0[16];
extern int G_h01_34D4[16];
extern int G_h01_34D8[16];
extern int G_h01_34DC[16];
extern int G_h01_34E0;
extern char G_h01_34E1;
extern int G_h01_6F24;
extern int G_h01_6F26;
extern int G_h01_6F28;
extern int G_h01_6F2A;
extern int G_h01_6F2C;
extern int G_h01_6F2E;
extern int G_h01_6F30;
extern int G_h01_6F34;
extern char G_h01_6F36;
extern char G_h01_6F37;
extern int G_h01_6F38;
extern unsigned char G_h01_6F3A;
extern unsigned char G_h01_6F3B;
extern unsigned char G_h01_10ED;
extern long G_h01_10EE;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern long G_h01_46E6;
extern char G_h01_46E0;
extern char *G_h01_5370;
extern int F_h00_435E();
extern int F_h00_57D2();
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern int F_h08_3DF4();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_330E();
extern int F_h08_4018();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_8A46();
extern int F_h08_1C30();
extern int F_h08_1D42();
extern int F_h08_1F4C();
extern int F_h00_34E0();
extern int F_h00_30F0();
extern int F_h08_3FC0();
extern int F_h00_4376();
extern int F_h00_7B00();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_09C0();
extern int F_h08_1AB8();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h08_3F70();
extern int F_h00_868C();
extern int G_h01_3426;
extern int G_h01_33F0;
extern int G_h01_33F6;
extern int G_h01_33F8;
extern int G_h01_33FE;
extern int G_h01_342C;
extern int G_h01_342E;
extern int G_h01_3434;
extern int G_h01_3462;
extern int G_h01_3464;
extern int G_h01_346A;
extern int G_h01_34A2;
extern int G_h01_34A4;
extern int G_h01_34AA;
extern int G_h01_349C;
extern char G_h01_6F29;
extern int G_h01_6F38;

recovered(P)
int P;
{
    long saved;
    long handle;
    struct Sprite spr;
    int local40, local42, local44, local46, local48, local4a, local4c, local4e;
    int local50, local52, local54, local56, local58, local5a;
    unsigned char c5b, c5c, c5d, c5e, c5f, c60, c61;
    unsigned char dummy62;
    unsigned char c63;
    char c64;
    unsigned char c65;
    int local68, local6a;
    int ret;

    c5d = 0;
    dummy62 = 1;
    F_h00_435E();
    F_h00_57D2(0x21);
    saved = G_h01_46DA;
    F_h00_0FDE(2);
    handle = F_h00_86DC("DT2:mt.arc", 1005L);
    G_h01_46DA = handle;
    F_h00_2816(G_h01_46DA);
    F_h00_291E(0x11, &G_h01_3424);
    F_h00_291E(0x10, &G_h01_33EE);
    G_h01_3424 = 0x28;
    G_h01_3426 = 0xab;
    G_h01_33EE = 8;
    G_h01_33F0 = 0xaf;
    G_h01_10EE = 0;
    G_h01_10EE = F_h00_291E(0, G_h01_10EE);
    F_h00_291E(1, &G_h01_349A);
    F_h00_291E(2, G_h01_6EB8);
    F_h00_291E(3, G_h01_6EEE);
    F_h00_291E(4, &spr);
    F_h00_291E(12, &G_h01_345A);
    F_h08_3DF4();
    switch (P) {
    case 0:
        G_h01_6EB0 = G_h01_0AC4;
        G_h01_6F3C = (struct Entry *)G_h01_10F2;
        break;
    case 1:
        G_h01_6EB0 = G_h01_0CD2;
        G_h01_6F3C = (struct Entry *)G_h01_1188;
        break;
    case 2:
        G_h01_6EB0 = G_h01_0EE0;
        G_h01_6F3C = (struct Entry *)G_h01_121E;
        break;
    default:
        G_h01_6EB0 = G_h01_0AC4;
        G_h01_6F3C = (struct Entry *)G_h01_10F2;
        break;
    }
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(4);
    F_h00_0FDE(2);
    F_h00_2816(G_h01_46DA);
    G_h01_2C2C = 0;
    G_h01_2C26 = 0;
    F_h00_330E();
    G_h01_12BB = 0;
    G_h01_6F3B = 3;
    c65 = 0;
    F_h08_4018();
    F_h00_435E();
    while (G_h01_6F3B > 0 && !c65) {
        G_h01_6F2A = 0;
        for (local42 = 1; G_h01_6EB0[local42] == 'F'; local42++)
            ;
        G_h01_6EB4 = G_h01_6EB8;
        G_h01_6F2C = local42;
        G_h01_6F24 = G_h01_6F2C * 16;
        G_h01_6F26 = 0x83;
        G_h01_6F28 = 0x14;
        G_h01_6F2E = 0;
        G_h01_34D0[0] = G_h01_6F24;
        G_h01_34D4[0] = G_h01_6F26;
        G_h01_34D8[0] = G_h01_6F28;
        G_h01_34DC[0] = G_h01_6F2E;
        G_h01_34D0[1] = G_h01_6F24;
        G_h01_34D4[1] = G_h01_6F26;
        G_h01_34D8[1] = G_h01_6F28;
        G_h01_34DC[1] = G_h01_6F2E;
        G_h01_6EB4[0x34] = 20;
        G_h01_6F30 = 0;
        c63 = 0;
        G_h01_6F36 = 0;
        local40 = 0;
        c5d = 0;
        F_h08_3FC0();
        switch (G_h01_6F3B) {
        case 3:
            G_h01_1608 = 0x500;
            G_h01_160A = 0x800;
            G_h01_160C = 0xc00;
            G_h01_160E = 0xd44;
            break;
        case 2:
            G_h01_1608 = 5;
            G_h01_160A = 8;
            G_h01_160C = 0x11c;
            G_h01_160E = 0x44d;
            break;
        case 1:
            G_h01_1608 = 0x62;
            G_h01_160A = 0x82;
            G_h01_160C = 0xb3;
            G_h01_160E = 0x4d8;
            break;
        }
        F_h00_30F0(0);
        *(int *)G_h01_6EB4 = G_h01_6F24;
        ((int *)G_h01_6EB4)[1] = G_h01_6F26;
        F_h08_1C30(c5d);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
        F_h08_1D42();
        F_h08_1F4C(c5d, 0);
        F_h00_34E0(G_h01_6EB4);
        F_h00_307C();
        G_h01_46D6 = G_h01_15E6;
        F_h00_31AA(G_h01_15E6);
        F_h08_1C30(c5d);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
        F_h08_1D42();
        F_h08_1F4C(c5d, 0);
        F_h00_34E0(G_h01_6EB4);
        F_h00_307C();
        c5e = 0;
        while (!c5e) {
            c5b = 0;
            c5b = F_h00_4376();
            c5c = (c5b & 0x80) ? 1 : 0;
            if (--local40 <= 0) {
                local40 = 0;
                switch (G_h01_6F2E) {
                case 0:
                    G_h01_6EB4 = G_h01_6EB8;
                    if (c5c) {
                        if (G_h01_6F30 == 0) {
                            G_h01_6F28 = 0x15;
                            c64 = 0;
                            local48 = 0xb;
                            local4a = 0xe;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + G_h01_6F24 + 0xb;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + G_h01_6F26 + 0xe;
                        } else {
                            G_h01_6F28 = 0x1b;
                            c64 = 8;
                            local48 = 0x17;
                            local4a = 0xe;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + G_h01_6F24 + 0x17;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + G_h01_6F26 + 0xe;
                        }
                        G_h01_6F2E = 4;
                        F_h00_57D2(0x10);
                        G_h01_6F34 = 10;
                        G_h01_6F36 = 1;
                    } else {
                        G_h01_6F36 = 0;
                        switch ((unsigned char)c5b) {
                        case 1:
                            if (G_h01_6F37 != 0) {
                                G_h01_6F2E = 10;
                                F_h00_57D2(0x13);
                            } else {
                                if (G_h01_6F30 == 0) {
                                    if (G_h01_6EB0[(long)(G_h01_6F2A + 1) * 21 + (G_h01_6F2C + 1)] == '0') {
                                        G_h01_6F28 = 0x16;
                                        G_h01_6F24 += 0x10;
                                        G_h01_6F2E = 3;
                                        F_h00_57D2(0x19);
                                        G_h01_6F34 = 0;
                                        local40 = 1;
                                    } else {
                                        G_h01_6F28 = 0x16;
                                        G_h01_6F24 += 0x10;
                                        G_h01_6F2E = 2;
                                        local40 = 1;
                                        G_h01_6F34 = 1;
                                    }
                                } else if (G_h01_6F30 == 1) {
                                    if (G_h01_6EB0[(long)(G_h01_6F2A + 1) * 21 + (G_h01_6F2C - 1)] == '8') {
                                        G_h01_6F28 = 0x1c;
                                        G_h01_6F24 -= 16;
                                        G_h01_6F2E = 3;
                                        F_h00_57D2(0x19);
                                        G_h01_6F34 = 0;
                                        local40 = 1;
                                    } else {
                                        G_h01_6F28 = 0x1c;
                                        G_h01_6F24 -= 16;
                                        G_h01_6F2E = 2;
                                        local40 = 1;
                                        G_h01_6F34 = 1;
                                    }
                                }
                            }
                            break;
                        case 5:
                            if (G_h01_6F30 == 0) {
                                if (G_h01_6F28 == 0x14)
                                    G_h01_6F24 += 16;
                                G_h01_6F28 = 0x16;
                                local40 = 5;
                            } else if (G_h01_6F30 == 1) {
                                if (G_h01_6F28 == 0x1a)
                                    G_h01_6F24 -= 16;
                                G_h01_6F28 = 0x1c;
                                local40 = 5;
                            }
                            break;
                        case 7:
                            if (G_h01_6F30 == 0) {
                                G_h01_6F28 = 0x1a;
                                G_h01_6F30 = 1;
                                G_h01_6F24 += 16;
                                local40 = 2;
                            } else {
                                if (c63 == 0)
                                    G_h01_6F28 = 0xa;
                                else
                                    G_h01_6F28 = 0xf;
                                c63 ^= 1;
                                G_h01_6F24 -= 16;
                                G_h01_6F2E = 1;
                                G_h01_6F34 = 0;
                            }
                            break;
                        case 3:
                            if (G_h01_6F30 == 1) {
                                G_h01_6F28 = 0x14;
                                G_h01_6F30 = 0;
                                G_h01_6F24 -= 16;
                                local40 = 2;
                            } else {
                                if (c63 == 0)
                                    G_h01_6F28 = 0;
                                else
                                    G_h01_6F28 = 5;
                                c63 ^= 1;
                                G_h01_6F24 += 16;
                                G_h01_6F2E = 1;
                                G_h01_6F34 = 0;
                            }
                            break;
                        default:
                            if (G_h01_6F28 == 0x16)
                                G_h01_6F24 -= 16;
                            else if (G_h01_6F28 == 0x1c)
                                G_h01_6F24 += 16;
                            G_h01_6F28 = (G_h01_6F30 == 0) ? 0x14 : 0x1a;
                            break;
                        }
                    }
                    break;
                case 1:
                    G_h01_6EB4 = G_h01_6EB8;
                    local40 = 0;
                    G_h01_6F34++;
                    if (G_h01_6F34 == 3)
                        F_h00_57D2(10);
                    if (G_h01_6F30 == 0) {
                        if (G_h01_6F34 < 5)
                            G_h01_6F28++;
                        else
                            G_h01_6F2E = 0;
                    } else {
                        if (G_h01_6F34 < 5)
                            G_h01_6F28++;
                        else
                            G_h01_6F2E = 0;
                    }
                    break;
                case 2:
                    if (G_h01_6F34 != 0) {
                        G_h01_6EB4 = G_h01_6EEE;
                        if (G_h01_6F30 == 0)
                            G_h01_6F28 = 0;
                        else
                            G_h01_6F28 = 6;
                        local40 = 1;
                        G_h01_6F26 -= 8;
                        G_h01_6F34 = 0;
                    } else {
                        G_h01_6EB4 = G_h01_6EB8;
                        F_h00_57D2(10);
                        if (G_h01_6F30 == 0) {
                            G_h01_6F28 = 0x14;
                            G_h01_6F24 += 16;
                        } else {
                            G_h01_6F28 = 0x1a;
                            G_h01_6F24 -= 16;
                        }
                        G_h01_6F26 += 8;
                        local40 = 0;
                        G_h01_6F2E = 0;
                    }
                    break;
                case 3:
                    G_h01_6F34++;
                    G_h01_6EB4 = G_h01_6EEE;
                    if (G_h01_6F30 == 0) {
                        switch (G_h01_6F34) {
                        case 1:
                            G_h01_6F28 = 0;
                            G_h01_6F24 -= 8;
                            G_h01_6F26 -= 16;
                            break;
                        case 2:
                            G_h01_6F28 = 1;
                            G_h01_6F24 += 8;
                            G_h01_6F26 -= 10;
                            local40 = 2;
                            break;
                        case 3:
                            G_h01_6F28 = 2;
                            local40 = 2;
                            break;
                        case 4:
                            G_h01_6F28 = 3;
                            G_h01_6F26++;
                            local40 = 2;
                            break;
                        case 0:
                        case 5:
                        default:
                            G_h01_6F28 = 0x14;
                            G_h01_6EB4 = G_h01_6EB8;
                            G_h01_6F26 -= 15;
                            G_h01_6F2E = 0;
                            G_h01_6F2A++;
                            local40 = 0;
                            break;
                        }
                    } else {
                        switch (G_h01_6F34) {
                        case 1:
                            G_h01_6F28 = 6;
                            G_h01_6F26 -= 16;
                            break;
                        case 2:
                            G_h01_6F28 = 7;
                            G_h01_6F24 -= 8;
                            G_h01_6F26 -= 10;
                            local40 = 2;
                            break;
                        case 3:
                            G_h01_6F28 = 8;
                            local40 = 2;
                            break;
                        case 4:
                            G_h01_6F28 = 9;
                            G_h01_6F26 += 1;
                            local40 = 2;
                            break;
                        case 0:
                        case 5:
                        default:
                            G_h01_6F28 = 0x1a;
                            G_h01_6EB4 = G_h01_6EB8;
                            G_h01_6F24 += 8;
                            G_h01_6F26 -= 15;
                            G_h01_6F2E = 0;
                            G_h01_6F2A++;
                            local40 = 0;
                            break;
                        }
                    }
                    break;
                case 4:
                    local40 = 0;
                    if (!c5c && G_h01_6F34 > 0)
                        c5c = 1;
                    if (c5c) {
                        if (G_h01_6F30 == 0) {
                            c64--;
                            c64 &= 0xf;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + G_h01_6F24 + 11;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + G_h01_6F26 + 14;
                        } else {
                            c64++;
                            c64 &= 0xf;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + G_h01_6F24 + 0x17;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + G_h01_6F26 + 14;
                        }
                        G_h01_6F34--;
                        if (c64 == 4)
                            F_h00_57D2(0x10);
                        else if (c64 == 12)
                            F_h00_57D2(0x1d);
                    } else {
                        if (G_h01_6F30 == 0) {
                            local50 = -G_h01_0AA2[2 * (15 - c64) + 1];
                            local52 = -G_h01_0AA2[2 * (15 - c64)];
                            c64 -= 2;
                            c64 &= 0xf;
                        } else {
                            local50 = -G_h01_0AA2[2 * c64 + 1];
                            local52 = G_h01_0AA2[2 * c64];
                            c64 += 2;
                            c64 &= 0xf;
                        }
                        local4c += local50;
                        local4e += local52;
                        G_h01_6F34 = (4 >> (G_h01_46E0)) + 8;
                        G_h01_6F2E = 5;
                        F_h00_57D2(12);
                    }
                    break;
                case 5:
                    if (G_h01_6F34 > 0) {
                        G_h01_6F34--;
                        local4c += local50;
                        local4e += local52;
                        if (local4e <= 0 || ((local4e + 8) % 40 < 16 && local4e < G_h01_6F26 + 16)) {
                            if (local4e < 0)
                                local4e = 0;
                            if (local4c < 0)
                                local4c = 0;
                            if (local4c > 320)
                                local4c = 320;
                            c5f = c5d + (160 - (local4e + 8)) / 40 + 1;
                            if (c5f < 25) {
                                c60 = (int)G_h01_6EB0[(long)c5f * 21 + (local4c >> 4)];
                                switch (c60) {
                                case '0': case '8':
                                    if (local4c > G_h01_6F24 + 12) {
                                        local56 = (local4c - (G_h01_6F24 + 12) >> 1) + G_h01_6F26 + 16;
                                        local58 = (local4c - (G_h01_6F24 + 12) >> 2) - 8;
                                        local5a = 0;
                                        c61 = 1;
                                        G_h01_6F24 += 24;
                                    } else {
                                        local56 = (G_h01_6F24 + 12 - local4c >> 1) + G_h01_6F26 + 16;
                                        local58 = (G_h01_6F24 + 12 - local4c >> 2) - 8;
                                        local5a = 0;
                                        c61 = 0;
                                        G_h01_6F24 -= 24;
                                    }
                                    if (local56 > 128)
                                        local56 = 128;
                                    if (c60 == '0') {
                                        G_h01_6F28 = 0x18;
                                        G_h01_6F30 = 0;
                                        local48 = 0x15;
                                        local4c = (local4c & 0xfff0) + 5;
                                        local54 = local4c - 0x15;
                                    } else {
                                        G_h01_6F28 = 0x1e;
                                        G_h01_6F30 = 1;
                                        local48 = 0xb;
                                        local4c = (local4c & 0xfff0) + 0xb;
                                        local54 = local4c - 0xb;
                                    }
                                    local4e = 160 - (c5f - c5d) * 40;
                                    local4a = 0;
                                    F_h00_57D2(0x11);
                                    G_h01_6F2E = 6;
                                    break;
                                case 1: case 2: case 3: case 4: case 5: case 6: case 7:
                                    if (local52 > 0) {
                                        local52 = -4;
                                        local4e -= 16;
                                    } else {
                                        local52 = 4;
                                        local4e += 16;
                                    }
                                    break;
                                case 'F':
                                default:
                                    break;
                                }
                            }
                        }
                    } else {
                        F_h00_57D2(0x16);
                        G_h01_6F36 = 0;
                        G_h01_6F2E = 0;
                        if (G_h01_6F30 == 0)
                            G_h01_6F28 = 0x14;
                        else
                            G_h01_6F28 = 0x1a;
                    }
                    break;
                case 6:
                    if (local54 > G_h01_6F24) {
                        if (c61 == 1) {
                            G_h01_6F24 += 8;
                            G_h01_6F26 += 2;
                        } else {
                            G_h01_6F24 -= 8;
                            G_h01_6F26 -= 2;
                        }
                    } else {
                        if (c61 == 1) {
                            G_h01_6F24 += 8;
                            G_h01_6F26 -= 2;
                        } else {
                            G_h01_6F24 -= 8;
                            G_h01_6F26 += 2;
                        }
                    }
                    if (G_h01_6F26 > 128)
                        G_h01_6F26 = 128;
                    if (G_h01_6F24 < 0) {
                        G_h01_6F24 = 0;
                        local58--;
                    } else if (G_h01_6F26 > 0x118) {
                        G_h01_6F24 = 0x118;
                        local58--;
                    }
                    local5a++;
                    if (local5a >= local58) {
                        local58 -= 8;
                        local5a = 0;
                        c61 ^= 1;
                        F_h00_57D2(c61 ? 0x5a : 0x5d);
                    }
                    if (local58 <= 0) {
                        G_h01_6F24 = local54;
                        G_h01_6F2E = 7;
                        F_h00_57D2(0);
                        G_h01_6F34 = 0;
                        local40 = 1;
                    }
                    break;
                case 7:
                    if (G_h01_6F26 - 16 < local4e) {
                        G_h01_6EB4 = G_h01_6EEE;
                        switch (G_h01_6F34) {
                        case 0:
                            G_h01_6F36 = 0;
                            G_h01_6F26 = local4e - 16;
                            if (G_h01_6F30 == 0)
                                G_h01_6F28 = 1;
                            else
                                G_h01_6F28 = 7;
                            local40 = 3;
                            break;
                        case 1:
                            G_h01_6F28 = G_h01_6F30 == 0 ? 2 : 8;
                            local40 = 3;
                            break;
                        case 2:
                            F_h00_57D2(0x77);
                            G_h01_6F28 = G_h01_6F30 == 0 ? 3 : 9;
                            local40 = 3;
                            break;
                        case 3:
                        default:
                            G_h01_6F24 = local4c & 0xfff0;
                            if (G_h01_6F30 == 1)
                                G_h01_6F26 -= 16;
                            G_h01_6F26 = local4e - 29;
                            G_h01_6F2E = 0;
                            G_h01_6EB4 = G_h01_6EB8;
                            if (G_h01_6F30 == 0)
                                G_h01_6F28 = 0x14;
                            else
                                G_h01_6F28 = 0x1a;
                            local40 = 0;
                            break;
                        }
                        G_h01_6F34++;
                    } else {
                        G_h01_6EB4 = G_h01_6EB8;
                        switch (G_h01_6F28) {
                        case 30:
                            G_h01_6F26 -= 9;
                            G_h01_6F28 = 0x1f;
                            local40 = 2;
                            break;
                        case 31:
                            G_h01_6F26 -= 6;
                            G_h01_6F28 = 0x1e;
                            local40 = 3;
                            break;
                        case 24:
                            G_h01_6F26 -= 9;
                            G_h01_6F28 = 0x19;
                            local40 = 2;
                            break;
                        case 25:
                            G_h01_6F26 -= 6;
                            G_h01_6F28 = 0x18;
                            local40 = 3;
                            break;
                        }
                    }
                    break;
                case 8:
                    if (G_h01_6F26 > 128) {
                        G_h01_6F3B--;
                        c5e = 1;
                        continue;
                    }
                    G_h01_6EB4 = G_h01_6EEE;
                    if (G_h01_6EB0[(long)G_h01_6F2A * 21 + G_h01_6F2C] != 'F' && G_h01_6F26 % 40 < 16) {
                        G_h01_6F28 = G_h01_6F30 == 0 ? 5 : 11;
                        local40 = 0;
                    } else {
                        G_h01_6F28 = G_h01_6F30 == 0 ? 4 : 10;
                        local40 = 1;
                    }
                    G_h01_6F26 += 8;
                    G_h01_6F36 = 0;
                    break;
                case 9:
                    G_h01_6EB4 = G_h01_6EEE;
                    if (G_h01_6F26 > 120) {
                        G_h01_6EB4 = G_h01_6EB8;
                        G_h01_6F28 = G_h01_6F30 == 0 ? 20 : 26;
                        G_h01_6F26 = 0x83;
                        G_h01_6F2E = 0;
                        F_h00_57D2(0x77);
                        local40 = 0;
                    } else if (G_h01_6EB0[(long)G_h01_6F2A * 21 + G_h01_6F2C] != 'F' && G_h01_6F26 % 40 > 16 && G_h01_6F34 > 10) {
                        G_h01_6EB4 = G_h01_6EB8;
                        G_h01_6F28 = G_h01_6F30 == 0 ? 20 : 26;
                        G_h01_6F26 = 160 - (G_h01_6F2A - c5d) * 40 - 29;
                        G_h01_6F2E = 0;
                        F_h00_57D2(0x77);
                        local40 = 0;
                    } else {
                        G_h01_6F26 += 8;
                        G_h01_6F28 = 10;
                        G_h01_6F34++;
                    }
                    G_h01_6F36 = 0;
                    break;
                case 10:
                    if (G_h01_6F2A < G_h01_6F3A)
                        G_h01_6F26 -= 40;
                    else if (G_h01_6F2A > G_h01_6F3A)
                        G_h01_6F26 += 40;
                    else {
                        G_h01_6F24 = G_h01_6F38;
                        G_h01_6F2E = 0;
                        F_h00_57D2(0x14);
                        G_h01_6EB4 = G_h01_6EB8;
                        G_h01_6F28 = G_h01_6F30 == 0 ? 20 : 26;
                    }
                    G_h01_6F36 = 0;
                    break;
                }
            }
            if (G_h01_6F24 < 0)
                G_h01_6F24 = 0;
            if (G_h01_6F24 > 0x120)
                G_h01_6F24 = 0x120;
            G_h01_6F2A = c5d + (160 - (G_h01_6F26 + 16)) / 40;
            G_h01_6F2C = (G_h01_6F24 >> 4) - G_h01_6F30 + 1;
            if (G_h01_6F28 == 0x16)
                G_h01_6F2C--;
            else if (G_h01_6F28 == 0x1c)
                G_h01_6F2C++;
            if (G_h01_6F2C == local68 && G_h01_6F2A == local6a && (G_h01_6F28 == 0x14 || G_h01_6F28 == 0x1a))
                G_h01_10ED++;
            else {
                local68 = G_h01_6F2C;
                local6a = G_h01_6F2A;
                G_h01_10ED = 0;
            }
            if (G_h01_6F2E == 0 && G_h01_6EB0[(long)G_h01_6F2A * 21 + G_h01_6F2C] == 'F' && G_h01_6F2A != 0) {
                if (G_h01_6EB0[(long)(G_h01_6F2A - 1) * 21 + G_h01_6F2C] != 'F') {
                    G_h01_6F2A--;
                    G_h01_6F26 = 160 - (G_h01_6F2A - c5d) * 40 - 29;
                    G_h01_6EB4 = G_h01_6EB8;
                    if (G_h01_6F30 == 0) {
                        G_h01_6F28 = 0x16;
                        G_h01_6F24 += 16;
                    } else {
                        G_h01_6F28 = 0x1c;
                        G_h01_6F24 -= 16;
                    }
                    local40 = 2;
                } else {
                    G_h01_6F2E = 8;
                    F_h00_57D2(0xf);
                    G_h01_6F26 += 8;
                    G_h01_6F34 = 0;
                }
            }
            if (G_h01_6F2A > c5d + 2) {
                local42 = 10;
                do {
                    G_h01_6F26 += 10;
                    local4e += 10;
                    local46 = (((unsigned int)(c5d + 5)) % 5) * 40;
                    F_h00_8A46(G_h01_10EE, 0L, (long)(local46 + 40 - local42), G_h01_46D2, 0L, 0L, 320L, (long)local42, 192L, 255L, 0L);
                    if (c5d + 5 < 25) {
                        local44 = 0;
                        do {
                            if (G_h01_6EB0[(long)(c5d + 5) * 21 + local44] != 'F') {
                                G_h01_34CE = G_h01_6EB0[(long)(c5d + 5) * 21 + local44] - '0';
                                G_h01_349A = local44 * 16;
                                G_h01_349C = local42 - 40;
                                F_h00_34E0(&G_h01_349A);
                            }
                            local44++;
                        } while (local44 < 20);
                    }
                    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, (long)local42, 320L, (long)(168 - local42), 192L, 255L, 0L);
                    F_h08_1F4C(c5d, local42);
                    *(int *)G_h01_6EB4 = G_h01_6F24;
                    ((int *)G_h01_6EB4)[1] = G_h01_6F26;
                    G_h01_6EB4[0x34] = G_h01_6F29;
                    if (G_h01_6F2E != 10)
                        F_h00_34E0(G_h01_6EB4);
                    if (G_h01_6F36 != 0) {
                        if (local4c < 0)
                            local4c = 0;
                        else if (local4c > 0x136)
                            local4c = 0x136;
                        if (local4e < 0)
                            local4e = 0;
                        else if (local4e > 0xbe)
                            local4e = 0xbe;
                        *G_h01_5370 = 0x10;
                        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
                        F_h00_8B4C(G_h01_46CA, (long)(G_h01_6F24 + local48), (long)(G_h01_6F26 + local4a));
                        F_h00_8AA8(G_h01_46CA, (long)local4c, (long)local4e);
                    }
                    F_h08_1D42();
                    G_h01_34D0[G_h01_34E0] = G_h01_6F24;
                    G_h01_34D4[G_h01_34E0] = G_h01_6F26;
                    G_h01_34D8[G_h01_34E0] = G_h01_6F28;
                    G_h01_34DC[G_h01_34E0] = G_h01_6F2E;
                    G_h01_34E1 ^= 1;
                    F_h00_307C();
                    local42 += 10;
                } while (local42 <= 40);
                c5d++;
                F_h08_1C30(c5d);
                F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
            } else {
                if (G_h01_6F2A <= c5d && c5d > 0 && G_h01_6F2E != 8 && G_h01_6F2E != 6 && G_h01_6F2E != 7) {
                    local42 = 10;
                    do {
                        G_h01_6F26 -= 10;
                        local4e -= 10;
                        F_h00_8A46(G_h01_46CE, 0L, (long)local42, G_h01_46D2, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
                        if (local42 > 32 && c5d > 0) {
                            local46 = ((unsigned int)(c5d - 1) % 5) * 40;
                            F_h00_8A46(G_h01_10EE, 0L, (long)local46, G_h01_46D2, 0L, (long)(200 - local42), 320L, (long)(local42 - 32), 192L, 255L, 0L);
                            local44 = 0;
                            do {
                                if (G_h01_6EB0[(long)(c5d - 1) * 21 + local44] != 'F') {
                                    G_h01_34CE = G_h01_6EB0[(long)(c5d - 1) * 21 + local44] - '0';
                                    G_h01_349A = local44 * 16;
                                    G_h01_349C = 200 - local42;
                                    F_h00_34E0(&G_h01_349A);
                                }
                                local44++;
                            } while (local44 < 20);
                        }
                        F_h08_1F4C(c5d, -local42);
                        *(int *)G_h01_6EB4 = G_h01_6F24;
                        ((int *)G_h01_6EB4)[1] = G_h01_6F26;
                        G_h01_6EB4[0x34] = G_h01_6F29;
                        if (G_h01_6F2E != 10)
                            F_h00_34E0(G_h01_6EB4);
                        if (G_h01_6F36 != 0) {
                            if (local4c < 0)
                                local4c = 0;
                            else if (local4c > 0x136)
                                local4c = 0x136;
                            if (local4e < 0)
                                local4e = 0;
                            else if (local4e > 0xbe)
                                local4e = 0xbe;
                            *G_h01_5370 = 0x10;
                            F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
                            F_h00_8B4C(G_h01_46CA, (long)(G_h01_6F24 + local48), (long)(G_h01_6F26 + local4a));
                            F_h00_8AA8(G_h01_46CA, (long)local4c, (long)local4e);
                        }
                        F_h08_1D42();
                        G_h01_34D0[G_h01_34E0] = G_h01_6F24;
                        G_h01_34D4[G_h01_34E0] = G_h01_6F26;
                        G_h01_34D8[G_h01_34E0] = G_h01_6F28;
                        G_h01_34DC[G_h01_34E0] = G_h01_6F2E;
                        G_h01_34E1 ^= 1;
                        F_h00_307C();
                        local42 += 10;
                    } while (local42 <= 40);
                    c5d--;
                    F_h08_1C30(c5d);
                    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
                } else {
                    F_h08_1AB8(c5d);
                    F_h00_34E0(&G_h01_3424);
                    F_h00_09C0(168, 174, G_h01_46E6, 1, 26, 1);
                }
            }
            if (G_h01_6F2A == 24 && G_h01_6F2E == 0) {
                c65 = 1;
                c5e = 1;
            }
            F_h08_1F4C(c5d, 0);
            *(int *)G_h01_6EB4 = G_h01_6F24;
            ((int *)G_h01_6EB4)[1] = G_h01_6F26;
            G_h01_6EB4[0x34] = G_h01_6F29;
            if (G_h01_6F2E != 10)
                F_h00_34E0(G_h01_6EB4);
            if (G_h01_6F36 != 0) {
                *G_h01_5370 = 0x10;
                if (local4c < 0)
                    local4c = 0;
                else if (local4c > 0x136)
                    local4c = 0x136;
                if (local4e < 0)
                    local4e = 0;
                else if (local4e > 0xbe)
                    local4e = 0xbe;
                F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
                F_h00_8B4C(G_h01_46CA, (long)(G_h01_6F24 + local48), (long)(G_h01_6F26 + local4a));
                F_h00_8AA8(G_h01_46CA, (long)local4c, (long)local4e);
            }
            if (G_h01_6F2E == 4 || G_h01_6F2E == 5) {
                spr.x = local4c;
                spr.y = local4e - 3;
                spr.st = c64;
                F_h00_34E0(&spr);
                if (spr.y > 160)
                    F_h08_1D42();
            }
            G_h01_34D0[G_h01_34E0] = G_h01_6F24;
            G_h01_34D4[G_h01_34E0] = G_h01_6F26;
            G_h01_34D8[G_h01_34E0] = G_h01_6F28;
            G_h01_34DC[G_h01_34E0] = G_h01_6F2E;
            G_h01_34E1 ^= 1;
            F_h00_307C();
        }
        F_h00_57D2(0);
        ret = c65;
        F_h00_330E();
    }
    F_h00_330E();
    F_h00_4EC6();
    F_h00_3AE4(&G_h01_6EC8, G_h01_6EC0, G_h01_6EC2);
    F_h00_3AE4(&G_h01_6EFE, G_h01_6EF6, G_h01_6EF8);
    F_h00_3AE4(&G_h01_34AA, G_h01_34A2, G_h01_34A4);
    F_h00_3AE4(&G_h01_3434, G_h01_342C, G_h01_342E);
    F_h00_3AE4(&G_h01_33FE, G_h01_33F6, G_h01_33F8);
    F_h00_3AE4(&G_h01_346A, G_h01_3462, G_h01_3464);
    F_h00_3AE4(spr.data, spr.w, spr.h);
    F_h00_3B84(G_h01_10EE);
    F_h08_3F70();
    F_h00_868C(handle);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
    return ret;
}
