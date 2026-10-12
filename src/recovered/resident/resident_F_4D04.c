struct Level {
    unsigned int u0;
    unsigned int w2;
    char *p4;
};

struct Cell {
    unsigned int u0;
    char *p2;
};

extern struct Level *G_h01_27E4[1];
extern unsigned char *G_h01_1F9E[1];
extern unsigned char G_h01_2042[1];
extern char *G_h01_A7CE[1];
extern char *G_h01_46DA;
extern struct Cell *G_h01_B206[1];
extern unsigned int G_h01_A7DA;
extern long G_h01_B202;
extern char G_h01_B1F0;
extern int F_h00_2816();
extern long F_h00_291E();
extern int F_h00_46CE();

recovered(n)
unsigned int n;
{
    int i, v, w, k;
    long tmp_a;
    struct Level *pt;
    struct Level tmp_b;
    char *saved;

    w = 0;
    G_h01_B202 = k = 0;
    saved = G_h01_46DA;
    G_h01_46DA = G_h01_A7CE[G_h01_2042[n]];
    F_h00_2816(G_h01_46DA);
    for (i = 0; G_h01_1F9E[n][i] != 0xff; i++) {
        v = G_h01_1F9E[n][i];
        G_h01_B206[i] = 0;
        if (!(G_h01_B206[i] = F_h00_291E(v, 0L))) {
            G_h01_46DA = saved;
            return 0;
        }
        if (G_h01_A7DA == 6) {
            F_h00_46CE(k++ + 11, G_h01_B206[i]->p2);
        } else {
            pt = G_h01_27E4[i + 57];
            pt->w2 = G_h01_B206[i]->u0 >> 1;
            pt->p4 = G_h01_B206[i]->p2;
        }
        G_h01_B202 += G_h01_B206[i]->u0;
    }
    G_h01_B1F0 = n;
    switch (n) {
    case 0:
        break;
    default:
        break;
    }
    G_h01_46DA = saved;
    if (G_h01_46DA)
        F_h00_2816(G_h01_46DA);
}
