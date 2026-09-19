/* Ownership probe for ov11_F_20F2: parse L header and seven-word rows. */
extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();

extern char G_h01_8A66[1];

recovered(text)
char *text;
{
    char *line;
    int rows;
    char *record;

    line = F_h00_75D8(text, 'L');
    if (F_h00_704E(line, "L %d", &rows) < 1)
        F_h00_3674(55);
    line = F_h00_75D8(line, '\n') + 1;
    record = G_h01_8A66;
    while ((record - G_h01_8A66) / 14 < rows) {
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d\n",
                record, record + 2, record + 4, record + 6,
                record + 8, record + 10, record + 12) != 7)
            F_h00_3674(67);
        line = F_h00_75D8(line, '\n') + 1;
        record += 14;
    }
}
