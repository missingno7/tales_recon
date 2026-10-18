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

extern struct ScreenRecord jg_scenery_object_records[1];
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
extern int jg_set_p_section_object_state();
extern int point_inside_rectangle();
extern int jg_select_player_animation();
extern int F_h11_45EC();
extern int jg_advance_animation_sequence();
extern long squared_distance_long();
extern int jg_start_animation_sequence();
extern int F_h00_463E();
extern int play_sound();

recovered(index)
int index;
{
    struct ScreenRecord *record;
    int changed,step,row_index;

    record=&jg_scenery_object_records[index];
    changed=0;
    step=0;
    if (G_h01_8A3C) G_h01_3722=G_h01_3720;
    else G_h01_3722--;
    switch (record->mode) {
    case 14:
        if (G_h01_3722==0) {
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
            jg_select_player_animation(14);
        }
        if (G_h01_3722!=0) goto shared_tail;
        {
                if ((F_h00_463E()%100)<G_h01_371C) {
                    record->mode=14;
                    G_h01_3722=G_h01_3720*3;
                    changed=1;
                    step=1;
                } else if ((F_h00_463E()%100)<G_h01_371E) {
                    if (point_inside_rectangle(record->x+6,record->y+12,
                        G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16,
                        record->x+58,record->y+64) && G_h01_94AE!=8) {
                        record->mode=19;
                        changed=1;
                        step=1;
                        play_sound(99);
                    }
                }
        }
        break;
    case 19:
        if (G_h01_94AE!=10) {
            if (point_inside_rectangle(record->x,record->y,
                G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16,
                record->x+64,record->y+48)) {
                G_h01_94C0-=24;
                if (G_h01_94B6) G_h01_94B6=0;
                G_h01_94AE=2;
                jg_select_player_animation(2);
            }
        }
        if (F_h11_45EC(record)) {
            record->mode=18;
            changed=1;
            step=1;
        } else {
            changed=1;
            jg_advance_animation_sequence(11,record);
        }
        break;
    }
shared_tail:
    if (G_h01_8A3C) {
        jg_set_p_section_object_state(index,0);
    } else {
        if (changed || squared_distance_long(record->x+32,record->y+24,
            G_h01_94BE+(8>>G_h01_94B0),G_h01_94C0+16)<10000) {
            jg_set_p_section_object_state(index,5);
        } else {
            row_index=record->x/104;
            if (*((int *)((char *)G_h01_8A6A+((long)row_index*14))) ||
                *((int *)((char *)G_h01_8A6A+((long)(row_index-1)*14))))
                record->slot0c++;
        }
    }
    if (step)
        jg_start_animation_sequence(11,record,record->mode,record->x,record->y);
    if (G_h01_3722<=0)
        G_h01_3722=G_h01_3720;
}
