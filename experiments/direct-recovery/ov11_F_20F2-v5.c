/* Ownership probe for ov11_F_20F2: parse L header and seven-word rows. */
struct Record {
    int ignored;
    int value1;
    int value2;
    int value3;
    int value4;
    int value5;
    int value6;
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_8A66[1];

recovered(text)
char *text;
{
    char *line;
    int rows;
    struct Record *record;

    line = F_h00_75D8(text, 'L');
    if (F_h00_704E(line, "L %d", &rows) < 1)
        F_h00_3674(55);
    line = F_h00_75D8(line, '\n') + 1;
    for (record = G_h01_8A66; record - G_h01_8A66 < rows; record++) {
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d\n",
                &record->ignored, &record->value1, &record->value2,
                &record->value3, &record->value4, &record->value5,
                &record->value6) != 7)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(67);
next_record:
        ;
    }
}
