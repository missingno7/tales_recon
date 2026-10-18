extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern char G_h01_1826[1];
extern char G_h01_14A6[1];

extern int play_sound();
extern int load_arc_record();
extern int fade_palette_to_black();
extern int BltBitMap();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int F_h04_18A6();
extern int wait_for_fire_input();
extern int F_h00_4EC6();

recovered()
{
    int unused;

    play_sound(0);
    load_arc_record(1, archive_image_bitmap);
    fade_palette_to_black();
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    switch_display_buffer();
    palette_fade_target = G_h01_1826;
    fade_palette_to_target(G_h01_1826);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h04_18A6();
    load_arc_record(0, archive_image_bitmap);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    fade_palette_to_black();
    switch_display_buffer();
    palette_fade_target = G_h01_14A6;
    fade_palette_to_target(G_h01_14A6);
    if (wait_for_fire_input(40))
        play_sound(36);
    play_sound(0);
    F_h00_4EC6();
}
