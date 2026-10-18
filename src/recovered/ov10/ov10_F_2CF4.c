/* Direct recovery candidate for ov10_F_2CF4 (v2: inverted tail dispatch). */
struct Flags { char pad; char bits; };
extern char G_h01_79AA;
extern char G_h01_726A;
extern int G_h01_7236;
extern int G_h01_7238;
extern int G_h01_723E;
extern int G_h01_7240;
extern char G_h01_7246;
extern short cave_player_sprite_record;
extern char G_h01_788A;
extern int G_h01_7962;
extern int G_h01_7964;
extern char G_h01_7972;
extern int G_h01_796A;
extern int G_h01_796C;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern long total_money;
extern short G_h01_0476;
extern short G_h01_04AA;
extern short G_h01_04DA;
extern short G_h01_050A;
extern short G_h01_053E;
extern short G_h01_0572;
extern short G_h01_059A;
extern short G_h01_05D6;
extern int request_disk();
extern int load_arc_record();
extern int switch_display_buffer();
extern int draw_masked_sprite();
extern int draw_text();
extern int free_bitmap_planes();
extern int play_sound();
extern int BltBitMap();
extern int draw_cave_actor_sprite();

recovered(start, count, pairs, kind, flags)
int start, count;
short *pairs;
int kind;
struct Flags *flags;
{
    int i, frame;
    char draw;

    if (G_h01_79AA)
        return;
    draw = 0;
    frame = start;
    request_disk(2);
    if (pairs == &G_h01_0476 || pairs == &G_h01_05D6) {
        draw = 1;
        load_arc_record(24, &G_h01_7962);
        G_h01_7962 = 0;
        G_h01_7964 = 0;
    } else if (pairs == &G_h01_04DA || pairs == &G_h01_0572) {
        draw = 1;
        load_arc_record(25, &G_h01_7962);
        G_h01_7962 = 240;
        G_h01_7964 = 0;
    }
    for (i = 0; i < count; i++, frame++) {
        if (frame > 3)
            frame = 0;
        G_h01_726A = frame;
        G_h01_7236 = pairs[2 * i];
        G_h01_7238 = pairs[2 * i + 1];
        draw_cave_actor_sprite(&G_h01_7236, kind, frame);
        if (pairs == &G_h01_0476 || pairs == &G_h01_04DA ||
            pairs == &G_h01_053E || pairs == &G_h01_059A) {
            if (!(flags->bits & 0x10) && !(flags->bits & 0x40) && i < 8)
                draw_masked_sprite(&G_h01_788A);
        }
        if (draw)
            draw_masked_sprite(&G_h01_7962);
        switch_display_buffer();
    }
    if (draw)
        free_bitmap_planes(&G_h01_7972, G_h01_796A, G_h01_796C);
    if (pairs != &G_h01_04AA && pairs != &G_h01_050A &&
        pairs != &G_h01_0572 && pairs != &G_h01_05D6) {
        if (!(flags->bits & 0x10) && !(flags->bits & 0x40)) {
            total_money += 50;
            play_sound(32);
        }
        for (i = 0; i < 4; i++) {
            BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
                0L, 0L, 320L, 200L, 192L, 255L, 0L);
            draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
            if (!(flags->bits & 0x10) && !(flags->bits & 0x40))
                draw_text(132, 128, "$50", 14, 0, 0);
            switch_display_buffer();
        }
    } else {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch_display_buffer();
    }
    free_bitmap_planes(&G_h01_7246, G_h01_723E, G_h01_7240);
}
