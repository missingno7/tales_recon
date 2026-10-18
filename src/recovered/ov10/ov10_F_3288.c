extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern short G_h01_752A;
extern short G_h01_752C;
extern short G_h01_7532;
extern short G_h01_7534;
extern short G_h01_753A;
extern char G_h01_755E;
extern short cave_player_sprite_record;
extern char G_h01_730C;
extern short G_h01_72D8;
extern char G_h01_74F4[1];
extern char G_h01_7452[1];
extern char G_h01_741C[1];

extern void draw_cave_actor_sprite();
extern int BltBitMap();
extern int switch_display_buffer();
extern int draw_masked_sprite();
extern int request_disk();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int load_arc_record();
extern int Delay();
extern int play_sound();
extern int SetRast();
extern int fade_palette_to_black();
extern int free_bitmap_planes();

void recovered()
{
    int i;

    for (i = 0; i < 4; i++) {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
        switch_display_buffer();
    }
    for (i = 0; i < 6; i++) {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        draw_masked_sprite(&cave_player_sprite_record);
        if ((i & 1) && i < 4)
            G_h01_730C = 3;
        else if (i < 4)
            G_h01_730C = 4;
        else
            G_h01_730C = 4;
        draw_masked_sprite(&G_h01_72D8);
        draw_masked_sprite(G_h01_74F4);
        draw_masked_sprite(G_h01_7452);
        draw_masked_sprite(G_h01_741C);
        switch_display_buffer();
    }
    request_disk(2);
    F_h00_4EC6();
    F_h00_4D04(7);
    load_arc_record(0x1b, &G_h01_752A);
    G_h01_752A = 0x62;
    G_h01_752C = 0x37;
    G_h01_755E = 4;
    draw_masked_sprite(&G_h01_752A);
    switch_display_buffer();
    Delay(0x32L);
    G_h01_755E = 1;
    draw_masked_sprite(&G_h01_752A);
    switch_display_buffer();
    Delay(5L);
    for (i = 0; i < 6; i++) {
        if (i == 4) {
            play_sound(0x4b);
        } else {
            SetRast(screen_rast_port, 0L);
            G_h01_755E = i;
            draw_masked_sprite(&G_h01_752A);
            switch_display_buffer();
            if (i == 1) {
                Delay(5L);
            } else {
                if (i & 1)
                    Delay(0x32L);
                else
                    Delay(0x19L);
                if (i > 1 && i < 6) {
                    G_h01_755E = 1;
                    draw_masked_sprite(&G_h01_752A);
                    switch_display_buffer();
                    Delay(3L);
                }
            }
        }
    }
    G_h01_755E = 0;
    draw_masked_sprite(&G_h01_752A);
    switch_display_buffer();
    Delay(0x96L);
    fade_palette_to_black();
    F_h00_4EC6();
    free_bitmap_planes(&G_h01_753A, G_h01_7532, G_h01_7534);
}
