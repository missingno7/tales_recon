extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern int G_h01_50E6;
extern int G_h01_50F0;
extern int G_h01_51BE;
extern int G_h01_51F4;
extern int G_h01_522A;
extern int G_h01_5234;
extern int G_h01_5260;
extern int G_h01_526A;
extern int G_h01_5296;
extern int G_h01_52A0;
extern int G_h01_52CC;
extern int G_h01_52D6;
extern int G_h01_5302;
extern int G_h01_530C;
extern char input_fire_action_pending;
extern int G_h01_50B0;
extern int G_h01_50B8;
extern int G_h01_50C0;
extern char G_h01_50E4;
extern int G_h01_50EE;
extern char G_h01_50F6;
extern char G_h01_511A;
extern int G_h01_5232;
extern char G_h01_523A;
extern int G_h01_529E;
extern char G_h01_52A6;
extern int G_h01_5268;
extern char G_h01_5270;
extern int G_h01_52D4;
extern char G_h01_52DC;
extern int G_h01_530A;
extern char G_h01_5312;
extern int invest_office_palette;
extern int G_h01_511C;
extern int G_h01_50B2;
extern int G_h01_50B4;
extern int G_h01_50E8;
extern int G_h01_50EA;
extern int G_h01_50F2;
extern int G_h01_50F8;
extern int G_h01_50BA;
extern int G_h01_50BC;
extern int G_h01_50C2;
extern int G_h01_522C;
extern int G_h01_522E;
extern int G_h01_5236;
extern int G_h01_523C;
extern int G_h01_5298;
extern int G_h01_529A;
extern int G_h01_52A2;
extern int G_h01_52A8;
extern int G_h01_5262;
extern int G_h01_526C;
extern int G_h01_52D8;
extern int G_h01_530E;
extern int G_h01_5272;
extern int G_h01_52CE;
extern int G_h01_52DE;
extern int G_h01_5304;
extern int G_h01_5306;
extern int G_h01_5314;

extern int request_disk();
extern int Delay();
extern int load_arc_record();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int fade_palette_to_black();
extern int draw_masked_sprite();
extern int free_bitmap_planes();
extern int poll_controller_and_keyboard_input();
extern int play_sound();
extern int BltBitMap();
extern int load_opening_animation_assets();
extern int F_h04_0B50();
extern int F_h04_0926();
extern int F_h04_0DBE();

recovered()
{
    int state;
    int index;
    char coordinates[10];
    coordinates[0] = -57;
    coordinates[1] = 29;
    coordinates[2] = -23;
    coordinates[3] = 25;
    coordinates[4] = 36;
    coordinates[5] = 30;
    coordinates[6] = 49;
    coordinates[7] = 29;
    coordinates[8] = 99;
    coordinates[9] = 29;

    load_opening_animation_assets();
    request_disk(1);
    load_arc_record(8, &G_h01_50E6);
    poll_controller_and_keyboard_input();
    G_h01_50E6 = 0xd8;
    G_h01_50E8 = 0x20;
    G_h01_511A = 0;
    draw_masked_sprite(&G_h01_50E6);
    fade_palette_to_black();
    poll_controller_and_keyboard_input();
    switch_display_buffer();

    palette_fade_target = (char *)&invest_office_palette;
    fade_palette_to_target((char *)&invest_office_palette);
    BltBitMap(
        archive_image_bitmap, 0L, 0L,
        active_screen_bitmap, 0L, 0L,
        0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    draw_masked_sprite(&G_h01_50E6);
    switch_display_buffer();

    load_arc_record(9, &G_h01_50B0);
    load_arc_record(11, &G_h01_522A);
    load_arc_record(12, &G_h01_5296);
    load_arc_record(13, &G_h01_5260);
    load_arc_record(14, &G_h01_52CC);
    load_arc_record(15, &G_h01_5302);
    poll_controller_and_keyboard_input();
    G_h01_522A = 0x7f;
    G_h01_522C = 0x22;
    G_h01_5296 = 0x97;
    G_h01_5298 = 0x22;
    G_h01_5302 = 0xba;
    G_h01_5304 = 0x67;
    play_sound(0x6e);

    state = 2;
    index = 0;
    goto frame_test;
frame_body:
        if (state == 4)
            state = 0;
        G_h01_50B0 = coordinates[index * 2];
        G_h01_50B2 = coordinates[index * 2 + 1];
        G_h01_50E4 = state;
        BltBitMap(
            archive_image_bitmap, 0L, 0x14L,
            active_screen_bitmap, 0L, 0x14L,
            0x140L, 0x82L, 0xc0L, 0xffL, 0L);
        if (index == 0)
            G_h01_511A = 1;
        draw_masked_sprite(&G_h01_50E6);
        draw_masked_sprite(&G_h01_50B0);
        poll_controller_and_keyboard_input();
        if (input_fire_action_pending) {
            free_bitmap_planes(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
            free_bitmap_planes(&G_h01_50C0, G_h01_50B8, G_h01_50BA);
            free_bitmap_planes(&G_h01_523A, G_h01_5232, G_h01_5234);
            free_bitmap_planes(&G_h01_52A6, G_h01_529E, G_h01_52A0);
            free_bitmap_planes(&G_h01_5270, G_h01_5268, G_h01_526A);
            free_bitmap_planes(&G_h01_52DC, G_h01_52D4, G_h01_52D6);
            free_bitmap_planes(&G_h01_5312, G_h01_530A, G_h01_530C);
            play_sound(0);
            return;
        }
        switch_display_buffer();
        Delay(10L);
        ++state;
        ++index;
frame_test:
    if (index < 5)
        goto frame_body;

    BltBitMap(
        archive_image_bitmap, 0L, 0x14L,
        active_screen_bitmap, 0L, 0x14L,
        0x140L, 0x82L, 0xc0L, 0xffL, 0L);
    draw_masked_sprite(&G_h01_522A);
    draw_masked_sprite(&G_h01_5302);
    draw_masked_sprite(&G_h01_5296);
    draw_masked_sprite(&G_h01_50E6);
    switch_display_buffer();
    free_bitmap_planes(&G_h01_50C0, G_h01_50B8, G_h01_50BA);
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        free_bitmap_planes(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        play_sound(0);
        return;
    }

    request_disk(1);
    load_arc_record(10, &G_h01_51BE);
    poll_controller_and_keyboard_input();
    F_h04_0B50(1, 5, 8);
    F_h04_0B50(6, 10, 8);
    load_arc_record(16, &G_h01_51F4);
    F_h04_0926(1, 3, 5);
    F_h04_0926(4, 6, 4);
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        F_h04_0DBE();
        free_bitmap_planes(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        play_sound(0);
        return;
    }

    F_h04_0B50(11, 14, 6);
    F_h04_0B50(15, 19, 6);
    F_h04_0B50(20, 23, 5);
    F_h04_0B50(24, 26, 5);
    poll_controller_and_keyboard_input();
    if (input_fire_action_pending) {
        F_h04_0DBE();
        free_bitmap_planes(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        play_sound(0);
        return;
    }

    F_h04_0926(7, 9, 5);
    F_h04_0926(10, 12, 5);
    F_h04_0926(13, 13, 1);
    F_h04_0926(13, 14, 1);
    F_h04_0926(13, 15, 1);
    F_h04_0DBE();
    free_bitmap_planes(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
}
