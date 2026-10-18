extern char invest_trade_confirmation_palette[1];
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern char difficulty_level;

extern int load_scene_graphic();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int fade_palette_to_black();
extern int draw_text();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int seed_random();
extern int play_sound();
extern int BltBitMap();
extern int SetRast();
extern int Delay();

recovered()
{
    int unused;
    unsigned char buttons;

    unused = 0;
    buttons = 0;
    SetRast(screen_rast_port, 0L);
    switch_display_buffer();
    SetRast(screen_rast_port, 0L);
    difficulty_level = 0;
    load_scene_graphic(9);
    draw_text(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
    draw_text(176, 80, "Easy Money", 24, 0);
    draw_text(176, 100, "Standard Wages", 1, 0);
    draw_text(176, 120, "Hard Earned Cash", 1, 0);
    switch_display_buffer();
    palette_fade_target = invest_trade_confirmation_palette;
    fade_palette_to_target(invest_trade_confirmation_palette);
    clear_input_direction_and_fire_state();
    while (!(buttons & 0x80)) {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 176L, 200L, 192L, 255L, 0L);
        draw_text(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
        buttons &= 0x3f;
        if (buttons & 0x40)
            return 0x25;
        if (buttons == 1) {
            if (difficulty_level == 0)
                difficulty_level = 2;
            else
                --difficulty_level;
            play_sound(36);
        } else if (buttons == 5) {
            if (difficulty_level == 2)
                difficulty_level = 0;
            else
                ++difficulty_level;
            play_sound(36);
        }

        switch (difficulty_level) {
        case 0:
            draw_text(168, 80, ">Easy Money", 24, 0);
            draw_text(176, 100, "Standard Wages", 1, 0);
            draw_text(176, 120, "Hard Earned Cash", 1, 0);
            break;
        case 2:
            draw_text(176, 80, "Easy Money", 1, 0);
            draw_text(176, 100, "Standard Wages", 1, 0);
            draw_text(168, 120, ">Hard Earned Cash", 24, 0);
            break;
        default:
            draw_text(176, 80, "Easy Money", 1, 0);
            draw_text(168, 100, ">Standard Wages", 24, 0);
            draw_text(176, 120, "Hard Earned Cash", 1, 0);
            break;
        }
        switch_display_buffer();
        Delay((long)5);
        buttons = poll_controller_and_keyboard_input();
    }

    play_sound(36);
    seed_random();
    SetRast(screen_rast_port, 0L);
    return fade_palette_to_black();
}
