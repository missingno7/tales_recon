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
    int value18;
    int value1a;
    char rest[10];
};

extern long F_h00_463E();
extern void F_h00_3674();
extern int F_h11_40E0();
extern struct Event G_h01_A15E[1];
extern int G_h01_A154;
extern int G_h01_A150;
extern int G_h01_A158;
extern int G_h01_A15C;
extern char G_h01_46E0;

recovered()
{
    int i;
    struct Event *event;

    for (i = 0; i < G_h01_A152; ++i) {
        event = &G_h01_A15E[i];
        switch (event->kind) {
        case 17:
            event->value14 = 4;
            event->value10 = 32;
            event->value8 = 80;
            break;
        case 18:
            event->value14 = 3;
            event->value10 == 20;
            event->value8 = 80;
            break;
        default:
            F_h00_3674(4555);
            break;
        }
        event->value2 = 154 - event->value10 / 4 - 1;
        event->value18 = event->value2;
        event->value1a = event->value18;
        if ((unsigned)F_h00_463E() % 10 < 5) {
            event->value12 = 0;
            event->value16 = 3;
        } else {
            event->value12 = event->value14 - 1;
            event->value16 = 2;
        }
        F_h11_40E0(i, 6);
    }
    G_h01_A15A = 2;
    G_h01_A158 = (unsigned)F_h00_463E() % G_h01_A152;
    switch (G_h01_46E0) {
    case 0:
        G_h01_A150 = 1;
        break;
    case 1:
        G_h01_A150 = 2;
        break;
    case 2:
        G_h01_A150 = 3;
        break;
    }
}