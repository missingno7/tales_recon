struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
struct StringEntry { char *text; char pad[8]; };
extern struct FlagEntry rival_treasure_collected[35];
extern struct LinkEntry G_h01_4528[35];
extern struct StringEntry map_location_table[36];
extern char G_h01_1424;
extern char G_h01_17A6[1];
extern long G_h01_2A16;
extern char G_h01_3AB2;
extern unsigned char G_h01_46C8;
extern long screen_rast_port;
extern char *G_h01_46D6;
extern char difficulty_level;
extern char game_day;
extern char G_h01_46E2;
extern long G_h01_46EA;
extern long G_h01_46F2;
extern int F_h00_0640();
extern int wait_for_fire_input();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern unsigned int F_h00_463E();
extern int play_sound();
extern int mul36();
extern int strlen();
extern int Delay();
extern int SetRast();
extern int F_h14_03C2();
extern char F_h14_0412();
extern char F_h14_04A8();
extern char F_h14_0540();
extern char F_h03_154E();

recovered(a)
char a;
{
    unsigned int local_02;
    int local_04;
    int local_06;
    int local_08;
    int local_0a;
    int local_0c;
    int local_0e;
    int local_10;
    int local_12;

    if (G_h01_46E2 > game_day || game_day <= 1 || G_h01_46C8 == 0) {
        if (a == 0)
            return;
    }

    SetRast(screen_rast_port, 0L);

    if (a == 0) {
        switch ((long)difficulty_level) {
        case 0:
            if (G_h01_46EA > 1000L)
                G_h01_3AB2 = 0;
            else
                G_h01_3AB2 = F_h14_03C2(G_h01_1424);
            break;
        case 1:
            if (G_h01_46EA > 5000L) {
                G_h01_3AB2 = 0;
            } else if (G_h01_46E2 & 1) {
                G_h01_3AB2 = F_h14_04A8(G_h01_1424);
            } else {
                G_h01_3AB2 = F_h14_0412(G_h01_1424);
            }
            break;
        case 2:
            if (G_h01_46EA > 10000L)
                G_h01_3AB2 = 0;
            else
                G_h01_3AB2 = F_h14_0540(G_h01_1424);
            break;
        }
    }

    G_h01_46E2 += F_h03_154E(G_h01_1424, G_h01_3AB2);
    if (G_h01_3AB2 != 0) {
    local_02 = F_h00_463E() % 100;
    if (local_02 < 25)
        --G_h01_46E2;
    else if (local_02 < 50)
        ++G_h01_46E2;
    else if (local_02 < 55 && a == 0)
        G_h01_46EA = 0L;

    local_02 = F_h00_463E();
    if ((local_02 & 1) || a) {
        ((struct FlagEntry *)((char *)&rival_treasure_collected + (long)G_h01_3AB2 * 12L))->value = 1;
        G_h01_46EA += ((int *)(((struct LinkEntry *)((char *)&G_h01_4528 + (long)G_h01_3AB2 * 12L))->target))[1];
        F_h00_0640(10);

        local_02 = F_h00_463E();
        if (local_02 & 1) {
            F_h00_35DC(0xa8, 0x3c, "Give it up,", 1, 0);
            F_h00_35DC(0xa8, 0x4c, "Scrooge!", 1, 0);
        } else {
            F_h00_35DC(0xa8, 0x3c, "You don't have a", 1, 0);
            F_h00_35DC(0xa8, 0x4c, "chance, McDuck!", 1, 0);
        }
        F_h00_35DC(0xa8, 0x64, "I've taken the", 1, 0);
        F_h00_35DC(0xa8, 0x74, "treasure from", 1, 0);

        local_10 = strlen(((struct StringEntry *)((char *)&map_location_table + (long)G_h01_3AB2 * 12L))->text);
        local_10 <<= 2;
        F_h00_35DC(0xe0 - local_10, 0x84,
                   ((struct StringEntry *)((char *)&map_location_table + (long)G_h01_3AB2 * 12L))->text,
                   1, 0);
        F_h00_35DC(0xe0 + local_10, 0x84, ".", 1, 0);
        play_sound(0x6e);
        F_h00_307C();
        G_h01_46D6 = &G_h01_17A6[0];
        F_h00_31AA(&G_h01_17A6[0]);
        clear_input_direction_and_fire_state();

        local_12 = 0;
        while (G_h01_2A16 != 0L) {
            local_12 = poll_controller_and_keyboard_input();
            if (local_12 & 0x80)
                break;
            Delay(10L);
            local_12 = 1;
        }
        if (local_12 == 0 && wait_for_fire_input(0x28))
            play_sound(0x24);
        F_h00_330E();
        play_sound(0x21);
    }
    } else {
        G_h01_46F2 += G_h01_46EA;
        G_h01_46EA = 0L;
    }
    G_h01_1424 = G_h01_3AB2;
}
