/* resident_F_0A44: "Do you wish to quit the game?" Y/N box; on Y releases the screen and calls the ov04 exit path. l1 is stored but never read, as in the original. */
extern int F_h00_3A6E();
extern int F_h00_307C();
extern int BltBitMap();
extern int F_h00_35DC();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int poll_controller_and_keyboard_input();
extern int F_h00_330E();
extern int F_h00_3AE4();
extern int request_disk();
extern int arc_read_index();
extern int clear_input_direction_and_fire_state();
extern int F_h04_1D32();
extern int shutdown_av();
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern unsigned int G_h01_A7A4;
extern unsigned int G_h01_A7A6;
extern char G_h01_A7A9;
extern char G_h01_A7CC;
extern long G_h01_A7AC;
extern long screen_rast_port;
extern long G_h01_46D2;
extern long arc_file;
extern long main_arc_file_handle;
extern char *G_h01_5370;

recovered()
{
    char key;
    int quit;
    long l1;

    quit = 0;
    l1 = 0;
    G_h01_A7CC = 1;
    G_h01_A7A4 = 32;
    G_h01_A7A6 = 32;
    G_h01_A7A9 = 5;
    palette_cycle_countdown_step = 0;
    palette_cycle_callback_index = 0;
    G_h01_A7AC = 0;
    F_h00_3A6E(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    F_h00_307C();
    BltBitMap(G_h01_46D2, 32L, 80L, &G_h01_A7A4, 0L, 0L, 248L, 32L, 192L, 255L, 0L);
    F_h00_35DC(40, 88, "Do you wish to quit the game?", 15, 1);
    F_h00_35DC(40, 96, "     Type 'Y' or 'N'.        ", 15, 1);
    *G_h01_5370 = 15;
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 39L, 87L);
    Draw(screen_rast_port, 272L, 87L);
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 39L, 104L);
    Draw(screen_rast_port, 272L, 104L);
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 39L, 87L);
    Draw(screen_rast_port, 39L, 104L);
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 272L, 87L);
    Draw(screen_rast_port, 272L, 104L);
    F_h00_307C();
    key = poll_controller_and_keyboard_input();
    for (;;) {
        if (key == 'y' || key == 'Y') {
            quit = 1;
            break;
        }
        if (key == 'n' || key == 'N') {
            break;
        }
        key = poll_controller_and_keyboard_input();
    }
    if (quit) {
        F_h00_330E();
        F_h00_3AE4(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        request_disk(1);
        arc_file = main_arc_file_handle;
        arc_read_index(arc_file);
        F_h04_1D32();
        shutdown_av("");
    } else {
        BltBitMap(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 32L, 80L, 248L, 32L, 192L, 255L, 0L);
        F_h00_307C();
        BltBitMap(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 32L, 80L, 248L, 32L, 192L, 255L, 0L);
        F_h00_307C();
        F_h00_3AE4(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    }
    G_h01_A7CC = 0;
    clear_input_direction_and_fire_state();
}
