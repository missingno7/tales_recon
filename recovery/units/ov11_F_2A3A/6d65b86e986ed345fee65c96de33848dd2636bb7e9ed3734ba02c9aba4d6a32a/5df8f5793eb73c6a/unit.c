struct Record {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};

struct Slot { long value; char unused[12]; };

extern char G_h01_46E0;
extern char G_h01_9D2C[1];
extern char G_h01_9D4C[1];
extern char G_h01_9D6C[1];
extern char G_h01_9D9C[1];
extern char G_h01_9E5C[1];
extern long G_h01_9F6A;
extern struct Record G_h01_9FCE[1];
extern int G_h01_1300[16];
extern int G_h01_34D8[16];

extern int G_h01_9D30;
extern int G_h01_9D40;
extern int G_h01_9D4A;
extern int G_h01_9D50;
extern int G_h01_9D5A;
extern int G_h01_9D60;
extern int G_h01_9D6A;
extern int G_h01_9D70;
extern int G_h01_9D72;
extern int G_h01_9D80;
extern int G_h01_9D82;
extern int G_h01_9D90;
extern int G_h01_9DA0;
extern int G_h01_9DB0;
extern int G_h01_9DB2;
extern int G_h01_9DC0;
extern int G_h01_9DD0;
extern int G_h01_9DD2;
extern int G_h01_9DE0;
extern int G_h01_9DF0;
extern int G_h01_9DF2;
extern int G_h01_9E00;
extern int G_h01_9E10;
extern int G_h01_9E12;
extern int G_h01_9E20;
extern int G_h01_9E30;
extern int G_h01_9E32;
extern int G_h01_9E40;
extern int G_h01_9E50;
extern int G_h01_9E52;
extern int G_h01_9E60;
extern int G_h01_9E62;
extern int G_h01_9E70;
extern int G_h01_9E72;
extern int G_h01_9E80;
extern int G_h01_9E82;
extern int G_h01_9E90;
extern int G_h01_9E92;
extern int G_h01_9EA0;
extern int G_h01_9EA2;

extern int F_h11_2E26();
extern int F_h11_41F6();

recovered()
{
    int i;
    struct Record *record;

    for (i = 0; i < 2; i++) {
        ((struct Slot *)G_h01_9D4C)[i].value = G_h01_9F6A;
        ((struct Slot *)G_h01_9D2C)[i].value = G_h01_9F6A;
    }

    G_h01_9D50 = 0;
    G_h01_9D5A = 0;
    G_h01_9D60 = 1;
    G_h01_9D6A = 12;
    G_h01_9D30 = 0;
    G_h01_9D40 = 1;
    G_h01_9D4A = 12;

    for (i = 0; i < 3; i++)
        ((struct Slot *)G_h01_9D6C)[i].value = G_h01_9F6A;

    G_h01_9D70 = 2;
    G_h01_9D72 = 5;
    G_h01_9D80 = 3;
    G_h01_9D82 = 128;
    G_h01_9D90 = 1;

    for (i = 0; i < 12; i++)
        ((struct Slot *)G_h01_9D9C)[i].value = G_h01_9F6A;

    G_h01_9DA0 = 4;
    G_h01_9DB0 = 5;
    G_h01_9DB2 = 2;
    G_h01_9DC0 = 4;
    G_h01_9DD0 = 5;
    G_h01_9DD2 = 2;
    G_h01_9DE0 = 4;
    G_h01_9DF0 = 5;
    G_h01_9DF2 = 2;
    G_h01_9E00 = 4;
    G_h01_9E10 = 5;
    G_h01_9E12 = 2;
    G_h01_9E20 = 4;
    G_h01_9E30 = 5;
    G_h01_9E32 = 2;
    G_h01_9E40 = 4;
    G_h01_9E50 = 5;
    G_h01_9E52 = 2;

    for (i = 0; i < 5; i++)
        ((struct Slot *)G_h01_9E5C)[i].value = G_h01_9F6A;

    G_h01_9E60 = 6;
    G_h01_9E62 = 3;
    G_h01_9E70 = 7;
    G_h01_9E72 = 0;
    G_h01_9E80 = 7;
    G_h01_9E82 = 0;
    G_h01_9E90 = 7;
    G_h01_9E92 = 64;
    G_h01_9EA0 = 6;
    G_h01_9EA2 = 3;

    switch (G_h01_46E0) {
    case 0:
        G_h01_34D8[8] = 6;
        break;
    case 1:
        G_h01_1300[13] = 50;
        G_h01_1300[14] = 75;
        G_h01_1300[15] = 75;
        G_h01_34D8[8] = 3;
        break;
    case 2:
        G_h01_1300[13] = 75;
        G_h01_1300[14] = 75;
        G_h01_1300[15] = 85;
        G_h01_34D8[8] = 2;
        break;
    }

    for (i = 0; i < 6; i++) {
        record = &G_h01_9FCE[i];
        record->field30 = record->field34;
        *(int *)((char *)record + 44) = 14;
        *(int *)((char *)record + 46) = 0;
        *(int *)((char *)record + 62) = G_h01_34D8[8];
        F_h11_2E26(i, 7);
        F_h11_41F6(2, (char *)record + 2, 14,
                   *(int *)((char *)record + 30),
                   *(int *)((char *)record + 32));
    }
}

struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
extern struct Record G_h01_9FCE[1];
extern int F_h11_4696();
extern int F_h11_5962();

F_h11_2E26(index, state)
int index;
int state;
{
    struct Record *record;

    record = &G_h01_9FCE[index];
    *(int *)((char *)record + 14) = 2;

    if (*(int *)((char *)record + 16) == 0 || state == 7)
        *(int *)((char *)record + 16) = state;

    if (state == 7) {
        F_h11_4696(*(int *)((char *)record + 38),
                   *(int *)((char *)record + 42), 64, 74, index + 1);
        if (*(int *)((char *)record + 24))
            F_h11_5962(*(int *)((char *)record + 24), 7);
        if (*(int *)((char *)record + 26))
            F_h11_5962(*(int *)((char *)record + 26), 7);
        if (*(int *)((char *)record + 28))
            F_h11_5962(*(int *)((char *)record + 28), 7);
    }
}


struct State {
    int value0;
    int value2;
    int unused4;
    int value6;
    int value8;
    int code;
    int unusedc;
    int unusede;
    char *address;
    int value14;
};

struct Target {
    char padding[6];
    int value6;
};

extern char G_h01_9F0C[1];
extern char G_h01_9C2C[1];
extern char G_h01_9CBC[1];
extern char G_h01_9CFC[1];
extern char G_h01_9CEC[1];
extern char G_h01_9EBC[1];
extern char G_h01_9EAC[1];
extern char G_h01_9D9C[1];
extern char G_h01_9E5C[1];
extern char G_h01_9D6C[1];
extern char G_h01_9D3C[1];
extern char G_h01_9D4C[1];
extern char G_h01_9D2C[1];
extern int F_h00_57D2();
extern int F_h00_86A8();

F_h11_41F6(mode, state, kind, value0, value2)
int mode;
struct State *state;
int kind;
int value0;
int value2;
{
    state->value6 = 0;
    state->value14 = kind;
    state->value0 = value0;
    state->value2 = value2;

    switch (mode) {
    case 33:
        state->address = G_h01_9F0C;
        state->code = 4;
        F_h00_57D2(89);
        break;
    case 24:
        switch (kind) {
        case 1:
            state->code = 1;
            state->address = G_h01_9C2C;
            break;
        case 3:
            state->code = 6;
            state->address = G_h01_9C2C;
            break;
        }
        break;
    case 11:
        switch (kind) {
        case 14:
            state->code = 0;
            state->address = G_h01_9CEC;
            break;
        case 18:
            state->code = 0;
            state->address = G_h01_9CFC;
            break;
        case 19:
            state->code = 3;
            state->address = G_h01_9CBC;
            break;
        }
        break;
    case 8:
        switch (kind) {
        case 20:
            state->code = 1;
            state->address = G_h01_9EAC;
            break;
        case 45:
            state->code = 5;
            state->address = G_h01_9EBC;
            break;
        }
        break;
    case 2:
        switch (kind) {
        case 12:
            state->code = 2;
            state->address = G_h01_9D4C;
            break;
        case 11:
            state->code = 2;
            state->address = G_h01_9D2C;
            break;
        case 15:
            state->code = 3;
            state->address = G_h01_9D6C;
            break;
        case 13:
            state->code = 0;
            state->address = G_h01_9D3C;
            break;
        case 18:
            state->code = 12;
            state->address = G_h01_9D9C;
            F_h00_57D2(0);
            F_h00_86A8((long)5);
            F_h00_57D2(97);
            break;
        case 17:
            state->code = 5;
            state->address = G_h01_9E5C;
            break;
        case 16:
            state->code = 0;
            state->address = G_h01_9E5C;
            break;
        }
        break;
    }
    state->value8 = ((struct Target *)state->address)->value6;
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

