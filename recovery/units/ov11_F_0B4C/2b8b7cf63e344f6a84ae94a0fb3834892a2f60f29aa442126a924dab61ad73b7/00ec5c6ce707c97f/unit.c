extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int F_h11_5FB2();
extern int F_h11_405A();
extern int F_h11_4B0C();
extern int F_h11_415A();
extern int F_h11_40E0();

recovered()
{
    if (G_h01_94B4) {
        F_h11_5FB2(G_h01_94D6, &G_h01_94C0);
    } else if (G_h01_94B6) {
        if (F_h11_405A(G_h01_94D4)) {
            G_h01_94AE = 2;
            F_h11_4B0C(2);
            G_h01_94B6 = 0;
        } else {
            F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            F_h11_40E0(G_h01_94D4, 10);
        }
    }
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

struct Record { int state; char tail[30]; };
extern struct Record G_h01_A16A[36];
F_h11_405A(n) int n; { return G_h01_A16A[n].state==4; }

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

struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record G_h01_A554[36];
F_h11_6ED6(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&G_h01_A554[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}

