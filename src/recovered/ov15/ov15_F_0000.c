/* Candidate h3 for ov15_F_0000: h3 with k stored and reloaded before the shift (one-factor change). */
struct Point {
    char pad[32];
    int x;
    int y;
};

struct PointRef {
    struct Point *point;
    char reserved[8];
};

struct Pair {
    int first;
    int second;
};

extern long G_h01_2A16;
extern char G_h01_14E6;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern long arc_file;
extern long main_arc_file_handle;
extern char game_day;
extern char current_location;
extern char matter_transmitter_unlocked;
extern long total_money;
extern char bombastium_location_index;
extern char *G_h01_5370;
extern struct PointRef map_location_table[36];
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44AE;
extern int G_h01_44B0;
extern int G_h01_4478;
extern int G_h01_447A;
extern int G_h01_43D6;
extern int G_h01_43D8;
extern int G_h01_440C;
extern int G_h01_440E;
extern int G_h01_44E4;
extern int G_h01_44E6;
extern int G_h01_4480;
extern int G_h01_4482;
extern int G_h01_4488;
extern int G_h01_44B6;
extern int G_h01_44B8;
extern int G_h01_44BE;
extern int G_h01_444A;
extern int G_h01_444C;
extern int G_h01_4452;
extern int G_h01_43DE;
extern int G_h01_43E0;
extern int G_h01_43E6;
extern int G_h01_4414;
extern int G_h01_4416;
extern int G_h01_441C;
extern int G_h01_A770;
extern int G_h01_A772;
extern int G_h01_A778;
extern int G_h01_44EC;
extern int G_h01_44EE;
extern int G_h01_44F4;

extern int clear_input_direction_and_fire_state();
extern int play_sound();
extern int SetRast();
extern int F_h00_4EC6();
extern int request_disk();
extern int F_h00_4D04();
extern int arc_read_index();
extern long load_arc_record();
extern int BltBitMap();
extern int draw_text();
extern int draw_masked_sprite();
extern int draw_decimal_value();
extern int security_decode_challenge();
extern int FreeSeg();
extern int fade_palette_to_black();
extern int F_h04_1D32();
extern int shutdown_av();
extern int Delay();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int map_move_cursor_from_input();
extern int map_show_location_details();
extern int draw_map_cursor_marker();
extern long squared_distance();
extern int strlen();
extern int free_bitmap_planes();
extern int free_bitmap();

recovered(p1, flag)
int p1;
char *flag;
{
    struct PointRef *ent;
    int x, y, xs, ys, i, k;
    long t1, t2;
    int r;
    long h;

    h = 0;
    ent = 0;
    clear_input_direction_and_fire_state();
    play_sound(0x21);
    while (G_h01_2A16 != 0)
        ;
    play_sound(0);
    SetRast(screen_rast_port, 0L);
    F_h00_4EC6();
    request_disk(1);
    F_h00_4D04(1);
    request_disk(1);
    arc_read_index(arc_file);
    if (p1 == 1)
        load_arc_record(0x14, archive_image_bitmap);
    else
        load_arc_record(0x15, archive_image_bitmap);
    h = load_arc_record(0x16, h);
    load_arc_record(0x18, &G_h01_4442);
    G_h01_4442 = 0x16;
    G_h01_4444 = 0x73;
    load_arc_record(0x17, &G_h01_44AE);
    G_h01_44AE = 0x28;
    G_h01_44B0 = 0xac;
    load_arc_record(0x19, &G_h01_4478);
    G_h01_4478 = 8;
    G_h01_447A = 0xaf;
    load_arc_record(0x1a, &G_h01_43D6);
    G_h01_43D6 = 0xc0;
    G_h01_43D8 = 0xaa;
    load_arc_record(0x1b, &G_h01_440C);
    G_h01_440C = 0xf8;
    G_h01_440E = 0xae;
    load_arc_record(0x1c, &G_h01_A768);
    if (matter_transmitter_unlocked && p1) {
        load_arc_record(0x1d, &G_h01_44E4);
        G_h01_44E4 = 0x119;
        G_h01_44E6 = 0xaa;
    }
    if (current_location == 0x23) {
        x = 0x2e;
        xs = 0x2e;
        y = 0x8b;
        ys = 0x8b;
    } else {
        x = map_location_table[current_location].point->x;
        xs = x;
        y = map_location_table[current_location].point->y;
        ys = y;
    }
    if (*flag) {
        *flag = 0;
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        draw_text(0x64, 6, "Security System", 1, 0xf);
        draw_masked_sprite(&G_h01_4478);
        draw_masked_sprite(&G_h01_44AE);
        draw_decimal_value(0xb0, 0xaf, total_money, 1, 9, 1);
        if (game_day < 10)
            draw_decimal_value(0x12, 0xb6, (long)game_day, 7, 1, 0);
        else
            draw_decimal_value(0xe, 0xb6, (long)game_day, 7, 1, 0);
        if (security_decode_challenge() == 0) {
            FreeSeg(security_decode_challenge);
            fade_palette_to_black();
            arc_file = main_arc_file_handle;
            arc_read_index(arc_file);
            F_h04_1D32();
            shutdown_av("Beagle-Boy");
        }
        load_arc_record(0x14, archive_image_bitmap);
        play_sound(0x21);
        while (G_h01_2A16 != 0)
            ;
        fade_palette_to_black();
    }
    play_sound(0);
    Delay(5L);
    play_sound(0x1f);
    BltBitMap(h, 0L, 0L, active_screen_bitmap, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    ent = map_location_table;
    for (i = 0; i < 35 && ent->point != 0; i++, ent++) {
        if (ent->reserved[6] != 0)
            *G_h01_5370 = 0xe;
        else if (ent->reserved[7] != 0)
            *G_h01_5370 = 9;
        else
            *G_h01_5370 = 0xc;
        draw_map_cursor_marker(ent->point->x, ent->point->y);
    }
    BltBitMap(active_screen_bitmap, 0x18L, 0x14L, h, 0L, 0L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    BltBitMap(h, 0L, 0L, active_screen_bitmap, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    draw_masked_sprite(&G_h01_4478);
    draw_masked_sprite(&G_h01_44AE);
    draw_masked_sprite(&G_h01_4442);
    Delay(0x19L);
    clear_input_direction_and_fire_state();
    fade_palette_to_black();
    switch_display_buffer();
    palette_fade_target = &G_h01_14E6;
    fade_palette_to_target(&G_h01_14E6);
    for (;;) {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        BltBitMap(h, 0L, 0L, active_screen_bitmap, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
        draw_masked_sprite(&G_h01_4478);
        draw_masked_sprite(&G_h01_44AE);
        draw_masked_sprite(&G_h01_4442);
        if ((r = map_move_cursor_from_input(&x, &y)) != 0) {
            if (r == 0x25)
                break;
            if (x >= G_h01_4442 && x <= G_h01_4442 + 0x30 && y >= G_h01_4444 && y <= G_h01_4444 + 0x30) {
                r = 0x23;
                break;
            }
            if (x >= 0x18 && x <= 0x125 && y >= 0x14 && y <= 0x9f) {
                if (p1 == 1)
                    r = map_show_location_details(G_h01_0666);
                else
                    r = 1;
                if (r == 1) {
                    r = G_h01_0666;
                    break;
                }
                if (r == 0x24) {
                    x = xs;
                    y = ys;
                    Delay(10L);
                    clear_input_direction_and_fire_state();
                }
            }
        }
        if (x >= G_h01_4442 && x <= G_h01_4442 + 0x30 && y >= G_h01_4444 && y <= G_h01_4444 + 0x30) {
            draw_text(0x88, 6, "OFFICE", 1, 0xf);
        } else if (x >= 0x18 && x <= 0x125 && y >= 0x14 && y <= 0x9f) {
            G_h01_0666 = 0;
            ent = map_location_table;
            t1 = squared_distance(x, ent->point->x, y, ent->point->y);
            for (i = 0; i < 35 && ent->point != 0; i++, ent++) {
                t2 = squared_distance(x, ent->point->x, y, ent->point->y);
                if (t2 < t1) {
                    G_h01_0666 = i;
                    t1 = t2;
                }
            }
            ent = &map_location_table[G_h01_0666];
            k = strlen(ent->point);
            k = k << 2;
            if (bombastium_location_index == G_h01_0666)
                draw_text(0xa0 - k, 6, ent->point, 7, 0xf);
            else
                draw_text(0xa0 - k, 6, ent->point, 1, 0xf);
            *G_h01_5370 = 8;
            draw_map_cursor_marker(ent->point->x, ent->point->y);
        }
        draw_decimal_value(0xb0, 0xaf, total_money, 1, 9, 1);
        if (game_day < 10)
            draw_decimal_value(0x12, 0xb6, (long)game_day, 7, 1, 0);
        else
            draw_decimal_value(0xe, 0xb6, (long)game_day, 7, 1, 0);
        switch_display_buffer();
        Delay(2L);
    }
    free_bitmap_planes(&G_h01_4488, G_h01_4480, G_h01_4482);
    free_bitmap_planes(&G_h01_44BE, G_h01_44B6, G_h01_44B8);
    free_bitmap_planes(&G_h01_4452, G_h01_444A, G_h01_444C);
    free_bitmap_planes(&G_h01_43E6, G_h01_43DE, G_h01_43E0);
    free_bitmap_planes(&G_h01_441C, G_h01_4414, G_h01_4416);
    free_bitmap_planes(&G_h01_A778, G_h01_A770, G_h01_A772);
    if (matter_transmitter_unlocked && p1)
        free_bitmap_planes(&G_h01_44F4, G_h01_44EC, G_h01_44EE);
    free_bitmap(h);
    fade_palette_to_black();
    return r;
}
