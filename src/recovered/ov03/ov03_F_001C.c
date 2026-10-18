/* ov03_F_001C: recovered source. */
/* Structured restructure of ov03_F_001C: switch/if/while control flow, no gotos. */
struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
struct PointRef { struct Point *point; char reserved[8]; };
extern char G_h01_1766[1];
extern char G_h01_17A6[1];
extern char G_h01_17E6[1];
extern char G_h01_1866[1];
extern char G_h01_18A6[1];
extern long G_h01_2A16;
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern struct PointRef map_location_table[36];
extern struct LinkEntry G_h01_4528[35];
extern struct FlagEntry player_treasure_collected[35];
extern struct FlagEntry rival_treasure_collected[35];
extern char *G_h01_46D6;
extern long arc_file;
extern char difficulty_level;
extern char game_day;
extern char G_h01_46E2;
extern char current_location;
extern char matter_transmitter_unlocked;
extern char G_h01_46E5;
extern long total_money;
extern long G_h01_46EA;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern int G_h01_46F6;
extern int G_h01_46FE;
extern char G_h01_46DF;
extern long main_arc_file_handle;
extern long G_h01_4706;
extern char input_fire_action_capture_enabled;
extern char G_h01_4705;
extern int FreeSprite();
extern int F_h00_01BA();
extern int F_h00_09C0();
extern int F_h04_0000();
extern int invest_load_market_data();
extern int F_h04_1302();
extern int ui_choose_difficulty();
extern int money_bin_scene();
extern int office_select_destination();
extern int map_select_destination();
extern int F_h00_0640();
extern int request_disk();
extern int wait_for_fire_input();
extern int arc_read_index();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern unsigned int F_h00_463E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int play_sound();
extern int FreeSeg();
extern int mul36();
extern int strlen();
extern int Delay();
extern long Open();
long F_h03_154E();
extern int F_h03_1500();
extern int plane_scene();
extern int invest_run_office_menu();
extern int invest_update_daily_market();
extern int F_h14_0000();
extern int F_h14_03AE();
extern int F_h04_1A3A();
extern int F_h04_1AA2();
extern int ui_prompt_play_again();
extern int F_h04_1D32();

recovered()
{
    char st;
    int done;
    int flag2;
    int r8;
    int idx;
    int tmp;
    int rv;
    unsigned int mod;
    char tb[13];
    char tc;
    char f1f;

    rv = 0;
    request_disk(1);
    arc_file = Open("DT1:main.arc", 1005L);
    G_h01_46F6++;
    arc_read_index(arc_file);
    main_arc_file_handle = arc_file;
    idx = 0;
    do {
        FreeSprite((long)idx);
        idx++;
    } while (idx < 8);
    F_h04_1302();
    input_fire_action_capture_enabled = 0;
    F_h00_4EC6();
    FreeSeg(F_h04_1302);
    ui_choose_difficulty();
    done = 0;
    while (!done) {

    G_h01_4705 = 0;
    matter_transmitter_unlocked = 0;
    G_h01_46E5 = 0;
    ((char *)rival_treasure_collected)[409] = 0;
    game_day = 1;
    G_h01_46DF = 0;
    total_money = 0;
    G_h01_46EE = 0;
    G_h01_46EA = 0;
    G_h01_46F2 = 0;
    G_h01_46E2 = 1;
    invest_load_market_data();
    F_h04_0000();
    FreeSeg(F_h04_1302);
    current_location = 0x23;
    st = 0x23;
    tb[0] = 1;
    idx = 0;
    do {
        FreeSprite((long)idx);
        idx++;
    } while (idx < 8);
    G_h01_46FE = 0;
    flag2 = 0;
    while (flag2 == 0) {
    switch (st) {
    case 0x23:
    game_day += F_h03_154E(current_location, st);
        current_location = 0x23;
        if (game_day <= 0x1e) {
            st = office_select_destination();
            FreeSeg(office_select_destination);
        } else {
            st = 0;
        }
        break;

    case 0:
    G_h01_46FE = 0;
        game_day += F_h03_154E(current_location, st);
        current_location = 0;
        F_h03_1500();
        if (game_day >= 0x1e)
            flag2 = 1;
        else
            st = 0x24;
        break;

    case 0x25:
    current_location = 0x25;
        game_day = 0x1e;
        st = 0;
        break;

    case 0x24:
    st = map_select_destination(0, tb);
        tc = 0x24;
        FreeSeg(map_select_destination);
        rv = -5;
        break;

    case 0x28:
    st = map_select_destination(1, tb);
        tc = 0x28;
        FreeSeg(map_select_destination);
        break;

    case 0x26:
    rv = money_bin_scene();
        F_h00_0640(9);
        if (rv != 0) {
            F_h00_35DC(176, 60, "It must be", 1, 0);
            F_h00_35DC(176, 76, "your lucky day!", 1, 0);
            F_h00_35DC(176, 92, "That rare coin", 1, 0);
            F_h00_35DC(176, 108, "is worth $1000!", 1, 0);
            total_money += 1000;
        } else {
            F_h00_35DC(184, 60, "Mr. McDuck,", 1, 0);
            F_h00_35DC(184, 76, "don't forget", 1, 0);
            F_h00_35DC(184, 92, "about the", 1, 0);
            F_h00_35DC(184, 108, "contest!", 1, 0);
        }
        F_h00_307C();
        G_h01_46D6 = G_h01_1766;
        F_h00_31AA(G_h01_1766);
        if (wait_for_fire_input(0x32))
            play_sound(0x24);
        F_h00_330E();
        FreeSeg(money_bin_scene);
        st = 0x23;
        break;

    case 0x27:
    invest_run_office_menu();
        FreeSeg(invest_run_office_menu);
        st = 0x23;
        break;

    default:
        G_h01_46FE = 0;
        if (player_treasure_collected[st].value != 0) {
        F_h00_0640(3);
        F_h00_35DC(168, 60, "Uh...", 1, 0);
        F_h00_35DC(168, 76, "Gee, Mr. McD,", 1, 0);
        F_h00_35DC(168, 92, "you already have", 1, 0);
        F_h00_35DC(168, 108, "that treasure.", 1, 0);
        F_h00_35DC(168, 132, "Why don't I", 1, 0);
        F_h00_35DC(168, 148, "take you to", 1, 0);
        F_h00_35DC(168, 164, "somewhere else?", 1, 0);
        F_h00_307C();
        G_h01_46D6 = G_h01_1866;
        F_h00_31AA(G_h01_1866);
        if (wait_for_fire_input(0x50))
            play_sound(0x24);
        F_h00_330E();
        st = tc;
        break;
        }
        if (rival_treasure_collected[st].value != 0) {
        F_h00_0640(10);
        F_h00_35DC(168, 60, "Hah! You're too", 1, 0);
        F_h00_35DC(168, 76, " late Scrooge!", 1, 0);
        F_h00_35DC(168, 100, " This treasure", 1, 0);
        F_h00_35DC(168, 116, "   is mine!", 1, 0);
        play_sound(0x6e);
        F_h00_307C();
        G_h01_46D6 = G_h01_17A6;
        F_h00_31AA(G_h01_17A6);
        clear_input_direction_and_fire_state();
        idx = 0;
        while (G_h01_2A16 != 0) {
            idx = poll_controller_and_keyboard_input();
            if (idx & 0x80)
                break;
            Delay(5L);
            idx = 1;
        }
        if (idx == 0) {
            if (wait_for_fire_input(0x28))
                play_sound(0x24);
        }
        F_h00_330E();
        play_sound(0x21);
        while (G_h01_2A16 != 0)
            ;
        play_sound(0);
        st = tc;
        break;
        }
        idx = (char)F_h03_154E(current_location, st);
        if (idx != 0) {
            if (G_h01_46E5 != 0) {
        mod = F_h00_463E() % 100;
        if ((unsigned int)mod > (unsigned int)((difficulty_level + 1) << 3)) {
            game_day += F_h03_154E(current_location, st);
            play_sound(0);
            Delay(5L);
            play_sound(0x54);
        } else {
            play_sound(0);
            Delay(5L);
            play_sound(0x45);
            while (G_h01_2A16 != 0)
                ;
            idx = 1;
            do {
                if (player_treasure_collected[idx].value == 0 && rival_treasure_collected[idx].value == 0) {
                    st = idx;
                    break;
                }
                idx++;
            } while (idx < 35);
            F_h00_0640(2);
            F_h00_35DC(168, 60, "The Atomic Matter", 1, 0);
            F_h00_35DC(168, 76, "Transmitter ", 1, 0);
            F_h00_35DC(168, 92, "malfunctioned", 1, 0);
            F_h00_35DC(168, 108, "and sent you to", 1, 0);
            idx = strlen(map_location_table[st].point);
            idx = idx << 2;
            F_h00_35DC(232 - idx, 124, map_location_table[st].point, 1, 0);
            F_h00_35DC(idx + 232, 124, ".", 1, 0);
            F_h00_307C();
            G_h01_46D6 = G_h01_17E6;
            F_h00_31AA(G_h01_17E6);
            if (wait_for_fire_input(0x3c))
                play_sound(0x24);
            F_h00_330E();
            game_day += F_h03_154E(current_location, st);
        }
            } else {
                r8 = (char)F_h03_154E(current_location, st);
                F_h00_0640(3);
                play_sound(0x21);
                while (G_h01_2A16 != 0)
                    ;
                play_sound(0);
                F_h00_4EC6();
                request_disk(1);
                idx = F_h00_463E() % 3;
                switch (idx) {
                case 0:
                    F_h00_4D04(3);
                    F_h00_35DC(168, 60, "Launchpad McQuack,", 1, 0);
                    F_h00_35DC(168, 76, "Flying Ace...", 1, 0);
                    F_h00_35DC(168, 92, "At your service!", 1, 0);
                    break;
                case 1:
                    F_h00_4D04(13);
                    F_h00_35DC(168, 60, "Ready to", 1, 0);
                    F_h00_35DC(168, 76, "hit the skies,", 1, 0);
                    F_h00_35DC(168, 92, "Mr. McD!", 1, 0);
                    break;
                case 2:
                    F_h00_4D04(14);
                    F_h00_35DC(168, 60, "Ready to", 1, 0);
                    F_h00_35DC(168, 76, "take off,", 1, 0);
                    F_h00_35DC(168, 92, "Mr. McD!", 1, 0);
                    break;
                }

                request_disk(1);
                arc_read_index(arc_file);
                F_h00_307C();
                G_h01_46D6 = G_h01_1866;
                F_h00_31AA(G_h01_1866);
                play_sound(0x77);
                while (G_h01_2A16 != 0)
                    ;
                F_h00_4EC6();
                switch (difficulty_level) {
                case 0:
                    idx = 25;
                    break;
                case 1:
                    idx = 50;
                    break;
                case 2:
                    idx = 75;
                    break;
                }
                mod = F_h00_463E() % 100;
                f1f = 0;
                if ((unsigned int)mod < (unsigned int)idx) {
                    if (rival_treasure_collected[st].value == 0) {
                        f1f = 1;
                        F_h14_03AE(current_location, st);
                    }
                }

                FreeSeg(F_h04_1302);
                FreeSeg(office_select_destination);
                rv = plane_scene(r8, f1f);
                FreeSeg(plane_scene);
                F_h00_330E();
                if (rv == 0 && f1f == 0) {
                    F_h00_0640(2);
                    F_h00_35DC(168, 60, "Sorry, Mr. McDuck,", 1, 0);
                    F_h00_35DC(168, 76, "but it will take", 1, 0);
                    F_h00_35DC(168, 92, "2 days to fix", 1, 0);
                    F_h00_35DC(168, 108, "the plane.", 1, 0);
                    game_day += 2;
                    F_h00_307C();
                    G_h01_46D6 = G_h01_17E6;
                    F_h00_31AA(G_h01_17E6);
                    if (wait_for_fire_input(0x3c))
                        play_sound(0x24);
                    F_h00_330E();
                    if (total_money > 0) {
                        mod = F_h00_463E();
                        mod = mod % 10;
                        switch (mod) {
                        case 0:
                        case 1:
                            mod = 0;
                            break;
                        case 2:
                        case 3:
                        case 4:
                            mod = total_money >> 3;
                            break;
                        case 5:
                        case 6:
                        case 7:
                            mod = total_money >> 2;
                            break;
                        case 8:
                        case 9:
                            mod = total_money >> 1;
                            break;
                        }
                        F_h00_0640(9);
                        F_h00_35DC(168, 44, "I've searched the", 1, 0);
                        F_h00_35DC(168, 60, "wreckage for your", 1, 0);
                        F_h00_35DC(168, 76, "treasure, and I'm", 1, 0);
                        if (mod == 0) {
                            F_h00_35DC(168, 92, "happy to report", 1, 0);
                            F_h00_35DC(168, 108, "that nothing", 1, 0);
                        } else {
                            F_h00_35DC(168, 92, "sorry to report", 1, 0);
                            F_h00_35DC(168, 108, "that $", 1, 0);
                            F_h00_09C0(216, 108, (long)mod, 1, 0, 0);
                            total_money -= mod;
                        }
                        F_h00_35DC(168, 124, "was lost in", 1, 0);
                        F_h00_35DC(168, 140, "the crash!", 1, 0);
                        F_h00_307C();
                        G_h01_46D6 = G_h01_1766;
                        F_h00_31AA(G_h01_1766);
                        if (wait_for_fire_input(0x64))
                            play_sound(0x24);
                        F_h00_330E();
                    }
                } else if (f1f != 0 && rv == 0) {
                    F_h14_0000(1);
                    FreeSeg(F_h14_0000);
                    current_location = st;
                    st = 0x24;
                    rv = -5;
                    break;
                }
            }
        }
        current_location = st;
        if (game_day > 0x1e)
            break;
        rv = F_h00_01BA(current_location);
        game_day += 1;
        if (rv != 0) {
            if (G_h01_4706 != 0) {
                G_h01_4706 = 0;
                request_disk(1);
                arc_read_index(arc_file);
            } else {
                F_h00_4EC6();
                tmp = F_h00_463E() % 3;
                request_disk(2);
                switch (tmp) {
                case 0:
                    F_h00_4D04(11);
                    tmp = 0x77;
                    break;
                case 1:
                    F_h00_4D04(11);
                    tmp = 0x27;
                    break;
                case 2:
                    F_h00_4D04(24);
                    tmp = 0x49;
                    break;
                }
                arc_file = main_arc_file_handle;
                F_h00_0640(6);
                F_h00_35DC(168, 60, "Congratulations!", 1, 0);
                F_h00_35DC(168, 76, "You have acquired", 1, 0);
                F_h00_35DC(168, 92, "another valuable", 1, 0);
                F_h00_35DC(168, 108, "   treasure!", 1, 0);
                idx = *(int *)(G_h01_4528[current_location].target + 2);
                total_money += idx;
                F_h00_35DC(208, 128, "$", 1, 0);
                F_h00_09C0(216, 128, (long)idx, 1, 0, 0);
                F_h00_330E();
                F_h00_307C();
                G_h01_46D6 = G_h01_18A6;
                F_h00_31AA(G_h01_18A6);
                play_sound(tmp);
                palette_cycle_callback_index = 1;
                palette_cycle_countdown_step = 8;
                if (wait_for_fire_input(0x28))
                    play_sound(0x24);
                palette_cycle_countdown_step = 0;
                palette_cycle_callback_index = 0;
                F_h00_4EC6();
            }
            F_h00_330E();
            player_treasure_collected[current_location].value = 1;
            if (current_location == G_h01_4705) {
                matter_transmitter_unlocked = 1;
                F_h00_0640(2);
                F_h00_35DC(160, 16, "Now that you", 1, 0);
                F_h00_35DC(160, 32, "have found", 1, 0);
                F_h00_35DC(160, 48, "bombastium I", 1, 0);
                F_h00_35DC(160, 64, "can build you", 1, 0);
                F_h00_35DC(160, 80, "a matter transmitter", 1, 0);
                F_h00_35DC(160, 96, "you can use", 1, 0);
                F_h00_35DC(160, 112, "next time you're", 1, 0);
                F_h00_35DC(160, 128, "in the office", 1, 0);
                F_h00_35DC(160, 146, "to transport", 1, 0);
                F_h00_35DC(160, 162, "yourself to any", 1, 0);
                F_h00_35DC(160, 180, "destination.", 1, 0);
                F_h00_330E();
                F_h00_307C();
                G_h01_46D6 = G_h01_17E6;
                F_h00_31AA(G_h01_17E6);
                play_sound(0x54);
                if (wait_for_fire_input(0x64))
                    play_sound(0x24);
                F_h00_330E();
            }
        } else {
            request_disk(1);
            arc_file = main_arc_file_handle;
            arc_read_index(arc_file);
        }
        st = 0x24;
        break;
    }
    if (game_day > 0x1e) {
        st = 0;
        current_location = 0;
    } else if (rv != -5) {
        F_h14_0000(0);
        FreeSeg(F_h14_0000);
        invest_update_daily_market();
        FreeSeg(invest_update_daily_market);
    }
    }

    if (G_h01_46F2 > G_h01_46EE) {
        F_h04_1A3A(0);
        F_h04_1AA2(0);
    } else {
        F_h04_1A3A(1);
        F_h04_1AA2(1);
    }
    F_h00_4EC6();
    request_disk(1);
    F_h00_4D04(0);
    request_disk(1);
    arc_read_index(arc_file);
    done = ui_prompt_play_again();
    if (done == 0) {
        ui_choose_difficulty();
    }
    play_sound(0);
    }
    F_h04_1D32();
    G_h01_46F6--;
}
