/* ov10_F_0000: cave-map load, 8x8 grid state machine, action dispatch. Three unused locals (c1, c2, i1) are kept: the original 134-byte frame and its slot offsets require them. */
struct Rec54 { char b[54]; };
extern char G_h01_5E5E;
extern long screen_rast_port;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long arc_file;
extern char difficulty_level;
extern long total_money;
extern short G_h01_4356[64];
extern long G_h01_7998;
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
extern unsigned int G_h01_79A8;
extern short G_h01_799C;
extern char G_h01_79A2;
extern char G_h01_79A4;
extern char G_h01_79A5;
extern char G_h01_79A6;
extern char G_h01_79AA;
extern short G_h01_79AC;
extern short G_h01_79AE;
extern short G_h01_79B0;
extern short G_h01_79B2;
extern char G_h01_79B4;
extern short G_h01_79B6;
extern short G_h01_79B8;
extern short G_h01_79BE;
extern short G_h01_79C0;
extern short G_h01_79EC;
extern short G_h01_79EE;
extern short G_h01_7A22;
extern short G_h01_7A24;
extern short G_h01_7A58;
extern short G_h01_7A5A;
extern short G_h01_7452;
extern short G_h01_7454;
extern short G_h01_741C;
extern short G_h01_741E;
extern short G_h01_74F4;
extern short G_h01_74F6;
extern short G_h01_7746;
extern short G_h01_7748;
extern short G_h01_730E;
extern short G_h01_7310;
extern short G_h01_788A;
extern short G_h01_788C;
extern short G_h01_777C;
extern short G_h01_777E;
extern short G_h01_77B2;
extern short G_h01_77B4;
extern short G_h01_77E8;
extern short G_h01_77EA;
extern short G_h01_781E;
extern short G_h01_7820;
extern short G_h01_7854;
extern short G_h01_7856;
extern short G_h01_7560;
extern short G_h01_7568;
extern short G_h01_756A;
extern short G_h01_7602;
extern short G_h01_7604;
extern short G_h01_7638;
extern short G_h01_763A;
extern short G_h01_766E;
extern short G_h01_7670;
extern short G_h01_76A4;
extern short G_h01_76A6;
extern short G_h01_76DA;
extern short G_h01_76DC;
extern short G_h01_7710;
extern short G_h01_7712;
extern short G_h01_75CC;
extern short G_h01_75CE;
extern short G_h01_75D4;
extern short G_h01_75D6;
extern short G_h01_759E;
extern short G_h01_75A0;
extern short G_h01_7932;
extern short G_h01_7934;
extern short G_h01_7936;
extern short G_h01_792C;
extern short G_h01_792E;
extern short G_h01_78F6;
extern short G_h01_78F8;
extern short G_h01_7596;
extern short G_h01_7598;
extern short G_h01_72AA;
extern short G_h01_72AC;
extern short G_h01_72E0;
extern short G_h01_72E2;
extern short G_h01_7274;
extern short G_h01_7276;
extern short G_h01_7316;
extern short G_h01_7318;
extern short G_h01_734C;
extern short G_h01_734E;
extern short G_h01_7382;
extern short G_h01_7384;
extern short G_h01_73B8;
extern short G_h01_73BA;
extern short G_h01_73EE;
extern short G_h01_73F0;
extern short G_h01_74FC;
extern short G_h01_74FE;
extern short G_h01_7426;
extern short G_h01_7424;
extern short G_h01_745A;
extern short G_h01_745C;
extern short G_h01_7784;
extern short G_h01_7786;
extern short G_h01_77BA;
extern short G_h01_77BC;
extern short G_h01_77F0;
extern short G_h01_77F2;
extern short G_h01_7826;
extern short G_h01_7828;
extern short G_h01_785C;
extern short G_h01_785E;
extern short G_h01_774E;
extern short G_h01_7750;
extern short G_h01_7892;
extern short G_h01_7894;
extern short G_h01_78C8;
extern short G_h01_78CA;
extern short G_h01_78FE;
extern short G_h01_7900;
extern short G_h01_79F4;
extern short G_h01_79F6;
extern short G_h01_7A60;
extern short G_h01_7A62;
extern short G_h01_7A2A;
extern short G_h01_7A2C;
extern char G_h01_16A6[1];
extern char G_h01_1726[1];
extern char G_h01_7236[1];
extern char G_h01_726C[1];
extern char G_h01_727C[1];
extern char G_h01_72A2[1];
extern char G_h01_72B2[1];
extern char G_h01_72D8[1];
extern char G_h01_72E8[1];
extern char G_h01_731E[1];
extern char G_h01_7344[1];
extern char G_h01_7354[1];
extern char G_h01_737A[1];
extern char G_h01_738A[1];
extern char G_h01_73B0[1];
extern char G_h01_73C0[1];
extern char G_h01_73E6[1];
extern char G_h01_73F6[1];
extern char G_h01_742C[1];
extern char G_h01_7462[1];
extern char G_h01_7504[1];
extern char G_h01_7570[1];
extern char G_h01_75A6[1];
extern char G_h01_75DC[1];
extern char G_h01_7756[1];
extern char G_h01_778C[1];
extern char G_h01_77C2[1];
extern char G_h01_77F8[1];
extern char G_h01_782E[1];
extern char G_h01_7864[1];
extern char G_h01_789A[1];
extern char G_h01_78C0[1];
extern char G_h01_78D0[1];
extern char G_h01_7906[1];
extern char G_h01_793C[1];
extern char G_h01_79C6[1];
extern char G_h01_79FC[1];
extern char G_h01_7A32[1];
extern char G_h01_7A68[1];
extern char G_h01_0476[1];
extern char G_h01_04AA[1];
extern char G_h01_04DA[1];
extern char G_h01_050A[1];
extern char G_h01_053E[1];
extern char G_h01_0572[1];
extern char G_h01_059A[1];
extern char G_h01_05D6[1];
extern long G_h01_2A16;
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern long F_h00_0976();
extern int request_disk();
extern int wait_for_fire_input();
extern int arc_read_index();
extern long F_h00_291E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3AE4();
extern int F_h00_3B84();
extern int F_h00_3C0E();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern unsigned int F_h00_463E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int play_sound();
extern int sscanf();
extern int Close();
extern int Delay();
extern long Open();
extern int BltBitMap();
extern long SetRast();
extern int F_h10_2160();
extern int F_h10_25A2();
extern int F_h10_2634();
extern int F_h10_2B8A();
extern int F_h10_2BAC();
extern int F_h10_2BCA();
extern int F_h10_2CF4();
extern int F_h10_2FA0();
extern int F_h10_3288();

recovered(arg)
int arg;
{
    long saved_handle;
    long exp_handle;
    int i;
    int j;
    char *bitmap;
    short *cell;
    long grid_base;
    char *text;
    char c1;
    char line[80];
    int action;
    char c2;
    char kind;
    char kind2;
    char tile;
    unsigned int tick;
    unsigned int phase;
    int last;
    int dx;
    int dy;
    char flag7f;
    char flag80;
    char flag81;
    char flag82;
    int res;
    int i1;

    /* A: state reset and grid clear. */
    flag82 = 0;
    res = 0;
    G_h01_5E5E = 0;
    action = 0;
    tile = 0;
    tick = 0;
    phase = 0;
    last = 0;
    G_h01_79A6 = 0;
    flag7f = 0;
    flag80 = 0;
    saved_handle = arc_file;
    for (i = 0; i < 64; i++)
        G_h01_4356[i] = 0;

    /* B: open cave map, parse 8 rows of 8 cell words. */
    request_disk(2);
    arc_file = Open("DT2:cavemaps.arc", 1005L);
    arc_read_index(arc_file);
    bitmap = F_h00_291E(arg, 0L);
    text = *(char **)(bitmap + 2);
    for (i = 0; i < 64; i += 8) {
        text = (char *)F_h00_0976(text, line);
        sscanf(line, "%d %d %d %d %d %d %d %d",
                   &G_h01_4356[i], &G_h01_4356[i + 1], &G_h01_4356[i + 2], &G_h01_4356[i + 3],
                   &G_h01_4356[i + 4], &G_h01_4356[i + 5], &G_h01_4356[i + 6], &G_h01_4356[i + 7]);
    }
    F_h00_3C0E(bitmap);
    Close(arc_file);

    /* C: open exp.arc, draw static panels, set panel geometry. */
    request_disk(2);
    arc_file = Open("DT2:exp.arc", 1005L);
    arc_read_index(arc_file);
    exp_handle = arc_file;
    F_h00_291E(17, &G_h01_730E);
    G_h01_730E = 82;
    G_h01_7310 = 38;
    if (G_h01_79AA != 0) {
        F_h00_291E(18, G_h01_7344);
        F_h00_291E(19, G_h01_737A);
        F_h00_291E(20, G_h01_73E6);
        F_h00_291E(21, G_h01_73B0);
    }
    F_h00_291E(4, &G_h01_79B6);
    G_h01_79B6 = 220;
    G_h01_79B8 = 40;
    F_h00_291E(5, &G_h01_79EC);
    G_h01_79EC = 0;
    G_h01_79EE = 144;
    F_h00_291E(6, &G_h01_7A22);
    G_h01_7A22 = 240;
    G_h01_7A24 = 122;
    F_h00_291E(3, &G_h01_7A58);
    G_h01_7A58 = 40;
    G_h01_7A5A = 24;
    F_h00_291E(22, &G_h01_7452);
    G_h01_7452 = 71;
    G_h01_7454 = 141;
    F_h00_291E(23, &G_h01_741C);
    G_h01_741C = 176;
    G_h01_741E = 110;
    F_h00_291E(26, &G_h01_74F4);
    G_h01_74F4 = 141;
    G_h01_74F6 = 3;
    F_h00_291E(37, &G_h01_7746);
    G_h01_7746 = 112;
    G_h01_7748 = 137;
    F_h00_291E(38, &G_h01_777C);
    F_h00_291E(39, &G_h01_77B2);
    F_h00_291E(40, &G_h01_77E8);
    F_h00_291E(41, &G_h01_781E);
    F_h00_291E(42, &G_h01_7854);
    F_h00_291E(43, &G_h01_788A);
    G_h01_777C = G_h01_730E + 16;
    G_h01_77B2 = G_h01_730E + 28;
    G_h01_77E8 = G_h01_730E + 53;
    G_h01_781E = G_h01_730E + 99;
    G_h01_7854 = G_h01_730E + 112;
    G_h01_777E = G_h01_7310 + 61;
    G_h01_77B4 = G_h01_7310 + 39;
    G_h01_77EA = G_h01_7310 + 15;
    G_h01_7820 = G_h01_7310 + 41;
    G_h01_7856 = G_h01_7310 + 59;
    G_h01_788A = 160;
    G_h01_788C = 115;
    G_h01_7998 = 0;
    G_h01_7998 = F_h00_291E(47, G_h01_7998);
    F_h00_291E(14, G_h01_726C);
    G_h01_79AC = 14;
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(21);
    arc_file = exp_handle;
    request_disk(2);
    arc_read_index(arc_file);
    SetRast(screen_rast_port, 0L);
    F_h00_34E0(&G_h01_7746);

    /* D: locate the marked start cell (bit 5) and the goal cell (bit 4). */
    grid_base = (long)(cell = G_h01_4356);
    F_h10_2160(cell);
    for (i = 0; i < 64; i++, cell++) {
        if (*cell & 0x20)
            G_h01_79A8 = i;
        else if (*cell & 0x10)
            G_h01_799E = i;
    }
    for (;;) {
        if ((G_h01_79A0 = F_h00_463E() & 63) != G_h01_799E)
            break;
    }
    cell = G_h01_4356 + G_h01_799E;
    G_h01_79B2 = 1;
    kind = 0;
    kind2 = 0;
    G_h01_79A2 = 0;
    G_h01_79A4 = 0;
    G_h01_79A5 = 0;
    switch (difficulty_level) {
    case 0:
        flag81 = 20;
        G_h01_79AE = 64;
        break;
    case 1:
        flag81 = 16;
        G_h01_79AE = 48;
        break;
    case 2:
        flag81 = 7;
        G_h01_79AE = 32;
        break;
    }
    G_h01_79B0 = G_h01_79AE >> 2;
    play_sound(0);
    palette_cycle_callback_index = 0;
    palette_cycle_countdown_step = 0;
    F_h00_330E();
    clear_input_direction_and_fire_state();

    /* E: main input loop. Sentinel actions (-1, -2, -3) leave the loop for section F. */
    for (;;) {
        if (G_h01_799E == G_h01_79A8)
            break;
        G_h01_799C = F_h10_2BCA(G_h01_79A8, G_h01_799E);
        if (G_h01_79B2 != 0) {
            G_h01_79A4++;
            if (G_h01_79A4 == (G_h01_79AE >> 1) && G_h01_79AC == 14) {
                F_h00_3AE4(&G_h01_727C, G_h01_7274, G_h01_7276);
                G_h01_79AC = 15;
                request_disk(2);
                F_h00_291E(15, G_h01_72A2);
            } else if (G_h01_79A4 == (G_h01_79AE - G_h01_79B0) && G_h01_79AC == 15) {
                F_h00_3AE4(G_h01_72B2, G_h01_72AA, G_h01_72AC);
                G_h01_79AC = 16;
                request_disk(2);
                F_h00_291E(16, G_h01_72D8);
            }
            if ((*cell & 0x40) != 0)
                G_h01_79A6 = 1;
            phase++;
            F_h00_330E();
            request_disk(2);
            F_h00_291E(0, G_h01_46CE);
            F_h10_2FA0(cell, 1);
            if (kind == 0 || G_h01_79AA != 0)
                F_h10_2634(&G_h01_730E, 17, 0);
            if (G_h01_79A4 > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0)
                F_h00_34E0(&G_h01_788A);
            F_h00_307C();
            F_h10_2FA0(cell, 0);
            if (kind == 0 || G_h01_79AA != 0)
                F_h10_2634(&G_h01_730E, 17, 0);
            if (G_h01_79A4 > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0)
                F_h00_34E0(&G_h01_788A);
            F_h00_307C();
            G_h01_46D6 = G_h01_16A6;
            F_h00_31AA(G_h01_16A6);
            G_h01_79B2 = 0;
            if (G_h01_79AA != 0) {
                if (G_h01_79A4 > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0) {
                    F_h10_2FA0(cell, 0);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    Delay(50L);
                    total_money += 50;
                    play_sound(32);
                    F_h00_35DC(132, 128, "$50", 14, 0, 0);
                    F_h00_307C();
                    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                }
            } else {
                if (kind == 1) {
                    F_h00_291E(10, G_h01_7236);
                    F_h10_2CF4(3, 13, G_h01_0476, 10, cell);
                } else if (kind == 2) {
                    F_h00_291E(11, G_h01_7236);
                    F_h10_2CF4(0, 12, G_h01_04DA, 11, cell);
                } else if (kind == 3) {
                    F_h00_291E(12, G_h01_7236);
                    F_h10_2CF4(0, 13, G_h01_053E, 12, cell);
                } else if (kind == 4) {
                    F_h00_291E(13, G_h01_7236);
                    F_h10_2CF4(3, 15, G_h01_059A, 13, cell);
                }
                for (i = 0; i < 2; i++) {
                    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                }
            }
            *cell = *cell | 0x10;
            if ((*cell & 0x40) == 0x40) {
                action = -2;
                break;
            }
            if (G_h01_79A4 >= G_h01_79AE) {
                action = -1;
                break;
            }
            if (G_h01_79AA == 0) {
                request_disk(2);
                if (*cell & 1) {
                    F_h00_291E(18, G_h01_7344);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 4) {
                    F_h00_291E(19, G_h01_737A);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 8) {
                    F_h00_291E(20, G_h01_73E6);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 2) {
                    F_h00_291E(21, G_h01_73B0);
                    F_h10_2634(&G_h01_730E, 17, 0);
                    F_h00_307C();
                    G_h01_79B4 |= 1;
                }
                play_sound(36);
            }
            clear_input_direction_and_fire_state();
        }
        action = 0;
        action = poll_controller_and_keyboard_input();

        /* Action class from the low five bits decides the feedback draw. */
        if ((action & 31) == 1 || (action & 31) == 2) {
            if (*cell & 8) {
                F_h10_2634(&G_h01_73E6, 17, 5);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 3 || (action & 31) == 4) {
            if (*cell & 2) {
                F_h10_2634(&G_h01_73B0, 17, 4);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 7 || (action & 31) == 8) {
            if (*cell & 1) {
                F_h10_2634(&G_h01_7344, 17, 2);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 5 || (action & 31) == 6) {
            if (*cell & 4) {
                F_h10_2634(&G_h01_737A, 17, 3);
                flag82 = 0;
            } else {
                F_h10_2634(&G_h01_730E, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else {
            F_h10_2634(&G_h01_730E, 17, 0);
            flag82 = 0;
            if ((F_h00_463E() & 0xff) > 230 && tile == 0) {
                tile = F_h00_463E() % 5;
                if (tile == 0)
                    F_h00_34E0(&G_h01_777C);
                else if (tile == 1)
                    F_h00_34E0(&G_h01_77B2);
                else if (tile == 2)
                    F_h00_34E0(&G_h01_77E8);
                else if (tile == 3)
                    F_h00_34E0(&G_h01_781E);
                else
                    F_h00_34E0(&G_h01_7854);
                tile = 1;
            } else {
                tile = 0;
            }
            if (tick > 14) {
                G_h01_79A4++;
                tick = 0;
                if (G_h01_79A4 == (G_h01_79AE >> 1) && G_h01_79AC == 14) {
                    F_h00_3AE4(&G_h01_727C, G_h01_7274, G_h01_7276);
                    G_h01_79AC = 15;
                    request_disk(2);
                    F_h00_291E(15, G_h01_72A2);
                } else if (G_h01_79A4 == (G_h01_79AE - G_h01_79B0) && G_h01_79AC == 15) {
                    F_h00_3AE4(G_h01_72B2, G_h01_72AA, G_h01_72AC);
                    G_h01_79AC = 16;
                    request_disk(2);
                    F_h00_291E(16, G_h01_72D8);
                }
                if (G_h01_79A4 >= G_h01_79AE) {
                    action = -1;
                    break;
                }
            }
        }

        flag7f = 0;
        if (phase++ > flag81) {
            if ((G_h01_799E - 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 4))
                || (G_h01_799E - 1 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 2))
                || (G_h01_799E + 1 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 1))
                || (G_h01_799E + 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 8))
                || (G_h01_799E - 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 1))
                || G_h01_79A0 == G_h01_799E) {
            if (G_h01_799E + 1 == G_h01_79A0 || G_h01_79A0 == G_h01_799E)
                G_h01_79A0 = G_h01_799E - 8;
            else if (G_h01_799E + 8 == G_h01_79A0)
                G_h01_79A0 = G_h01_799E - 1;
            G_h01_79A6 = 1;
            action = -3;
            break;
            }
            if ((unsigned int)G_h01_799C <= 6) {
                dx = F_h10_2B8A();
                dy = F_h10_2BAC();
                if (dy == 0) {
                    if (dx < 0)
                        phase = 0;
                    else if (dx > 0)
                        phase = 1;
                } else if (dy < 0) {
                    phase = 2;
                } else if (dy > 0) {
                    phase = 3;
                }
            } else {
                phase = F_h00_463E() & 3;
            }
            switch (phase) {
            case 0:
                if (G_h01_79A0 > 0 && (G_h01_79A0 & 7) != 0 && last + 1 != G_h01_79A0) {
                    if (G_h01_799E + 1 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 1) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0--;
                        flag7f = 1;
                    }
                }
                break;
            case 1:
                if (G_h01_79A0 + 1 <= 63 && (G_h01_79A0 & 7) != 7 && G_h01_79A0 + 1 != last) {
                    if (G_h01_799E == G_h01_79A0 + 1 && (G_h01_4356[G_h01_79A0] & 2) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0++;
                        flag7f = 1;
                    }
                }
                break;
            case 2:
                if (G_h01_79A0 >= 8 && last + 8 != G_h01_79A0) {
                    if (G_h01_799E + 8 == G_h01_79A0 && (G_h01_4356[G_h01_79A0] & 8) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0 -= 8;
                        flag7f = 1;
                    }
                }
                break;
            case 3:
                if (G_h01_79A0 + 8 <= 63 && last != G_h01_79A0 + 8) {
                    if (G_h01_799E == G_h01_79A0 + 8 && (G_h01_4356[G_h01_79A0] & 4) == 0)
                        ;
                    else {
                        last = G_h01_79A0;
                        G_h01_79A0 += 8;
                        flag7f = 1;
                    }
                }
                break;
            }
            phase = 0;
            if (flag7f != 0) {
                play_sound(82);
                flag7f = 0;
            }
        }
        if (tick++ > 60000)
            tick = 0;
        F_h00_307C();
        if ((action & 128) && ((action & 31) == 1 || (action & 31) == 2)) {
            if (*cell & 8) {
                request_disk(2);
                play_sound(36);
                F_h10_25A2(cell);
                cell -= 8;
                G_h01_799E -= 8;
                kind = 3;
                G_h01_79B2 = 1;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    F_h00_291E(12, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(0, 10, G_h01_0572, 12, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 5 || (action & 31) == 6)) {
            if (*cell & 4) {
                play_sound(36);
                F_h10_25A2(cell);
                cell += 8;
                G_h01_799E += 8;
                G_h01_79B2 = 1;
                kind = 2;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    F_h00_291E(11, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(0, 13, G_h01_050A, 11, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 3 || (action & 31) == 4)) {
            if (*cell & 2) {
                play_sound(36);
                F_h10_25A2(cell);
                cell += 1;
                G_h01_799E += 1;
                G_h01_79B2 = 1;
                kind = 1;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    F_h00_291E(10, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(1, 12, G_h01_04AA, 10, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 7 || (action & 31) == 8)) {
            if (*cell & 1) {
                play_sound(36);
                F_h10_25A2(cell);
                cell -= 1;
                G_h01_799E -= 1;
                G_h01_79B2 = 1;
                kind = 4;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    F_h00_291E(13, G_h01_7236);
                    kind2 = kind;
                    F_h10_2CF4(2, 13, G_h01_05D6, 13, cell);
                }
            }
        }
        action = 0;
    }

    /* F: action sentinels after the loop. */
    if (action == -1) {
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        F_h10_3288();
        F_h00_3B84(G_h01_7998);
        F_h10_25A2(cell);
    } else if (action == -3) {
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        request_disk(2);
        F_h00_291E(46, &G_h01_792C);
        F_h10_2634(&G_h01_730E, 17, 0);
        G_h01_792C = 102;
        G_h01_792E = 200 - G_h01_7932;
        F_h00_291E(29, &G_h01_7596);
        F_h10_2634(&G_h01_730E, 17, 0);
        G_h01_7596 = 76;
        G_h01_7598 = 43;
        F_h00_34E0(&G_h01_792C);
        play_sound(83);
        F_h00_307C();
        F_h00_291E(30, &G_h01_75CC);
        F_h10_2634(&G_h01_730E, 17, 0);
        G_h01_75CC = 70;
        G_h01_75CE = 43;
        F_h00_34E0(&G_h01_792C);
        F_h00_307C();
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_792C);
        BltBitMap(G_h01_46D2, 0L, 0L, G_h01_46CE, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        for (i = 0; i < 16; i++) {
            BltBitMap(G_h01_46CE, 64L, 5L, G_h01_46D2, 64L, 5L, 176L, 195L, 192L, 255L, 0L);
            F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + (i & 1)));
            F_h00_34E0(&G_h01_792C);
            F_h00_307C();
        }
        F_h00_3AE4(&G_h01_75DC, G_h01_75D4, G_h01_75D6);
        F_h00_3AE4(&G_h01_75A6, G_h01_759E, G_h01_75A0);
        F_h00_3AE4(&G_h01_793C, G_h01_7934, G_h01_7936);
        F_h10_25A2(cell);
        F_h00_3B84(G_h01_7998);
        F_h00_330E();
        while (G_h01_2A16 != 0)
            ;
    } else if (action == -2) {
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        request_disk(2);
        F_h00_291E(28, &G_h01_7560);
        for (i = 0; i < 2; i++) {
            BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_7560, 17, 6);
            F_h00_307C();
        }
        F_h00_291E(29, &G_h01_7596);
        G_h01_7596 = 76;
        G_h01_7598 = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(30, &G_h01_75CC);
        G_h01_75CC = 70;
        G_h01_75CE = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(31, &G_h01_7602);
        G_h01_7602 = 88;
        G_h01_7604 = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(32, &G_h01_7638);
        G_h01_7638 = 90;
        G_h01_763A = 43;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(33, &G_h01_766E);
        G_h01_766E = 88;
        G_h01_7670 = 64;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_291E(34, &G_h01_76A4);
        G_h01_76A4 = 70;
        G_h01_76A6 = 73;
        F_h10_2634(&G_h01_7560, 17, 6);
        F_h00_307C();
        F_h00_3AE4(&G_h01_7570, G_h01_7568, G_h01_756A);
        F_h00_3B84(G_h01_7998);
        F_h00_291E(35, &G_h01_76DA);
        G_h01_76DA = 61;
        G_h01_76DC = 54;
        F_h00_291E(36, &G_h01_7710);
        G_h01_7710 = 70;
        G_h01_7712 = 42;
        play_sound(0);
        for (i = 0; i < 2; i++) {
            BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_730E, 17, 0);
            F_h00_307C();
        }
        F_h00_4EC6();
        request_disk(2);
        F_h00_4D04(22);
        request_disk(2);
        arc_read_index(arc_file);
        play_sound(72);
        for (j = 0; j < 4; j++) {
            for (i = 0; i < 3; i++) {
                if (j == 0)
                    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                else
                    BltBitMap(G_h01_46CE, 64L, 40L, G_h01_46D2, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
                F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + i));
                F_h00_307C();
            }
            if (j == 0)
                BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            else
                BltBitMap(G_h01_46CE, 64L, 40L, G_h01_46D2, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
            F_h00_34E0(&G_h01_75CC);
            F_h00_307C();
        }
        for (i = 0; i < 3; i++) {
            BltBitMap(G_h01_46CE, 64L, 40L, G_h01_46D2, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
            F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + i));
            F_h00_307C();
        }
        F_h00_4EC6();
        request_disk(2);
        F_h00_4D04(40);
        request_disk(2);
        arc_read_index(arc_file);
        play_sound(71);
        for (i = 3; i < 8; i++) {
            BltBitMap(G_h01_46CE, 64L, 10L, G_h01_46D2, 64L, 10L, 176L, 190L, 192L, 255L, 0L);
            F_h00_34E0((char *)((struct Rec54 *)&G_h01_7596 + i));
            F_h00_307C();
            Delay(1L);
        }
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
        for (i = 0; i < 8; i++)
            F_h00_3AE4((char *)((struct Rec54 *)&G_h01_75A6 + i), *(short *)((struct Rec54 *)&G_h01_759E + i),
                       *(short *)((struct Rec54 *)&G_h01_75A0 + i));
        while (G_h01_2A16 != 0)
            ;
    } else {
        G_h01_79A6 = 1;
        F_h10_25A2(cell);
        request_disk(2);
        F_h00_291E(44, &G_h01_78C0);
        F_h00_291E(45, &G_h01_78F6);
        G_h01_78F6 = 96;
        G_h01_78F8 = 94;
        F_h00_330E();
        F_h00_291E(0, G_h01_46CE);
        F_h10_2FA0(cell, 0);
        F_h10_2634(&G_h01_730E, 17, 0);
        F_h00_34E0(&G_h01_78F6);
        F_h00_34E0(&G_h01_7452);
        F_h00_307C();
        G_h01_46D6 = G_h01_16A6;
        F_h00_31AA(G_h01_16A6);
        F_h10_2FA0(cell, 0);
        F_h10_2634(&G_h01_730E, 17, 0);
        F_h00_34E0(&G_h01_78F6);
        F_h00_34E0(&G_h01_7452);
        F_h00_307C();
        for (i = 0; i < 3; i++) {
            BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_730E, 17, 0);
            F_h00_34E0(&G_h01_78F6);
            F_h00_34E0(&G_h01_7452);
            F_h00_307C();
        }
        G_h01_79A6 = 2;
        F_h00_4EC6();
        request_disk(2);
        F_h00_4D04(24);
        request_disk(2);
        arc_read_index(arc_file);
        play_sound(73);
        for (i = 0; i < 10; i++) {
            BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_78C0, 17, 0);
            F_h00_34E0(&G_h01_78F6);
            F_h00_34E0(&G_h01_7452);
            F_h00_307C();
        }
        F_h00_3AE4(&G_h01_78D0, G_h01_78C8, G_h01_78CA);
        F_h00_3AE4(&G_h01_7906, G_h01_78FE, G_h01_7900);
        F_h00_3AE4(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        F_h00_3AE4(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        F_h00_3AE4(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        F_h00_3AE4(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 1;
        while (G_h01_2A16 != 0)
            ;
        F_h00_4EC6();
        F_h00_3B84(G_h01_7998);
    }

    /* G: teardown, restore the saved map handle, return the result word. */
    play_sound(0);
    switch (G_h01_79AC) {
    case 14:
        F_h00_3AE4(&G_h01_727C, G_h01_7274, G_h01_7276);
        break;
    case 15:
        F_h00_3AE4(&G_h01_72B2, G_h01_72AA, G_h01_72AC);
        break;
    case 16:
        F_h00_3AE4(&G_h01_72E8, G_h01_72E0, G_h01_72E2);
        break;
    }
    F_h00_3AE4(&G_h01_7462, G_h01_745A, G_h01_745C);
    F_h00_3AE4(&G_h01_742C, G_h01_7424, G_h01_7426);
    F_h00_3AE4(&G_h01_731E, G_h01_7316, G_h01_7318);
    if (G_h01_79AA != 0) {
        F_h00_3AE4(&G_h01_7354, G_h01_734C, G_h01_734E);
        F_h00_3AE4(&G_h01_738A, G_h01_7382, G_h01_7384);
        F_h00_3AE4(&G_h01_73C0, G_h01_73B8, G_h01_73BA);
        F_h00_3AE4(&G_h01_73F6, G_h01_73EE, G_h01_73F0);
    }
    F_h00_3AE4(&G_h01_7504, G_h01_74FC, G_h01_74FE);
    F_h00_3AE4(&G_h01_778C, G_h01_7784, G_h01_7786);
    F_h00_3AE4(&G_h01_77C2, G_h01_77BA, G_h01_77BC);
    F_h00_3AE4(&G_h01_77F8, G_h01_77F0, G_h01_77F2);
    F_h00_3AE4(&G_h01_782E, G_h01_7826, G_h01_7828);
    F_h00_3AE4(&G_h01_7864, G_h01_785C, G_h01_785E);
    F_h00_3AE4(&G_h01_7756, G_h01_774E, G_h01_7750);
    F_h00_3AE4(&G_h01_789A, G_h01_7892, G_h01_7894);
    Close(arc_file);
    arc_file = saved_handle;
    arc_read_index(arc_file);
    F_h00_330E();
    F_h00_4EC6();
    if (res == 0) {
        request_disk(1);
        arc_read_index(arc_file);
        F_h00_330E();
        F_h00_291E(34, G_h01_46CE);
        BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_35DC(176, 60, "Launchpad McQuack", 1, 0);
        F_h00_35DC(188, 76, "saves the day!", 1, 0);
        F_h00_307C();
        G_h01_46D6 = G_h01_1726;
        F_h00_31AA(G_h01_1726);
        if (wait_for_fire_input(20) != 0)
            play_sound(36);
        F_h00_4EC6();
    }
    return res;
}
