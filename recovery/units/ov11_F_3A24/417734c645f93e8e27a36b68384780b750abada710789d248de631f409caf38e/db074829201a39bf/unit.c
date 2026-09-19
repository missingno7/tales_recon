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
extern int G_h01_A152;
extern int G_h01_A150;
extern int G_h01_A158;
extern int G_h01_A15A;
extern char G_h01_46E0;

recovered()
{
    int i;
    struct Event *event;

    for (i = 0; i < G_h01_A152; ++i) {
        event = &G_h01_A15E[i];
        switch (event->kind) {
        case 18:
            event->value14 = 4;
            event->value10 = 32;
            event->value8 = 80;
            break;
        case 17:
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

