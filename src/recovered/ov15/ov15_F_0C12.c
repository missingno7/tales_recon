struct Point {
    char pad[30];
    int selected;
};

struct PointRef {
    struct Point *point;
    char reserved[8];
};

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
};

extern char G_h01_5E5E;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern long arc_file;
extern char game_day;
extern char current_location;
extern char matter_transmitter_unlocked;
extern char G_h01_46E5;
extern long total_money;
extern char G_h01_14E6;
extern char G_h01_43D6;
extern char G_h01_4478;
extern char G_h01_44AE;
extern char G_h01_440C;
extern char G_h01_44E4;
extern struct PointRef map_location_table[36];

extern long Open();
extern int request_disk();
extern int arc_read_index();
extern long load_arc_record();
extern long F_h00_0976();
extern int strlen();
extern int calculate_travel_days();
extern int clear_input_direction_and_fire_state();
extern int BltBitMap();
extern int draw_masked_sprite();
extern int draw_text();
extern int draw_decimal_value();
extern int draw_map_option_outline();
extern int fade_palette_to_black();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int poll_controller_and_keyboard_input();
extern int play_sound();
extern int Delay();
extern int free_text_block();
extern int Close();

recovered(n)
int n;
{
    struct PointRef *p;
    int i, w8, y, x, e;
    char f;
    int g;
    long q, s, t, u1, u2;
    char buf[81];
    long r1, r2, r3, r4;
    int st, k;

    st = 0;
    G_h01_5E5E = 1;
    i = 0;
    do {
        buf[i] = 0;
        i++;
    } while (i <= 80);
    t = arc_file;
    request_disk(1);
    arc_file = Open("DT1:loc.arc", 1005L);
    u1 = arc_file;
    arc_read_index(arc_file);
    p = &map_location_table[n];
    q = 0;
    q = load_arc_record(p->point->selected, q);
    r1 = ((struct Object *)q)->name;
    r1 = F_h00_0976(r1, buf);
    r1 = F_h00_0976(r1, buf);
    r3 = r1;
    request_disk(1);
    arc_file = Open("DT1:loot.arc", 1005L);
    arc_read_index(arc_file);
    u2 = arc_file;
    p = &map_location_table[n];
    s = 0;
    s = load_arc_record((*(struct Pair **)p->reserved)->first, s);
    r2 = ((struct Object *)s)->name;
    r2 = F_h00_0976(r2, buf);
    r4 = r2;
    w8 = strlen(p->point);
    w8 <<= 2;
    f = calculate_travel_days(current_location, n);
    clear_input_direction_and_fire_state();
    i = 0;
    do {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        draw_masked_sprite(&G_h01_4478);
        draw_masked_sprite(&G_h01_44AE);
        draw_masked_sprite(&G_h01_43D6);
        draw_masked_sprite(&G_h01_440C);
        if (matter_transmitter_unlocked)
            draw_masked_sprite(&G_h01_44E4);
        draw_text(160 - w8, 6, p->point, 7, 15);
        r1 = r3;
        r1 = F_h00_0976(r1, buf);
        y = 22;
        draw_text(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        draw_text(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        draw_text(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        draw_text(32, y, buf, 1, 0);
        if (n != 0) {
            r2 = r4;
            y += 16;
            draw_text(32, y, "TREASURE: ", 1, 0);
            r2 = F_h00_0976(r2, buf);
            if (strlen(buf) < 24)
                x = 112;
            else {
                x = 32;
                y += 8;
            }
            draw_text(x, y, buf, 1, 0);
            y += 16;
            draw_text(32, y, "TREASURE DESCRIPTION: ", 1, 0);
            r2 = F_h00_0976(r2, buf);
            y += 8;
            draw_text(32, y, buf, 1, 0);
            r2 = F_h00_0976(r2, buf);
            y += 8;
            draw_text(32, y, buf, 1, 0);
            y += 16;
            draw_text(32, y, "TREASURE VALUE: ", 1, 0);
            if (p->reserved[6] || p->reserved[7])
                draw_decimal_value(160, y, 0L, 1, 0, 0L);
            else
                draw_decimal_value(160, y, (long)(*(struct Pair **)p->reserved)->second, 1, 0, 0L);
        }
        y += 16;
        draw_text(32, y, "TRAVEL TIME:   day", 1, 0);
        if (f != 1)
            draw_text(176, y, "s", 1, 0);
        draw_decimal_value(136, y, (long)f, 1, 0, 0L);
        draw_decimal_value(176, 175, total_money, 1, 9, 1);
        if (game_day < 10)
            draw_decimal_value(18, 182, (long)game_day, 7, 1, 0);
        else
            draw_decimal_value(14, 182, (long)game_day, 7, 1, 0);
        draw_map_option_outline(&G_h01_43D6, 52, 27);
        if (i == 0) {
            fade_palette_to_black();
            switch_display_buffer();
            palette_fade_target = &G_h01_14E6;
            fade_palette_to_target(&G_h01_14E6);
        } else
            switch_display_buffer();
        i++;
    } while (i < 2);
    for (;;) {
        clear_input_direction_and_fire_state();
        BltBitMap(archive_image_bitmap, 0L, 0xa8L, active_screen_bitmap, 0L, 0xa8L, 0x140L, 0x20L, 0xc0L, 0xffL, 0L);
        draw_masked_sprite(&G_h01_4478);
        draw_masked_sprite(&G_h01_44AE);
        draw_masked_sprite(&G_h01_43D6);
        draw_masked_sprite(&G_h01_440C);
        if (matter_transmitter_unlocked)
            draw_masked_sprite(&G_h01_44E4);
        e = 0;
        e = poll_controller_and_keyboard_input();
        k = (e & 0x80) ? 1 : 0;
        if (k == 0) {
            e &= 0x3f;
            if (e == 3) {
                if (st == 2)
                    st = 0;
                else if (st == 1 && !matter_transmitter_unlocked)
                    st = 0;
                else
                    st++;
                play_sound(36);
                Delay(5L);
            } else if (e == 7) {
                if (st == 0) {
                    if (matter_transmitter_unlocked)
                        st = 2;
                    else
                        st = 1;
                } else
                    st--;
                play_sound(36);
                Delay(5L);
            }
        }
        switch (st) {
        case 0:
            draw_map_option_outline(&G_h01_43D6, 52, 27);
            e = 36;
            break;
        case 1:
            G_h01_46E5 = 0;
            draw_map_option_outline(&G_h01_440C, 32, 18);
            e = 1;
            break;
        case 2:
            G_h01_46E5 = 1;
            draw_map_option_outline(&G_h01_44E4, 37, 27);
            e = 1;
            break;
        }
        draw_decimal_value(176, 175, total_money, 1, 9, 1);
        if (game_day < 10)
            draw_decimal_value(18, 182, (long)game_day, 7, 1, 0);
        else
            draw_decimal_value(14, 182, (long)game_day, 7, 1, 0);
        switch_display_buffer();
        if (k != 0)
            break;
        Delay(1L);
    }
    free_text_block(s);
    Close(u2);
    free_text_block(q);
    Close(u1);
    arc_file = t;
    request_disk(1);
    arc_read_index(arc_file);
    clear_input_direction_and_fire_state();
    Delay(5L);
    return e;
}
