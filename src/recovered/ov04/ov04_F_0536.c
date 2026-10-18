struct ArcEntry {
    unsigned int length;
    char *text;
};

extern long arc_file;
extern char market_update_day;
extern char investment_company_table;
extern char investment_market_state;
extern char G_h01_4D84;
extern char G_h01_4D86;
extern char G_h01_4D88;
extern char market_price_history;

extern int request_disk();
extern long Open();
extern int arc_read_index();
extern long F_h00_291E();
extern long F_h00_0976();
extern int sscanf();
extern int F_h00_463E();
extern int F_h00_3C0E();
extern int Close();

recovered()
{
    struct ArcEntry *item;
    char *name;
    long unused1;
    long unused2;
    unsigned int i;
    int value;
    int spare_top;
    int state[15];
    int spare_after_state;
    int id;
    long saved;
    int j;
    int lower[3];
    char buffer[77];

    saved = arc_file;
    market_update_day = 0;
    request_disk(1);
    arc_file = Open("DT1:invest.arc", 1005L);
    arc_read_index(arc_file);

    for (i = 0; i < 15; ++i)
        state[i] = -1;

    for (i = 0; i < 15; ++i) {
        item = 0;
        item = (struct ArcEntry *)F_h00_291E(i, (long)item);
        name = item->text;
        id = item->length;
        item->text[item->length - 1] = 0;
        name = (char *)F_h00_0976(name,
            (char *)&investment_company_table + (long)i * 46L);
        name = (char *)F_h00_0976(name, buffer);
        sscanf(buffer, "%d %d",
            (int *)((char *)&investment_market_state + (long)i * 46L),
            (int *)((char *)&G_h01_4D88 + (long)i * 46L));
        *((unsigned int *)((char *)&investment_market_state + (long)i * 46L)) =
            (unsigned int)F_h00_463E() % 120;
        *((unsigned int *)((char *)&G_h01_4D88 + (long)i * 46L)) =
            (unsigned int)F_h00_463E() % 5;
        *((unsigned char *)((char *)&G_h01_4D86 + (long)i * 46L)) = 0;
        *((unsigned int *)((char *)&G_h01_4D84 + (long)i * 46L)) = 0;
        F_h00_3C0E(item);
    }

    Close(arc_file);
    request_disk(1);
    arc_file = Open("DT1:chart.arc", 1005L);
    arc_read_index(arc_file);

    for (i = 0; i < 5; ++i) {
        item = 0;
        item = (struct ArcEntry *)F_h00_291E(i, (long)item);
        name = item->text;
        id = item->length;
        j = 0;
        do {
            name = (char *)F_h00_0976(name, buffer);
            sscanf(buffer, "%d", &value);
            *((char *)&market_price_history + (long)i * 31L + j) = ((char *)&value)[1];
            ++j;
        } while (j < 30);
        F_h00_3C0E(item);
    }

    Close(arc_file);
    request_disk(1);
    arc_file = saved;
    arc_read_index(arc_file);
}
