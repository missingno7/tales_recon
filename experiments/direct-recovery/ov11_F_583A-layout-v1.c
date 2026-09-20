/* Layout-only normal source-unit experiment; not canonical recovery source. */
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
extern int F_h11_5C42();
extern int F_h11_66FE();
extern int F_h11_5962();

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

F_h11_5962(index,mode)
int index; int mode;
{
    struct ClusterRecord *record;
    record=&G_h01_8BEC[index];
    record->state40=2;
    if (record->value42==0 || mode==2) record->value42=mode;
    if (mode!=3 && record->value8) F_h11_5C42(index,2);
    if (mode!=8 && record->value10) F_h11_66FE(record->value10,2);
}
