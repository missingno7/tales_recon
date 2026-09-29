extern int G_h01_94C2;
extern int G_h01_94C4;
struct Object;
extern struct Object *G_h01_94CE;
extern struct Object *G_h01_9F4E;
extern struct Object *G_h01_9F52;
extern struct Object *G_h01_9F56;
extern struct Object *G_h01_9F8E;
extern int F_h11_4696();
extern int F_h11_583A();

recovered()
{
    if (G_h01_94CE == G_h01_9F4E ||
        G_h01_94CE == G_h01_9F56) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 0x28, 0x21, 0x16);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 0x28, 0x21, 0x0a);
    } else if (G_h01_94CE == G_h01_9F52) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 0x30, 0x29, 0x16);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 0x30, 0x29, 0x0a);
    } else if (G_h01_94CE == G_h01_9F8E) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 0x58, 0x22, 0x16);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 0x58, 0x22, 0x0a);
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

