/* Ownership probe for ov11_F_3926: parse F header and indexed records. */
struct Record {
    char unused0[4];
    int value1;
    int value2;
    char unused1[12];
    int value3;
    char unused2[12];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern int G_h01_A152;
extern struct Record G_h01_A15E[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'F');
    F_h00_704E(line, "F %d", &rows);
    G_h01_A152 = rows;
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(1021);
            goto next_record;
        }
        record = &G_h01_A15E[index];
        if (F_h00_704E(line, "%*d %d %d %d\n",
                &record->value1, &record->value2, &record->value3) != 3)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(1032);
next_record:
        ;
    }
}
