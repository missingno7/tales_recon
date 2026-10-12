F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

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


struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
struct Row { int field0; int field2; int field4; };
extern struct Record G_h01_9FCE[1];
extern int G_h01_1300[16];
extern struct Row G_h01_12C0[32];
extern int G_h01_34D8[16];
extern int G_h01_7A92;
extern int G_h01_8A3C;
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_A14E;
extern unsigned int F_h00_463E();
extern int F_h00_57D2();
extern int F_h11_25D6();
extern int F_h11_2E26();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_45EC();

recovered(index)
int index;
{
    int *object;
    int changed;
    int redraw;
    int near;
    object = (int *)&G_h01_9FCE[index];
    changed = 0;
    redraw = 0;
    near = F_h11_45EC(object + 1);
    object[31]--;
    changed = 1;
    switch (object[22]) {
    case 14:
        if (object[31] == 0) {
            if (object[15] > G_h01_94BE && object[0] != 0 &&
                (int)F_h00_463E() % 100 < 75) {
                object[22] = 12; changed = 1; redraw = 1;
            } else if (object[15] > ((8 >> G_h01_94B0) + G_h01_94BE - 32) &&
                       (int)F_h00_463E() % 100 < 75) {
                object[22] = 16; object[16] = 8;
                G_h01_34D8[9] = (G_h01_94BE - object[15] + 12) % 64;
                object[15] = object[17] + G_h01_34D8[9];
                changed = 1; redraw = 1;
            }
        }
        break;
    case 16:
        if (object[15] < ((8 >> G_h01_94B0) + G_h01_94BE - 64)) {
            object[22] = 14; object[15] = object[17];
            changed = 1; redraw = 1;
        } else if (object[23] == 0 &&
                   (int)F_h00_463E() % 100 < G_h01_1300[15]) {
            object[22] = 17; G_h01_7A92 = index;
            object[23] = 1; object[24] = 3;
            object[25] = object[28] = object[27] = object[15] + 8;
            object[26] = object[30] = object[29] = object[16] + 28;
            changed = 1; redraw = 1;
        }
        break;
    case 17:
        if (object[31] == 0)
            goto state17_body;
        goto state17_done;
state17_body:
        if (near) {
            object[22] = 14; changed = 1; redraw = 1;
        } else {
            if (object[4] == 2) F_h00_57D2(96);
            F_h11_4474(2, object + 1);
        }
state17_done:
        break;
    case 12:
        if (object[31] == 0)
            goto state12_body;
        goto state12_done;
state12_body:
        if (near) {
                object[16] += 12;
                if (object[16] > 80) {
                    object[22] = 13;
                    changed = 1;
                    redraw = 1;
                } else if (object[16] + 28 < G_h01_94C0 + 32) {
                    changed = 1;
                    redraw = 1;
                } else {
                    object[22] = 13;
                    changed = 1;
                    redraw = 1;
                }
            } else {
                F_h11_4474(2, object + 1);
            }
state12_done:
        break;

    case 11:
        if (object[31] == 0)
            goto state11_body;
        goto state11_done;
state11_body:
        if (near) {
                object[16] -= 12;
                if (object[16] < 16) {
                    object[22] = 14;
                    changed = 1;
                    redraw = 1;
                } else if (object[16] + 32 > G_h01_94C0 + 32 || object[15] < G_h01_94BE) {
                    changed = 1;
                    redraw = 1;
                } else {
                    object[22] = 13;
                    changed = 1;
                    redraw = 1;
                }
            } else {
                F_h11_4474(2, object + 1);
            }
state11_done:
        break;

    case 13:
        if (object[31] <= 0) {
            if ((int)F_h00_463E() % 100 < G_h01_1300[13]) {
                if (object[23] == 0 &&
                    ((8 >> G_h01_94B0) + G_h01_94BE) <= object[15]) {
                    object[22] = 15; G_h01_12C0[16].field0 = 1;
                    changed = 1; redraw = 1; G_h01_7A92 = index;
                    G_h01_A14E = 0; object[23] = 1; object[24] = 0;
                    object[25] = object[28] = object[27] = object[15] + 44;
                    object[26] = object[30] = object[29] = object[16] + 22;
                }
            } else if ((int)F_h00_463E() % 100 < G_h01_1300[14]) {
                if (F_h11_25D6(object[15] - 32,
                               (8 >> G_h01_94B0) + G_h01_94BE,
                               object[15] + 32) != 0 || object[15] < G_h01_94BE) {
                    object[22] = 11; changed = 1; redraw = 1;
                } else if (object[16] + 20 < G_h01_94C0 && object[16] < 80) {
                    object[22] = 12; changed = 1; redraw = 1;
                } else if (object[16] + 20 > G_h01_94C0 + 32) {
                    object[22] = 11; changed = 1; redraw = 1;
                }
            }
        }
        break;
    case 15:
        if (near) {
            object[22] = 13; changed = 1; redraw = 1;
        } else {
            if (object[4] == 1 && G_h01_12C0[16].field0 != 0) {
                F_h00_57D2(96); G_h01_12C0[16].field0 = 0;
                F_h11_4474(2, object + 1);
            } else {
                F_h11_4474(2, object + 1);
            }
        }
        break;
    case 18:
        if (near) { object[22] = 13; changed = 1; redraw = 1; }
        else F_h11_4474(2, object + 1);
        break;
    }
    if (G_h01_8A3C != 0 || changed) F_h11_2E26(index, 7);
    if (redraw) F_h11_41F6(2, object + 1, object[22], object[15], object[16]);
    if (object[31] <= 0) object[31] = G_h01_34D8[8];
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
struct Counter {
    char pad[6];
    int value;
};

struct State {
    char pad0[6];
    int index;
    int countdown;
    int limit;
    char pad1[4];
    char *counter;
    int action;
};

extern char G_h01_9F0C;
extern char G_h01_9C2C;
extern int F_h00_57D2();

F_h11_4474(action,state)
int action;
struct State *state;
{
    if (state->countdown > 0)
        state->countdown--;
    else {
        state->index++;
        if (state->index < state->limit && state->counter)
            state->counter += 16;
        switch (action) {
        case 33:
            if (state->action && state->index >= state->limit) {
                state->index = 0;
                state->limit = 4;
                state->counter = &G_h01_9F0C;
            }
            break;
        case 24:
            switch (state->action) {
            case 1:
                if (state->index >= state->limit) {
                    state->index = 0;
                    state->limit = 1;
                    state->counter = &G_h01_9C2C;
                }
                break;
            case 3:
                if (state->index >= state->limit) {
                    state->index = 0;
                    state->limit = 6;
                    state->counter = &G_h01_9C2C;
                    F_h00_57D2(94);
                } else if (state->index == 3)
                    F_h00_57D2(87);
                break;
            }
            break;
        }
        if (state->index < state->limit && state->counter)
            state->countdown = ((struct Counter *)state->counter)->value;
    }
}

F_h11_45EC(p) int *p; { return p[3]>=p[5]-1; }

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

