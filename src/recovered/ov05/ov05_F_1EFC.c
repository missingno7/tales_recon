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
extern int draw_masked_sprite();
extern int play_sound();
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

recovered(idx)
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
            draw_masked_sprite(&G_h01_55A4);
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
                draw_masked_sprite(&G_h01_55DA);
                break;
            case 1:
                G_h01_5612 = G_h01_55A6 + G_h01_55AA;
                G_h01_5610 = G_h01_55A4 + 16;
                r[0] = G_h01_55A4 + 8;
                p->w32 = G_h01_5612 + 4;
                r[1] = p->w32;
                draw_masked_sprite(r);
                draw_masked_sprite(&G_h01_5610);
                if (--p->b27 == 0) {
                    play_sound(0x33);
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
                        draw_masked_sprite(r);
                        draw_masked_sprite(&G_h01_55DA);
                        if (p->b41 == 22)
                            p->w32 += 4;
                        else if (p->b41 == 20)
                            p->w32 += 5;
                        p->b27 = 8;
                        if (p->b41 == 20)
                            play_sound(0x28);
                        else if (p->b41 == 22)
                            play_sound(0x29);
                        else if (p->b41 == 24)
                            play_sound(0x38);
                        else
                            play_sound(0x34);
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
                draw_masked_sprite(r);
                draw_masked_sprite(&G_h01_55DA);
                break;
            case 3:
                if (p->b27 > 5) {
                    q[0] = G_h01_55A4 + 8;
                    q[1] = p->w32 - 2;
                    draw_masked_sprite(q);
                }
                G_h01_55DA = G_h01_55A4 + 16;
                p->w18 = G_h01_55A6 + G_h01_55AA;
                G_h01_55DC = p->w18;
                draw_masked_sprite(&G_h01_55DA);
                if (--p->b27 == 0) {
                    p->b40 = 0;
                    p->b13 = 0;
                }
                break;
            case 4:
                play_sound(0x3a);
                G_h01_5C32 = G_h01_55A4 - 12;
                G_h01_5C34 = 160 - G_h01_5C38;
                draw_masked_sprite(&G_h01_5C32);
                G_h01_55DA = G_h01_55A4 + 16;
                p->w18 = G_h01_55A6 + G_h01_55AA;
                G_h01_55DC = p->w18;
                draw_masked_sprite(&G_h01_55DA);
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
            draw_masked_sprite(&G_h01_5BFC);
            t0 = (int)(G_h01_5E34 - (float)*(int *)((char *)p - 12));
            if (t0 < -128 || t0 > 128 || G_h01_5E38 > 134) {
                if (p->b13 == 0)
                    {
                    p = (struct Obj *)((char *)p + 14);
                    continue;
                }
            }
            if (p->b13 == 0 && ((char *)p)[-8] == 2) {
                play_sound(0x2a);
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
                play_sound(0x31);
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
                draw_masked_sprite(&G_h01_5646);
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
                draw_masked_sprite(&G_h01_5646);
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
                draw_masked_sprite(&G_h01_5BC6);
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
                draw_masked_sprite(&G_h01_5A4C);
                if (--p->b27 == 0) {
                    p->b13 = 2;
                    p->b27 = 2;
                }
                break;
            case 2:
                G_h01_5A82 = p->w2;
                G_h01_5A84 = p->w4;
                draw_masked_sprite(&G_h01_5A82);
                if (--p->b27 == 0) {
                    p->b13 = 3;
                    p->b27 = 2;
                }
                break;
            case 3:
                G_h01_5AB8 = p->w2;
                G_h01_5ABA = p->w4;
                draw_masked_sprite(&G_h01_5AB8);
                if (--p->b27 == 0) {
                    play_sound(0x37);
                    p->b13 = 4;
                    p->b27 = 6;
                }
                break;
            case 4:
                G_h01_59E0 = p->w2;
                G_h01_59E2 = p->w4 - G_h01_59E6;
                G_h01_5AB8 = p->w2;
                G_h01_5ABA = p->w4;
                draw_masked_sprite(&G_h01_59E0);
                draw_masked_sprite(&G_h01_5AB8);
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
                draw_masked_sprite(&G_h01_5A16);
                draw_masked_sprite(&G_h01_5AB8);
                if (--p->b27 == 0) {
                    p->b13 = 3;
                    p->b27 = 6;
                }
                break;
            case 6:
                G_h01_5A82 = p->w2;
                G_h01_5A84 = p->w4;
                draw_masked_sprite(&G_h01_5A82);
                if (--p->b27 == 0) {
                    p->b13 = 7;
                    p->b27 = 5;
                }
                break;
            case 7:
                G_h01_5A4C = p->w2;
                G_h01_5A4E = p->w4;
                draw_masked_sprite(&G_h01_5A4C);
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
            draw_masked_sprite(&G_h01_589C);
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
                draw_masked_sprite(&G_h01_5908);
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
            draw_masked_sprite(&G_h01_5B24);
            break;
        default:
            break;
        }
        p = (struct Obj *)((char *)p + 14);
    }
}
