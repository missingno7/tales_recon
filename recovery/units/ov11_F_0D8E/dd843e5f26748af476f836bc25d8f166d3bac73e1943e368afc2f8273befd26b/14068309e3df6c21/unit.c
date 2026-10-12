struct ClusterRecord { char pad0[8]; int value8; int value10; char pad12[2]; int value14; int value16; char pad18[12]; int state30; int value32; char pad34[6]; int state40; int value42; int value2c; int value2e; char tail[4]; };
extern int G_h01_94AE;
extern int G_h01_94B0;
extern char G_h01_94B3;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int G_h01_94D8;
extern char *G_h01_94DA;
extern int G_h01_94DE;
extern int G_h01_94E0;
extern int G_h01_94E6;
extern int G_h01_945C[1];
extern int G_h01_8B1C[41][4];
extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h00_57D2();
extern int F_h11_3F90();
extern int F_h11_40AE();
extern int F_h11_415A();
extern int F_h11_4AA4();
extern int F_h11_4B0C();
extern int F_h11_5EC0();
extern int F_h11_6ED6();
extern int F_h11_6F78();

recovered()
{
    int r2;
    int r4;
    int t6;
    int t8;
    int done;
    int prev;
    int tick;
    char *cursor;

    done = 0;
    prev = G_h01_94AE;
    tick = (G_h01_94DE + 1 >= G_h01_94E0);
    cursor = (char *)G_h01_8BEC + ((long)G_h01_94D6 * 52);
    if (G_h01_94E6 > 0)
        return;
    G_h01_94BA = ((8 >> G_h01_94B0) + G_h01_94BE) / 53;
    G_h01_94BC = (G_h01_94C0 - 16) >> 5;

    switch (G_h01_94AE) {
    case 19:
        if (tick) {
            G_h01_94C0 += 8;
            G_h01_94AE = 5;
        }
        break;
    case 18:
        if (tick) {
            G_h01_94AE = 5;
            G_h01_94BE += G_h01_94B0 == 0 ? 14 : -14;
        }
        break;
    case 17:
        if (tick) {
            if ((t8 = G_h01_945C[G_h01_94BA]) != 0 && F_h11_6F78(t8, G_h01_94BE + 15, G_h01_94C0 + 24, 0x144)) {
                G_h01_94D8 = t8;
                G_h01_94AE = 8;
            } else {
                G_h01_94AE = 2;
            }
        }
        break;
    case 16:
        if (tick) {
            if ((t8 = G_h01_945C[G_h01_94BA]) != 0 && F_h11_6F78(t8, G_h01_94BE + 4, G_h01_94C0 + 8, 0x144)) {
                G_h01_94D8 = t8;
                G_h01_94AE = 8;
            } else {
                G_h01_94AE = 2;
            }
        }
        break;
    case 14:
        if (tick)
            G_h01_94AE = 2;
        break;
    case 12:
        if (tick) {
            G_h01_94C0 = ((G_h01_94C0 >> 5) << 5) + 16;
            G_h01_94AE = 5;
        }
        break;
    case 20:
        if (tick) {
            G_h01_94C0 += 7;
            G_h01_94AE = 5;
        }
        break;
    case 21:
        if (tick) {
            G_h01_94C0 += 6;
            G_h01_94AE = 5;
        } else if (G_h01_94DE == 5) {
            if (G_h01_8B1C[G_h01_94BA][G_h01_94BC + 1] == 0)
                G_h01_94AE = 2;
        }
        break;
    case 13:
        if (tick) {
            G_h01_94C0 += 5;
            if ((t6 = F_h11_3F90(G_h01_94BE)) >= 0) {
                G_h01_94D4 = t6;
                F_h11_40AE(G_h01_94D4);
                G_h01_94B6 = 1;
                G_h01_94AE = 5;
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            } else {
                G_h01_94AE = 2;
            }
        }
        break;
    case 10:
        if (tick)
            G_h01_94AE = 5;
        break;
    case 3:
        if (G_h01_94DE == 1) {
            F_h11_5EC0(G_h01_94D6);
        } else if (G_h01_94DE == 6) {
            t8 = G_h01_8B1C[G_h01_94BA][(G_h01_94C0 + 14) >> 5];
            if (t8 == 0 || (G_h01_94B4 && t8 == G_h01_94D6)) {
                G_h01_94AE = 2;
                break;
            }
        } else if (tick) {
            G_h01_94C0 = ((((G_h01_94C0 + 14) >> 5)) << 5) + 16;
            G_h01_94AE = 5;
            F_h00_57D2(0x77);
        }
        if ((t8 = G_h01_945C[G_h01_94BA]) != 0 && F_h11_6F78(t8, (8 >> G_h01_94B0) + G_h01_94BE, G_h01_94C0 + 16, 0x400)) {
            G_h01_94D8 = t8;
            G_h01_94AE = 8;
        }
        break;
    case 4:
        if (G_h01_94DE == 4 && ((G_h01_94C0 + 14) >> 5) > 2) {
            G_h01_94C0 += 8;
        } else if (tick) {
            if (G_h01_94BC >= 3) {
                if ((t6 = F_h11_3F90((8 >> G_h01_94B0) + G_h01_94BE)) >= 0) {
                    G_h01_94D4 = t6;
                    F_h11_40AE(G_h01_94D4);
                    F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                    F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                    G_h01_94B6 = 1;
                } else {
                    G_h01_94AE = 6;
                }
            }
            G_h01_94AE = 5;
            F_h00_57D2(0x77);
        }
        break;
    case 1:
        if (tick) {
            F_h00_57D2(10);
            G_h01_94B3 ^= 1;
            G_h01_94AE = 5;
        }
        break;
    case 2:
        if (G_h01_94C0 + 40 >= 154) {
            if ((t6 = F_h11_3F90((8 >> G_h01_94B0) + G_h01_94BE)) >= 0) {
                G_h01_94D4 = t6;
                F_h11_40AE(G_h01_94D4);
                G_h01_94B6 = 1;
                G_h01_94AE = 5;
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
                F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            } else {
                G_h01_94AE = 6;
            }
        } else {
            G_h01_94C0 += 16;
            done = 1;
        }
        break;
    case 8:
        F_h11_6ED6(G_h01_94D8, &r2, &r4, &G_h01_94BE, &G_h01_94C0);
        if (G_h01_94BE < r2) {
            G_h01_94DA[52] = G_h01_94B0 == 1 ? 0x1c : 0x1e;
            if (G_h01_94B0 == 0) {
                G_h01_94BE -= 20;
                G_h01_94C0 -= 13;
            } else {
                G_h01_94BE -= 9;
                G_h01_94C0 -= 12;
            }
        } else if (G_h01_94BE > r2) {
            G_h01_94DA[52] = G_h01_94B0 == 1 ? 0x1d : 0x1f;
            if (G_h01_94B0 == 0) {
                G_h01_94BE -= 6;
                G_h01_94C0 -= 12;
            } else {
                G_h01_94BE += 4;
                G_h01_94C0 -= 10;
            }
        } else {
            G_h01_94DA[52] = G_h01_94B0 == 1 ? 0x17 : 0x1b;
            if (G_h01_94B0 == 0) {
                G_h01_94BE -= 12;
                G_h01_94C0 -= 1;
            } else {
                G_h01_94BE -= 5;
                G_h01_94C0 += 0;
            }
        }
        done = 1;
        break;
    case 6:
        if (tick)
            G_h01_94AE = 7;
        break;
    default:
        done = 1;
        break;
    }

    if (!done) {
        if (prev != G_h01_94AE)
            F_h11_4B0C(G_h01_94AE);
        else
            F_h11_4AA4();
    }
    G_h01_94BA = ((8 >> G_h01_94B0) + G_h01_94BE) / 53;
    G_h01_94BC = (G_h01_94C0 - 16) >> 5;
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

/* Direct reconstruction candidate for ov11_F_40AE. */
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

extern short G_h01_A156;
extern struct Event G_h01_A15E[1];
extern int F_h00_57D2();
extern int F_h00_86A8();

F_h11_40AE(index)
int index;
{
    struct Event *record;

    record = &G_h01_A15E[index];
    G_h01_A156 = 0;
    F_h00_86A8(5L);
    F_h00_57D2(91);
}

struct Row {
	short word0;
	short word2;
	short unused4[4];
	short word12;
	short word14;
	short unused16[8];
};

extern short G_h01_94AE;
extern short G_h01_94B6;
extern short G_h01_94C0;
extern short G_h01_94D4;
extern short G_h01_A156;
extern short G_h01_A15A;
extern short G_h01_A15E[1];

void F_h11_415A(index, cursor, output)
short index;
short *cursor;
short *output;
{
	struct Row *row;
	short next;

	row = (struct Row *)((char *)G_h01_A15E + (long)index * 32L);
	if (row->word12 >= row->word14 || F_h11_3F90(*cursor) < 0) {
		G_h01_94B6 = 0;
		G_h01_94D4 = 0;
		G_h01_94AE = 6;
		F_h11_4B0C(6);
    } else if (G_h01_A15A == 0) {

	*cursor += 4;
	next = row->word12 * 2 + row->word2 - 26;
	if (G_h01_A156 == 0)
		G_h01_A156 = G_h01_94C0;
	*output += next - G_h01_A156;
	G_h01_A156 = next;
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

