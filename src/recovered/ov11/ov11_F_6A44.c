/* Parse adjacent V and J sections. */
struct VRecord {
    int field0;
    int field2;
    char unused0[8];
    int field12;
    int field14;
    int field16;
    char unused1[6];
    int field24;
    int field26;
    int field28;
    char unused2[4];
};

extern long F_h00_75D8();
extern int sscanf();
extern int report_loader_error();
extern struct VRecord jg_moving_object_records[1];
extern int G_h01_945C[1];

recovered(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct VRecord *record;

    line = F_h00_75D8(text, 'V');
    sscanf(line, "V %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (sscanf(line, "%d", &index) < 1) {
            report_loader_error(888);
            goto next_v;
        }
        record = &jg_moving_object_records[index];
        if (sscanf(line, "%*d %d %d %d %d %d %d %d %d\n",
                         &record->field12, &record->field14,
                         &record->field16, &record->field24,
                         &record->field26, &record->field28,
                         &record->field0, &record->field2) != 8)
            goto bad_v;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_v;
bad_v:
        report_loader_error(890);
next_v:
        ;
    }

    line = F_h00_75D8(text, 'J');
    sscanf(line, "J %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (sscanf(line, "%d", &index) < 1) {
            report_loader_error(988);
            goto next_j;
        }
        if (sscanf(line, "%*d %d \n", &G_h01_945C[index]) != 1)
            goto bad_j;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_j;
bad_j:
        report_loader_error(990);
next_j:
        ;
    }
}
