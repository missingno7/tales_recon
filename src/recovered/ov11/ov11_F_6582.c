struct Item {
    int value0;
    int value2;
    char pad4[6];
    int value10;
    char pad12[20];
    int state;
    int value34;
    int value36;
    char pad38[2];
};

extern struct Item jg_contact_hazard_records[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_8A3C;
extern int point_inside_rectangle();
extern int jg_select_player_animation();
extern int jg_start_animation_sequence();
extern int play_sound();

recovered(index)
int index;
{
    struct Item *item;
    int result;
    int y;
    int x;

    item = jg_contact_hazard_records + index;
    result = 0;
    y = (8 >> G_h01_94B0) + G_h01_94BE;
    x = G_h01_94C0 + 16;
    if (G_h01_94AE == 19)
        x += 8;
    else if (G_h01_94AE == 18)
        y -= 16;

    if (item->state != 45 && G_h01_94AE != 2 &&
        G_h01_94AE != 6 && G_h01_94AE != 7) {
        if (point_inside_rectangle(item->value34 + 16,
                       item->value36,
                       y,
                       x,
                       item->value34 + 48,
                       item->value36 + 56) != 0) {
            if (G_h01_94B6 != 0) {
                G_h01_94B6 = 0;
                G_h01_94D4 = 0;
            }
            G_h01_94AE = 45;
            jg_select_player_animation(G_h01_94AE);
            item->state = 45;
            jg_start_animation_sequence(8, &item->value10, 45,
                       item->value34, item->value36);
            play_sound(98);
            G_h01_8A3C = 3;
            result = 1;
        } else if (item->value0 == G_h01_94BA &&
                   ((G_h01_94C0 + 14) >> 5) == item->value2 &&
                   (G_h01_94AE == 12 || G_h01_94AE == 1 || G_h01_94AE == 5)) {
            G_h01_94AE = 14;
            jg_select_player_animation(14);
        }
    }
    return result;
}