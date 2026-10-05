struct ArcEntry {
    unsigned int length;
    char *text;
};

extern long G_h01_46DA;
extern char G_h01_4D60;
extern char G_h01_4D62;
extern char G_h01_4D82;
extern char G_h01_4D84;
extern char G_h01_4D86;
extern char G_h01_4D88;
extern char G_h01_5014;

extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_463E();
extern int F_h00_3C0E();
extern int F_h00_868C();

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

    saved = G_h01_46DA;
    G_h01_4D60 = 0;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:invest.arc", 1005L);
    F_h00_2816(G_h01_46DA);

    for (i = 0; i < 15; ++i)
        state[i] = -1;

    for (i = 0; i < 15; ++i) {
        item = 0;
        item = (struct ArcEntry *)F_h00_291E(i, (long)item);
        name = item->text;
        id = item->length;
        item->text[item->length - 1] = 0;
        name = (char *)F_h00_0976(name,
            (char *)&G_h01_4D62 + (long)i * 46L);
        name = (char *)F_h00_0976(name, buffer);
        F_h00_704E(buffer, "%d %d",
            (int *)((char *)&G_h01_4D82 + (long)i * 46L),
            (int *)((char *)&G_h01_4D88 + (long)i * 46L));
        *((unsigned int *)((char *)&G_h01_4D82 + (long)i * 46L)) =
            (unsigned int)F_h00_463E() % 120;
        *((unsigned int *)((char *)&G_h01_4D88 + (long)i * 46L)) =
            (unsigned int)F_h00_463E() % 5;
        *((unsigned char *)((char *)&G_h01_4D86 + (long)i * 46L)) = 0;
        *((unsigned int *)((char *)&G_h01_4D84 + (long)i * 46L)) = 0;
        F_h00_3C0E(item);
    }

    F_h00_868C(G_h01_46DA);
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:chart.arc", 1005L);
    F_h00_2816(G_h01_46DA);

    for (i = 0; i < 5; ++i) {
        item = 0;
        item = (struct ArcEntry *)F_h00_291E(i, (long)item);
        name = item->text;
        id = item->length;
        j = 0;
        do {
            name = (char *)F_h00_0976(name, buffer);
            F_h00_704E(buffer, "%d", &value);
            *((char *)&G_h01_5014 + (long)i * 31L + j) = ((char *)&value)[1];
            ++j;
        } while (j < 30);
        F_h00_3C0E(item);
    }

    F_h00_868C(G_h01_46DA);
    F_h00_0FDE(1);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}
