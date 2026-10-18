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

extern int G_h01_37EC;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int G_h01_37F2;
extern char difficulty_level[3];
extern struct ClusterRecord jg_platform_records[1];
extern short jg_tile_reward_available_flags[1];
extern int jg_set_platform_record_state();
extern int jg_get_grid_row_right_boundary();
extern int jg_get_grid_row_left_boundary();
extern int jg_set_platform_render_state();
extern int jg_start_animation_sequence();
extern unsigned int F_h00_463E();

recovered(mode)
int mode;
{
    int i, selected, result;

    G_h01_37F2 = 1;
    switch (difficulty_level[0]) {
    case 0:
        selected = 35;
        break;
    case 1:
        selected = 25;
        break;
    case 2:
        selected = 15;
        break;
    }

    for (i = 1; i < G_h01_37EC; i++) {
        jg_set_platform_record_state(i, 2);
        if (jg_platform_records[i].value8 != 0) {
            ((int *)&jg_platform_records[i])[24] = 1;
            jg_platform_records[i].value2c =
                ((int *)&jg_platform_records[i])[0] * 53 +
                ((((((int *)&jg_platform_records[i])[0] & 1) ^ 1) == 0) ? 4 : -8) - 1;
            jg_platform_records[i].value2e = ((int *)&jg_platform_records[i])[1] * 32 + 48;
            jg_set_platform_render_state(i, 3);
            jg_start_animation_sequence(24, jg_platform_records[i].pad18, 1,
                       jg_platform_records[i].value2c,
                       jg_platform_records[i].value2e);
        }
        else if (mode && F_h00_463E() % 100 < 25)
            jg_tile_reward_available_flags[i] = 1;
    }

    G_h01_37F0 = 0;
    G_h01_37EE = 0;
    if (mode) {
        result = jg_get_grid_row_left_boundary(1, 0);
        result = jg_get_grid_row_right_boundary(1, 0);
    }
}
