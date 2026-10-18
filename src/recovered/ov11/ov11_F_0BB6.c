extern short G_h01_94AE;
extern short G_h01_94B0;
extern short G_h01_94B4;
extern short G_h01_94BA;
extern short G_h01_94BC;
extern short G_h01_94BE;
extern short G_h01_94C0;
extern short G_h01_8A3C;
extern short jg_grid_tile_indices[40][4];
extern short jg_tile_reward_available_flags[1];
extern long total_money;
extern int integer_within_inclusive_range();
extern int play_sound();
extern int jg_get_grid_row_right_boundary();
extern int jg_get_grid_row_left_boundary();
extern int jg_select_player_animation();

recovered()
{
    int tile, xpos, offset, ypos;

    offset = (8 >> G_h01_94B0) + G_h01_94BE;
    if (((G_h01_94C0 + 14) >> 5) < 3) {
        if ((tile = jg_grid_tile_indices[G_h01_94BA][((G_h01_94C0 + 14) >> 5)]) != 0 &&
            jg_tile_reward_available_flags[tile] != 0) {
            xpos = G_h01_94BA * 53;
            ypos = (((G_h01_94C0 + 14) >> 5) << 5) + 0x30;
            if (integer_within_inclusive_range(xpos + 0x0f, offset, xpos + 0x21) &&
                integer_within_inclusive_range(ypos - 0x0f, G_h01_94C0 + 0x12, ypos)) {
                play_sound(0x20);
                jg_tile_reward_available_flags[tile] = 0;
                total_money += 0x32;
                G_h01_8A3C = 3;
            }
        }
    }

    switch (G_h01_94AE) {
    case 1:
    case 5:
        do {
            if (G_h01_94B4 != 0) {
                break;
            }
            if (jg_grid_tile_indices[G_h01_94BA][((G_h01_94C0 + 14) >> 5)] == 0 &&
                G_h01_94BC < 3) {
                if (jg_grid_tile_indices[G_h01_94BA - 1][((G_h01_94C0 + 14) >> 5)] != 0 &&
                    offset + 1 < jg_get_grid_row_right_boundary(0, G_h01_94BA - 1)) {
                    break;
                }
                if (jg_grid_tile_indices[G_h01_94BA + 1][((G_h01_94C0 + 14) >> 5)] != 0 &&
                    offset + 4 > jg_get_grid_row_left_boundary(0, G_h01_94BA + 1)) {
                    break;
                }
                G_h01_94AE = 2;
                jg_select_player_animation(2);
            }
        } while (0);
        break;
    }
}
