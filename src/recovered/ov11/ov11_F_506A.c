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
extern int sscanf();
extern int report_loader_error();
extern struct Record jg_scenery_object_records[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'P');
    sscanf(line, "P %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (sscanf(line, " %d ", &index) < 1) {
            report_loader_error(435);
            goto next_record;
        }
        record = &jg_scenery_object_records[index];
        if (sscanf(line, "%*d %d %d %d %d %d %d %d %d\n",
                &record->value34, &record->value36, &record->value38,
                &record->value26, &record->value28, &record->value30,
                &record->value32, &record->value24) != 8)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        report_loader_error(444);
next_record:
        ;
    }
}
