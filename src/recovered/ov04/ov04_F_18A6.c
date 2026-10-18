extern char G_h01_06FE[624];

extern int clear_input_direction_and_fire_state();
extern int wait_for_fire_input();
extern int play_sound();
extern int F_h00_35DC();
extern int F_h00_307C();

recovered()
{
    int i;
    int scratch;

    clear_input_direction_and_fire_state();
    if (wait_for_fire_input(20)) {
        return play_sound(36);
    }
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    i = 0;
    do {
        F_h00_35DC(64, 192, G_h01_06FE + (long)i * 26, 1, 3);
        F_h00_307C();
        if (wait_for_fire_input(20)) {
            return play_sound(36);
        }
        ++i;
    } while (i < 24);
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
}