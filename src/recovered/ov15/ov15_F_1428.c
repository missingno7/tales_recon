struct Pair {
    int first;
    int second;
};

extern char G_h01_5E5E;
extern char G_h01_451B;
extern int map_input_action;
extern int map_direction_hold_count;
extern int map_direction_restart_pending;
extern int map_cursor_horizontal_step;
extern int map_cursor_vertical_step;
extern struct Pair G_h01_A768;

extern int poll_controller_and_keyboard_input();
extern int F_h00_34E0();
extern int clear_input_direction_and_fire_state();

int recovered(px, py)
int *px, *py;
{
    G_h01_5E5E = 0;
    map_input_action = poll_controller_and_keyboard_input();
    if (map_input_action & 0x80)
        return 1;
    switch (map_input_action & 0x3f) {
    case 1:
        (*py)--;
        map_cursor_vertical_step = -1;
        map_cursor_horizontal_step = 0;
        break;
    case 2:
        (*py)--;
        *px += 2;
        map_cursor_vertical_step = -1;
        map_cursor_horizontal_step = 1;
        break;
    case 3:
        (*px)++;
        map_cursor_horizontal_step = 1;
        map_cursor_vertical_step = 0;
        break;
    case 4:
        (*py)++;
        *px += 2;
        map_cursor_vertical_step = 1;
        map_cursor_horizontal_step = 1;
        break;
    case 5:
        (*py)++;
        map_cursor_vertical_step = 1;
        map_cursor_horizontal_step = 0;
        break;
    case 6:
        (*py)++;
        *px -= 2;
        map_cursor_vertical_step = 1;
        map_cursor_horizontal_step = -1;
        break;
    case 7:
        (*px)--;
        map_cursor_horizontal_step = -1;
        map_cursor_vertical_step = 0;
        break;
    case 8:
        (*py)--;
        *px -= 2;
        map_cursor_horizontal_step = -1;
        map_cursor_vertical_step = -1;
        break;
    case 0:
    default:
        map_direction_hold_count = 0;
        map_input_action = 0;
        map_cursor_vertical_step = 0;
        map_cursor_horizontal_step = 0;
        map_direction_restart_pending = 0;
        break;
    }
    if ((map_input_action & 0x3f) != 0 && map_direction_hold_count < 0x100) {
        if (map_direction_hold_count != 0) {
            switch (map_input_action & 0x3f) {
            case 2:
            case 4:
                map_cursor_horizontal_step++;
                break;
            case 6:
            case 8:
                map_cursor_horizontal_step--;
                break;
            }
        }
        map_direction_hold_count++;
    }
    if (map_direction_hold_count == 0) {
        map_direction_hold_count = 1;
        map_direction_restart_pending = 1;
    }
    *px = *px + (map_direction_hold_count - 1) * map_cursor_horizontal_step;
    *py = *py + (map_direction_hold_count - 1) * map_cursor_vertical_step;
    if (map_direction_restart_pending) {
        map_direction_hold_count = 0;
        map_direction_restart_pending = 0;
    }
    if (*px < 0x20)
        *px = 0x20;
    else if (*px > 0x11d)
        *px = 0x11d;
    if (*py < 0x1c)
        *py = 0x1c;
    else if (*py > 0x97)
        *py = 0x97;
    G_h01_A768.first = *px - 8;
    G_h01_A768.second = *py - 8;
    F_h00_34E0(&G_h01_A768);
    clear_input_direction_and_fire_state();
    G_h01_5E5E = 1;
    return 0;
}
