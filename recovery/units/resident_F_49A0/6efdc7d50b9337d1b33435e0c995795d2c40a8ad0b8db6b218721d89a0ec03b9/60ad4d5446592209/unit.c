extern long F_h00_8708();
extern long F_h00_2DBA();
extern long F_h00_2D66();
extern long G_h01_A7EE[104];
extern long G_h01_A7D6;
extern int G_h01_A7DA;
extern int G_h01_A7DC;
extern int G_h01_A7DE;
extern int G_h01_A7E0;
extern int G_h01_A7E2;
extern int G_h01_A7E4;

F_h00_287C(index, fh)
int index;
long fh;
{
    long offset;
    offset = G_h01_A7EE[index];
    F_h00_8708(fh, offset, -1L);
    F_h00_2DBA(fh, &G_h01_A7D6);
    F_h00_2D66(fh, &G_h01_A7DA);
    F_h00_2D66(fh, &G_h01_A7DC);
    F_h00_2D66(fh, &G_h01_A7DE);
    F_h00_2D66(fh, &G_h01_A7E0);
    F_h00_2D66(fh, &G_h01_A7E2);
    F_h00_2D66(fh, &G_h01_A7E4);
    return 0;
}


extern long F_h00_86F6();
extern short G_h01_A7E8;

F_h00_2D66(fh, buf)
long fh;
char *buf;
{
    char *p;
    char c;

    F_h00_86F6(fh, buf, 2L);
    G_h01_A7E8 = *(short *)buf;
    p = buf;
    c = *p;
    *p = p[1];
    p[1] = c;
    G_h01_A7E8 = *(short *)buf;
}

extern long F_h00_86F6();
extern long G_h01_A7EA;

long F_h00_2DBA(fh, buf)
long fh;
char *buf;
{
    char *p;
    char c;

    F_h00_86F6(fh, buf, 4L);
    G_h01_A7EA = *(long *)buf;
    p = buf;
    c = *p;
    p[0] = p[3];
    p[3] = c;
    c = p[1];
    p[1] = p[2];
    p[2] = c;
    G_h01_A7EA = *(long *)buf;
}

/* Worker candidate fn-resident_F_46CE v4 variant: v4 index: (long)q + (long)(L16*p). */
struct Level {
    unsigned int u0;
    unsigned int w2;
    char *p4;
};

extern struct Level *G_h01_27E4[1];
extern unsigned int G_h01_A7DE;
extern unsigned int G_h01_A7E0;
extern unsigned int G_h01_A7E2;
extern unsigned int G_h01_A7E4;

F_h00_46CE(n, base)
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
    hdr = G_h01_27E4[L8];
    plane = G_h01_27E4[L8] + 1;
    src = base + G_h01_A7DE;
    L16 = G_h01_A7E0 << G_h01_A7E2;
    dst = base + G_h01_A7E4 - (long)L16 * 3;
    hdr->w2 = G_h01_A7DE >> 1;
    hdr->p4 = base;
    for (p = 0; p < 3; p++) {
        plane = G_h01_27E4[L8 + p] + 1;
        plane->w2 = L16 >> 1;
        plane->p4 = dst + (long)L16 * p;
        for (q = 0; q < L16; q++)
            dst[(long)q + (long)(L16 * p)] = src[(q << p) % G_h01_A7E0];
    }
    lv[1] = base + G_h01_A7DE;
    lv[2] = base + ((G_h01_A7DE >> 1) + G_h01_A7DE);
    for (q = 1; q < 3; q++) {
        pT = G_h01_27E4[L8 + q];
        pT->w2 = G_h01_A7DE >> (q + 1);
        pT->p4 = lv[q];
        for (p = 0; p < (G_h01_A7DE >> q); p++)
            pT->p4[p] = hdr->p4[(p << q)];
    }
}

struct Sample {
    unsigned int field0;
    unsigned int length;
    char *data;
};
/* This function accesses entries 48..54; the complete table extent is unknown. */
extern struct Sample *G_h01_27E4[55];
extern long G_h01_A7CE;
extern unsigned long G_h01_A7D6;
extern int G_h01_A7D8;
extern int G_h01_A7E4;
extern int G_h01_B1FE;
extern char *G_h01_5426;
extern char *G_h01_5422;
extern long F_h00_2816();
extern int F_h00_287C();
extern int F_h00_46CE();
extern long F_h00_86F6();

recovered()
{
    int i;
    int state;
    int offset;
    int count;
    struct Sample *sample;

    offset = 0;
    F_h00_2816(G_h01_A7CE);
    for (i = 0; i < 7; i++) {
        sample = G_h01_27E4[i + 48];
        if (F_h00_287C(i + 11, G_h01_A7CE)) ;
        sample->length = G_h01_A7D6 >> 1;
        sample->data = G_h01_5426 + offset;
        offset += G_h01_A7D8;
        F_h00_86F6(G_h01_A7CE, sample->data, G_h01_A7D6);
    }
    if (F_h00_287C(18, G_h01_A7CE)) ;
    count = F_h00_86F6(G_h01_A7CE, G_h01_5426 + offset, G_h01_A7D6);
    F_h00_46CE(8, G_h01_5426 + offset);
    offset += G_h01_A7E4;
    G_h01_B1FE = offset;
    if (F_h00_287C(19, G_h01_A7CE)) ;
    count = F_h00_86F6(G_h01_A7CE, G_h01_5422 + 4864, G_h01_A7D6);
    F_h00_46CE(9, G_h01_5422 + 4864);
    return 0;
}

