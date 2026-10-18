extern char palette_cycle_countdown_step;
extern long palette_cycle_callback_index;
extern long G_h01_2A16;
extern long screen_rast_port;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_1526;
extern char G_h01_0668;
extern char G_h01_068B;
extern char G_h01_06A6;
extern char G_h01_06BF;
extern char G_h01_06DB;
extern int F_h00_330E();
extern int SetRast();
extern int F_h00_307C();
extern int request_disk();
extern long F_h00_291E();
extern int play_sound();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_35DC();
extern int F_h00_31AA();
extern int wait_for_fire_input();
extern int BltBitMap();
extern int show_random_clue();

recovered(arg)
int arg;
{
    palette_cycle_countdown_step = 0;
    palette_cycle_callback_index = 0;
    F_h00_330E();
    SetRast(screen_rast_port, 0L);
    F_h00_307C();
    SetRast(screen_rast_port, 0L);
    request_disk(1);
    F_h00_291E(0x1f, G_h01_46CE);
    play_sound(0x21);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(0x19);
    play_sound(0);
    F_h00_330E();
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_35DC(0x18, 0xc, &G_h01_0668, 0, 0);
    switch (arg) {
    case 1:
        F_h00_35DC(0x18, 0x18, &G_h01_06A6, 0, 0);
        show_random_clue(1);
        break;
    case 2:
        F_h00_35DC(0x18, 0x18, &G_h01_068B, 0, 0);
        show_random_clue(0);
        break;
    case 4:
        F_h00_35DC(0x18, 0x18, &G_h01_06DB, 0, 0);
        show_random_clue(3);
        break;
    case 8:
        F_h00_35DC(0x18, 0x18, &G_h01_06BF, 0, 0);
        show_random_clue(2);
        break;
    }
    F_h00_307C();
    G_h01_46D6 = &G_h01_1526;
    F_h00_31AA(&G_h01_1526);
    palette_cycle_callback_index = 4;
    palette_cycle_countdown_step = 15;
    play_sound(0x71);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    wait_for_fire_input(0x1e);
}
