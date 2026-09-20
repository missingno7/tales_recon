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

extern int F_h00_463E();
extern int F_h11_40E0();
extern struct Event G_h01_A15E[1];
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern int G_h01_8A42;
extern int G_h01_94C0;
extern int G_h01_A150;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;
extern int G_h01_A15A;

recovered()
{
    int base;
    int index;
    int i;
    struct Event *event;

    if (G_h01_8A42)
        G_h01_A15A = 3;
    else if (G_h01_A15A <= 0)
        G_h01_A15A = 2;
    --G_h01_A15A;
    base = (G_h01_A158 + G_h01_8A3E / 128) % G_h01_A152;
    for (i = 0; i < 5; ++i) {
        index = (base + i) % G_h01_A152;
        event = &G_h01_A15E[index];
        if (G_h01_A15A == 0) {
            if (event->pad4[0]) {
                if (event->value18 + event->value8 > 1168) {
                    if (event->value12 < event->value14)
                        ++event->value12;
                }
            } else if (event->pad4[0] == 1 && (F_h00_463E() & 15) < event->value16) {
                if (event->value16 == 2) {
                    if (event->value12 <= 0) {
                        if ((F_h00_463E() & 15) < G_h01_A150)
                            event->value16 = 3;
                    } else
                        --event->value12;
                } else if (event->value16 == 3) {
                    if (event->value12 >= event->value14) {
                        if ((F_h00_463E() & 15) < G_h01_A150)
                            event->value16 = 2;
                    } else
                        ++event->value12;
                }
            }
            F_h11_40E0(index, 6);
        }
        if ((G_h01_94C0 + 16) / 32 >= 3)
            F_h11_40E0(index, 10);
        else if (G_h01_8A3C)
            F_h11_40E0(index, 6);
    }
    if (G_h01_A15A == 0) {
        G_h01_A154 += 4;
        if (G_h01_A154 >= 128) {
            G_h01_A154 = 0;
            --G_h01_A158;
            if (G_h01_A158 < 0)
                G_h01_A158 = G_h01_A152 - 1;
        }
    }
}