/* resident_F_0A44: "Do you wish to quit the game?" Y/N box; on Y releases the screen and calls the ov04 exit path. l1 is stored but never read, as in the original. */
extern int allocate_bitmap_planes();
extern int switch_display_buffer();
extern int BltBitMap();
extern int draw_text();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int poll_controller_and_keyboard_input();
extern int fade_palette_to_black();
extern int free_bitmap_planes();
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
extern long active_screen_bitmap;
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
    allocate_bitmap_planes(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    switch_display_buffer();
    BltBitMap(active_screen_bitmap, 32L, 80L, &G_h01_A7A4, 0L, 0L, 248L, 32L, 192L, 255L, 0L);
    draw_text(40, 88, "Do you wish to quit the game?", 15, 1);
    draw_text(40, 96, "     Type 'Y' or 'N'.        ", 15, 1);
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
    switch_display_buffer();
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
        fade_palette_to_black();
        free_bitmap_planes(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        request_disk(1);
        arc_file = main_arc_file_handle;
        arc_read_index(arc_file);
        F_h04_1D32();
        shutdown_av("");
    } else {
        BltBitMap(&G_h01_A7A4, 0L, 0L, active_screen_bitmap, 32L, 80L, 248L, 32L, 192L, 255L, 0L);
        switch_display_buffer();
        BltBitMap(&G_h01_A7A4, 0L, 0L, active_screen_bitmap, 32L, 80L, 248L, 32L, 192L, 255L, 0L);
        switch_display_buffer();
        free_bitmap_planes(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    }
    G_h01_A7CC = 0;
    clear_input_direction_and_fire_state();
}
