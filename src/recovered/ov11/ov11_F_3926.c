/* Ownership probe for ov11_F_3926: parse F header and indexed records. */
struct Record {
    char unused0[4];
    int value1;
    int value2;
    char unused1[10];
    int value3;
    char unused2[12];
};

extern long F_h00_75D8();
extern int sscanf();
extern int report_loader_error();
extern int G_h01_A152;
extern struct Record jg_event_records[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'F');
    sscanf(line, "F %d", &rows);
    G_h01_A152 = rows;
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (sscanf(line, " %d ", &index) < 1) {
            report_loader_error(1021);
            goto next_record;
        }
        record = &jg_event_records[index];
        if (sscanf(line, "%*d %d %d %d\n",
                &record->value2, &record->value1, &record->value3) != 3)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        report_loader_error(1032);
next_record:
        ;
    }
}
