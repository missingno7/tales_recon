/* Direct recovery candidate for ov04_F_0104. */
struct Location {
    char pad[30];
    int selected;
    int a;
    int b;
    int c;
    int d;
};

extern long G_h01_46DA;
extern char G_h01_470A;
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_7AF0();
extern int F_h00_3C0E();
extern unsigned int F_h00_463E();
extern int F_h00_868C();
extern int F_h04_0088();
extern int F_h04_00C4();
extern int F_h04_00E6();

recovered()
{
    int count;
    struct Location *location;
    long state;
    long page;
    long saved;
    int choices[35];
    char text[81];
    int row;
    int picked;

    page = 0;
    row = 0;
    picked = 0;
    for (count = 1; count < 35; ++count)
        choices[count] = 36;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loc.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    page = 0;
    page = F_h00_291E(0, page);
    choices[0] = 0;
    location = (struct Location *)&G_h01_470A;
    state = *(long *)((char *)page + 2);
    state = F_h00_0976(state, text);
    F_h00_704E(text, "%d %d %d %d", &location->a, &location->b,
        &location->c, &location->d);
    location->selected = 0;
    state = F_h00_0976(state, text);
    F_h00_7AF0(location, text);
    F_h00_3C0E(page);
    row = F_h00_463E();
    row = (unsigned)row % 30;
    picked = F_h00_463E();
    picked = (unsigned)picked % 5;
    for (count = 1; count < 35; ++count) {
        while (!F_h04_0088(row, choices))
            row = F_h04_00E6(row);
        choices[(unsigned)row] = row;
        location = (struct Location *)(&G_h01_470A + (long)count * 40);
        page = 0;
        page = F_h00_291E(row, page);
        state = *(long *)((char *)page + 2);
        state = F_h00_0976(state, text);
        F_h00_704E(text, "%d %d %d %d", &location->a, &location->b,
            &location->c, &location->d);
        state = F_h00_0976(state, text);
        F_h00_7AF0(location, text);
        location->selected = row;
        F_h00_3C0E(page);
        row = F_h04_00C4(row, picked);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}
