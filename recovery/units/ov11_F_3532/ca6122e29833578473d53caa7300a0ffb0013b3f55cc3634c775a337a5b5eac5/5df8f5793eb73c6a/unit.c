struct Record {
    int field0;
    char gap2[6];
    int field8;
    char gap10[14];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char gap36[8];
    int field44;
    int field46;
    int field48;
    int field50;
    int field52;
    char gap54[2];
    int field56;
    int field58;
    int field60;
    int field62;
};

struct TableCell {
    int value;
    char unused[12];
};

extern struct Record G_h01_9FCE[1];
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern struct TableCell G_h01_8A68[1];
extern int G_h01_A14E;
extern int F_h11_41F6();
extern int F_h11_4696();
extern int F_h11_583A();
extern int F_h11_54F8();

recovered(index)
int index;
{
    struct Record *record;
    int row;

    record = &G_h01_9FCE[index];
    if (record->field46 != 1)
        goto exit;
    if (record->field8 == 0)
        goto state_update;
    if (record->field48 != 0)
        goto state_update;
    if (record->field50 > G_h01_8A3E - 16)
        goto upper;

    record->field44 = 13;
    record->field46 = 0;
    G_h01_7A92 = 0;
    F_h11_41F6(2, (char *)record + 2, 13,
               record->field30, record->field32);
    goto position_join;

upper:
    if (record->field50 < G_h01_8A3E + 320)
        goto adjust;
    record->field46 = 0;
    goto position_join;

adjust:
    if (G_h01_A14E)
        goto subtract_eight;
    G_h01_A14E = 1;
    record->field50 -= 32;
    goto position_join;

subtract_eight:
    record->field50 -= 8;
position_join:
    goto draw;

state_update:
    if (record->field48 != 3)
        goto draw;
    if (record->field8 <= 2)
        goto draw;
    record->field52 += 8;
    if (record->field52 < 169)
        goto draw;
    record->field44 = 16;
    record->field46 = 0;
    F_h11_41F6(2, (char *)record + 2, 16,
               record->field30, record->field32);

draw:
    F_h11_4696(record->field56, record->field60, 24, 16,
               index + 12);
    F_h11_583A(record->field56, record->field60, 24, 16, 11);
    row = record->field56 / 104;
    if (G_h01_8A68[row].value)
        F_h11_54F8(G_h01_8A68[row].value, 11);
exit:
    ;
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

