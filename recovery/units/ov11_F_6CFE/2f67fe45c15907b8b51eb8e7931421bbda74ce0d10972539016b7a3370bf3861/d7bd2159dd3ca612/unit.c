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

struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h11_5C42();
extern int F_h11_66FE();

F_h11_5962(index,mode)
int index;
int mode;
{
    struct ClusterRecord *record;

    record=&G_h01_8BEC[index];
    record->state40=2;
    if (record->value42==0 || mode==2) record->value42=mode;
    if (mode!=3 && record->value8) F_h11_5C42(index,2);
    if (mode!=8 && record->value10) F_h11_66FE(record->value10,2);
}

struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h11_4696();
extern int F_h11_5962();

F_h11_5C42(index,mode)
int index;
int mode;
{
    struct ClusterRecord *record;

    record=&G_h01_8BEC[index];
    record->state30=2;
    if (record->value32==0 || mode==3) record->value32=mode;
    if (mode==3) {
        F_h11_4696(record->value2c,record->value2e-6,72,32,24);
        if (record->value14) F_h11_5962(record->value14,2);
        if (record->value16) F_h11_5962(record->value16,2);
    }
}

struct Record { int padding[11],state,value; char tail[14]; };
extern struct Record G_h01_A464[36];
F_h11_66FE(a,b) int a,b; { struct Record *p; p=&G_h01_A464[a]; p->state=2; if(!p->value || b==8)p->value=b; }

struct Record { int unused0, unused2; int left, right, top, bottom; int initial_x, initial_y, offset_y; int x, y, flags; int unused24, unused26, unused28; int step, active; };
extern int G_h01_94AE;
extern int G_h01_94D8;
extern struct Record G_h01_A554[10];
extern int F_h00_57D2();
extern int F_h11_4696();
extern int F_h11_5962();
extern int F_h11_727A();
extern int F_h11_729C();

recovered(index)
int index;
{
    struct Record *record;
    int dx;
    int dy;

    record = &G_h01_A554[index];
    record->flags += record->unused28;
    if (record->flags > record->unused26) {
        record->unused28 *= -1;
        if (G_h01_94AE == 8 && index == G_h01_94D8)
            F_h00_57D2(0x5a);
    } else {
        if (record->flags < record->unused24) {
            record->unused28 *= -1;
            if (G_h01_94AE == 8 && index == G_h01_94D8)
                F_h00_57D2(0x5d);
        }
    }

    record->x = record->initial_x +
        (F_h11_729C(record->flags - 0x80) * record->offset_y) / 0x100;
    record->y = record->initial_y +
        (F_h11_727A(record->flags - 0x80) * record->offset_y) / 0x100;

    if (record->initial_x <= record->right) {
        dx = record->right - record->initial_x;
        record->right = record->initial_x;
    } else {
        dx = record->initial_x - record->right;
    }
    dx += 0x10;
    dy = record->bottom - record->initial_y + 1;
    F_h11_4696(record->right, record->initial_y, dx, dy, index + 0x1c);

    if (record->unused0)
        F_h11_5962(record->unused0, 4);
    if (record->unused2)
        F_h11_5962(record->unused2, 4);
}

extern int G_h01_1322[64];

unsigned F_h11_727A(n)
unsigned n;
{
    return G_h01_1322[(n >> 2) & 63];
}

extern int G_h01_13A2[64];

unsigned F_h11_729C(n)
unsigned n;
{
    return G_h01_13A2[(n >> 2) & 63];
}

