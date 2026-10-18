struct Sample {
    unsigned int field0;
    unsigned int length;
    char *data;
};
/* This function accesses entries 48..54; the complete table extent is unknown. */
extern struct Sample *audio_sample_descriptor_table[55];
extern long G_h01_A7CE;
extern unsigned long arc_record_stored_length;
extern int G_h01_A7D8;
extern int G_h01_A7E4;
extern int G_h01_B1FE;
extern char *G_h01_5426;
extern char *G_h01_5422;
extern long arc_read_index();
extern int read_arc_record_header();
extern int F_h00_46CE();
extern long Read();

recovered()
{
    int i;
    int state;
    int offset;
    int count;
    struct Sample *sample;

    offset = 0;
    arc_read_index(G_h01_A7CE);
    for (i = 0; i < 7; i++) {
        sample = audio_sample_descriptor_table[i + 48];
        if (read_arc_record_header(i + 11, G_h01_A7CE)) ;
        sample->length = arc_record_stored_length >> 1;
        sample->data = G_h01_5426 + offset;
        offset += G_h01_A7D8;
        Read(G_h01_A7CE, sample->data, arc_record_stored_length);
    }
    if (read_arc_record_header(18, G_h01_A7CE)) ;
    count = Read(G_h01_A7CE, G_h01_5426 + offset, arc_record_stored_length);
    F_h00_46CE(8, G_h01_5426 + offset);
    offset += G_h01_A7E4;
    G_h01_B1FE = offset;
    if (read_arc_record_header(19, G_h01_A7CE)) ;
    count = Read(G_h01_A7CE, G_h01_5422 + 4864, arc_record_stored_length);
    F_h00_46CE(9, G_h01_5422 + 4864);
    return 0;
}
