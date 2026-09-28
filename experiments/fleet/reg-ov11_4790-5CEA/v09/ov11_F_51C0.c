struct ScreenRecord {
    char prefix[22];
    int mode;
    int frame;
    int x;
    int y;
    int row;
    int column;
    int id;
    int flags;
    int tail;
};

extern struct ScreenRecord G_h01_3724[1];
extern int G_h01_00A8;
extern int G_h01_00CC;
extern int G_h01_371C;
extern int G_h01_371E;
extern int G_h01_3720;
extern int G_h01_3722;
extern int G_h01_8A3E;
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_9F5E[1];
extern int F_h11_54F8();
extern int F_h11_25F8();
extern int F_h11_4B0C();
extern int F_h11_45EC();
extern int F_h11_4474();
extern int F_h11_2562();
extern int F_h11_41F6();
extern int F_h00_463E();
extern int F_h00_57D2();

recovered(index)
int index;
{
    struct ScreenRecord *record;
    int kind,changed,mode,step;

    record=&G_h01_3724[index];
    changed=0;
    if (G_h01_8A3E) G_h01_371E=G_h01_371C;
    else G_h01_371E--;
    mode=record->mode;
    if (mode==18) {
        record->frame=18;
        changed=1;
    }
    if (record->flags!=G_h01_94B0) {
        F_h00_463E(record->flags);
        record->flags=G_h01_94B0;
    }
    if (record->mode==0) {
        F_h11_54F8(index,0);
        F_h11_4B0C(2,index);
        changed=1;
    }
    if (mode==14) {
        F_h11_25F8(record->x,record->y,record->row,record->column);
        F_h11_4B0C(index,2);
        if (F_h11_45EC(index)) {
            record->mode=18;
            record->frame=1;
            changed=1;
        }
    }
    if (mode==4) {
        F_h11_4B0C(record->x,record->y);
        if (record->flags) {
            F_h11_4474(index,11);
            record->mode=18;
            changed=1;
        }
    }
    if (mode==1 || mode==2 || mode==3) {
        F_h00_57D2(record->x,record->y);
        F_h11_2562(record->x,record->y,record->row,record->column);
        G_h01_9F5E[0]=record->x;
        G_h01_9F5E[1]=record->y;
        G_h01_9F5E[2]=record->mode;
        F_h11_41F6(record,index,record->x,record->y,mode,11);
    }
    if (changed) {
        step=G_h01_371E;
        G_h01_3720=step;
        G_h01_3722=G_h01_3720+1;
    }
}
