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
