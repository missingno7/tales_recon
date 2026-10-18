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
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long arc_file;
extern long main_arc_file_handle;
extern char game_day;
extern char current_location;
extern char matter_transmitter_unlocked;
extern long total_money;
extern char G_h01_4705;
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
extern long F_h00_291E();
extern int BltBitMap();
extern int F_h00_35DC();
extern int F_h00_34E0();
extern int F_h00_09C0();
extern int security_decode_challenge();
extern int FreeSeg();
extern int F_h00_330E();
extern int F_h04_1D32();
extern int shutdown_av();
extern int Delay();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int map_move_cursor_from_input();
extern int map_show_location_details();
extern int F_h15_08B0();
extern long F_h00_08FC();
extern int strlen();
extern int F_h00_3AE4();
extern int F_h00_3B84();

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
        F_h00_291E(0x14, G_h01_46CE);
    else
        F_h00_291E(0x15, G_h01_46CE);
    h = F_h00_291E(0x16, h);
    F_h00_291E(0x18, &G_h01_4442);
    G_h01_4442 = 0x16;
    G_h01_4444 = 0x73;
    F_h00_291E(0x17, &G_h01_44AE);
    G_h01_44AE = 0x28;
    G_h01_44B0 = 0xac;
    F_h00_291E(0x19, &G_h01_4478);
    G_h01_4478 = 8;
    G_h01_447A = 0xaf;
    F_h00_291E(0x1a, &G_h01_43D6);
    G_h01_43D6 = 0xc0;
    G_h01_43D8 = 0xaa;
    F_h00_291E(0x1b, &G_h01_440C);
    G_h01_440C = 0xf8;
    G_h01_440E = 0xae;
    F_h00_291E(0x1c, &G_h01_A768);
    if (matter_transmitter_unlocked && p1) {
        F_h00_291E(0x1d, &G_h01_44E4);
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
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_35DC(0x64, 6, "Security System", 1, 0xf);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_09C0(0xb0, 0xaf, total_money, 1, 9, 1);
        if (game_day < 10)
            F_h00_09C0(0x12, 0xb6, (long)game_day, 7, 1, 0);
        else
            F_h00_09C0(0xe, 0xb6, (long)game_day, 7, 1, 0);
        if (security_decode_challenge() == 0) {
            FreeSeg(security_decode_challenge);
            F_h00_330E();
            arc_file = main_arc_file_handle;
            arc_read_index(arc_file);
            F_h04_1D32();
            shutdown_av("Beagle-Boy");
        }
        F_h00_291E(0x14, G_h01_46CE);
        play_sound(0x21);
        while (G_h01_2A16 != 0)
            ;
        F_h00_330E();
    }
    play_sound(0);
    Delay(5L);
    play_sound(0x1f);
    BltBitMap(h, 0L, 0L, G_h01_46D2, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    ent = map_location_table;
    for (i = 0; i < 35 && ent->point != 0; i++, ent++) {
        if (ent->reserved[6] != 0)
            *G_h01_5370 = 0xe;
        else if (ent->reserved[7] != 0)
            *G_h01_5370 = 9;
        else
            *G_h01_5370 = 0xc;
        F_h15_08B0(ent->point->x, ent->point->y);
    }
    BltBitMap(G_h01_46D2, 0x18L, 0x14L, h, 0L, 0L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    BltBitMap(h, 0L, 0L, G_h01_46D2, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
    F_h00_34E0(&G_h01_4478);
    F_h00_34E0(&G_h01_44AE);
    F_h00_34E0(&G_h01_4442);
    Delay(0x19L);
    clear_input_direction_and_fire_state();
    F_h00_330E();
    F_h00_307C();
    G_h01_46D6 = &G_h01_14E6;
    F_h00_31AA(&G_h01_14E6);
    for (;;) {
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        BltBitMap(h, 0L, 0L, G_h01_46D2, 0x18L, 0x14L, 0x110L, 0x8cL, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_34E0(&G_h01_4442);
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
            F_h00_35DC(0x88, 6, "OFFICE", 1, 0xf);
        } else if (x >= 0x18 && x <= 0x125 && y >= 0x14 && y <= 0x9f) {
            G_h01_0666 = 0;
            ent = map_location_table;
            t1 = F_h00_08FC(x, ent->point->x, y, ent->point->y);
            for (i = 0; i < 35 && ent->point != 0; i++, ent++) {
                t2 = F_h00_08FC(x, ent->point->x, y, ent->point->y);
                if (t2 < t1) {
                    G_h01_0666 = i;
                    t1 = t2;
                }
            }
            ent = &map_location_table[G_h01_0666];
            k = strlen(ent->point);
            k = k << 2;
            if (G_h01_4705 == G_h01_0666)
                F_h00_35DC(0xa0 - k, 6, ent->point, 7, 0xf);
            else
                F_h00_35DC(0xa0 - k, 6, ent->point, 1, 0xf);
            *G_h01_5370 = 8;
            F_h15_08B0(ent->point->x, ent->point->y);
        }
        F_h00_09C0(0xb0, 0xaf, total_money, 1, 9, 1);
        if (game_day < 10)
            F_h00_09C0(0x12, 0xb6, (long)game_day, 7, 1, 0);
        else
            F_h00_09C0(0xe, 0xb6, (long)game_day, 7, 1, 0);
        F_h00_307C();
        Delay(2L);
    }
    F_h00_3AE4(&G_h01_4488, G_h01_4480, G_h01_4482);
    F_h00_3AE4(&G_h01_44BE, G_h01_44B6, G_h01_44B8);
    F_h00_3AE4(&G_h01_4452, G_h01_444A, G_h01_444C);
    F_h00_3AE4(&G_h01_43E6, G_h01_43DE, G_h01_43E0);
    F_h00_3AE4(&G_h01_441C, G_h01_4414, G_h01_4416);
    F_h00_3AE4(&G_h01_A778, G_h01_A770, G_h01_A772);
    if (matter_transmitter_unlocked && p1)
        F_h00_3AE4(&G_h01_44F4, G_h01_44EC, G_h01_44EE);
    F_h00_3B84(h);
    F_h00_330E();
    return r;
}
