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

recovered(p)
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
