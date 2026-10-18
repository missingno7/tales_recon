extern char G_h01_1766[1];
extern long screen_rast_port;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char difficulty_level;

extern int F_h00_0640();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
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
    F_h00_307C();
    SetRast(screen_rast_port, 0L);
    difficulty_level = 0;
    F_h00_0640(9);
    F_h00_35DC(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
    F_h00_35DC(176, 80, "Easy Money", 24, 0);
    F_h00_35DC(176, 100, "Standard Wages", 1, 0);
    F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    clear_input_direction_and_fire_state();
    while (!(buttons & 0x80)) {
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 176L, 200L, 192L, 255L, 0L);
        F_h00_35DC(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
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
            F_h00_35DC(168, 80, ">Easy Money", 24, 0);
            F_h00_35DC(176, 100, "Standard Wages", 1, 0);
            F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
            break;
        case 2:
            F_h00_35DC(176, 80, "Easy Money", 1, 0);
            F_h00_35DC(176, 100, "Standard Wages", 1, 0);
            F_h00_35DC(168, 120, ">Hard Earned Cash", 24, 0);
            break;
        default:
            F_h00_35DC(176, 80, "Easy Money", 1, 0);
            F_h00_35DC(168, 100, ">Standard Wages", 24, 0);
            F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
            break;
        }
        F_h00_307C();
        Delay((long)5);
        buttons = poll_controller_and_keyboard_input();
    }

    play_sound(36);
    seed_random();
    SetRast(screen_rast_port, 0L);
    return F_h00_330E();
}
