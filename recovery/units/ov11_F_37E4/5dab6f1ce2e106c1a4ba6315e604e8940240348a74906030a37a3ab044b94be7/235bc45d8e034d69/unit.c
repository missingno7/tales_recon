F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

extern int F_h11_25D6();
F_h11_25F8(a,b,c,d,e,f) int a,b,c,d,e,f; { return F_h11_25D6(a,c,e) && F_h11_25D6(b,d,f); }

F_h11_262E(a,b,c,d,e,f,g,h) int a,b,c,d,e,f,g,h; { return g>=a && e<=c && h>=b && f<=d; }

struct Record { int pad[23]; int state; int gap; int x,y; char tail[10]; };
extern struct Record G_h01_9FCE[36];
F_h11_37A0(n,x,y) int n,*x,*y; {
 struct Record *p;
 p=&G_h01_9FCE[n];
 if(p->state) { *x=p->x; *y=p->y; }
 return p->state;
}

struct Object {
    char pad00[0x1e];
    int value1e;
    int value20;
    char pad24[10];
    int state2c;
    int gate2e;
    int state30;
    int y32;
    int x34;
    char pad36[2];
    int value38;
    char pad3a[2];
    int value3c;
    char pad3e[2];
};

extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern struct Object G_h01_9FCE[1];
extern int F_h11_262E();
extern int F_h11_41F6();
extern int F_h11_4B0C();
extern int F_h11_4696();
extern int F_h11_407C();

recovered(index)
int index;
{
    int left;
    int top;
    struct Object *object;
    int hit;

    left = (8 >> G_h01_94B0) + G_h01_94BE;
    top = G_h01_94C0 + 16;
    object = &G_h01_9FCE[index];
    hit = 0;
    if (object->gate2e != 0) {
        hit = F_h11_262E(left - 4, top - 6, left + 4, top + 6,
                         object->y32 + 4, object->x34 + 2,
                         object->y32 + 8, object->x34 + 12);
    }
    if (hit != 0) {
        if (object->state30 == 0) {
            object->state2c = 0x12;
            F_h11_41F6(2, (char *)object + 2, 0x12,
                       object->value1e, object->value20);
        } else if (G_h01_94B6 != 0) {
            F_h11_407C(G_h01_94D4);
            G_h01_94B6 = 0;
        }
        G_h01_94AE = 2;
        F_h11_4B0C(2);
        object->gate2e = 0;
        F_h11_4696(object->value38, object->value3c, 0x18, 0x10,
                   index + 12);
    }
    return hit;
}
/* Ownership probe for ov11_F_3926: parse F header and indexed records. */
struct Record {
    char unused0[4];
    int value1;
    int value2;
    char unused1[10];
    int value3;
    char unused2[12];
};

extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern int G_h01_A152;
extern struct Record G_h01_A15E[1];

F_h11_3926(text)
char *text;
{
    char *line;
    int i;
    int rows;
    int index;
    struct Record *record;

    line = F_h00_75D8(text, 'F');
    F_h00_704E(line, "F %d", &rows);
    G_h01_A152 = rows;
    line = F_h00_75D8(line, '\n') + 1;
    for (i = 0; i < rows; i++) {
        if (F_h00_704E(line, " %d ", &index) < 1) {
            F_h00_3674(1021);
            goto next_record;
        }
        record = &G_h01_A15E[index];
        if (F_h00_704E(line, "%*d %d %d %d\n",
                &record->value2, &record->value1, &record->value3) != 3)
            goto bad_record;
        line = F_h00_75D8(line, '\n') + 1;
        goto next_record;
bad_record:
        F_h00_3674(1032);
next_record:
        ;
    }
}

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

extern long F_h00_463E();
extern void F_h00_3674();
extern int F_h11_40E0();
extern struct Event G_h01_A15E[1];
extern int G_h01_A152;
extern int G_h01_A150;
extern int G_h01_A158;
extern int G_h01_A15A;
extern char G_h01_46E0;

F_h11_3A24()
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

F_h11_3B92()
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
        if (event->count1c > 0 && event->value12 < event->value14) {
            switch (event->kind) {
            case 18:
                G_h01_9F66->value34 = ((unsigned char *)&event->value12)[1] + 0;
                G_h01_9F66->x = screen_x - G_h01_8A3E;
                G_h01_9F66->y = screen_y;
                if (G_h01_9F66->x < 320)
                    F_h00_34E0(G_h01_9F66);
                break;
            case 17:
                G_h01_9F8A->value34 = ((unsigned char *)&event->value12)[1] + 0;
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
    int value18;
    int value1a;
    char rest[10];
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

F_h11_3D9A()
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
        event = &G_h01_A15E[(base + i) % G_h01_A152];
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
/* Direct reconstruction candidate for ov11_F_3F90. */
struct Event {
    char pad0[4];
    int value4;
    char pad6[2];
    int value8;
    char padA[2];
    int valueC;
    int valueE;
    char tail[16];
};

extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;
extern struct Event G_h01_A15E[1];
extern int F_h11_25D6();

int F_h11_3F90(a)
int a;
{
    struct Event *event;
    int page;
    int index;
    int screen_x;
    int result;

    result=-1;
    page=a/128+1;
    if (a%128<G_h01_A154)
        --page;
    screen_x=(page-1)*128+G_h01_A154;
    index=(G_h01_A158+page)%G_h01_A152;
    event=&G_h01_A15E[index];
    if (event->value4==1 && event->valueC<event->valueE)
        if (F_h11_25D6(event->valueC+screen_x+10,
                        (8>>G_h01_94B0)+G_h01_94BE,
                        event->value8+screen_x))
            result=index;
    return result;
}

struct Record { int state; char tail[30]; };
extern struct Record G_h01_A16A[36];
F_h11_405A(n) int n; { return G_h01_A16A[n].state==4; }

/* Direct reconstruction candidate for ov11_F_407C. */
struct Record {
    char pad0[12];
    int value12;
    int value14;
    char pad2[6];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};

extern struct Record G_h01_A15E[1];
extern int F_h11_40E0();

F_h11_407C(index)
int index;
{
    G_h01_A15E[index].value12 = G_h01_A15E[index].value14;
    F_h11_40E0(index, 6);
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

struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record G_h01_A554[36];
F_h11_6ED6(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&G_h01_A554[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}

