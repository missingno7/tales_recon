F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

extern int F_h11_25D6();
F_h11_25F8(a,b,c,d,e,f) int a,b,c,d,e,f; { return F_h11_25D6(a,c,e) && F_h11_25D6(b,d,f); }

struct Record { int pad[23]; int state; int gap; int x,y; char tail[10]; };
extern struct Record G_h01_9FCE[36];
F_h11_37A0(n,x,y) int n,*x,*y; {
 struct Record *p;
 p=&G_h01_9FCE[n];
 if(p->state) { *x=p->x; *y=p->y; }
 return p->state;
}

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
    char pad12[2];
    int work14;
    int work16;
    int work18;
    int work1a;
    int count1c;
    int value1e;
};
struct Sprite { int x,y; char pad4[48]; char value34; };
extern int F_h11_37A0();
extern int F_h11_25F8();
extern int F_h11_40E0();
extern void F_h00_34E0();
extern struct Event G_h01_A15E[1];
extern struct Sprite *G_h01_9F66;
extern struct Sprite *G_h01_9F8A;
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;

recovered()
{
    int quotient;
    int base;
    int i;
    int x;
    int y;
    struct Event *event;
    int screen_x;
    int screen_y;

    quotient = G_h01_8A3E / 128;
    base = (G_h01_A158 + quotient) % G_h01_A152;
    for (i = 0; i < 4; ++i) {
        event = &G_h01_A15E[(base + i) % G_h01_A152];
        if (event->value4 == 1) {
            screen_x = (quotient + i - 1) * 128 + G_h01_A154;
            screen_y = event->value2;
            if (G_h01_7A92 && F_h11_37A0(G_h01_7A92, &x, &y) &&
                F_h11_25F8(screen_x, screen_y - event->value10, x, y,
                            event->value8 + screen_x, event->value10 + screen_y))
                F_h11_40E0((base + i) % G_h01_A152, 7);
        }
        if (event->count1c > 0 && event->value12 < event->value14) {
            switch (event->kind) {
            case 18:
                G_h01_9F66->value34 = ((unsigned char *)&event->value12)[1];
                G_h01_9F66->x = screen_x - G_h01_8A3E;
                G_h01_9F66->y = screen_y;
                if (G_h01_9F66->x < 320)
                    F_h00_34E0(G_h01_9F66);
                break;
            case 17:
                G_h01_9F8A->value34 = ((unsigned char *)&event->value12)[1];
                G_h01_9F8A->x = screen_x - G_h01_8A3E;
                G_h01_9F8A->y = screen_y;
                if (G_h01_9F8A->x < 320)
                    F_h00_34E0(G_h01_9F8A);
                break;
            }
            --event->count1c;
            if (event->count1c == 0)
                event->value1e = 0;
        }
        event->work16 = event->work14;
        event->work1a = event->work18;
        event->work14 = screen_x;
        event->work18 = screen_y;
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

