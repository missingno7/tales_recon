/* Parse M records into 64-byte resident records. */
struct Record {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_9FCE[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'M');
    F_h00_704E(line, "M %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, "%d ", &index) < 1) {
            F_h00_3674(901);
            goto next_record;
        }
        record = &G_h01_9FCE[index];
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d\n",
                         &record->field24, &record->field26,
                         &record->field28, &record->field30,
                         &record->field32, &record->field0) != 6)
            goto bad_record;
        record->field34 = record->field30;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(902);
next_record:
        ;
    }
}
