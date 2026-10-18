/* Direct recovery candidate for ov04_F_0926. */
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int G_h01_0320;
extern int G_h01_0322;
extern long G_h01_0324;
extern int G_h01_50E6;
extern int G_h01_522A;
extern int G_h01_5296;
extern int G_h01_5302;
extern int G_h01_51F4;
extern int G_h01_51F6;
extern char G_h01_511A;
extern char input_fire_action_pending;
extern int BltBitMap();
extern int draw_masked_sprite();
extern int draw_text();
extern int switch_display_buffer();
extern int poll_controller_and_keyboard_input();
extern int play_sound();
extern int Delay();
extern unsigned int F_h00_463E();

recovered(first,last,rounds)
int first,last,rounds;
{
    int i;
    int round;

    G_h01_51F4 = 128;
    G_h01_51F6 = 0;
    for (round = 0; round < rounds; ++round) {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        G_h01_511A = 3;
        draw_masked_sprite(&G_h01_50E6);
        draw_masked_sprite(&G_h01_522A);
        draw_masked_sprite(&G_h01_5296);
        draw_masked_sprite(&G_h01_5302);
        draw_masked_sprite(&G_h01_51F4);
        for (i = first - 1; i < last; ++i)
            draw_text(*((int *)((char *)&G_h01_0320 + ((long)i << 3))),
                *((int *)((char *)&G_h01_0322 + ((long)i << 3))),
                *((long *)((char *)&G_h01_0324 + ((long)i << 3))), 0, 1);
        switch_display_buffer();
        poll_controller_and_keyboard_input();
        if (input_fire_action_pending) {
            play_sound(0);
            return;
        }
        Delay(5L);
        poll_controller_and_keyboard_input();
        if (input_fire_action_pending) {
            play_sound(0);
            return;
        }
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        G_h01_511A = 2;
        draw_masked_sprite(&G_h01_50E6);
        draw_masked_sprite(&G_h01_522A);
        draw_masked_sprite(&G_h01_5296);
        draw_masked_sprite(&G_h01_5302);
        draw_masked_sprite(&G_h01_51F4);
        for (i = first - 1; i < last; ++i)
            draw_text(*((int *)((char *)&G_h01_0320 + ((long)i << 3))),
                *((int *)((char *)&G_h01_0322 + ((long)i << 3))),
                *((long *)((char *)&G_h01_0324 + ((long)i << 3))), 0, 1);
        switch_display_buffer();
        poll_controller_and_keyboard_input();
        if (input_fire_action_pending) {
            play_sound(0);
            return;
        }
        Delay((long)(unsigned)(((F_h00_463E() & 2) + 1) * 5));
        poll_controller_and_keyboard_input();
        if (input_fire_action_pending) {
            play_sound(0);
            return;
        }
    }
    Delay(15L);
}
