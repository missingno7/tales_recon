/* Structured candidate for resident_F_0FDE: name-independent control flow,
   mechanical callee and global names, no original code bytes. */
extern int strcpy();
extern int F_h00_3008();
extern int allocate_bitmap_planes();
extern int fade_palette_to_black();
extern int switch_display_buffer();
extern int BltBitMap();
extern int draw_text();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int copy_palette_to_color_map();
extern int copy_palette_to_copper_lists();
extern int Delay();
extern int clear_input_direction_and_fire_state();
extern int free_bitmap_planes();
extern long Open();
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern int G_h01_A7A4;
extern int G_h01_A7A6;
extern char G_h01_A7A9;
extern long G_h01_A7AC;
extern long G_h01_A7D2;
extern int G_h01_19E6;
extern long active_screen_bitmap;
extern long screen_rast_port;
extern char *palette_fade_target;
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
        allocate_bitmap_planes(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        fade_palette_to_black();
        switch_display_buffer();
        BltBitMap(active_screen_bitmap, 100L, 80L, &G_h01_A7A4, 0L, 0L, 120L, 24L, 192L, 255L, 0L);
        draw_text(100, 80, "               ", 15, 1);
        if (a == 1)
            draw_text(100, 88, " INSERT DISK 1 ", 15, 1);
        else
            draw_text(100, 88, " INSERT DISK 2 ", 15, 1);
        draw_text(100, 96, "               ", 15, 1);
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
        copy_palette_to_color_map(palette_fade_target);
        copy_palette_to_copper_lists();
        switch_display_buffer();
        Delay(25L);
        clear_input_direction_and_fire_state();
        while (F_h00_3008(buf) == 0)
            Delay(20L);
        switch_display_buffer();
        BltBitMap(&G_h01_A7A4, 0L, 0L, active_screen_bitmap, 100L, 80L, 120L, 24L, 192L, 255L, 0L);
        switch_display_buffer();
        free_bitmap_planes(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        Delay(5L);
        clear_input_direction_and_fire_state();
    }
    if (G_h01_19E6 == 0 && a == 2) {
        G_h01_A7D2 = Open("dt2:dt2.as", 1005L);
        G_h01_19E6 = 1;
    }
}
