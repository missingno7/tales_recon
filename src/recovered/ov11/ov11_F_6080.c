struct ARecord { int value0; int value2; int value4; int value6; };
struct BRecord {
    int value0; int value2; int value4; int value6; int value8;
    int value10; int value12; int value14; int value16;
    char padding[26]; int value44; int value46; int unused48; int unused50;
};

extern long F_h00_75D8();
extern int sscanf();
extern int report_loader_error();
extern struct ARecord jg_grid_tile_indices[1];
extern struct BRecord jg_platform_records[1];
extern int G_h01_37EC;

recovered(text)
char *text;
{
    char *line;
    int rows;
    struct BRecord *record;
    int i;

    line = F_h00_75D8(text, 'A');
    if (sscanf(line, "A %d", &rows) < 1)
        report_loader_error(231);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; ++i) {
        if (sscanf(line, "%*d %d %d %d %d\n",
                &jg_grid_tile_indices[i].value0, &jg_grid_tile_indices[i].value2,
                &jg_grid_tile_indices[i].value4, &jg_grid_tile_indices[i].value6) == 4)
            line = F_h00_75D8(line, '\n') + 1;
        else
            report_loader_error(241);
    }
    line = F_h00_75D8(text, 'B');
    if (sscanf(line, "B %d", &rows) < 1)
        report_loader_error(88);
    G_h01_37EC = rows;
    if (G_h01_37EC > 40)
        report_loader_error(89);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0, record = jg_platform_records; i < rows; ++i, ++record) {
        if (sscanf(line, "%*d %d %d %d %d %d %d %d %d %d %d %d\n",
                &record->value0, &record->value2, &record->value44,
                &record->value46, &record->value4, &record->value6,
                &record->value8, &record->value10, &record->value12,
                &record->value14, &record->value16) == 11)
            line = F_h00_75D8(line, '\n') + 1;
        else
            report_loader_error(89);
    }
}
