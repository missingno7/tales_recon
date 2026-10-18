struct Event {
    char pad0[2];
    int value2;
    int value4;
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

extern int F_h00_463E();
extern int jg_set_event_draw_state();
extern struct Event jg_event_records[1];
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
    int quotient;
    int base;
    struct Event *event;
    int i;
    int index;

    if (G_h01_8A42)
        G_h01_A15A = 3;
    else if (G_h01_A15A <= 0)
        G_h01_A15A = 2;
    --G_h01_A15A;
    quotient = G_h01_8A3E / 128;
    base = (G_h01_A158 + quotient) % G_h01_A152;
    for (i = 0; i < 5; ++i) {
        event = &jg_event_records[(base + i) % G_h01_A152];
        index = (base + i) % G_h01_A152;
        if (G_h01_A15A == 0) {
            if (event->value4 && event->value1a + event->value8 > 1168) {
                if (event->value12 < event->value14)
                    ++event->value12;
            } else if (event->value4 == 1 && (unsigned)(F_h00_463E() & 15) < (unsigned)event->value18) {
                if (event->value16 == 2) {
                    if (event->value12 <= 0 &&
                        (unsigned)(F_h00_463E() & 15) < (unsigned)G_h01_A150)
                        event->value16 = 3;
                    else if (event->value12 > 0)
                        --event->value12;
                } else if (event->value16 == 3) {
                    if (event->value12 >= event->value14 &&
                        (unsigned)(F_h00_463E() & 15) < (unsigned)G_h01_A150)
                        event->value16 = 2;
                    else if (event->value12 < event->value14)
                        ++event->value12;
                }
            }
            jg_set_event_draw_state(index, 6);
        }
        if ((G_h01_94C0 + 16) >> 5 >= 3)
            jg_set_event_draw_state(index, 10);
        else if (G_h01_8A3C)
            jg_set_event_draw_state(index, 6);
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