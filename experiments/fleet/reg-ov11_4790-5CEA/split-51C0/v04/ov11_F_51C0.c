struct ScreenRecord {
    char prefix[12];
    int slot0c;
    char reserved0e[8];
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
extern int G_h01_8A6A[1];
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B2;
extern int G_h01_94B8;
extern int G_h01_94C2;
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
extern long F_h11_2562();
extern int F_h11_41F6();
extern int F_h00_463E();
extern int F_h00_57D2();

recovered(index)
int index;
{
    struct ScreenRecord *record;
    int changed,step,row_index;

    record=&G_h01_3724[index];
    changed=0;
    step=0;
    if (G_h01_8A3C) G_h01_371E=G_h01_371C;
    else G_h01_371E--;
    switch (record->mode) {
    case 14:
        if (G_h01_371E==0) {
            record->mode=18;
            changed=1;
            step=1;
        }
        break;
    case 18:
        if (record->row==G_h01_94BA &&
            record->column==((G_h01_94C0+14)>>5) &&
            (G_h01_94AE==5 || G_h01_94AE==1 || G_h01_94AE==12)) {
            G_h01_94AE=14;
            F_h11_4B0C(14);
        }
        if (G_h01_371E==0) {
                if ((F_h00_463E()%100)<G_h01_371C) {
                    record->mode=14;
                    G_h01_371E=G_h01_371C*3;
                    changed=1;
                    step=1;
                } else if ((F_h00_463E()%100)<G_h01_371E) {
                    if (F_h11_25F8(record->x+6,record->y+12,
                        G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16,
                        record->x+58,record->y+64) && G_h01_94AE!=8) {
                        record->mode=19;
                        changed=1;
                        step=1;
                        F_h00_57D2(99);
                    }
                }
        }
        break;
    case 19:
        if (G_h01_94B0!=10) {
            if (F_h11_25F8(record->x,record->y,
                G_h01_94C0+(8>>G_h01_94B2),G_h01_94C2+16,
                record->x+64,record->y+48)) {
                G_h01_94C2-=24;
                if (G_h01_94B8) G_h01_94B8=0;
                G_h01_94B0=2;
                F_h11_4B0C(2);
            }
        }
        if (F_h11_45EC(record)) {
            record->mode=18;
            changed=1;
            step=1;
        } else {
            changed=1;
            F_h11_4474(11,record);
        }
        break;
    }
    if (G_h01_8A3C) {
        F_h11_54F8(index,0);
    } else {
        if (changed) {
            row_index=record->x/104;
            if (*((int *)((char *)G_h01_8A6A+((long)row_index*14))) ||
                *((int *)((char *)G_h01_8A6A+((long)(row_index-1)*14))))
                record->slot0c++;
        } else {
            if (F_h11_2562(record->x+32,record->y+24,
                G_h01_94C0+(8>>G_h01_94B2),G_h01_94C2+16)<10000)
                F_h11_54F8(index,5);
        }
    }
    if (step)
        F_h11_41F6(11,record,record->mode,record->x,record->y);
    if (G_h01_371E<=0)
        G_h01_371E=G_h01_371C;
}
