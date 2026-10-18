/* Structured candidate for resident_F_0FDE: name-independent control flow,
   mechanical callee and global names, no original code bytes. */
extern int strcpy();
extern int F_h00_3008();
extern int F_h00_3A6E();
extern int F_h00_330E();
extern int F_h00_307C();
extern int BltBitMap();
extern int F_h00_35DC();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int F_h00_3178();
extern int F_h00_30F0();
extern int Delay();
extern int clear_input_direction_and_fire_state();
extern int F_h00_3AE4();
extern long Open();
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern int G_h01_A7A4;
extern int G_h01_A7A6;
extern char G_h01_A7A9;
extern long G_h01_A7AC;
extern long G_h01_A7D2;
extern int G_h01_19E6;
extern long G_h01_46D2;
extern long screen_rast_port;
extern char *G_h01_46D6;
extern char *G_h01_5370;

recovered(a)
int a;
{
    char buf[5];

    if (a == 1)
        strcpy(buf, "DT1");
    else
        strcpy(buf, "DT2");
    if (F_h00_3008(buf) == 0) {
        palette_cycle_countdown_step = 0;
        palette_cycle_callback_index = 0;
        G_h01_A7A4 = 16;
        G_h01_A7A6 = 24;
        G_h01_A7A9 = 5;
        G_h01_A7AC = 0;
        F_h00_3A6E(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        F_h00_330E();
        F_h00_307C();
        BltBitMap(G_h01_46D2, 100L, 80L, &G_h01_A7A4, 0L, 0L, 120L, 24L, 192L, 255L, 0L);
        F_h00_35DC(100, 80, "               ", 15, 1);
        if (a == 1)
            F_h00_35DC(100, 88, " INSERT DISK 1 ", 15, 1);
        else
            F_h00_35DC(100, 88, " INSERT DISK 2 ", 15, 1);
        F_h00_35DC(100, 96, "               ", 15, 1);
        *G_h01_5370 = 15;
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 100L, 80L);
        Draw(screen_rast_port, 219L, 80L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 100L, 80L);
        Draw(screen_rast_port, 100L, 103L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 100L, 103L);
        Draw(screen_rast_port, 219L, 103L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 219L, 80L);
        Draw(screen_rast_port, 219L, 103L);
        F_h00_3178(G_h01_46D6);
        F_h00_30F0();
        F_h00_307C();
        Delay(25L);
        clear_input_direction_and_fire_state();
        while (F_h00_3008(buf) == 0)
            Delay(20L);
        F_h00_307C();
        BltBitMap(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 100L, 80L, 120L, 24L, 192L, 255L, 0L);
        F_h00_307C();
        F_h00_3AE4(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        Delay(5L);
        clear_input_direction_and_fire_state();
    }
    if (G_h01_19E6 == 0 && a == 2) {
        G_h01_A7D2 = Open("dt2:dt2.as", 1005L);
        G_h01_19E6 = 1;
    }
}
