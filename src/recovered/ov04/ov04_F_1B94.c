extern long screen_rast_port;
extern long arc_file;
extern char G_h01_1766[1];
extern char *G_h01_46D6;
extern int F_h00_330E();
extern int SetRast();
extern int F_h00_4EC6();
extern int request_disk();
extern int F_h00_4D04();
extern int arc_read_index();
extern int play_sound();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int clear_input_direction_and_fire_state();
extern char poll_controller_and_keyboard_input();
extern int F_h00_35DC();
extern int Delay();

recovered()
{
    int selection;
    unsigned char buttons;

    selection = 0;
    buttons = 0;
    F_h00_330E();
    SetRast(screen_rast_port, 0L);
    F_h00_4EC6();
    request_disk(1);
    F_h00_4D04(0);
    request_disk(1);
    arc_read_index(arc_file);
    play_sound(1);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    clear_input_direction_and_fire_state();
    buttons = poll_controller_and_keyboard_input();
    while (!(buttons & 128)) {
        if ((buttons & 1) || (buttons & 5))
            selection ^= 1;
        SetRast(screen_rast_port, 0L);
        F_h00_35DC(112, 70, "PLAY AGAIN?", 1, 0);
        if (!selection) {
            F_h00_35DC(136, 100, ">YES", 24, 0);
            F_h00_35DC(144, 120, "NO", 1, 0);
        } else {
            F_h00_35DC(144, 100, "YES", 1, 0);
            F_h00_35DC(136, 120, ">NO", 24, 0);
        }
        F_h00_307C();
        if ((buttons & 1) || (buttons & 5)) {
            clear_input_direction_and_fire_state();
            Delay((long)10);
        }
        buttons = poll_controller_and_keyboard_input();
    }
    SetRast(screen_rast_port, 0L);
    F_h00_307C();
    play_sound(0);
    F_h00_4EC6();
    return selection;
}
