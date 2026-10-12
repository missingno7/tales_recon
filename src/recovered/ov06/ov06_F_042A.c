struct Rec {
    int f0;
    int f2;
    int f4;
    int f6;
    char rest[46];
};

extern int F_h00_34E0();
extern int G_h01_302C;
extern int G_h01_302E;
extern char G_h01_3096;
extern char G_h01_30CC;
extern struct Rec G_h01_30CE[6];
extern int G_h01_322A;
extern int G_h01_322C;
extern int G_h01_322E;
extern int G_h01_3230;

recovered(a1, a2, a3, a4, pv, c, n1, n2)
int a1, a2, a3, a4;
long pv;
char c;
int n1, n2;
{
    int i;
    int spare;
    struct Rec *p;
    struct Rec *q;
    int shift;

    shift = 3;
    p = G_h01_30CE;
    q = G_h01_30CE;
    F_h00_34E0(pv);
    G_h01_302C = a1;
    G_h01_302E = a2;
    for (i = 0; i <= n1; i++) {
        p->f0 = ((0x70 - (p->f4 << shift)) >> 1) + G_h01_302C;
        p->f2 = G_h01_302E - p->f6;
        if (i == 0)
            p->f0 = p->f0 + 8;
        else if (i == 1)
            p->f2 = p->f2 - 14;
        else if (i == 3) {
            p->f0 = p->f0 - 8;
            p->f2 = p->f2 - 13;
        } else if (i == 4)
            p->f2 = p->f2 - 27;
        F_h00_34E0(p);
        G_h01_322A = p->f0;
        G_h01_322C = p->f2;
        p++;
    }
    if (n1 > -1)
        p--;
    F_h00_34E0(&G_h01_302C);
    G_h01_302C = a3;
    G_h01_302E = a4;
    for (i = 0; i <= n2; i++) {
        q->f0 = ((0x70 - (q->f4 << shift)) >> 1) + G_h01_302C;
        q->f2 = G_h01_302E - q->f6;
        if (i == 0)
            q->f0 = q->f0 + 8;
        else if (i == 1)
            q->f2 = q->f2 - 14;
        else if (i == 3) {
            q->f0 = q->f0 - 8;
            q->f2 = q->f2 - 13;
        } else if (i == 4)
            q->f2 = q->f2 - 27;
        F_h00_34E0(q);
        G_h01_322E = q->f0;
        G_h01_3230 = q->f2;
        q++;
    }
    F_h00_34E0(&G_h01_302C);
    G_h01_3096 = c;
    G_h01_30CC = c;
}
