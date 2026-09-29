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

extern int G_h01_8B1C[41][4];
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_945C[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94B8;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D6;
extern int G_h01_94D8;
extern int G_h01_7A90;
extern int G_h01_34D8[16];
extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h11_4B0C();
extern int F_h11_5A12();
extern int F_h11_5A62();
extern int F_h11_5AB0();
extern int F_h11_5EC0();
extern int F_h11_3F90();
extern int F_h11_6F78();

void recovered()
{
    unsigned int key;
    int found;
    int animated;
    int old_state;
    int old_direction;
    struct ClusterRecord *record;

    animated = 0;
    old_state = G_h01_94AE;
    old_direction = G_h01_94B0;
    record = &G_h01_8BEC[G_h01_94D6];
    key = F_h00_4376();
    G_h01_7A90 = key;

    if (key & 0x80)
        key |= 0x80;
    if (G_h01_34D8[7] > 0) {
        --G_h01_34D8[7];
        return;
    }

    if (G_h01_94AE == 5) {
        switch (key) {
        case 3:
            G_h01_94AE = 1;
            if (G_h01_94B0 == 0)
                G_h01_94B0 = 1;
            if ((8 >> G_h01_94B0) + G_h01_94BE + 20 >
                F_h11_5A12(0, G_h01_94BA)) {
                if (G_h01_94B4) {
                    G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                    F_h11_5EC0(G_h01_94D6);
                } else if (!G_h01_94B6 &&
                           !G_h01_8B1C[G_h01_94BA + 1][G_h01_94BC]) {
                    if (F_h11_5AB0(1, 3, &found) ||
                        (G_h01_94BC == 2 &&
                         F_h11_3F90((8 >> G_h01_94B0) +
                                    G_h01_94BE + 16) > 0))
                        G_h01_94AE = 4;
                }
            }
            break;

        case 7:
            if (G_h01_94BE - 16 <= 0) {
                G_h01_94AE = 5;
                goto state5_switch_end;
            } else {
                G_h01_94AE = 1;
                if (G_h01_94B0 == 1)
                    G_h01_94B0 = 0;
                if ((8 >> G_h01_94B0) + G_h01_94BE - 18 <
                    F_h11_5A62(0, G_h01_94BA)) {
                    if (G_h01_94B4 &&
                        G_h01_8B1C[G_h01_94BA + 1][((int *)record)[1]]) {
                        G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                        F_h11_5EC0(G_h01_94D6);
                    } else if (!G_h01_94B6 &&
                               !G_h01_8B1C[G_h01_94BA - 1][G_h01_94BC]) {
                        if (F_h11_5AB0(0, 3, &found) ||
                            (G_h01_94BC == 2 &&
                             F_h11_3F90((8 >> G_h01_94B0) +
                                        G_h01_94BE - 16) > 0))
                            G_h01_94AE = 4;
                    }
                }
            }
            break;

        case 128:
            G_h01_94AE = 18;
            break;

        case 1:
            if (G_h01_94B4 && G_h01_94B0 == 1) {
                G_h01_94AE = 3;
            } else if (F_h11_5AB0(2, 2, &found)) {
                if (G_h01_94B6) {
                    G_h01_94B6 = 0;
                    G_h01_94C0 = 0x82;
                    G_h01_94BC = (G_h01_94C0 - 16) >> 5;
                    G_h01_94AE = 12;
                } else
                    G_h01_94AE = 20;
            } else {
                if (!G_h01_945C[G_h01_94BA])
                    goto key1_fallback_missing;
                if (G_h01_94B6) {
                    G_h01_94AE = 19;
                    goto key1_fallback_done;
                }
                if (G_h01_94B0 == 1) {
                    if (G_h01_945C[G_h01_94BA + 1]) {
                        G_h01_94AE = 17;
                        goto key1_fallback_done;
                    }
                }
                if (G_h01_94B0 == 0 &&
                    G_h01_945C[G_h01_94BA - 1]) {
                    G_h01_94AE = 16;
                    goto key1_fallback_done;
                }
key1_fallback_invalid:
                G_h01_94AE = 19;
key1_fallback_done:
                goto key1_fallback_exit;
key1_fallback_missing:
                G_h01_94AE = 19;
            }
key1_fallback_exit:
            break;

        case 5:
            if (G_h01_94B6)
                G_h01_94AE = 10;
            else if (((G_h01_94C0 + 14) >> 5) >= 2) {
                if (G_h01_94B4) {
                    G_h01_94C0 = ((int *)record)[1] * 32 + 16;
                    F_h11_5EC0(G_h01_94D6);
                }
                G_h01_94AE = 13;
            } else
                G_h01_94AE = 21;
            break;

        default:
            ++G_h01_94B8;
            break;
        }
state5_switch_end:
        goto state8_join;
    }
    if (G_h01_94AE == 8) {
        G_h01_34D8[7] = 2;
        switch (key) {
        case 5:
            ++G_h01_94BC;
            G_h01_94C0 = G_h01_94BC * 32 + 16;
            G_h01_94D8 = 0;
            if (G_h01_94C0 + 16 > 0x70)
                G_h01_94AE = 2;
            else
                G_h01_94AE = 5;
            break;

        case 3:
            if (F_h11_6F78(G_h01_94D8 + 1,
                           (8 >> G_h01_94B0) + G_h01_94BE,
                           G_h01_94C0 + 16, 0x100)) {
                ++G_h01_94D8;
                animated = 1;
            } else {
                ++G_h01_94BC;
                G_h01_94C0 = G_h01_94BC * 32 + 16;
                if (G_h01_94C0 + 16 > 0x70)
                    G_h01_94AE = 2;
                else
                    G_h01_94AE = 5;
                G_h01_94D8 = 0;
            }
            break;

        case 7:
            if (F_h11_6F78(G_h01_94D8 - 1,
                           (8 >> G_h01_94B0) + G_h01_94BE,
                           G_h01_94C0 + 16, 0x100)) {
                --G_h01_94D8;
                animated = 1;
            } else {
                ++G_h01_94BC;
                G_h01_94C0 = G_h01_94BC * 32 + 16;
                G_h01_94D8 = 0;
                if (G_h01_94C0 + 16 > 0x70)
                    G_h01_94AE = 2;
                else
                    G_h01_94AE = 5;
            }
            break;

        default:
            G_h01_34D8[7] = 0;
            break;
        }
    }

state8_join:
    ;

    if (!animated &&
        (G_h01_94AE != old_state || G_h01_94B0 != old_direction))
        F_h11_4B0C(G_h01_94AE);
    G_h01_94BA = ((8 >> G_h01_94B0) + G_h01_94BE) / 53;
    G_h01_94BC = (G_h01_94C0 - 16) >> 5;
    F_h00_435E();
}

long F_h11_2562(x1,y1,x2,y2)
int x1,y1,x2,y2;
{
    long dx,dy;

    dx=(x1-x2<0)?-(x1-x2):x1-x2;
    dy=(y1-y2<0)?-(y1-y2):y1-y2;
    return dx*dx+dy*dy;
}

F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

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

/* Fingerprint-derived direct reconstruction candidate for ov11_F_6F78. */
struct DistanceRecord {
    char pad0[18];
    int value18;
    int value20;
    char tail[12];
};

extern char G_h01_46E0;
extern struct DistanceRecord G_h01_A554[1];
extern long F_h11_2562();

int F_h11_6F78(index,x,y,scale)
int index;
int x;
int y;
int scale;
{
    struct DistanceRecord *record;

    record=&G_h01_A554[index];
    switch (G_h01_46E0) {
    case 0:
        scale*=3;
        break;
    case 1:
        scale*=2;
        break;
    case 2:
        break;
    }
    return index>0 && (long)scale>F_h11_2562(x,y,record->value18,record->value20);
}

