struct ClusterRecord {
    int value0;
    int value2;
    char pad4[14];
    char pad18[26];
    int value2c;
    int value2e;
    int state30;
    int value32;
};

extern int G_h01_7A92;
extern int G_h01_8A3C;
extern struct ClusterRecord jg_platform_records[1];
extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94C0;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int point_inside_rectangle();
extern int jg_get_actor_world_position();
extern int jg_start_animation_sequence();
extern int jg_advance_animation_sequence();
extern int jg_set_platform_render_state();

recovered(index)
int index;
{
    struct ClusterRecord *record;
    int x, y, update, state;

    record = &jg_platform_records[index];
    update = 0;
    state = record->state30;

    switch (record->state30) {
    case 1:
        if (((G_h01_94C0 + 14) >> 5) == ((int *)record)[1] &&
            ((int *)record)[0] == G_h01_94BA) {
            G_h01_94B4 = 1;
            G_h01_94D6 = index;
            state = 3;
            update = 1;
        }
        break;
    case 3:
        if ((((int *)record)[0] != G_h01_94BA && G_h01_94AE != 18) ||
            G_h01_94B6) {
            state = 1;
            G_h01_94B4 = 0;
            G_h01_94D6 = 0;
            G_h01_37F0 = 0;
            G_h01_37EE = 0;
            update = 1;
        } else {
            update = 1;
            jg_advance_animation_sequence(24, &record->pad18[0]);
        }
        break;
    default:
        break;
    }

    if (record->state30 != state) {
        record->state30 = state;
        jg_start_animation_sequence(24, &record->pad18[0], state,
                   record->value2c, record->value2e);
    }

    if (G_h01_8A3C) {
        jg_set_platform_render_state(index, 0);
    } else if (update) {
        jg_set_platform_render_state(index, 3);
    } else if (G_h01_7A92 &&
               jg_get_actor_world_position(G_h01_7A92, &x, &y) &&
               point_inside_rectangle(record->value2c, record->value2e - 6,
                          x, y, record->value2c + 64,
                          record->value2e + 32)) {
        jg_set_platform_render_state(index, 3);
    }
}
