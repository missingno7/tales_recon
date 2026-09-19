/* Ownership probe for ov11_F_506A: parse P header and 40-byte records. */
struct Record {
    char unused[24];
    int value24;
    int value26;
    int value28;
    int value30;
    int value32;
    int value34;
    int value36;
    int value38;
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_3724[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'P');
    F_h00_704E(line, "P %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(435);
            goto next_record;
        }
        record = &G_h01_3724[index];
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d %d\n",
                &record->value34, &record->value36, &record->value38,
                &record->value26, &record->value28, &record->value30,
                &record->value32, &record->value24) != 8)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(444);
next_record:
        ;
    }
}
