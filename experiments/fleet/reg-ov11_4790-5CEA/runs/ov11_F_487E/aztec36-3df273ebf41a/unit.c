long F_h11_2562(x1,y1,x2,y2)
int x1,y1,x2,y2;
{
    long dx,dy;

    dx=(x1-x2<0)?-(x1-x2):x1-x2;
    dy=(y1-y2<0)?-(y1-y2):y1-y2;
    return dx*dx+dy*dy;
}

F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

extern int F_h11_25D6();
F_h11_25F8(a,b,c,d,e,f) int a,b,c,d,e,f; { return F_h11_25D6(a,c,e) && F_h11_25D6(b,d,f); }

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

/* Direct reconstruction candidate for ov11_F_4790. */
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
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();

F_h11_4790()
{
    struct Rect *rect;

    for (rect = G_h01_34EC; rect - G_h01_34EC < 40; rect++)
        if (rect->kind) {
            rect->kind--;
            if (rect->width > 0)
                if (rect->height > 0)
                    F_h00_8A46(G_h01_46CE, (long)rect->x,
                        (long)rect->y, G_h01_46D2, (long)rect->x,
                        (long)rect->y, (long)rect->width,
                        (long)rect->height, (long)192, (long)255, 0L);
        }
}

struct Record {
    int value;
    char rest[12];
};

extern struct Record G_h01_34EC[40];

F_h11_4848()
{
    struct Record *p;

    for (p = G_h01_34EC; p - G_h01_34EC < 40; p++)
        p->value = 0;
}

extern int F_h00_8A46();
extern int F_h11_55B8();
extern int F_h11_645E();
extern long G_h01_46D2;
extern long G_h01_46CE;
extern long G_h01_A460;
extern int G_h01_8A6E[1];
extern int G_h01_94AE;

recovered(x,y,width,height)
int x,y,width,height;
{
    int first,last,step,column,limit;

    first=(x+48)/104;
    last=(y+48)/104;
    step=0;
    limit=width;
    if (last<limit) {
        step=104-(x%104);
        if (step<0) step=0;
    }
    F_h00_8A46((long)G_h01_A460,(long)last,(long)0,(long)G_h01_46D2,(long)y,(long)0,(long)step,(long)176,(long)192,(long)255,(long)0);
    while (step<limit) {
        y+=step;
        step=104;
        F_h00_8A46((long)G_h01_A460,(long)last,(long)0,(long)G_h01_46D2,(long)y,(long)0,(long)step,(long)176,(long)192,(long)255,(long)0);
    }
    F_h11_55B8();
    column=(x+320)/104;
    for (first=first;first<=column;first++) {
        if (G_h01_8A6E[first*7] && G_h01_94AE!=45)
            F_h11_645E(G_h01_8A6E[first*7]);
    }
    if (height) {
        F_h00_8A46((long)G_h01_A460,(long)y,(long)0,(long)G_h01_46CE,(long)x,(long)0,(long)height,(long)200,(long)192,(long)255,(long)0);
        G_h01_A460=G_h01_94AE;
    }
}

extern int G_h01_8A3E;
extern int G_h01_A45E;
F_h11_49CE() { G_h01_8A3E=0; G_h01_A45E%=320; }

/* Direct reconstruction candidate for ov11_F_49EA. */
struct Controller { int x; int y; char pad[48]; char state; };
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern struct Controller *G_h01_9F5A;
extern long G_h01_A460;
extern int G_h01_A45E;
extern int G_h01_8A3E;
extern int F_h00_8BC8();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern long F_h00_3B16();

F_h11_49EA()
{
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 176L, 192L, 255L, 0L);
    G_h01_9F5A->x = 48;
    G_h01_9F5A->y = 0;
    G_h01_9F5A->state = 1;
    F_h00_34E0(G_h01_9F5A);
    G_h01_A460 = F_h00_3B16(128, 176);
    F_h00_8A46(G_h01_46D2, 56L, 0L, G_h01_A460,
        0L, 0L, 104L, 176L, 192L, 255L, 0L);
    G_h01_A45E = 0;
    G_h01_8A3E = 0;
}

extern long G_h01_A460;
extern int F_h00_3B84();

int F_h11_4A92() {
    return F_h00_3B84(G_h01_A460);
}

struct Destination { char pad[52]; char value; };
struct Source {
    struct Destination *destination;
    char pad0;
    char value;
    int delay;
    char pad1[4];
    int x;
    int y;
};

extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Destination *G_h01_94DA;
extern int G_h01_94DE;
extern int G_h01_94E0;
extern int G_h01_94E4;
extern struct Source *G_h01_94E8;

F_h11_4AA4()
{
    if (G_h01_94E4 > 0) {
        G_h01_94E4--;
    } else {
        G_h01_94DE++;
        if (G_h01_94DE < G_h01_94E0)
            if (G_h01_94E8 != 0) {
                G_h01_94E8++;
                G_h01_94BE += G_h01_94E8->x;
                G_h01_94C0 += G_h01_94E8->y;
                G_h01_94DA = G_h01_94E8->destination;
                G_h01_94DA->value = G_h01_94E8->value;
                G_h01_94E4 = G_h01_94E8->delay;
            }
    }
}

/* Isolated source-shape probe for ov11_F_4B0C; no source ownership claimed. */
struct Descriptor { long object; char pad4; char state; int type; char pad8[4]; int dy; int dx; };
struct Object { char pad[52]; char state; };
extern int G_h01_94B0; extern int G_h01_94B0; extern int G_h01_94B2; extern int G_h01_94B4; extern int G_h01_94B6;
extern int G_h01_94BE; extern int G_h01_94C0; extern int G_h01_94C0; extern int G_h01_94D8;
extern struct Object *G_h01_94DA; extern int G_h01_94DE; extern int G_h01_94E0; extern int G_h01_94E0;
extern int G_h01_94E4; extern int G_h01_94E6; extern struct Descriptor *G_h01_94E8;
extern struct Object *G_h01_9F4E; extern struct Object *G_h01_9F52;
extern struct Descriptor G_h01_94EC[1]; extern struct Descriptor G_h01_958C[1];
extern struct Descriptor G_h01_962C[1]; extern struct Descriptor G_h01_96AC[1];
extern struct Descriptor G_h01_972C[1]; extern struct Descriptor G_h01_978C[1];
extern struct Descriptor G_h01_975C[1]; extern struct Descriptor G_h01_97FC[1];
extern struct Descriptor G_h01_986C[1]; extern struct Descriptor G_h01_987C[1];
extern struct Descriptor G_h01_98BC[1]; extern struct Descriptor G_h01_994C[1];
extern struct Descriptor G_h01_99DC[1]; extern struct Descriptor G_h01_99FC[1];
extern struct Descriptor G_h01_9A1C[1]; extern struct Descriptor G_h01_9A6C[1];
extern struct Descriptor G_h01_9ABC[1]; extern struct Descriptor G_h01_9AEC[1];
extern struct Descriptor G_h01_9AFC[1]; extern struct Descriptor G_h01_9B4C[1];
extern struct Descriptor G_h01_9BBC[1]; extern struct Object *G_h01_9F52; extern struct Object *G_h01_9F4E;
extern int F_h00_57D2(); extern int F_h11_6ED6();

F_h11_4B0C(mode)
int mode;
{
    int x;
    int y;
    G_h01_94DE = 0;
    G_h01_94E4 = 0;
    G_h01_94E6 = 1;
    G_h01_94E8 = 0;
    switch (mode) {
    case 20: G_h01_94E0 = 7; G_h01_94E8 = G_h01_9B4C; break;
    case 21: G_h01_94E0 = 7; G_h01_94E8 = G_h01_9BBC; break;
    case 6: F_h00_57D2(0x58); G_h01_94C0 = 0x8e; G_h01_94E0 = 5; G_h01_94E8 = G_h01_9AFC; break;
    case 19: G_h01_94E0 = 3; G_h01_94E8 = G_h01_9ABC; break;
    case 18: G_h01_94E0 = 5; G_h01_94E8 = (G_h01_94B0 == 0) ? G_h01_9A1C : G_h01_9A6C; F_h00_57D2(0x64); break;
    case 17: G_h01_94E0 = 2; G_h01_94E8 = G_h01_99DC; break;
    case 16: G_h01_94E0 = 2; G_h01_94E8 = G_h01_99FC; break;
    case 14: G_h01_94E0 = 1; G_h01_94E8 = G_h01_9AEC; break;
    case 45: G_h01_94E0 = 0; break;    case 12: G_h01_94E0 = 7; G_h01_94E8 = G_h01_978C; break;
    case 13: G_h01_94E0 = 7; G_h01_94E8 = G_h01_97FC; break;
    case 3: G_h01_94E0 = 9; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_98BC : G_h01_994C; break;
    case 10: G_h01_94E0 = 3; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_972C : G_h01_975C; break;
    case 4: G_h01_94E0 = 8; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_962C : G_h01_96AC; break;
    case 5: G_h01_94E0 = 0; G_h01_94E8 = (G_h01_94B0 == 1) ? G_h01_986C : G_h01_987C; break;
    case 1:
        if (G_h01_94B2 != 0) { G_h01_94DE = 0; G_h01_94E0 = 5; }
        else { G_h01_94DE = 5; G_h01_94E0 = 10; }
        if (G_h01_94B0 == 1) G_h01_94E8 = &G_h01_94EC[G_h01_94DE];
        else G_h01_94E8 = &G_h01_958C[G_h01_94DE];
        break;
    case 2:
        G_h01_94B6 = 0; G_h01_94B4 = 0; G_h01_94E0 = 0; G_h01_94DA = G_h01_9F52;
        if (G_h01_94B0 == 1) G_h01_94DA->state = 1; else G_h01_94DA->state = 3;
        F_h00_57D2(0xf); break;
    case 8:
        G_h01_94E0 = 1; G_h01_94DA = G_h01_9F4E;
        F_h11_6ED6(G_h01_94D8, &x, &y, &G_h01_94BE, &G_h01_94C0);
        if (G_h01_94BE < x) {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x1c : 0x1e;
            if (G_h01_94B0 == 0) { G_h01_94BE -= 12; G_h01_94C0 += 8; }
            else { G_h01_94BE -= 3; G_h01_94C0 += 9; }
        } else if (G_h01_94BE > x) {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x1d : 0x1f;
            if (G_h01_94B0 == 0) { G_h01_94BE += 0; G_h01_94C0 += 10; }
            else { G_h01_94BE += 10; G_h01_94C0 += 17; }
        } else {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x17 : 0x1b;
            if (G_h01_94B0 == 0) { G_h01_94BE -= 6; G_h01_94C0 += 22; }
            else { G_h01_94BE += 1; G_h01_94C0 += 22; }
        }
        G_h01_94BE -= 6; G_h01_94C0 -= 21; break;

    }
    if (G_h01_94E8 != 0) {
        G_h01_94DA = G_h01_94E8->object;
        G_h01_94BE += G_h01_94E8->dy;
        G_h01_94C0 += G_h01_94E8->dx;
        G_h01_94DA->state = G_h01_94E8->state;
        G_h01_94E4 = G_h01_94E8->type;
    }
}

struct AnimRecord {
    char prefix[22];
    int animation;
    int flags;
    int x;
    int y;
    int row;
    int column;
    int value;
    int extra;
    int tail;
};

extern struct AnimRecord G_h01_3724[1];
extern long G_h01_9F82;
extern char G_h01_9C8C[1];
extern char G_h01_9CBC[1];
extern int G_h01_9C92[1];
extern int G_h01_9CC2[1];
extern int G_h01_9C90;
extern int G_h01_9CA0;
extern int G_h01_9CB0;
extern int G_h01_9CC0;
extern int G_h01_9CD0;
extern int G_h01_9CE0;
extern char G_h01_9CEC[1];
extern int G_h01_9CF0;
extern int G_h01_9D00;
extern int G_h01_9D10;
extern int G_h01_9D20;
extern int G_h01_371C;
extern int G_h01_371E;
extern int G_h01_3720;
extern int G_h01_3722;
extern char G_h01_46E0;
extern int F_h11_54F8();
extern int F_h11_41F6();

F_h11_4EC6()
{
    int i;
    struct AnimRecord *record;

    for (i=0;i<3;i++) {
        *((long *)(G_h01_9C8C+((long)i*16)))=G_h01_9F82;
        *((long *)(G_h01_9CBC+((long)i*16)))=G_h01_9F82;
        G_h01_9C92[i*8]=1;
        G_h01_9CC2[i*8]=1;
    }
    G_h01_9C90=6;
    G_h01_9CA0=7;
    G_h01_9CB0=6;
    G_h01_9CC0=2;
    G_h01_9CD0=3;
    G_h01_9CE0=2;
    for (i=0;i<4;i++)
        *((long *)(G_h01_9CEC+((long)i*16)))=G_h01_9F82;
    G_h01_9CF0=0;
    G_h01_9D00=1;
    G_h01_9D10=4;
    G_h01_9D20=5;
    for (i=0;i<5;i++) {
        record=&G_h01_3724[i];
        record->x=record->row*53;
        record->y=record->column*32+32;
        record->animation=14;
        F_h11_54F8(i,5);
        F_h11_41F6(record,11,record->x,record->y,14,5);
    }
    switch (G_h01_46E0) {
    case 0:
        G_h01_371C=80;
        G_h01_371E=75;
        G_h01_3720=20;
        break;
    case 1:
        G_h01_371C=70;
        G_h01_371E=85;
        G_h01_3720=20;
        break;
    case 2:
        G_h01_371C=60;
        G_h01_371E=90;
        G_h01_3720=10;
        break;
    }
    G_h01_3722=G_h01_3720*3;
}

/* Ownership probe for ov11_F_506A: parse P header and 40-byte records. */
struct Record {
    char unused[24];
    int value24;
    int value26;
    int value28;
    int value30;
    int value32;
    int value34;
    int value36;
    int value38;
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern struct Record G_h01_3724[1];

F_h11_506A(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'P');
    F_h00_704E(line, "P %d", &rows);
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(435);
            goto next_record;
        }
        record = &G_h01_3724[index];
        if (F_h00_704E(line, "%*d %d %d %d %d %d %d %d %d\n",
                &record->value34, &record->value36, &record->value38,
                &record->value26, &record->value28, &record->value30,
                &record->value32, &record->value24) != 8)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(444);
next_record:
        ;
    }
}

/* Direct recovery candidate for a 40-byte motion record dispatch. */
struct MotionRecord {
    char bytes[40];
};

extern struct MotionRecord G_h01_3724[1];
extern int F_h11_4610();

F_h11_519C(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_3724[n];
    F_h11_4610(record);
}

struct ScreenRecord {
    char prefix[22];
    int mode;
    int frame;
    int x;
    int y;
    int row;
    int column;
    int id;
    int flags;
    int tail;
};

extern struct ScreenRecord G_h01_3724[1];
extern int G_h01_00A8;
extern int G_h01_00CC;
extern int G_h01_371C;
extern int G_h01_371E;
extern int G_h01_3720;
extern int G_h01_3722;
extern int G_h01_8A3E;
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_9F5E[1];
extern int F_h11_54F8();
extern int F_h11_25F8();
extern int F_h11_4B0C();
extern int F_h11_45EC();
extern int F_h11_4474();
extern int F_h11_2562();
extern int F_h11_41F6();
extern int F_h00_463E();
extern int F_h00_57D2();

F_h11_51C0(index)
int index;
{
    struct ScreenRecord *record;
    int kind,changed,mode,step;

    record=&G_h01_3724[index];
    changed=0;
    if (G_h01_8A3E) G_h01_371E=G_h01_371C;
    else G_h01_371E--;
    mode=record->frame;
    if (mode==18) {
        record->frame=18;
        changed=1;
    }
    if (record->flags!=G_h01_94B0) {
        F_h00_463E(record->flags);
        record->flags=G_h01_94B0;
    }
    if (record->mode==0) {
        F_h11_54F8(index,0);
        F_h11_4B0C(2,index);
        changed=1;
    }
    if (mode==14) {
        F_h11_25F8(record->x,record->y,record->row,record->column);
        F_h11_4B0C(index,2);
        if (F_h11_45EC(index)) {
            record->mode=18;
            record->frame=1;
            changed=1;
        }
    }
    if (mode==4) {
        F_h11_4B0C(record->x,record->y);
        if (record->flags) {
            F_h11_4474(index,11);
            record->mode=18;
            changed=1;
        }
    }
    if (mode==1 || mode==2 || mode==3) {
        F_h00_57D2(record->x,record->y);
        F_h11_2562(record->x,record->y,record->row,record->column);
        G_h01_9F5E[0]=record->x;
        G_h01_9F5E[1]=record->y;
        G_h01_9F5E[2]=record->mode;
        F_h11_41F6(record,index,record->x,record->y,mode,11);
    }
    if (changed) {
        step=G_h01_371E;
        G_h01_3720=step;
        G_h01_3722=G_h01_3720+1;
    }
}

struct Record {
	char pad0[12];
	int state;
	int value;
	char pad10[10];
	int x;
	int y;
	char gap[4];
	int first;
	int second;
	int third;
};

extern struct Record G_h01_3724[1];
extern int F_h11_4696();
extern int F_h11_5962();

F_h11_54F8(index,mode)
int index,mode;
{
	struct Record *record;
	record=&G_h01_3724[index];
	record->state=2;
	if (record->value==0 || mode==5) record->value=mode;
	if (mode==5) {
		F_h11_4696(record->x,record->y,64,48,11);
		if (record->first) F_h11_5962(record->first,5);
		if (record->second) F_h11_5962(record->second,5);
		if (record->third) F_h11_5962(record->third,5);
	}
}
struct GridRecord {
    char prefix[8];
    int code;
    char pad10[0x1e];
    int y;
    int x;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37F2;
extern int G_h01_8A3E;
extern int G_h01_8B1C[41][4];
extern int G_h01_940C[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_8BEC[1];
extern int G_h01_9F5E[1];
extern int G_h01_9FA2[1];
extern int F_h11_5962();
extern int F_h00_34E0();

F_h11_55B8()
{
    int row,column,tile,base,vertical,horizontal;
    struct GridRecord *object;

    if (G_h01_37F2) {
        G_h01_37F2=0;
        for (row=0;row<18;row++) {
            vertical=row*53+((row&1)?-4:-24);
            for (column=2;column>=0;column--) {
                tile=G_h01_8B1C[row][column];
                if (tile) {
                    object=(struct GridRecord *)&G_h01_8BEC[tile*26];
                    if (!object->code) {
                        object->value2c=(column*32)+48;
                        object->value2e=vertical;
                    }
                }
            }
        }
    }
    for (row=0;row<18;row++) {
        for (column=0;column<3;column++) {
            tile=G_h01_8B1C[row][column];
            if (tile) {
                object=(struct GridRecord *)&G_h01_8BEC[tile*26];
                if (object->value2c>0 && !object->code) {
                    base=object->value2e-G_h01_8A3E;
                    horizontal=object->value2c;
                    G_h01_9F5E[0]=base;
                    G_h01_9F5E[1]=horizontal;
                    G_h01_9F5E[2]=object->value2e;
                    G_h01_9F5E[3]=object->prefix[7];
                    F_h00_34E0(G_h01_9F5E);
                    object->value2c--;
                    if (!object->value2c) object->value2e=0;
                }
            }
        }
    }
    vertical=G_h01_94AE;
    horizontal=G_h01_94B0;
    for (row=0;row<6;row++) {
        for (column=0;column<3;column++) {
            tile=G_h01_8B1C[row][column];
            if (tile) {
                object=(struct GridRecord *)&G_h01_8BEC[tile*26];
                if (object->value2c>0 && !object->code) {
                    G_h01_9FA2[0]=object->value2e+16;
                    G_h01_9FA2[1]=object->value2c-13;
                    F_h00_34E0(G_h01_9FA2);
                    F_h11_5962(tile,2);
                }
            }
        }
    }
    row=vertical+horizontal;
    G_h01_940C[row]=0;
    if (G_h01_37F2) F_h11_5962(G_h01_37F2,2);
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

struct MotionRecord {
    char pad[10];
    char motion;
    char remainder[29];
};

extern struct MotionRecord G_h01_A464[1];
extern int F_h11_4610();

F_h11_645E(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_A464[n];
    F_h11_4610(&record->motion);
}

struct Record { int padding[11],state,value; char tail[14]; };
extern struct Record G_h01_A464[36];
F_h11_66FE(a,b) int a,b; { struct Record *p; p=&G_h01_A464[a]; p->state=2; if(!p->value || b==8)p->value=b; }

struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record G_h01_A554[36];
F_h11_6ED6(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&G_h01_A554[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}

