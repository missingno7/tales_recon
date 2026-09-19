/* Parse X records into the observed ten-byte resident records. */
struct Record {
    int field0;
    int field2;
    char unused[6];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_A6A8[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'X');
    F_h00_704E(line, "X %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, "%d ", &index) < 1) {
            F_h00_3674(914);
            goto next_record;
        }
        record = &G_h01_A6A8[index];
        if (F_h00_704E(line, "%*d %d %d\n",
                         &record->field0, &record->field2) != 2)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(917);
next_record:
        ;
    }
}
