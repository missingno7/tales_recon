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
        if (record->row==G_h01_94BA &&
            record->column==((G_h01_94C0+14)>>5) &&
            (G_h01_94AE==5 || G_h01_94AE==1 || G_h01_94AE==12)) {
            G_h01_94AE=14;
            F_h11_4B0C(14);
            if (G_h01_371E==0) {
                kind=F_h00_463E()%100;
                if (kind<G_h01_371C) {
                    record->mode=14;
                    G_h01_3722=G_h01_3720*3;
                    changed=1;
                } else if ((F_h00_463E()%100)<G_h01_371E) {
                    if (F_h11_25F8(record->x+6,record->y+12,
                        G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16,
                        record->x+58,record->y+64) && G_h01_94AE!=8) {
                        record->mode=19;
                        changed=1;
                        F_h00_57D2(99);
                    }
                }
            }
        }
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
