/* Layout-only source-object experiment for the reciprocal ov11 call cluster. */
struct Target { int x; int y; char pad[48]; char state; };
struct Holder { struct Target *target; char pad0; char state; char pad1[6]; int x; int y; };
struct Motion { int x; int y; char pad[8]; int remaining; int active; struct Holder *holder; };
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
extern int G_h01_8A3E;
extern int G_h01_37EC;
extern int G_h01_37F4[40];
extern int G_h01_3844[40];
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_8B1C[41][4];
extern int F_h00_34E0();
extern int F_h11_4696();
extern int F_h11_66FE();

F_h11_4610(motion)
struct Motion *motion;
{
    struct Holder *holder;
    struct Target *target;
    holder=motion->holder;
    target=holder->target;
    if (motion->remaining>0) {
        target->x=motion->x+holder->x-G_h01_8A3E;
        target->y=motion->y+holder->y;
        target->state=holder->state;
        F_h00_34E0(target);
        motion->remaining--;
        if (motion->remaining==0) motion->active=0;
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

F_h11_59E6()
{
    int i;
    for (i=1;i<G_h01_37EC;i++) F_h11_5962(i,2);
}

F_h11_5A12(flag,index)
int flag,index;
{
    int i;
    if (flag) {
        for (i=0;i<40;i++) G_h01_37F4[i]=(i+1)*53+2;
    } else return G_h01_37F4[index];
}

F_h11_5A62(flag,index)
int flag,index;
{
    int i;
    if (flag) {
        for (i=0;i<40;i++) G_h01_3844[i]=i*53-2;
    } else return G_h01_3844[index];
}

F_h11_5AB0(direction,kind,result)
int direction,kind; int *result;
{
    int found,row,column;
    found=0; row=G_h01_94BA;
    if (direction==1) row++; else if (direction==0) row--;
    if (row<0) goto invalid_row;
    if (row<=40) goto select;
invalid_row:
    goto done;
select:
    if (direction==0 || direction==1) {
        if (kind==2) {
            if ((column=G_h01_94BC-1)>=0)
                if (G_h01_8B1C[row][column]) { *result=column; found=1; }
        } else if (kind==3) {
            if ((column=G_h01_94BC+1)<3)
                if (G_h01_8B1C[row][column]) { *result=column; found=1; }
        }
    } else if (direction==2) {
        if (G_h01_94BC>0)
            if (G_h01_8B1C[row][G_h01_94BC-1]) { *result=G_h01_94BC-1; found=1; }
    }
done:
    return found;
}

F_h11_5BC4(row,column)
int *row,*column;
{
    int i,j;
    for (i=0;i<6;i++)
        for (j=0;j<3;j++)
            if (G_h01_8B1C[i][j]) { *row=i; *column=j; return; }
}

F_h11_5C1A(n)
int n;
{
    struct ClusterRecord *record;
    record=&G_h01_8BEC[n];
    F_h11_4610(&record->pad18[0]);
}

F_h11_5C42(index,mode)
int index; int mode;
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

recovered(index)
int index;
{
    struct ClusterRecord *record;
    record=&G_h01_8BEC[index];
    return record->state30>0;
}
