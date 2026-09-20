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
    char rest[12];
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
            if (event->value4) {
                if (event->value1a + event->value8 > 1168) {
                    if (event->value12 < event->value14)
                        ++event->value12;
                }
            } else if (event->value4 == 1 && (F_h00_463E() & 15) < event->value18) {
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
        if ((G_h01_94C0 + 16) >> 5 >= 3)
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
/* Direct reconstruction candidate for ov11_F_40E0. */
struct Record {
    char pad0[22];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};

extern struct Record G_h01_A15E[1];
extern int F_h11_4696();

F_h11_40E0(index, mode)
int index;
int mode;
{
    struct Record *record;

    record = &G_h01_A15E[index];
    record->state = 2;
    if (record->value30 == 0 || mode == 6)
        record->value30 = mode;
    if (mode == 6)
        F_h11_4696(record->value22, record->value26, 88, 30,
                   index % 4 + 18);
}
/* Direct reconstruction candidate for ov11_F_4696. */
struct Rect {
    int kind;
    int x;
    int y;
    int width;
    int height;
    int index;
    char pad[2];
};

extern struct Rect G_h01_34EC[40];
extern int G_h01_8A3C;
extern int G_h01_8A3E;

F_h11_4696(x, y, width, height, index)
int x;
int y;
int width;
int height;
int index;
{
    struct Rect *rect;

    rect = &G_h01_34EC[index];
    if (G_h01_8A3C < 2) {
        x -= G_h01_8A3E;
        if (x < 0) {
            width += x;
            if (width <= 0)
                return;
            x = 0;
        } else {
            if (x >= 320)
                return;
            if (x + width > 320)
                width = 320 - x + 8;
        }
        if (y < 0) {
            height += y;
            if (height <= 0)
                return;
            y = 0;
        } else {
            if (y > 176)
                return;
            if (y + height > 176)
                height = 176 - y;
        }
        if (height <= 0)
            return;
        if (width <= 0)
            return;
        rect->kind = 2;
        rect->x = x;
        rect->y = y;
        rect->width = width;
        rect->height = height;
        rect->index = index;
    }
}

