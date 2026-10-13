/* Worker haiku-fn-ov05_F_3B6C: structured candidate for ov05_F_3B6C (v1). */
struct Lookup { int index; int f2; };
struct Record { char b0[4]; int value; char rest[8]; };
struct Pos { int x; int y; };

extern int G_h01_5E42;
extern int G_h01_5E64[1][2];
extern struct Lookup G_h01_5E66[16];
extern struct Record G_h01_606C[16];
extern char G_h01_5E5F;
extern char G_h01_5E60;
extern char G_h01_5E61;
extern char G_h01_5E62;
extern char G_h01_5E58;
extern long G_h01_5484[17];
extern struct Pos *G_h01_55A0;
extern struct Pos *G_h01_5898;
extern char G_h01_54C8;
extern char G_h01_54FE;
extern char G_h01_5534;
extern char G_h01_556A;
extern char G_h01_55A4;
extern char G_h01_55DA;
extern char G_h01_5610;
extern char G_h01_5646;
extern char G_h01_567C;
extern char G_h01_56B2;
extern char G_h01_56E8;
extern char G_h01_571E;
extern char G_h01_5754;
extern char G_h01_578A;
extern char G_h01_57C0;
extern char G_h01_57F6;
extern char G_h01_582C;
extern char G_h01_5862;
extern char G_h01_589C;
extern char G_h01_58D2;
extern char G_h01_5908;
extern char G_h01_59E0;
extern char G_h01_5A16;
extern char G_h01_5A4C;
extern char G_h01_5A82;
extern char G_h01_5AB8;
extern char G_h01_5AEE;
extern char G_h01_5B24;
extern char G_h01_5B5A;
extern char G_h01_5B90;
extern char G_h01_5BC6;
extern char G_h01_5BFC;
extern char G_h01_5C32;
extern char G_h01_5C68;
extern char G_h01_5C9E;
extern char G_h01_5D40;
extern unsigned int F_h00_463E();
extern int F_h00_0FDE();
extern long F_h00_291E();
extern int F_h05_42E6();
extern int F_h05_467E();

recovered()
{
    unsigned int s2;
    int j;
    int cursor;
    int delta;
    unsigned int kind;
    unsigned int r;

    kind = 0;
    G_h01_5E5F = 0;
    G_h01_5E61 = 0;
    G_h01_5E60 = 0;
    G_h01_5E62 = 0;
    for (j = 0; j < 130; j++) {
        G_h01_5E66[j].index = -1;
        G_h01_5E64[j][0] = 0;
    }
    for (j = 0; j < 260; j++) {
        G_h01_606C[j].b0[0] = -1;
        G_h01_606C[j].rest[6] = -1;
    }
    cursor = 0;
    delta = G_h01_5E42 / 4;
    kind = F_h00_463E() % 100;
    if (kind < 8)
        kind = 7;
    else if (kind < 14)
        kind = 3;
    else if (kind < 18)
        kind = 1;
    else
        kind = 20;
    F_h05_42E6(delta, kind, &cursor);

    s2 = F_h00_463E() % 100;
    if (s2 < 33) {
        s2 = F_h00_463E() & 1;
        if (s2 == 1) {
            F_h05_42E6(delta, 21, &cursor);
            F_h05_42E6(delta, kind, &cursor);
        } else {
            F_h05_42E6(delta, kind, &cursor);
            F_h05_42E6(delta, 21, &cursor);
        }
        if (kind != 20) {
            kind = F_h00_463E() % 100;
            if (kind < 10)
                kind = 7;
            else if (kind < 20)
                kind = 3;
            else if (kind < 30)
                kind = 1;
            else
                kind = 20;
        }
        F_h05_42E6(delta, kind, &cursor);
    } else if (s2 < 66) {
        for (j = 0; j < 2; j++)
            F_h05_42E6(delta, 21, &cursor);
        F_h05_42E6(delta, kind, &cursor);
    } else {
        for (j = 0; j < 3; j++) {
            if (kind != 20 && j == 1) {
                r = F_h00_463E() % 100;
                if (r < 10)
                    r = 7;
                else if (kind < 20)
                    r = 3;
                else if (kind < 30)
                    r = 1;
                else
                    r = 20;
                F_h05_42E6(delta, r, &cursor);
            } else {
                F_h05_42E6(delta, kind, &cursor);
            }
        }
    }

    G_h01_5E64[0][0] = 15;
    G_h01_5E66[0].f2 = 16;
    G_h01_5E64[G_h01_5E42 - 1][0] = 15;
    G_h01_5E64[G_h01_5E42][0] = 16;

    for (j = 0; j < 17; j++)
        G_h01_5484[j] = 0;
    F_h00_0FDE(1);
    G_h01_5484[0] = F_h00_291E(0, G_h01_5484[0]);
    G_h01_5484[1] = F_h00_291E(1, G_h01_5484[1]);
    G_h01_5484[2] = F_h00_291E(2, G_h01_5484[2]);
    G_h01_5484[3] = F_h00_291E(3, G_h01_5484[3]);
    G_h01_5484[4] = F_h00_291E(4, G_h01_5484[4]);
    G_h01_5484[5] = F_h00_291E(5, G_h01_5484[5]);
    G_h01_5484[6] = F_h00_291E(6, G_h01_5484[6]);
    G_h01_5484[7] = F_h00_291E(7, G_h01_5484[7]);
    G_h01_5484[8] = F_h00_291E(8, G_h01_5484[8]);
    G_h01_5484[9] = F_h00_291E(9, G_h01_5484[9]);
    G_h01_5484[10] = F_h00_291E(10, G_h01_5484[10]);
    G_h01_5484[11] = F_h00_291E(11, G_h01_5484[11]);
    G_h01_5484[12] = F_h00_291E(12, G_h01_5484[12]);
    G_h01_5484[13] = F_h00_291E(13, G_h01_5484[13]);
    G_h01_5484[14] = F_h00_291E(14, G_h01_5484[14]);
    G_h01_5484[15] = F_h00_291E(15, G_h01_5484[15]);
    G_h01_5484[16] = F_h00_291E(16, G_h01_5484[16]);

    F_h00_291E(0x11, &G_h01_55A4);
    F_h00_291E(0x12, &G_h01_55DA);
    F_h00_291E(0x13, &G_h01_5610);
    F_h00_291E(0x14, &G_h01_567C);
    F_h00_291E(0x15, &G_h01_56B2);
    F_h00_291E(0x16, &G_h01_56E8);
    F_h00_291E(0x17, &G_h01_571E);
    F_h00_291E(0x18, &G_h01_5754);
    F_h00_291E(0x19, &G_h01_578A);
    F_h00_291E(0x1a, &G_h01_54C8);
    F_h00_291E(0x1b, &G_h01_54FE);
    F_h00_291E(0x20, &G_h01_5646);
    F_h00_291E(0x21, &G_h01_5534);
    F_h00_291E(0x22, &G_h01_556A);

    G_h01_55A0 = 0;
    if ((s2 = F_h00_463E() % 6) == 0) {
        G_h01_55A0 = (struct Pos *)F_h00_291E(0x23, G_h01_55A0);
        G_h01_5E61 = 1;
    } else if (s2 == 1) {
        G_h01_55A0 = (struct Pos *)F_h00_291E(0x24, G_h01_55A0);
        G_h01_5E61 = 2;
    } else if (s2 == 2) {
        G_h01_55A0 = (struct Pos *)F_h00_291E(0x25, G_h01_55A0);
        G_h01_5E61 = 3;
    } else if (s2 == 3) {
        G_h01_55A0 = (struct Pos *)F_h00_291E(0x26, G_h01_55A0);
        G_h01_5E61 = 4;
    } else if (s2 == 4) {
        G_h01_55A0 = (struct Pos *)F_h00_291E(0x27, G_h01_55A0);
        G_h01_5E61 = 5;
    } else {
        G_h01_5898 = 0;
        G_h01_5898 = (struct Pos *)F_h00_291E(0x1c, G_h01_5898);
        G_h01_5E60 = 1;
    }

    if (G_h01_5E58 != 0) {
        F_h00_291E(0x3b, &G_h01_5C68);
        F_h00_291E(0x3c, &G_h01_5C9E);
    } else if (F_h00_463E() % 100 < 90) {
        if (G_h01_5E61 != 3 && G_h01_5E61 != 5 && G_h01_5E60 == 0)
            F_h00_291E(0x28, &G_h01_57C0);
        else
            F_h00_291E(0x29, &G_h01_57C0);
        F_h00_291E(0x29, &G_h01_57F6);
        F_h00_291E(0x2a, &G_h01_582C);
        F_h00_291E(0x2b, &G_h01_5862);
        G_h01_5E5F = 1;
    } else if (G_h01_5E61 != 3 && G_h01_5E61 != 5 && G_h01_5E60 == 0) {
        F_h00_291E(0x1d, &G_h01_589C);
        F_h00_291E(0x1e, &G_h01_58D2);
        F_h00_291E(0x1f, &G_h01_5908);
        G_h01_5E62 = 1;
    }

    F_h00_291E(0x2c, &G_h01_59E0);
    F_h00_291E(0x2d, &G_h01_5A16);
    F_h00_291E(0x2e, &G_h01_5A4C);
    F_h00_291E(0x2f, &G_h01_5A82);
    F_h00_291E(0x30, &G_h01_5AB8);
    F_h00_291E(0x31, &G_h01_5AEE);
    F_h00_291E(0x34, &G_h01_5B24);
    F_h00_291E(0x35, &G_h01_5B5A);
    F_h00_291E(0x36, &G_h01_5B90);
    F_h00_291E(0x37, &G_h01_5BC6);
    F_h00_291E(0x38, &G_h01_5BFC);
    F_h00_291E(0x39, &G_h01_5C32);
    F_h00_291E(0x3a, &G_h01_5D40);
    F_h05_467E(G_h01_5E42);
}

/* Declarations already used by canonical sources: candidate views, not provenance. */
extern unsigned int F_h00_463E();
extern int G_h01_5E64[1][2];

F_h05_42E6(delta, kind, p)
int delta;
char kind;
int *p;
{
    int i;
    unsigned int r;

    i = *p;
    *p = *p + delta;
    if (i == 0)
        i = 2;
    if (kind == 21) {
        for (; i < *p; i++) {
            if (G_h01_5E64[i - 1][0] != 12 && G_h01_5E64[i - 1][0] != 14)
                G_h01_5E64[i][0] = 14;
            else
                G_h01_5E64[i][0] = 12;
        }
    } else {
        for (; i < *p; i++) {
            if (G_h01_5E64[i - 1][0] == 12) {
                G_h01_5E64[i][0] = 13;
                continue;
            }
            G_h01_5E64[i][0] = 0;
            r = F_h00_463E() % 100;
            if (G_h01_5E64[i - 1][0] == 1)
                G_h01_5E64[i][0] = 2;
            else if (G_h01_5E64[i - 1][0] == 3)
                G_h01_5E64[i][0] = 4;
            else if (G_h01_5E64[i - 1][0] == 5)
                G_h01_5E64[i][0] = 6;
            else if (G_h01_5E64[i - 1][0] == 7)
                G_h01_5E64[i][0] = 11;
            else if (G_h01_5E64[i - 1][0] == 11)
                G_h01_5E64[i][0] = 8;
            else if (G_h01_5E64[i - 1][0] == 9)
                G_h01_5E64[i][0] = 10;
            else if (kind == 7 && i < *p - 2 && F_h00_463E() % 100 < 95)
                G_h01_5E64[i][0] = 7;
            else if (kind == 3 && i < *p - 2 && F_h00_463E() % 100 < 75)
                G_h01_5E64[i][0] = 3;
            else if (kind == 1 && i < *p - 2 && F_h00_463E() % 100 < 75)
                G_h01_5E64[i][0] = 1;
            else if (r < 80) {
                if (i < *p - 2 && kind == 20) {
                    r = F_h00_463E() % 5;
                    switch (r) {
                    case 0:
                        G_h01_5E64[i][0] = 1;
                        break;
                    case 1:
                        G_h01_5E64[i][0] = 3;
                        break;
                    case 2:
                        G_h01_5E64[i][0] = 5;
                        break;
                    case 3:
                        G_h01_5E64[i][0] = 7;
                        break;
                    case 4:
                        G_h01_5E64[i][0] = 9;
                        break;
                    default:
                        break;
                    }
                }
            }
        }
    }
}

/* Worker haiku-fn-ov05_F_467E: structured candidate for ov05_F_467E (v1). */
struct Item { char a; char pad[3]; int b; int unused; int c; int d; char e; char f; };
struct Lookup { int index; int pad; };
struct Record { char pad[4]; int value; char pad2[8]; };
struct Pos { int x; int y; };
struct Ent { int x; int y; char rest[50]; };
extern char G_h01_46E0;
extern int G_h01_5E42;
extern int G_h01_5E64[1][2];
extern struct Lookup G_h01_5E66[16];
extern struct Record G_h01_606C[16];
extern char G_h01_5E5F;
extern char G_h01_5E60;
extern char G_h01_5E61;
extern char G_h01_5E62;
extern int G_h01_54CC;
extern int G_h01_54CE;
extern int G_h01_5502;
extern int G_h01_5504;
extern struct Ent G_h01_5538[2];
extern struct Ent G_h01_57C4[2];
extern struct Pos *G_h01_55A0;
extern struct Pos *G_h01_5898;
extern int G_h01_55A8;
extern int G_h01_55AA;
extern int G_h01_55DE;
extern int G_h01_55E0;
extern int G_h01_564A;
extern int G_h01_564C;
extern int G_h01_5680;
extern int G_h01_5682;
extern int G_h01_56EC;
extern int G_h01_56EE;
extern int G_h01_5758;
extern int G_h01_575A;
extern int G_h01_578E;
extern int G_h01_5790;
extern int G_h01_5830;
extern int G_h01_5832;
extern int G_h01_5866;
extern int G_h01_5868;
extern int G_h01_58A0;
extern int G_h01_58A2;
extern int G_h01_590C;
extern int G_h01_590E;
extern int G_h01_59E4;
extern int G_h01_59E6;
extern int G_h01_5A1A;
extern int G_h01_5A1C;
extern int G_h01_5A50;
extern int G_h01_5A52;
extern int G_h01_5AF2;
extern int G_h01_5AF4;
extern int G_h01_5B28;
extern int G_h01_5B2A;
extern int G_h01_5C00;
extern int G_h01_5C02;
extern int G_h01_5D44;
extern int G_h01_5D46;
extern unsigned int F_h00_463E();
extern int F_h05_5BBC();
extern int F_h05_5C08();

F_h05_467E(n)
int n;
{
    unsigned int i;
    unsigned int r;
    unsigned int side;
    int total;
    struct Item *rp;
    int count;
    unsigned int k;
    char pr0, pr1, pr2, pr3, pr4, pr5, pr6, pr7, pr8, pr9;
    char f1b, f1c, f1d, f1e, f1f, f20, f21, f22, f23, f24;
    int sh;

    total = 2;
    pr0 = 0; pr1 = 0; pr2 = 0; pr3 = 0; pr4 = 0;
    pr5 = 0; pr6 = 0; pr7 = 0; pr8 = 0; pr9 = 0;
    f1b = 0; f1c = 0; f1d = 0; f1e = 0; f1f = 0;
    f20 = 0; f21 = 0; f22 = 0; f23 = 0; f24 = 0;
    sh = 3;
    rp = (struct Item *)G_h01_606C;
    G_h01_5E66[0].index = 0;
    F_h05_5BBC(0, 0xb0 - G_h01_54CE - 8, 0x1a, 0, G_h01_54CC << sh, G_h01_54CE, rp++, &count);
    F_h05_5BBC(0, 0xb0 - G_h01_5D46 - 0x24, 0x3a, 0, G_h01_5D44 << sh, G_h01_5D46, rp++, &count);
    k = F_h00_463E();
    k &= 3;

    for (i = 2; (unsigned int)i <= (unsigned int)(n - 2) && total < 257; i++) {
        if (G_h01_46E0 == 0 && i == 2) {
            F_h05_5C08(&pr0, &pr1, &pr2, &pr3, &pr4, &pr5, &pr6, &pr7, &pr8, &pr9,
                       5, 0, 6, 2, 2, 4, 0, 0, 5, 5);
        } else if (G_h01_46E0 == 0 && i == (n >> 1)) {
            F_h05_5C08(&pr0, &pr1, &pr2, &pr3, &pr4, &pr5, &pr6, &pr7, &pr8, &pr9,
                       10, 0, 12, 2, 6, 5, 4, 10, 9, 8);
        } else if (G_h01_46E0 == 1 && i == 2) {
            F_h05_5C08(&pr0, &pr1, &pr2, &pr3, &pr4, &pr5, &pr6, &pr7, &pr8, &pr9,
                       20, 0, 12, 2, 6, 10, 8, 40, 25, 15);
        } else if (G_h01_46E0 == 1 && i == (n >> 1)) {
            F_h05_5C08(&pr0, &pr1, &pr2, &pr3, &pr4, &pr5, &pr6, &pr7, &pr8, &pr9,
                       40, 5, 22, 4, 10, 20, 13, 60, 40, 25);
        } else if (G_h01_46E0 == 2 && i == 2) {
            F_h05_5C08(&pr0, &pr1, &pr2, &pr3, &pr4, &pr5, &pr6, &pr7, &pr8, &pr9,
                       60, 10, 28, 6, 15, 35, 25, 80, 55, 35);
        } else if (G_h01_46E0 == 2 && i == (n >> 1)) {
            F_h05_5C08(&pr0, &pr1, &pr2, &pr3, &pr4, &pr5, &pr6, &pr7, &pr8, &pr9,
                       80, 20, 35, 10, 25, 50, 35, 100, 70, 45);
        }

        count = 0;
        k = F_h00_463E() % 6;

        if (G_h01_5E64[i][0] == 11 && G_h01_5E61 != 0 && f20 == 0
            && F_h00_463E() % 100 < pr0) {
            if (G_h01_5E66[i].index == -1)
                G_h01_5E66[i].index = total;
            f1c = 1;
            F_h05_5BBC(i, 0xa0 - G_h01_55A0->y, 0x23, 0, G_h01_55A0->x << 3,
                       G_h01_55A0->y, rp++, &count);
            if (G_h01_5E64[i][0] < 10 && G_h01_5E64[i][0] != 5 && G_h01_5E64[i][0] != 6
                && F_h00_463E() % 100 < 40
                && (unsigned int)G_h01_55A0->y > 0x50 && f1b == 0) {
                f1b = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5AF4, 0x31, 0, G_h01_5AF2 << sh, G_h01_5AF4,
                           rp++, &count);
            }
            total += count;
            continue;
        }

        if (G_h01_5E64[i][0] == 11) {
            G_h01_5E64[i][0] = 8;
            if (G_h01_5E64[i + 1][0] != 15)
                G_h01_5E64[i + 1][0] = 0;
        }

        if (F_h00_463E() % 100 < pr1 && f24 == 0 && f1c == 0 && f1e == 0
            && f1b == 0 && f21 == 0 && f20 == 0 && f1d == 0 && f22 == 0 && f1f == 0
            && i > 5 && G_h01_5E64[i - 1][0] != 11 && G_h01_5E62 != 0) {
            f24 = 1;
            if (G_h01_5E66[i].index == -1)
                G_h01_5E66[i].index = total;
            F_h05_5BBC(i, -10, 0x1d, 0, G_h01_58A0 << sh, G_h01_58A2, rp++, &count);
            F_h05_5BBC(i, 0, 0x1f, 0, G_h01_590C << sh, G_h01_590E, rp++, &count);
            if (G_h01_5E64[i][0] < 11 && G_h01_5E64[i][0] != 5 && G_h01_5E64[i][0] != 6
                && G_h01_5E64[i][0] != 7 && G_h01_5E64[i][0] != 8
                && F_h00_463E() % 100 < 50 && f1b == 0) {
                f1b = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5AF4, 0x31, 0, G_h01_5AF2 << sh, G_h01_5AF4,
                           rp++, &count);
                goto e3e;
            }
            if (F_h00_463E() % 100 < 35 && f20 == 0 && G_h01_5E64[i][0] < 11) {
                f20 = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5B2A, 0x34, 0, G_h01_5B28 << sh, G_h01_5B2A,
                           rp++, &count);
            }
        e3e:
            total += count;
            continue;
        }

        r = F_h00_463E() % 100;
        if (r <= (unsigned int)pr2) {
            if (G_h01_5E66[i].index == -1)
                G_h01_5E66[i].index = total;
            side = (r & 1) ? 0 : 1;
            if (r > 18 && r < 30)
                r += 25;
            else if (r > 2 && r < 10)
                r -= 16;
            if (f23 > r - 10 && f23 < r + 10) {
                if (F_h00_463E() & 1)
                    r += 20;
                else
                    r -= 20;
            }
            f23 = (char)r;
            F_h05_5BBC(i, r, 0x21, side, G_h01_5538[side].x << sh, G_h01_5538[side].y,
                       rp++, &count);
        } else if (r > (unsigned int)pr2 && r < (unsigned int)pr2 + (unsigned int)pr3 && G_h01_5E5F != 0) {
            if (G_h01_5E66[i].index == -1)
                G_h01_5E66[i].index = total;
            r = F_h00_463E() % 50;
            if (r > 10 && r < 40)
                r -= 20;
            side = (F_h00_463E() & 1) ? 0 : 1;
            F_h05_5BBC(i, r, 0x28, side, G_h01_57C4[side].x << sh, G_h01_57C4[side].y,
                       rp++, &count);
            F_h05_5BBC(i, G_h01_57C4[side].y + r - 16, 0x2a, 0, G_h01_5830 << sh,
                       G_h01_5832, rp++, &count);
            F_h05_5BBC(i, G_h01_57C4[side].y + r - 16, 0x2b, 0, G_h01_5866 << sh,
                       G_h01_5868, rp++, &count);
            if (G_h01_5E64[i][0] < 11 && G_h01_5E64[i][0] != 5 && G_h01_5E64[i][0] != 6
                && G_h01_5E64[i][0] != 7 && G_h01_5E64[i][0] != 8
                && F_h00_463E() % 100 < 20 && f20 == 0 && f1c == 0 && f1e == 0
                && f1b == 0) {
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                f1b = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5AF4, 0x31, 0, G_h01_5AF2 << sh, G_h01_5AF4,
                           rp++, &count);
                goto t52b2;
            }
            if (G_h01_5E64[i][0] < 11 && f20 == 0 && f1c == 0 && f1e == 0 && f1b == 0
                && F_h00_463E() % 100 < 40) {
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                f20 = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5B2A, 0x34, 0, G_h01_5B28 << sh, G_h01_5B2A,
                           rp++, &count);
            }
        t52b2:
            total += count;
            continue;
        }

        if (G_h01_5E64[i][0] == 12 && F_h00_463E() % 100 < pr4
            && f1f == 0 && f1d == 0) {
            f1f = 1;
            if (G_h01_5E66[i].index == -1)
                G_h01_5E66[i].index = total;
            F_h05_5BBC(i, 0x8b, 0x2e, 0, G_h01_5A50 << sh, G_h01_5A52, rp++, &count);
            F_h05_5BBC(i, 0x8b - G_h01_59E6, 0x2c, 0, G_h01_59E4 << sh, G_h01_59E6,
                       rp++, &count);
            F_h05_5BBC(i, 0x8b - G_h01_5A1C, 0x2d, 0, G_h01_5A1A << sh, G_h01_5A1C,
                       rp++, &count);
            total += count;
            continue;
        }

        switch (k) {
        case 0:
            if (G_h01_5E64[i][0] < 11 && F_h00_463E() % 100 < pr5
                && f20 == 0 && f1c == 0 && f1e == 0 && f1b == 0) {
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                f20 = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5B2A, 0x34, 0, G_h01_5B28 << sh, G_h01_5B2A,
                           rp++, &count);
                total += count;
                continue;
            }
            break;
        case 1:
        case 2:
            if (G_h01_5E64[i][0] < 12 && F_h00_463E() % 100 < pr6
                && f22 == 0 && f1b == 0) {
                f22 = 1;
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                F_h05_5BBC(i, 0xa0 - G_h01_5C02 + 4, 0x38, 2, G_h01_5C00 << sh, G_h01_5C02,
                           rp++, &count);
                F_h05_5BBC(i, 0xa0 - G_h01_564C + 4, 0x20, 0, G_h01_564A << sh, G_h01_564C,
                           rp++, &count);
                total += count;
                continue;
            }
            break;
        case 3:
            if (G_h01_5E64[i][0] == 0 && G_h01_5E60 != 0
                && F_h00_463E() % 100 < pr7
                && f1e == 0 && f1c == 0 && f20 == 0 && f1b == 0 && f1d == 0) {
                f1e = 1;
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                F_h05_5BBC(i, 0xa0 - G_h01_5898->y + 1, 0x1c, 0, G_h01_5898->x << 3,
                           G_h01_5898->y, rp++, &count);
                total += count;
                continue;
            }
            break;
        case 4:
            if (F_h00_463E() % 100 < pr8 && f1d == 0 && f1e == 0 && f1c == 0) {
                f1d = 1;
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                if (F_h00_463E() & 1)
                    r = 0;
                F_h05_5BBC(i, r, 0x11, 0, G_h01_55A8 << sh, G_h01_55AA, rp++, &count);
                F_h05_5BBC(i, r + G_h01_55AA, 0x12, 2, G_h01_55DE << sh, G_h01_55E0,
                           rp++, &count);
                r = F_h00_463E() & 3;
                if (r == 0) {
                    F_h05_5BBC(i, 0x90, 0, 0x14, G_h01_5680 << sh, G_h01_5682, rp++, &count);
                } else if (r == 1) {
                    F_h05_5BBC(i, 0x90, 0, 0x16, G_h01_56EC << sh, G_h01_56EE, rp++, &count);
                } else if (r == 2) {
                    F_h05_5BBC(i, 0x90, 0, 0x18, G_h01_5758 << sh, G_h01_575A, rp++, &count);
                } else {
                    F_h05_5BBC(i, 0x90, 0, 0x19, G_h01_578E << sh, G_h01_5790, rp++, &count);
                }
                if (G_h01_5E64[i][0] < 11 && G_h01_5E64[i][0] != 5 && G_h01_5E64[i][0] != 6
                    && F_h00_463E() % 100 > 50 && G_h01_5E64[i][0] != 7
                    && G_h01_5E64[i][0] != 8 && f1b == 0 && f20 == 0 && f1e == 0
                    && f1c == 0 && f22 == 0) {
                    f1b = 1;
                    F_h05_5BBC(i, 0xb0 - G_h01_5AF4, 0x31, 0, G_h01_5AF2 << sh, G_h01_5AF4,
                               rp++, &count);
                }
                total += count;
                continue;
            }
            break;
        case 5:
            if (G_h01_5E64[i][0] < 11 && G_h01_5E64[i][0] != 5 && G_h01_5E64[i][0] != 6
                && G_h01_5E64[i][0] != 7 && G_h01_5E64[i][0] != 8
                && F_h00_463E() % 100 < pr9
                && f1b == 0 && f1d == 0 && f20 == 0 && f22 == 0 && f1c == 0 && f1e == 0) {
                if (G_h01_5E66[i].index == -1)
                    G_h01_5E66[i].index = total;
                f1b = 1;
                F_h05_5BBC(i, 0xb0 - G_h01_5AF4, 0x31, 0, G_h01_5AF2 << sh, G_h01_5AF4,
                           rp++, &count);
                total += count;
                continue;
            }
            break;
        default:
            break;
        }

        f1e = 0;
        f20 = 0;
        f1b = 0;
        f21 = 0;
        f1c = 0;
        f1f = 0;
        f22 = 0;
        f1d = 0;
        total += count;
    }

    if (G_h01_5E66[G_h01_5E42].index == -1)
        G_h01_5E66[G_h01_5E42].index = total;
    F_h05_5BBC(G_h01_5E42, 0xb0 - G_h01_5504 - 8, 0x1b, 0, G_h01_5502 << sh, G_h01_5504,
               rp++, &count);
    F_h05_5BBC(G_h01_5E42, 0xb0 - G_h01_5D46 - 0x24, 0x3a, 0xffff, G_h01_5D44 << sh,
               G_h01_5D46, rp++, &count);
}

struct Item { char a,pad[3]; int b,unused,c,d; char e,f; };
F_h05_5BBC(a,b,c,d,e,f,p,count) char a,c,d; int b,e,f; struct Item *p; int *count; { p->a=a; p->b=b; p->e=c; p->f=d; p->c=e; p->d=f; *count=*count+1; }

F_h05_5C08(p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,v0,v1,v2,v3,v4,v5,v6,v7,v8,v9) char *p0,*p1,*p2,*p3,*p4,*p5,*p6,*p7,*p8,*p9; char v0,v1,v2,v3,v4,v5,v6,v7,v8,v9; { *p0=v0; *p1=v1; *p2=v2; *p3=v3; *p4=v4; *p5=v5; *p6=v6; *p7=v7; *p8=v8; *p9=v9; }

