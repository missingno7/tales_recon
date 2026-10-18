/* Worker candidate fn-resident_F_46CE v4 variant: v4 index: (long)q + (long)(L16*p). */
struct Level {
    unsigned int u0;
    unsigned int w2;
    char *p4;
};

extern struct Level *audio_sample_descriptor_table[1];
extern unsigned int G_h01_A7DE;
extern unsigned int G_h01_A7E0;
extern unsigned int G_h01_A7E2;
extern unsigned int G_h01_A7E4;

recovered(n, base)
unsigned int n;
char *base;
{
    unsigned int p, q;
    unsigned int r;
    unsigned int L8;
    char *lv[3];
    unsigned int L16;
    char *src, *dst;
    struct Level *hdr, *plane, *pT;

    L8 = n * 3;
    hdr = audio_sample_descriptor_table[L8];
    plane = audio_sample_descriptor_table[L8] + 1;
    src = base + G_h01_A7DE;
    L16 = G_h01_A7E0 << G_h01_A7E2;
    dst = base + G_h01_A7E4 - (long)L16 * 3;
    hdr->w2 = G_h01_A7DE >> 1;
    hdr->p4 = base;
    for (p = 0; p < 3; p++) {
        plane = audio_sample_descriptor_table[L8 + p] + 1;
        plane->w2 = L16 >> 1;
        plane->p4 = dst + (long)L16 * p;
        for (q = 0; q < L16; q++)
            dst[(long)q + (long)(L16 * p)] = src[(q << p) % G_h01_A7E0];
    }
    lv[1] = base + G_h01_A7DE;
    lv[2] = base + ((G_h01_A7DE >> 1) + G_h01_A7DE);
    for (q = 1; q < 3; q++) {
        pT = audio_sample_descriptor_table[L8 + q];
        pT->w2 = G_h01_A7DE >> (q + 1);
        pT->p4 = lv[q];
        for (p = 0; p < (G_h01_A7DE >> q); p++)
            pT->p4[p] = hdr->p4[(p << q)];
    }
}
