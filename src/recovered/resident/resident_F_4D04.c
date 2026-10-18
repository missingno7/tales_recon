struct Level {
    unsigned int u0;
    unsigned int w2;
    char *p4;
};

struct Cell {
    unsigned int u0;
    char *p2;
};

extern struct Level *audio_sample_descriptor_table[1];
extern unsigned char *G_h01_1F9E[1];
extern unsigned char G_h01_2042[1];
extern char *G_h01_A7CE[1];
extern char *arc_file;
extern struct Cell *G_h01_B206[1];
extern unsigned int G_h01_A7DA;
extern long G_h01_B202;
extern char G_h01_B1F0;
extern int arc_read_index();
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
    saved = arc_file;
    arc_file = G_h01_A7CE[G_h01_2042[n]];
    arc_read_index(arc_file);
    for (i = 0; G_h01_1F9E[n][i] != 0xff; i++) {
        v = G_h01_1F9E[n][i];
        G_h01_B206[i] = 0;
        if (!(G_h01_B206[i] = F_h00_291E(v, 0L))) {
            arc_file = saved;
            return 0;
        }
        if (G_h01_A7DA == 6) {
            F_h00_46CE(k++ + 11, G_h01_B206[i]->p2);
        } else {
            pt = audio_sample_descriptor_table[i + 57];
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
    arc_file = saved;
    if (arc_file)
        arc_read_index(arc_file);
}
