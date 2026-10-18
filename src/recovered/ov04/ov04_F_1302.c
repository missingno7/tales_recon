extern char input_fire_action_pending;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern long palette_fade_target;
extern long arc_file;
extern char G_h01_1426;
extern long G_h01_2A16;
extern char input_fire_action_capture_enabled;

extern int request_disk();
extern int arc_read_index();
extern int load_arc_record();
extern int switch_display_buffer();
extern int copy_palette_to_copper_lists();
extern int fade_palette_to_target();
extern int copy_palette_to_color_map();
extern int fade_palette_to_black();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int play_sound();
extern int BltBitMap();
extern int SetRast();
extern int expand_center_bitmap_to_screen();
extern int run_opening_animation_sequence();

recovered()
{
    unsigned char key;

    fade_palette_to_black();
    input_fire_action_pending = 0;
    input_fire_action_capture_enabled = 1;
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    request_disk(1);
    load_arc_record(2, archive_image_bitmap);
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
    switch_display_buffer();
    palette_fade_target = (long)&G_h01_1426;
    fade_palette_to_target(&G_h01_1426);
    SetRast(screen_rast_port, 0L);
    switch_display_buffer();
    SetRast(screen_rast_port, 0L);
    copy_palette_to_color_map(&G_h01_1426);
    copy_palette_to_copper_lists();
    expand_center_bitmap_to_screen();
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        play_sound(0);
        return;
    }

    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    clear_input_direction_and_fire_state();
    while (G_h01_2A16) {
        key = poll_controller_and_keyboard_input();
        if (key & 0x80) {
            play_sound(0);
            play_sound(0x24);
            fade_palette_to_black();
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

    run_opening_animation_sequence();
    input_fire_action_capture_enabled = 0;
    if (input_fire_action_pending)
        play_sound(0x24);
    fade_palette_to_black();
}

