extern int G_h01_9FB6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int F_h11_4696();
extern int F_h11_247C();

recovered(a)
int a;
{
    G_h01_9FB6 = 2;
    if (a == 12)
        F_h11_4696(G_h01_9FC8, G_h01_9FCA, 40, 32, 33);
    F_h11_247C(12, G_h01_9FC8, G_h01_9FCA, 40, 32);
}

struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
extern struct Record G_h01_8A66[1];
extern int F_h11_5C42();
extern int F_h11_54F8();
extern int F_h11_2E26();
extern int F_h11_66FE();
extern int F_h11_717A();

F_h11_247C(a,b,c)
int a,c;
long b;
{
    struct Record *p,*last;

    if (((int *)&b)[0]<0) ((int *)&b)[0]=0;
    p=&G_h01_8A66[((int *)&b)[0]/104];
    last=&G_h01_8A66[(((int *)&b)[0]+c)/104];
    for (;p<=last;p++) {
        if (p->ignored) F_h11_5C42(p->ignored,a);
        if (p->value1) F_h11_54F8(p->value1,a);
        if (p->value5) F_h11_2E26(p->value5,a);
        if (p->value4) F_h11_66FE(p->value4,a);
        if (p->value6) F_h11_717A(p->value6,a);
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

struct Record { int value; char tail[8]; };
extern struct Record G_h01_A6B0[36];
F_h11_717A(a) int a; { G_h01_A6B0[a].value=2; }

