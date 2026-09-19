long F_h11_2562(x1,y1,x2,y2)
int x1,y1,x2,y2;
{
    long dx,dy;

    dx=(x1-x2<0)?-(x1-x2):x1-x2;
    dy=(y1-y2<0)?-(y1-y2):y1-y2;
    return dx*dx+dy*dy;
}

/* Direct reconstruction candidate for ov11_F_6F78. */
struct Record6F78 {
    char pad0[18];
    int value18;
    int value20;
    char pad1[12];
};

extern struct Record6F78 G_h01_A554[1];
extern char G_h01_46E0;
extern long F_h11_2562();

recovered(index, x, y, scale)
int index;
int x;
int y;
int scale;
{
    struct Record6F78 *record;

    record = &G_h01_A554[index];
    switch (G_h01_46E0) {
    case 0:
        scale *= 3;
        break;
    case 1:
        scale *= 2;
        break;
    }
    if (F_h11_2562(x, y, record->value18, record->value20, (long)scale) >= scale)
        return 1;
    return 0;
}
