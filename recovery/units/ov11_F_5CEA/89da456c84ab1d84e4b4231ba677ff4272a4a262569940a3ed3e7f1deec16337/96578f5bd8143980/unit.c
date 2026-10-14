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

/* Direct reconstruction candidate for ov11_F_4610. */
struct Target {
    int x;
    int y;
    char pad[48];
    char state;
};

struct Holder {
    struct Target *target;
    char pad0;
    char state;
    char pad1[6];
    int x;
    int y;
};

struct Motion {
    int x;
    int y;
    char pad[8];
    int remaining;
    int active;
    struct Holder *holder;
};

extern int G_h01_8A3E;
extern int F_h00_34E0();

F_h11_4610(motion)
struct Motion *motion;
{
    struct Holder *holder;
    struct Target *target;

    holder = motion->holder;
    target = holder->target;
    if (motion->remaining > 0) {
        target->x = motion->x + holder->x - G_h01_8A3E;
        target->y = motion->y + holder->y;
        target->state = holder->state;
        F_h00_34E0(target);
        motion->remaining--;
        if (motion->remaining == 0)
            motion->active = 0;
    }
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

/* Provisional source for normal ov11 layout evidence; never canonical by itself. */
extern int G_h01_8B1C[41][4];
extern void F_h11_5962();

F_h11_583A(x,y,width,height,mode)
int x,y,width,height,mode;
{
    int tile,i,j,x_end,y_end;
    if (mode==10) {
        x_end=x+width;
        y_end=y+height;
        x=(x-24)/53;
        y=(y-48)>>5;
        x_end=(x_end+24)/53;
        y_end=(y_end-16)>>5;
    } else {
        x_end=x+width;
        y_end=y+height;
        x=x/53;
        y=(y-48)>>5;
        x_end=x_end/53;
        y_end=(y_end-48)>>5;
    }
    if (x<0) x=0;
    if (y<0) y=0;
    for (i=x;i<=x_end;i++)
        for (j=y;j<=y_end;j++) {
            tile=G_h01_8B1C[i][j];
            if (tile) F_h11_5962(tile,mode);
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

extern int G_h01_37EC;
extern int F_h11_5962();
F_h11_59E6() { int i; for(i=1;i<G_h01_37EC;i++) F_h11_5962(i,2); }

extern int G_h01_37F4[40];

F_h11_5A12(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        for (i = 0; i < 40; i++)
            G_h01_37F4[i] = (i + 1) * 53 + 2;
    } else
        return G_h01_37F4[index];
}

extern int G_h01_3844[40];

F_h11_5A62(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        for (i = 0; i < 40; i++)
            G_h01_3844[i] = i * 53 - 2;
    } else
        return G_h01_3844[index];
}

/* Direct reconstruction candidate for ov11_F_5AB0. */
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_8B1C[41][4];

F_h11_5AB0(direction, kind, result)
int direction;
int kind;
int *result;
{
    int found;
    int row;
    int column;

    found = 0;
    row = G_h01_94BA;
    if (direction == 1)
        row++;
    else if (direction == 0)
        row--;
    if (row < 0)
        goto invalid_row;
    if (row <= 40)
        goto select;
invalid_row:
    goto done;

select:
    if (direction == 0 || direction == 1) {
        if (kind == 2) {
            if ((column = G_h01_94BC - 1) >= 0)
                if (G_h01_8B1C[row][column]) {
                    *result = column;
                    found = 1;
                }
        } else if (kind == 3) {
            if ((column = G_h01_94BC + 1) < 3)
                if (G_h01_8B1C[row][column]) {
                    *result = column;
                    found = 1;
                }
            }
    } else if (direction == 2) {
        if (G_h01_94BC > 0) {
            if (G_h01_8B1C[row][G_h01_94BC - 1]) {
                *result = G_h01_94BC - 1;
                found = 1;
            }
        }
    }
done:
    return found;
}

extern int G_h01_8B1C[6][4];

F_h11_5BC4(row, column)
int *row, *column;
{
    int i, j;

    for (i = 0; i < 6; i++)
        for (j = 0; j < 3; j++)
            if (G_h01_8B1C[i][j]) {
                *row = i;
                *column = j;
                return;
            }
}

struct MotionRecord {
    char pad[18];
    char motion;
    char remainder[33];
};

extern struct MotionRecord G_h01_8BEC[1];
extern int F_h11_4610();

F_h11_5C1A(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_8BEC[n];
    F_h11_4610(&record->motion);
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

struct Record { int fields[15]; int value; char tail[20]; };
extern struct Record G_h01_8BEC[1];
recovered(n) int n; { struct Record *p; p=&G_h01_8BEC[n]; return p->value>0 ? 1 : 0; }

struct ClusterRecord {
    int value0;
    int value2;
    char pad4[14];
    char pad18[26];
    int value2c;
    int value2e;
    int state30;
    int value32;
};

extern int G_h01_7A92;
extern int G_h01_8A3C;
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94C0;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_25F8();
extern int F_h11_37A0();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_5C42();

F_h11_5D14(index)
int index;
{
    struct ClusterRecord *record;
    int x, y, update, state;

    record = &G_h01_8BEC[index];
    update = 0;
    state = record->state30;

    switch (record->state30) {
    case 1:
        if (((G_h01_94C0 + 14) >> 5) == ((int *)record)[1] &&
            ((int *)record)[0] == G_h01_94BA) {
            G_h01_94B4 = 1;
            G_h01_94D6 = index;
            state = 3;
            update = 1;
        }
        break;
    case 3:
        if ((((int *)record)[0] != G_h01_94BA && G_h01_94AE != 18) ||
            G_h01_94B6) {
            state = 1;
            G_h01_94B4 = 0;
            G_h01_94D6 = 0;
            G_h01_37F0 = 0;
            G_h01_37EE = 0;
            update = 1;
        } else {
            update = 1;
            F_h11_4474(24, &record->pad18[0]);
        }
        break;
    default:
        break;
    }

    if (record->state30 != state) {
        record->state30 = state;
        F_h11_41F6(24, &record->pad18[0], state,
                   record->value2c, record->value2e);
    }

    if (G_h01_8A3C) {
        F_h11_5C42(index, 0);
    } else if (update) {
        F_h11_5C42(index, 3);
    } else if (G_h01_7A92 &&
               F_h11_37A0(G_h01_7A92, &x, &y) &&
               F_h11_25F8(record->value2c, record->value2e - 6,
                          x, y, record->value2c + 64,
                          record->value2e + 32)) {
        F_h11_5C42(index, 3);
    }
}

struct InitRecord { char prefix[0x2c]; int value2c; int value2e; int value30; int value32; };
extern struct InitRecord G_h01_8BEC[1];
extern int G_h01_94B4;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_5C42();
extern int F_h11_41F6();

F_h11_5EC0(index)
int index;
{
    struct InitRecord *record;

    record=&G_h01_8BEC[index];
    record->value30=1;
    G_h01_94B4=0;
    G_h01_94D6=0;
    G_h01_37F0=0;
    G_h01_37EE=0;
    F_h11_5C42(index,3);
    F_h11_41F6(24,&record->prefix[0x12],1,record->value2c,record->value2e);
}

extern int F_h11_25D6();
F_h11_5F2A(a,b,c,d,e,f,g,h) int a,b,c,d,e,f,g,h; {
 return (F_h11_25D6(a,e,b)||F_h11_25D6(a,f,b)) &&
        (F_h11_25D6(c,g,d)||F_h11_25D6(c,h,d)) ? 1 : 0;
}

struct Record { int field0,value; char tail[48]; };
extern struct Record G_h01_8BEC[1];
F_h11_5F90(n) int n; { struct Record *p; p=&G_h01_8BEC[n]; return p->value; }

/* ov11_F_5FB2: per-record scroll delta from float position math (m.lib FFP). */
struct ClusterRecord {
    char f0[8];
    int value8;
    int value10;
    char f12[2];
    int value14;
    int value16;
    char f18[12];
    int state30;
    int value32;
    int *ref34;
    char f38[2];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37EE;
extern int G_h01_37F0;
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;

F_h11_5FB2(index)
int index;
{
    struct ClusterRecord *record;
    int delta;
    int shift;

    record = &G_h01_8BEC[index];
    delta = (int)(((float)G_h01_94BE - (float)record->value2c)
                  * (float)record->ref34[4] / 104.0);
    shift = 0;
    if (record->ref34[2] == 2) {
        if ((8 >> G_h01_94B0) + G_h01_94BE - G_h01_37F0 - record->value2c > 45) {
            delta += 5;
            shift = -5;
        }
    }
    G_h01_94C0 += delta - G_h01_37EE;
    G_h01_94BE += shift - G_h01_37F0;
    G_h01_37EE = delta;
    G_h01_37F0 = shift;
}

struct Record { int padding[11],state,value; char tail[14]; };
extern struct Record G_h01_A464[36];
F_h11_66FE(a,b) int a,b; { struct Record *p; p=&G_h01_A464[a]; p->state=2; if(!p->value || b==8)p->value=b; }

