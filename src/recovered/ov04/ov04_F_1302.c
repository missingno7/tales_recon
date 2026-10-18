extern char input_fire_action_pending;
extern long screen_rast_port;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46D6;
extern long arc_file;
extern char G_h01_1426;
extern long G_h01_2A16;
extern char input_fire_action_capture_enabled;

extern int request_disk();
extern int arc_read_index();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_30F0();
extern int F_h00_31AA();
extern int F_h00_3178();
extern int F_h00_330E();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int play_sound();
extern int BltBitMap();
extern int SetRast();
extern int F_h04_1822();
extern int F_h04_0E44();

recovered()
{
    unsigned char key;

    F_h00_330E();
    input_fire_action_pending = 0;
    input_fire_action_capture_enabled = 1;
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    request_disk(1);
    F_h00_291E(2, G_h01_46CE);
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    request_disk(1);
    F_h00_4D04(0);
    request_disk(1);
    arc_read_index(arc_file);
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    play_sound(1);
    F_h00_307C();
    G_h01_46D6 = (long)&G_h01_1426;
    F_h00_31AA(&G_h01_1426);
    SetRast(screen_rast_port, 0L);
    F_h00_307C();
    SetRast(screen_rast_port, 0L);
    F_h00_3178(&G_h01_1426);
    F_h00_30F0();
    F_h04_1822();
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    clear_input_direction_and_fire_state();
    while (G_h01_2A16) {
        key = poll_controller_and_keyboard_input();
        if (key & 0x80) {
            play_sound(0);
            play_sound(0x24);
            F_h00_330E();
            key = 0;
            input_fire_action_pending = 0;
            break;
        }
    }

    F_h00_4EC6();
    clear_input_direction_and_fire_state();
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    F_h04_0E44();
    input_fire_action_capture_enabled = 0;
    if (input_fire_action_pending)
        play_sound(0x24);
    F_h00_330E();
}

