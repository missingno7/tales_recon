extern char G_h01_06FE[624];

extern int clear_input_direction_and_fire_state();
extern int wait_for_fire_input();
extern int play_sound();
extern int draw_text();
extern int switch_display_buffer();

recovered()
{
    int i;
    int scratch;

    clear_input_direction_and_fire_state();
    if (wait_for_fire_input(20)) {
        return play_sound(36);
    }
    draw_text(0, 192, "                                        ", 1, 3);
    switch_display_buffer();
    draw_text(0, 192, "                                        ", 1, 3);
    i = 0;
    do {
        draw_text(64, 192, G_h01_06FE + (long)i * 26, 1, 3);
        switch_display_buffer();
        if (wait_for_fire_input(20)) {
            return play_sound(36);
        }
        ++i;
    } while (i < 24);
    draw_text(0, 192, "                                        ", 1, 3);
    switch_display_buffer();
    draw_text(0, 192, "                                        ", 1, 3);
}