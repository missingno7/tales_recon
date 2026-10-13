/* Direct reconstruction candidate for ov11_F_40AE. */
struct Event {
    char pad0[2];
    int value2;
    char pad4[2];
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad18[6];
    int value18;
    int value1a;
    char rest[4];
};

extern short G_h01_A156;
extern struct Event G_h01_A15E[1];
extern int F_h00_57D2();
extern int F_h00_86A8();

F_h11_40AE(index)
int index;
{
    struct Event *record;

    record = &G_h01_A15E[index];
    G_h01_A156 = 0;
    F_h00_86A8(5L);
    F_h00_57D2(91);
}
