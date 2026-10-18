struct Record {
    int field0;
    int field2;
    char unused[30];
    int field34;
    int field36;
    char unused2[2];
};

extern long F_h00_75D8();
extern int sscanf();
extern int report_loader_error();
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
    sscanf(line, "S %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (sscanf(line, " %d ", &index) < 1) {
            report_loader_error(521);
            goto next_record;
        }
        record = &G_h01_A464[index];
        if (sscanf(line, "%*d %d %d %d %d\n",
                         &record->field0, &record->field2,
                         &record->field34, &record->field36) != 4)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        report_loader_error(523);
next_record:
        ;
    }
}
