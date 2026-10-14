long F_h11_2562(x1,y1,x2,y2)
int x1,y1,x2,y2;
{
    long dx,dy;

    dx=(x1-x2<0)?-(x1-x2):x1-x2;
    dy=(y1-y2<0)?-(y1-y2):y1-y2;
    return dx*dx+dy*dy;
}

struct Record { int pad[6]; int a,b,gap,c,d; char tail[12]; };
extern struct Record G_h01_A554[36];
F_h11_6ED6(n,a,b,c,d) int n,*a,*b,*c,*d; {
 struct Record *p;
 p=&G_h01_A554[n];
 *a=p->a; *b=p->b; *c=p->c; *d=p->d;
}

struct Record { int head[9],x,y; char tail[12]; };
extern struct Record G_h01_A554[1];
recovered(a,b,n) int a,b,n; { struct Record *p; int x,y;
 p=&G_h01_A554[n]; x=p->x/53; y=(p->y-48)>>5;
 return x==a && y==b ? 1 : 0;
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

