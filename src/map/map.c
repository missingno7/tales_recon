/* Map overlay (ov15), in original address order. Readability grouping only;
 * no claim of historical source filenames or original object/TU boundaries.
 * Conflicting Point/PointRef and scalar extern views stay function-local.
 * Overlay-call prototypes are local to avoid unused pinned-linker proxies.
 */

struct Pair {
    int first;
    int second;
};

struct Object {
    char padding[2];
    long name;
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
extern struct Pair G_h01_A768;
extern int G_h01_0666;
extern int G_h01_4442;
extern int G_h01_4444;
extern int G_h01_44B0;
extern int G_h01_447A;
extern int G_h01_43D8;
extern int G_h01_440E;
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
extern char G_h01_5E5E;
extern char G_h01_46E5;
extern char G_h01_451B;
extern int map_input_action;
extern int map_direction_hold_count;
extern int map_direction_restart_pending;
extern int map_cursor_horizontal_step;
extern int map_cursor_vertical_step;

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
extern int FreeSeg();
extern int fade_palette_to_black();
extern int Delay();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern long squared_distance();
extern int strlen();
extern int free_bitmap_planes();
extern int free_bitmap();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int WritePixel();
extern long Open();
extern long F_h00_0976();
extern int poll_controller_and_keyboard_input();
extern int free_text_block();
extern int Close();

/* Select a map destination, with location details or the office return. */
map_select_destination(p1, flag)
int p1;
char *flag;
{
    extern int security_decode_challenge();
    extern int F_h04_1D32();
    extern int shutdown_av();
    extern int map_move_cursor_from_input();
    extern int map_show_location_details();
    extern int draw_map_cursor_marker();

    struct Point {
        char pad[32];
        int x;
        int y;
    };
    struct PointRef {
        struct Point *point;
        char reserved[8];
    };
    extern struct PointRef map_location_table[36];
    extern int G_h01_44AE;
    extern int G_h01_4478;
    extern int G_h01_43D6;
    extern int G_h01_440C;
    extern int G_h01_44E4;

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

/* Draw a filled map cursor marker and its outline. */
draw_map_cursor_marker(x,y)
int x,y;
{
    char i,j;
    int x0,y0;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            SetAPen(screen_rast_port,(long)*G_h01_5370);
            WritePixel(screen_rast_port,(long)(x+j),(long)(y+i));
        }
    x0=x-1;
    y0=y-1;
    *G_h01_5370=0;
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x0,(long)y0);
    Draw(screen_rast_port,(long)(x0+4),(long)y0);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x0,(long)(y0+1));
    Draw(screen_rast_port,(long)x0,(long)(y0+4));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x0+4),(long)(y0+1));
    Draw(screen_rast_port,(long)(x0+4),(long)(y0+4));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x0,(long)(y0+4));
    Draw(screen_rast_port,(long)(x0+4),(long)(y0+4));
}

/* Outline a map option rectangle. */
draw_map_option_outline(p,width,height)
int *p,width,height;
{
    int x,y;

    x=p[0]-1;
    y=p[1]-1;
    *G_h01_5370=1;
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x,(long)y);
    Draw(screen_rast_port,(long)x,(long)(y+height+1));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x+width+1),(long)y);
    Draw(screen_rast_port,(long)(x+width+1),(long)(y+height+1));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x,(long)y);
    Draw(screen_rast_port,(long)(x+width+1),(long)y);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x,(long)(y+height+1));
    Draw(screen_rast_port,(long)(x+width+1),(long)(y+height+1));
}

/* Show location and treasure details and choose the travel method. */
map_show_location_details(n)
int n;
{
    extern int calculate_travel_days();
    extern int draw_map_option_outline();

    struct Point {
        char pad[30];
        int selected;
    };
    struct PointRef {
        struct Point *point;
        char reserved[8];
    };
    extern char G_h01_43D6;
    extern char G_h01_4478;
    extern char G_h01_44AE;
    extern char G_h01_440C;
    extern char G_h01_44E4;
    extern struct PointRef map_location_table[36];


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

/* Move and clamp the map cursor using directional input and hold acceleration. */
int map_move_cursor_from_input(px, py)
int *px, *py;
{
    G_h01_5E5E = 0;
    map_input_action = poll_controller_and_keyboard_input();
    if (map_input_action & 0x80)
        return 1;
    switch (map_input_action & 0x3f) {
    case 1:
        (*py)--;
        map_cursor_vertical_step = -1;
        map_cursor_horizontal_step = 0;
        break;
    case 2:
        (*py)--;
        *px += 2;
        map_cursor_vertical_step = -1;
        map_cursor_horizontal_step = 1;
        break;
    case 3:
        (*px)++;
        map_cursor_horizontal_step = 1;
        map_cursor_vertical_step = 0;
        break;
    case 4:
        (*py)++;
        *px += 2;
        map_cursor_vertical_step = 1;
        map_cursor_horizontal_step = 1;
        break;
    case 5:
        (*py)++;
        map_cursor_vertical_step = 1;
        map_cursor_horizontal_step = 0;
        break;
    case 6:
        (*py)++;
        *px -= 2;
        map_cursor_vertical_step = 1;
        map_cursor_horizontal_step = -1;
        break;
    case 7:
        (*px)--;
        map_cursor_horizontal_step = -1;
        map_cursor_vertical_step = 0;
        break;
    case 8:
        (*py)--;
        *px -= 2;
        map_cursor_horizontal_step = -1;
        map_cursor_vertical_step = -1;
        break;
    case 0:
    default:
        map_direction_hold_count = 0;
        map_input_action = 0;
        map_cursor_vertical_step = 0;
        map_cursor_horizontal_step = 0;
        map_direction_restart_pending = 0;
        break;
    }
    if ((map_input_action & 0x3f) != 0 && map_direction_hold_count < 0x100) {
        if (map_direction_hold_count != 0) {
            switch (map_input_action & 0x3f) {
            case 2:
            case 4:
                map_cursor_horizontal_step++;
                break;
            case 6:
            case 8:
                map_cursor_horizontal_step--;
                break;
            }
        }
        map_direction_hold_count++;
    }
    if (map_direction_hold_count == 0) {
        map_direction_hold_count = 1;
        map_direction_restart_pending = 1;
    }
    *px = *px + (map_direction_hold_count - 1) * map_cursor_horizontal_step;
    *py = *py + (map_direction_hold_count - 1) * map_cursor_vertical_step;
    if (map_direction_restart_pending) {
        map_direction_hold_count = 0;
        map_direction_restart_pending = 0;
    }
    if (*px < 0x20)
        *px = 0x20;
    else if (*px > 0x11d)
        *px = 0x11d;
    if (*py < 0x1c)
        *py = 0x1c;
    else if (*py > 0x97)
        *py = 0x97;
    G_h01_A768.first = *px - 8;
    G_h01_A768.second = *py - 8;
    draw_masked_sprite(&G_h01_A768);
    clear_input_direction_and_fire_state();
    G_h01_5E5E = 1;
    return 0;
}
