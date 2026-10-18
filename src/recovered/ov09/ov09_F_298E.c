struct Table {
    int first;
    int second;
    char pad[2];
};

extern long F_h00_463E();
extern int play_sound();
extern char timed_scene_event_spawn_chance_percent;
extern int timed_scene_bonus_event_type;
extern int timed_scene_route_point_indices[6];
extern unsigned char timed_scene_event_spawn_masks[96];
extern char G_h01_0468[16];
extern char timed_scene_active_events;
extern char G_h01_433E;
extern char G_h01_434A;
extern char difficulty_level;
extern char timed_scene_selected_option_index;
extern struct Table timed_scene_event_position_offsets[64];

recovered(mode)
char mode;
{
    unsigned row;
    int value;
    register char *event;

    for (;;) {
    if ((unsigned)F_h00_463E()%100 < timed_scene_event_spawn_chance_percent)
        row=timed_scene_bonus_event_type;
    else
        row=timed_scene_route_point_indices[(unsigned)F_h00_463E()%6];

    if (!mode) {
        value=(unsigned)F_h00_463E()%5;
        if (*((unsigned char *)timed_scene_event_spawn_masks+(long)(row-14)*6) & G_h01_0468[value]) {
            if (value==4)
                value=13;
            event=&timed_scene_active_events;
            event[0]=value+1;
            *(int *)(event+2)=row;
            event[4]=0;
            event[5]=1;
            if (!difficulty_level && timed_scene_selected_option_index)
                event[6]=2;
            else
                event[6]=1;
            *(int *)(event+8)=timed_scene_event_position_offsets[row-14].first;
            *(int *)(event+10)=timed_scene_event_position_offsets[row-14].second;
            play_sound(103);
            break;
        }
        break;
    }
    if (mode==1) {
        value=(int)F_h00_463E()&3;
        if (*((unsigned char *)timed_scene_event_spawn_masks+(long)(row-14)*6) & G_h01_0468[value+5]) {
            event=&G_h01_433E;
            event[0]=value+5;
            *(int *)(event+2)=row;
            event[4]=0;
            event[5]=1;
            if (!difficulty_level && timed_scene_selected_option_index!=1)
                event[6]=2;
            else
                event[6]=1;
            *(int *)(event+8)=timed_scene_event_position_offsets[row-14].first;
            *(int *)(event+10)=timed_scene_event_position_offsets[row-14].second;
            play_sound(105);
            break;
        }
        break;
    }
    if (mode==2) {
        value=(unsigned)F_h00_463E()%5;
        if (*((unsigned char *)timed_scene_event_spawn_masks+(long)(row-14)*6) & G_h01_0468[value+9]) {
            event=&G_h01_434A;
            event[0]=value+9;
            *(int *)(event+2)=row;
            event[4]=0;
            event[5]=1;
            if (!difficulty_level && timed_scene_selected_option_index!=2)
                event[6]=2;
            else
                event[6]=1;
            *(int *)(event+8)=timed_scene_event_position_offsets[row-14].first;
            *(int *)(event+10)=timed_scene_event_position_offsets[row-14].second;
            play_sound(104);
            break;
        }
        break;
    }
    }
}
