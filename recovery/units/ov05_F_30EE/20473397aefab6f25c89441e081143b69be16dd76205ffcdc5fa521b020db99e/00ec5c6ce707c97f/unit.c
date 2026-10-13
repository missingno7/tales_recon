/* ov05_F_131C: per-frame column sweep over the record table; float math through m.lib FFP. */
struct Pos { int x; int y; };
struct Entry { int f0; int index; };
struct Obj14 {
    unsigned char id;
    char f1;
    int x;
    int w4;
    char f6[4];
    int w10;
    char b12;
    char b13;
};
extern int G_h01_0A82;
extern int G_h01_0A84;
extern float G_h01_0A7E;
extern long G_h01_46CA;
extern long G_h01_46D2;
extern long G_h01_5484[17];
extern struct Entry G_h01_5E64[16];
extern struct Obj14 G_h01_606C[16];
extern struct Pos *G_h01_55A0;
extern struct Pos *G_h01_5898;
extern char G_h01_58D2;
extern char G_h01_5B5A;
extern int G_h01_5C32;
extern int G_h01_5C68;
extern int G_h01_5C6A;
extern int G_h01_5CD4;
extern int G_h01_5CD6;
extern char G_h01_5D08;
extern int G_h01_5D0A;
extern int G_h01_5D0C;
extern char G_h01_5D3E;
extern int G_h01_5D76;
extern int G_h01_5D78;
extern char G_h01_5E58;
extern char G_h01_5E59;
extern int G_h01_5E40;
extern int G_h01_5E42;
extern int G_h01_5E4C;
extern int G_h01_5E52;
extern int G_h01_5E54;
extern float G_h01_5E34;
extern float G_h01_5E38;
extern int F_h00_8BC8();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h05_3836();
extern int F_h05_1EFC();
extern int F_h05_2CD4();

F_h05_131C(p)
char *p;
{
    int i;
    int flag;
    int x;
    int k;
    int a;
    int c;
    int e;
    int j;
    int aux;
    struct Obj14 *q;
    long obj;
    struct Entry *ent;

    flag = 0;
    F_h00_8BC8(G_h01_46CA, 9L);
    F_h05_3836();
    x = -G_h01_5E4C;
    if (G_h01_5E4C >= 0) {
        i = G_h01_0A82;
    } else {
        x -= 80;
        i = G_h01_0A82 - 1;
    }
    j = i;
    ent = &G_h01_5E64[i];
    while (x < 320) {
        obj = G_h01_5484[ent->f0];
        a = 0;
        x &= 0xfff8;
        c = x;
        e = 80;
        if (x < 0) {
            e = x + 80;
            a = -x;
            c = 0;
        } else if (x > 240) {
            e = 320 - x;
        }
        if (e > 0) {
            if (ent->f0 >= 1 && ent->f0 <= 10)
                F_h00_8A46(obj, (long)a, 0L, G_h01_46D2, (long)c, 144L, (long)e, 32L, 192L, 255L, 0L);
            else
                F_h00_8A46(obj, (long)a, 0L, G_h01_46D2, (long)c, 160L, (long)e, 16L, 192L, 255L, 0L);
        }
        if (ent->index != -1) {
            q = &G_h01_606C[ent->index];
            while (q->id == i) {
                q->x = x;
                switch (q->b12) {
                case 35:
                case 36:
                    if (e > 0)
                        F_h00_8A46(G_h01_55A0, (long)a, 0L, G_h01_46D2, (long)c, (long)q->w4, (long)e, (long)q->w10, 192L, 255L, 0L);
                    break;
                case 28:
                    if (e > 0)
                        F_h00_8A46(G_h01_5898, (long)a, 0L, G_h01_46D2, (long)c, (long)q->w4, (long)e, (long)q->w10, 192L, 255L, 0L);
                    break;
                case 32:
                    q->x = q->x + 32;
                    break;
                case 27:
                    q->x = q->x + 40;
                    break;
                default:
                    break;
                }
                q++;
            }
        }
        if (G_h01_5E58) {
            if (G_h01_5E52 == i) {
                if (i >= G_h01_5E42 - 3 && G_h01_5C6A < 149)
                    G_h01_5C6A += 5;
                G_h01_5C68 = G_h01_5E54 + x;
                F_h00_34E0(&G_h01_5C68);
            }
            G_h01_5E54 += 2;
            if (G_h01_5E54 > 79) {
                G_h01_5E54 = 0;
                G_h01_5E52++;
            }
        }
        if (G_h01_5E42 - 2 == i)
            k = x;
        x += 80;
        if (G_h01_5E34 < (float)x) {
            if (flag == 0) {
                flag = 1;
                G_h01_0A84 = i;
            }
        }
        i++;
        ent++;
    }
    while (j < i) {
        F_h05_1EFC(j);
        if (j == G_h01_0A84) {
            if (G_h01_5E40 == 0) {
                if (p != &G_h01_5B5A && p != &G_h01_58D2 && p != (char *)&G_h01_5C32) {
                    G_h01_5CD4 = (int)G_h01_5E34;
                    G_h01_5CD6 = (int)(G_h01_5E38 + 9);
                    G_h01_5D08 = G_h01_5E59;
                    F_h00_34E0(&G_h01_5CD4);
                    if (G_h01_0A7E > 3 && G_h01_0A7E < 7) {
                        G_h01_5D3E = G_h01_5E59;
                        G_h01_5D0A = (int)(G_h01_5E34 + -30);
                        G_h01_5D0C = (int)(G_h01_5E38 + 12);
                        F_h00_34E0(&G_h01_5D0A);
                    }
                    G_h01_5E59++;
                    if (G_h01_5E59 > 3)
                        G_h01_5E59 = 0;
                } else {
                    F_h00_34E0(p);
                }
            } else {
                F_h00_34E0(p);
                if (G_h01_5E40 == 1) {
                    G_h01_5D3E = G_h01_5E59;
                    G_h01_5D0A = (int)(G_h01_5E34 + -28);
                    G_h01_5D0C = (int)(G_h01_5E38 + 18);
                    F_h00_34E0(&G_h01_5D0A);
                    G_h01_5E59++;
                    if (G_h01_5E59 > 3)
                        G_h01_5E59 = 0;
                } else if (G_h01_5E40 == 2) {
                    G_h01_5D3E = G_h01_5E59;
                    G_h01_5D0A = (int)(G_h01_5E34 + -28);
                    G_h01_5D0C = (int)(G_h01_5E38 + 22);
                    F_h00_34E0(&G_h01_5D0A);
                    G_h01_5E59++;
                    if (G_h01_5E59 > 3)
                        G_h01_5E59 = 0;
                }
            }
        }
        F_h05_2CD4(j);
        if (G_h01_5E42 - 2 == j++) {
            G_h01_5D76 = k + 40;
            G_h01_5D78 = 149;
            F_h00_34E0(&G_h01_5D76);
        }
    }
}

/* ov05_F_1EFC: per-frame update of the objects linked from G_h01_5E66[idx]; float position math through m.lib FFP. */
struct Lookup { int index; int f2; };
struct Record { char f0[4]; int value; char f6[8]; };
struct Obj {
    unsigned char id;
    char f1;
    int w2;
    int w4;
    char b6;
    char b7;
    int w8;
    int w10;
    char b12;
    char b13;
    char f14[2];
    int w16;
    int w18;
    char f20[7];
    char b27;
    char f28[4];
    int w32;
    char f34[4];
    int w38;
    char b40;
    char b41;
};
extern struct Lookup G_h01_5E66[16];
extern struct Record G_h01_606C[16];
extern int G_h01_5E64[1][2];
extern int F_h00_34E0();
extern int F_h00_57D2();
extern unsigned int F_h00_463E();
extern float G_h01_5E34;
extern float G_h01_5E38;
extern char G_h01_0A8A;
extern char G_h01_567A;
extern char G_h01_5BFA;
extern char G_h01_5C30;
extern int G_h01_55A4;
extern int G_h01_55A6;
extern int G_h01_55AA;
extern int G_h01_55DA;
extern int G_h01_55DC;
extern int G_h01_5610;
extern int G_h01_5612;
extern int G_h01_5646;
extern int G_h01_5648;
extern int G_h01_567C;
extern int G_h01_56B2;
extern int G_h01_56E8;
extern int G_h01_571E;
extern int G_h01_5754;
extern int G_h01_578A;
extern int G_h01_589C;
extern int G_h01_589E;
extern int G_h01_58A2;
extern int G_h01_5908;
extern int G_h01_590A;
extern int G_h01_590E;
extern int G_h01_59E0;
extern int G_h01_59E2;
extern int G_h01_59E6;
extern int G_h01_5A16;
extern int G_h01_5A18;
extern int G_h01_5A1C;
extern int G_h01_5A4C;
extern int G_h01_5A4E;
extern int G_h01_5A82;
extern int G_h01_5A84;
extern int G_h01_5AB8;
extern int G_h01_5ABA;
extern int G_h01_5ABE;
extern int G_h01_5B24;
extern int G_h01_5B26;
extern int G_h01_5BC6;
extern int G_h01_5BC8;
extern int G_h01_5BFC;
extern int G_h01_5BFE;
extern int G_h01_5C32;
extern int G_h01_5C34;
extern int G_h01_5C38;

F_h05_1EFC(idx)
int idx;
{
    long lx0;
    struct Obj *p;
    int *q;
    int *r;
    int t0;
    int t1;
    long lx1;

    if (G_h01_5E66[idx].index == -1)
        return;
    p = (struct Obj *)&G_h01_606C[G_h01_5E66[idx].index];
    while (p->id == idx) {
        switch (p->b12) {
        case 17:
            G_h01_55A4 = p->w2;
            t0 = p->w4 + p->w10;
            if (G_h01_5E38 > (t0 + 6))
                p->w4++;
            else if (G_h01_5E38 < (t0 - 6))
                p->w4--;
            G_h01_55A6 = p->w4;
            F_h00_34E0(&G_h01_55A4);
            t0 = (int)(G_h01_5E34 - p->w2);
            t1 = p->w4 + p->w10;
            if (p->b13 == 0 && t0 > -100 && t0 < 100 && G_h01_5E38 > t1) {
                if (p->w38 + 12 < 160 - p->w38) {
                    p->b40 = 2;
                    p->b13 = 1;
                    p->b27 = 2;
                }
            }
            if (p->b41 == 20) {
                r = &G_h01_567C;
                q = &G_h01_56B2;
            } else if (p->b41 == 22) {
                r = &G_h01_56E8;
                q = &G_h01_571E;
            } else if (p->b41 == 24) {
                r = &G_h01_5754;
                q = &G_h01_5754;
            } else {
                r = &G_h01_578A;
                q = &G_h01_578A;
            }
            switch (p->b13) {
            case 0:
                G_h01_55DA = G_h01_55A4 + 16;
                p->w18 = G_h01_55A6 + G_h01_55AA;
                G_h01_55DC = p->w18;
                F_h00_34E0(&G_h01_55DA);
                break;
            case 1:
                G_h01_5612 = G_h01_55A6 + G_h01_55AA;
                G_h01_5610 = G_h01_55A4 + 16;
                r[0] = G_h01_55A4 + 8;
                p->w32 = G_h01_5612 + 4;
                r[1] = p->w32;
                F_h00_34E0(r);
                F_h00_34E0(&G_h01_5610);
                if (--p->b27 == 0) {
                    F_h00_57D2(0x33);
                    p->b13 = 2;
                }
                break;
            case 2:
                G_h01_55DA = G_h01_55A4 + 16;
                p->w18 = G_h01_55A6 + G_h01_55AA;
                G_h01_55DC = p->w18;
                p->w32 = p->w32 + ++p->b40;
                if (p->w32 > 160 - p->w38) {
                    p->w32 = 160 - (p->w38 >> 1);
                    if (G_h01_5E64[idx][0] < 12) {
                        if (p->b41 == 22)
                            p->w32 -= 4;
                        else if (p->b41 == 20)
                            p->w32 -= 5;
                        r[0] = G_h01_55A4 + 8;
                        r[1] = p->w32;
                        F_h00_34E0(r);
                        F_h00_34E0(&G_h01_55DA);
                        if (p->b41 == 22)
                            p->w32 += 4;
                        else if (p->b41 == 20)
                            p->w32 += 5;
                        p->b27 = 8;
                        if (p->b41 == 20)
                            F_h00_57D2(0x28);
                        else if (p->b41 == 22)
                            F_h00_57D2(0x29);
                        else if (p->b41 == 24)
                            F_h00_57D2(0x38);
                        else
                            F_h00_57D2(0x34);
                        p->b13 = 3;
                        break;
                    }
                    if (p->b41 == 20)
                        p->w32 -= 5;
                    p->b27 = 2;
                    p->b13 = 4;
                }
                r[0] = G_h01_55A4 + 8;
                r[1] = p->w32;
                F_h00_34E0(r);
                F_h00_34E0(&G_h01_55DA);
                break;
            case 3:
                if (p->b27 > 5) {
                    q[0] = G_h01_55A4 + 8;
                    q[1] = p->w32 - 2;
                    F_h00_34E0(q);
                }
                G_h01_55DA = G_h01_55A4 + 16;
                p->w18 = G_h01_55A6 + G_h01_55AA;
                G_h01_55DC = p->w18;
                F_h00_34E0(&G_h01_55DA);
                if (--p->b27 == 0) {
                    p->b40 = 0;
                    p->b13 = 0;
                }
                break;
            case 4:
                F_h00_57D2(0x3a);
                G_h01_5C32 = G_h01_55A4 - 12;
                G_h01_5C34 = 160 - G_h01_5C38;
                F_h00_34E0(&G_h01_5C32);
                G_h01_55DA = G_h01_55A4 + 16;
                p->w18 = G_h01_55A6 + G_h01_55AA;
                G_h01_55DC = p->w18;
                F_h00_34E0(&G_h01_55DA);
                if (--p->b27 == 0) {
                    p->b40 = 0;
                    p->b27 = 5;
                    p->b13 = 0;
                }
                break;
            default:
                break;
            }
            break;
        case 32:
            if (p->b13 == 0 && ((char *)p)[-8] == 3)
                ((char *)p)[-8] = 0;
            G_h01_5BFC = *(int *)((char *)p - 12);
            G_h01_5BFE = *(int *)((char *)p - 10);
            if (--((char *)p)[-1] == 0 && ((char *)p)[-8] < 2) {
                ((char *)p)[-1] = 3;
                ((char *)p)[-8]++;
            }
            if (((char *)p)[-1] <= 0)
                ((char *)p)[-1] = 3;
            G_h01_5C30 = ((char *)p)[-8];
            F_h00_34E0(&G_h01_5BFC);
            t0 = (int)(G_h01_5E34 - (float)*(int *)((char *)p - 12));
            if (t0 < -128 || t0 > 128 || G_h01_5E38 > 134) {
                if (p->b13 == 0)
                    {
                    p = (struct Obj *)((char *)p + 14);
                    continue;
                }
            }
            if (p->b13 == 0 && ((char *)p)[-8] == 2) {
                F_h00_57D2(0x2a);
                ((char *)p)[-8] = 3;
                p->b13 = 1;
                p->w4 = 144;
                p->b6 = 2;
            } else if (p->b13 == 3 && p->b6 > 2) {
                p->b6 = 0;
                p->b13 = 0;
                {
                    p = (struct Obj *)((char *)p + 14);
                    continue;
                }
            }
            if (p->w4 < 0) {
                ((char *)p)[-8] = 0;
                p->w4 = 144;
                p->b13 = 0;
                {
                    p = (struct Obj *)((char *)p + 14);
                    continue;
                }
            }
            if (p->w4 < G_h01_5E38 && p->b13 < 3) {
                F_h00_57D2(0x31);
                ((char *)p)[-8] = 0;
                p->b13 = 3;
                p->b6 = 0;
            }
            switch (p->b13) {
            case 1:
                G_h01_567A = 0;
                G_h01_5646 = p->w2;
                G_h01_5648 = p->w4;
                p->w4 = p->w4 - 7;
                F_h00_34E0(&G_h01_5646);
                if (--p->b6 == 0) {
                    p->b6 = 2;
                    p->b13 = 2;
                }
                break;
            case 2:
                G_h01_567A = 1;
                G_h01_5646 = p->w2;
                G_h01_5648 = p->w4;
                p->w4 = p->w4 - 7;
                F_h00_34E0(&G_h01_5646);
                if (--p->b6 == 0) {
                    p->b6 = 3;
                    p->b13 = 1;
                }
                break;
            case 3:
            case 4:
            case 5:
                if (p->b13 == 3)
                    p->b6++;
                G_h01_5BFA = p->b13 - 3;
                G_h01_5BC6 = p->w2;
                G_h01_5BC8 = p->w4;
                F_h00_34E0(&G_h01_5BC6);
                p->b13 = p->b13 + 1;
                if (p->b13 > 5) {
                    p->b13 = 3;
                }
                break;
            default:
                break;
            }
            break;
        case 46:
            t0 = (int)(G_h01_5E34 - p->w2);
            if (G_h01_5E38 < (160 - (G_h01_5A1C + G_h01_5ABE)) || t0 < -120 || t0 > 120) {
                if (p->b13 == 0)
                    {
                    p = (struct Obj *)((char *)p + 14);
                    continue;
                }
            }
            if (p->b13 == 0) {
                p->b13 = 1;
                p->b27 = 1;
                {
                    p = (struct Obj *)((char *)p + 14);
                    continue;
                }
            }
            if (t0 < -128 || t0 > 128) {
                if (p->b13 < 6) {
                    p->b13 = 6;
                    p->b27 = 8;
                }
            }
            switch (p->b13) {
            case 1:
                G_h01_5A4C = p->w2;
                G_h01_5A4E = p->w4;
                F_h00_34E0(&G_h01_5A4C);
                if (--p->b27 == 0) {
                    p->b13 = 2;
                    p->b27 = 2;
                }
                break;
            case 2:
                G_h01_5A82 = p->w2;
                G_h01_5A84 = p->w4;
                F_h00_34E0(&G_h01_5A82);
                if (--p->b27 == 0) {
                    p->b13 = 3;
                    p->b27 = 2;
                }
                break;
            case 3:
                G_h01_5AB8 = p->w2;
                G_h01_5ABA = p->w4;
                F_h00_34E0(&G_h01_5AB8);
                if (--p->b27 == 0) {
                    F_h00_57D2(0x37);
                    p->b13 = 4;
                    p->b27 = 6;
                }
                break;
            case 4:
                G_h01_59E0 = p->w2;
                G_h01_59E2 = p->w4 - G_h01_59E6;
                G_h01_5AB8 = p->w2;
                G_h01_5ABA = p->w4;
                F_h00_34E0(&G_h01_59E0);
                F_h00_34E0(&G_h01_5AB8);
                if (--p->b27 == 0) {
                    p->b13 = 5;
                    p->b27 = 8;
                }
                break;
            case 5:
                G_h01_5A16 = p->w2;
                G_h01_5A18 = p->w4 - G_h01_5A1C;
                G_h01_5AB8 = p->w2;
                G_h01_5ABA = p->w4;
                F_h00_34E0(&G_h01_5A16);
                F_h00_34E0(&G_h01_5AB8);
                if (--p->b27 == 0) {
                    p->b13 = 3;
                    p->b27 = 6;
                }
                break;
            case 6:
                G_h01_5A82 = p->w2;
                G_h01_5A84 = p->w4;
                F_h00_34E0(&G_h01_5A82);
                if (--p->b27 == 0) {
                    p->b13 = 7;
                    p->b27 = 5;
                }
                break;
            case 7:
                G_h01_5A4C = p->w2;
                G_h01_5A4E = p->w4;
                F_h00_34E0(&G_h01_5A4C);
                if (--p->b27 == 0) {
                    p->b13 = 0;
                    p->b27 = 0;
                }
                break;
            default:
                break;
            }
            break;
        case 29:
            t0 = p->w4 + p->w10;
            if (G_h01_5E38 > (t0 + 6))
                p->w4 += 2;
            else if (G_h01_5E38 < (t0 - 6))
                p->w4 -= 2;
            t0 = 176 - G_h01_590E - p->w10;
            if (p->w4 < -52)
                p->w4 = -52;
            else if (p->w4 > t0)
                p->w4 = t0;
            G_h01_589C = p->w2;
            G_h01_589E = p->w4;
            F_h00_34E0(&G_h01_589C);
            G_h01_5908 = G_h01_589C + 7;
            p->w16 = G_h01_5908;
            G_h01_590A = G_h01_589E + G_h01_58A2 - 11;
            p->w18 = G_h01_590A;
            if ((G_h01_5E38 > G_h01_590A
                 && G_h01_5E38 < (G_h01_590A + G_h01_590E)
                 && G_h01_5E34 < (p->w8 + G_h01_589C + 16)
                 && G_h01_5E34 > (G_h01_589C - 16)
                 && F_h00_463E() % 100 > 5)
                || G_h01_0A8A > 0) {
                F_h00_34E0(&G_h01_5908);
                p->b27 = 1;
                if (G_h01_0A8A == 0)
                    G_h01_0A8A = 10;
                else
                    G_h01_0A8A--;
            } else {
                p->b27 = 0;
            }
            break;
        case 52:
            G_h01_5B24 = p->w2;
            G_h01_5B26 = p->w4;
            F_h00_34E0(&G_h01_5B24);
            break;
        default:
            break;
        }
        p = (struct Obj *)((char *)p + 14);
    }
}

/* Worker haiku-fn-ov05_F_2CD4: structured candidate for ov05_F_2CD4 (v8). */
struct Lookup { int index; int f2; };
struct Rec { unsigned char id; char a1; int x; int y; char b6; char b7; int w8; char b10; char b11; char type; char d; };
struct Pos { int x; int y; };
struct Ent { int x; int y; char rest[50]; };
extern struct Lookup G_h01_5E66[16];
extern struct Rec G_h01_606C[16];
extern struct Pos G_h01_54C8;
extern struct Pos G_h01_54FE;
extern struct Ent G_h01_5534[2];
extern struct Ent G_h01_57C0[2];
extern struct Pos G_h01_582C;
extern struct Pos G_h01_5862;
extern struct Pos G_h01_5AEE;
extern struct Pos G_h01_5D40;
extern char G_h01_5D74;
extern float G_h01_5E34;
extern int G_h01_2F10;
extern int G_h01_2F14;
extern int G_h01_2F16;
extern int G_h01_2F18;
extern int G_h01_2F1A;
extern int G_h01_2F1C;
extern int G_h01_0A7A;
extern int G_h01_0A7C;
extern int F_h00_34E0();
extern int F_h00_57D2();
extern unsigned int F_h00_463E();

F_h05_2CD4(arg)
int arg;
{
    int aux;
    char idx;
    int dxv;
    unsigned int r;
    struct Rec *p;

    if (G_h01_5E66[arg].index == -1)
        return;
    p = &G_h01_606C[G_h01_5E66[arg].index];
    while (p->id == arg) {
        switch (p->type) {
        case 33:
            idx = p->d;
            G_h01_5534[idx].x = p->x;
            G_h01_5534[idx].y = p->y;
            F_h00_34E0(&G_h01_5534[idx]);
            break;
        case 40:
            idx = p->d;
            G_h01_57C0[idx].x = p->x;
            G_h01_57C0[idx].y = p->y;
            F_h00_34E0(&G_h01_57C0[idx]);
            break;
        case 26:
            G_h01_54C8.x = p->x;
            G_h01_54C8.y = p->y;
            F_h00_34E0(&G_h01_54C8);
            break;
        case 27:
            G_h01_54FE.x = p->x;
            G_h01_54FE.y = p->y;
            F_h00_34E0(&G_h01_54FE);
            break;
        case 58:
            if (arg == 0)
                G_h01_5D40.x = p->x + 17;
            else
                G_h01_5D40.x = p->x + 62;
            G_h01_5D40.y = p->y;
            if (p->b6++ != 0) {
                p->b6 = 0;
            } else {
                G_h01_5D74 = p->d;
                p->d = p->d + 1;
            }
            if (p->d > 2)
                p->d = F_h00_463E() % 3;
            F_h00_34E0(&G_h01_5D40);
            break;
        case 42:
            r = F_h00_463E() % 100;
            dxv = (int)(G_h01_5E34 - (float)p->x);
            if (p->d == 0 && p[1].d == 0 && r < 10 && dxv > -96 && dxv < 96) {
                F_h00_57D2(54);
                p->d = p->d + 1;
            } else if (p->d <= 1 && p->d != 0) {
                p->d = p->d + 1;
                G_h01_582C.x = p->x;
                G_h01_582C.y = p->y;
                F_h00_34E0(&G_h01_582C);
            }
            break;
        case 43:
            if ((p - 1)->d > 1) {
                (p - 1)->d = 0;
                p->d = p->d + 1;
                G_h01_5862.x = p->x;
                G_h01_5862.y = p->y;
                F_h00_34E0(&G_h01_5862);
            } else if (p->d > 0 && p->d < 2) {
                p->d = p->d + 1;
                G_h01_5862.x = p->x;
                G_h01_5862.y = p->y;
                F_h00_34E0(&G_h01_5862);
                if (p->d == 2)
                    p->d = 0;
            }
            break;
        case 49:
            G_h01_2F1A = p->x;
            G_h01_2F1C = p->x + p->w8;
            G_h01_2F18 = p->y + 16;
            if (G_h01_2F10 > G_h01_2F18 + 16 && G_h01_2F14 > G_h01_2F1A
                && G_h01_2F16 < G_h01_2F1C) {
                G_h01_0A7A = 1;
            } else {
                G_h01_0A7A = 0;
                G_h01_0A7C = 0;
            }
            G_h01_5AEE.x = p->x;
            G_h01_5AEE.y = p->y;
            F_h00_34E0(&G_h01_5AEE);
            break;
        default:
            break;
        }
        p++;
    }
}

extern int G_h01_5E40;
extern char G_h01_5E41;
extern char G_h01_5482;
extern int G_h01_544E;
extern int F_h05_131C();
extern int F_h00_307C();
extern unsigned int F_h00_463E();
extern int F_h00_57D2();

recovered()
{
    int i;
    int saved;
    int cur;
    int flag;

    saved = G_h01_5E40;
    cur = G_h01_5E40;
    flag = 1;
    F_h00_57D2(46);
    for (i = 0; i < 6 || flag; i++) {
        if (flag) {
            cur = F_h00_463E() & 15;
            if (cur != saved)
                flag = 0;
            if (i >= 6)
                i = 0;
        }
        G_h01_5E40 += 2;
        if (G_h01_5E40 > 15)
            G_h01_5E40 = 0;
        G_h01_5482 = G_h01_5E41;
        F_h05_131C(&G_h01_544E);
        F_h00_307C();
    }
    if (cur == 4)
        cur = 5;
    G_h01_5E40 = cur;
}

/* ov05_F_3836: record and float-threshold updates; float math through m.lib FFP. */
extern int G_h01_0A84;
extern int G_h01_5E42;
extern char *G_h01_5370;
extern long G_h01_46CA;
extern char G_h01_46E1;
extern int G_h01_5E56;
extern int G_h01_5E52;
extern char G_h01_5E58;
extern int G_h01_593E;
extern int G_h01_5974;
extern int G_h01_59AA;
extern int G_h01_59AC;
extern int G_h01_5C9E;
extern int G_h01_5CA0;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_34E0();
extern int F_h00_09C0();

F_h05_3836()
{
    float a;
    float b;

    a = (float)G_h01_0A84;
    b = (float)G_h01_5E42;
    *G_h01_5370 = 4;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xb0L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xb0L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xc7L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xb1L);
    F_h00_8AA8(G_h01_46CA, 0L, 0xc7L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0x13fL, 0xb1L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
    F_h00_34E0(&G_h01_593E);
    if (G_h01_5E56 + 42 <= G_h01_0A84) {
        G_h01_46E1++;
        G_h01_5E56 += 42;
    }
    if (G_h01_46E1 < 10)
        F_h00_09C0(18, 184, (long)(G_h01_46E1 > 30 ? 30 : G_h01_46E1), 7, 1, 0);
    else
        F_h00_09C0(14, 184, (long)(G_h01_46E1 > 30 ? 30 : G_h01_46E1), 7, 1, 0);
    F_h00_34E0(&G_h01_5974);
    if (G_h01_5E58) {
        G_h01_59AA = (int)(a / b * 208.0 + 72.0);
        G_h01_59AC = 0xb1;
        F_h00_34E0(&G_h01_59AA);
        G_h01_5C9E = (int)((float)G_h01_5E52 / b * 208.0 + 72.0);
        G_h01_5CA0 = 0xba;
        F_h00_34E0(&G_h01_5C9E);
    } else {
        G_h01_59AA = (int)(a / b * 208.0 + 72.0);
        G_h01_59AC = 0xb6;
        F_h00_34E0(&G_h01_59AA);
    }
}

