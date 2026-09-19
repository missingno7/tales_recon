/* Direct recovery candidate for ov04_F_0104. */
struct Location {
    char pad[32];
    int a;
    int b;
    int c;
    int d;
};

extern long G_h01_46DA;
extern struct Location G_h01_470A[1];
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
    int choices[35];
    char text[81];
    int picked;
    int count;
    int row;
    long page;
    long state;
    long saved;
    struct Location *location;

    for (count = 1; count < 35; ++count)
        choices[count] = 36;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loc.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    page = F_h00_291E(0, 0L);
    choices[0] = 0;
    location = G_h01_470A;
    state = *(long *)((char *)page + 2);
    state = F_h00_0976(state, text);
    F_h00_704E(text, "%d %d %d %d", location->a, location->b,
        location->c, location->d);
    location->a = 0;
    state = F_h00_0976(state, text);
    F_h00_7AF0(location, text);
    F_h00_3C0E(page);
    row = (unsigned)F_h00_463E() % 30;
    picked = (unsigned)F_h00_463E() % 5;
    for (count = 1; count < 35; ++count) {
        while (!F_h04_0088(row, choices))
            row = F_h04_00E6(row);
        choices[row] = count;
        location = &G_h01_470A[count];
        page = F_h00_291E(row, 0L);
        state = *(long *)((char *)page + 2);
        state = F_h00_0976(state, text);
        F_h00_704E(text, "%d %d %d %d", location->a, location->b,
            location->c, location->d);
        state = F_h00_0976(state, text);
        F_h00_7AF0(location, text);
        location->a = row;
        F_h00_3C0E(page);
        row = F_h04_00C4(row, picked);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}
