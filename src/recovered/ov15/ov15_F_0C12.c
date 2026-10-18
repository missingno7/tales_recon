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
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
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
extern long F_h00_291E();
extern long F_h00_0976();
extern int strlen();
extern int F_h03_154E();
extern int clear_input_direction_and_fire_state();
extern int BltBitMap();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_09C0();
extern int F_h15_0A80();
extern int F_h00_330E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int poll_controller_and_keyboard_input();
extern int play_sound();
extern int Delay();
extern int F_h00_3C0E();
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
    q = F_h00_291E(p->point->selected, q);
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
    s = F_h00_291E((*(struct Pair **)p->reserved)->first, s);
    r2 = ((struct Object *)s)->name;
    r2 = F_h00_0976(r2, buf);
    r4 = r2;
    w8 = strlen(p->point);
    w8 <<= 2;
    f = F_h03_154E(current_location, n);
    clear_input_direction_and_fire_state();
    i = 0;
    do {
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_34E0(&G_h01_43D6);
        F_h00_34E0(&G_h01_440C);
        if (matter_transmitter_unlocked)
            F_h00_34E0(&G_h01_44E4);
        F_h00_35DC(160 - w8, 6, p->point, 7, 15);
        r1 = r3;
        r1 = F_h00_0976(r1, buf);
        y = 22;
        F_h00_35DC(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        F_h00_35DC(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        F_h00_35DC(32, y, buf, 1, 0);
        r1 = F_h00_0976(r1, buf);
        y += 8;
        F_h00_35DC(32, y, buf, 1, 0);
        if (n != 0) {
            r2 = r4;
            y += 16;
            F_h00_35DC(32, y, "TREASURE: ", 1, 0);
            r2 = F_h00_0976(r2, buf);
            if (strlen(buf) < 24)
                x = 112;
            else {
                x = 32;
                y += 8;
            }
            F_h00_35DC(x, y, buf, 1, 0);
            y += 16;
            F_h00_35DC(32, y, "TREASURE DESCRIPTION: ", 1, 0);
            r2 = F_h00_0976(r2, buf);
            y += 8;
            F_h00_35DC(32, y, buf, 1, 0);
            r2 = F_h00_0976(r2, buf);
            y += 8;
            F_h00_35DC(32, y, buf, 1, 0);
            y += 16;
            F_h00_35DC(32, y, "TREASURE VALUE: ", 1, 0);
            if (p->reserved[6] || p->reserved[7])
                F_h00_09C0(160, y, 0L, 1, 0, 0L);
            else
                F_h00_09C0(160, y, (long)(*(struct Pair **)p->reserved)->second, 1, 0, 0L);
        }
        y += 16;
        F_h00_35DC(32, y, "TRAVEL TIME:   day", 1, 0);
        if (f != 1)
            F_h00_35DC(176, y, "s", 1, 0);
        F_h00_09C0(136, y, (long)f, 1, 0, 0L);
        F_h00_09C0(176, 175, total_money, 1, 9, 1);
        if (game_day < 10)
            F_h00_09C0(18, 182, (long)game_day, 7, 1, 0);
        else
            F_h00_09C0(14, 182, (long)game_day, 7, 1, 0);
        F_h15_0A80(&G_h01_43D6, 52, 27);
        if (i == 0) {
            F_h00_330E();
            F_h00_307C();
            G_h01_46D6 = &G_h01_14E6;
            F_h00_31AA(&G_h01_14E6);
        } else
            F_h00_307C();
        i++;
    } while (i < 2);
    for (;;) {
        clear_input_direction_and_fire_state();
        BltBitMap(G_h01_46CE, 0L, 0xa8L, G_h01_46D2, 0L, 0xa8L, 0x140L, 0x20L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_4478);
        F_h00_34E0(&G_h01_44AE);
        F_h00_34E0(&G_h01_43D6);
        F_h00_34E0(&G_h01_440C);
        if (matter_transmitter_unlocked)
            F_h00_34E0(&G_h01_44E4);
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
            F_h15_0A80(&G_h01_43D6, 52, 27);
            e = 36;
            break;
        case 1:
            G_h01_46E5 = 0;
            F_h15_0A80(&G_h01_440C, 32, 18);
            e = 1;
            break;
        case 2:
            G_h01_46E5 = 1;
            F_h15_0A80(&G_h01_44E4, 37, 27);
            e = 1;
            break;
        }
        F_h00_09C0(176, 175, total_money, 1, 9, 1);
        if (game_day < 10)
            F_h00_09C0(18, 182, (long)game_day, 7, 1, 0);
        else
            F_h00_09C0(14, 182, (long)game_day, 7, 1, 0);
        F_h00_307C();
        if (k != 0)
            break;
        Delay(1L);
    }
    F_h00_3C0E(s);
    Close(u2);
    F_h00_3C0E(q);
    Close(u1);
    arc_file = t;
    request_disk(1);
    arc_read_index(arc_file);
    clear_input_direction_and_fire_state();
    Delay(5L);
    return e;
}
