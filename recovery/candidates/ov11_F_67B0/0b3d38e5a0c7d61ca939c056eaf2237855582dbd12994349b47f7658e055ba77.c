struct Record {
    int field0;
    int field2;
    char unused[30];
    int field34;
    int field36;
    char unused2[2];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern F_h00_3674();
extern struct Record G_h01_A464[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'S');
    F_h00_704E(line, "S %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(521);
            goto next_record;
        }
        record = &G_h01_A464[index];
        if (F_h00_704E(line, "%*d %d %d %d %d\n",
                         &record->field0, &record->field2,
                         &record->field34, &record->field36) != 4)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(523);
next_record:
        ;
    }
}
