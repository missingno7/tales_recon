extern char palette_cycle_countdown_step;
extern long palette_cycle_callback_index;
extern long G_h01_2A16;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern char G_h01_1526;
extern char guide_chapter_intro_text;
extern char mountain_climbing_guide_intro_text;
extern char jungle_survival_guide_intro_text;
extern char nature_photography_guide_intro_text;
extern char cave_exploring_guide_intro_text;
extern int fade_palette_to_black();
extern int SetRast();
extern int switch_display_buffer();
extern int request_disk();
extern long load_arc_record();
extern int play_sound();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int draw_text();
extern int fade_palette_to_target();
extern int wait_for_fire_input();
extern int BltBitMap();
extern int show_random_clue();

recovered(arg)
int arg;
{
    palette_cycle_countdown_step = 0;
    palette_cycle_callback_index = 0;
    fade_palette_to_black();
    SetRast(screen_rast_port, 0L);
    switch_display_buffer();
    SetRast(screen_rast_port, 0L);
    request_disk(1);
    load_arc_record(0x1f, archive_image_bitmap);
    play_sound(0x21);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(0x19);
    play_sound(0);
    fade_palette_to_black();
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    draw_text(0x18, 0xc, &guide_chapter_intro_text, 0, 0);
    switch (arg) {
    case 1:
        draw_text(0x18, 0x18, &jungle_survival_guide_intro_text, 0, 0);
        show_random_clue(1);
        break;
    case 2:
        draw_text(0x18, 0x18, &mountain_climbing_guide_intro_text, 0, 0);
        show_random_clue(0);
        break;
    case 4:
        draw_text(0x18, 0x18, &cave_exploring_guide_intro_text, 0, 0);
        show_random_clue(3);
        break;
    case 8:
        draw_text(0x18, 0x18, &nature_photography_guide_intro_text, 0, 0);
        show_random_clue(2);
        break;
    }
    switch_display_buffer();
    palette_fade_target = &G_h01_1526;
    fade_palette_to_target(&G_h01_1526);
    palette_cycle_callback_index = 4;
    palette_cycle_countdown_step = 15;
    play_sound(0x71);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    wait_for_fire_input(0x1e);
}
