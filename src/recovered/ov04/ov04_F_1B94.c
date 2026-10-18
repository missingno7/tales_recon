extern long screen_rast_port;
extern long arc_file;
extern char invest_trade_confirmation_palette[1];
extern char *palette_fade_target;
extern int fade_palette_to_black();
extern int SetRast();
extern int F_h00_4EC6();
extern int request_disk();
extern int F_h00_4D04();
extern int arc_read_index();
extern int play_sound();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int clear_input_direction_and_fire_state();
extern char poll_controller_and_keyboard_input();
extern int draw_text();
extern int Delay();

recovered()
{
    int selection;
    unsigned char buttons;

    selection = 0;
    buttons = 0;
    fade_palette_to_black();
    SetRast(screen_rast_port, 0L);
    F_h00_4EC6();
    request_disk(1);
    F_h00_4D04(0);
    request_disk(1);
    arc_read_index(arc_file);
    play_sound(1);
    switch_display_buffer();
    palette_fade_target = invest_trade_confirmation_palette;
    fade_palette_to_target(invest_trade_confirmation_palette);
    clear_input_direction_and_fire_state();
    buttons = poll_controller_and_keyboard_input();
    while (!(buttons & 128)) {
        if ((buttons & 1) || (buttons & 5))
            selection ^= 1;
        SetRast(screen_rast_port, 0L);
        draw_text(112, 70, "PLAY AGAIN?", 1, 0);
        if (!selection) {
            draw_text(136, 100, ">YES", 24, 0);
            draw_text(144, 120, "NO", 1, 0);
        } else {
            draw_text(144, 100, "YES", 1, 0);
            draw_text(136, 120, ">NO", 24, 0);
        }
        switch_display_buffer();
        if ((buttons & 1) || (buttons & 5)) {
            clear_input_direction_and_fire_state();
            Delay((long)10);
        }
        buttons = poll_controller_and_keyboard_input();
    }
    SetRast(screen_rast_port, 0L);
    switch_display_buffer();
    play_sound(0);
    F_h00_4EC6();
    return selection;
}
