/* ov10_F_0000: cave-map load, 8x8 grid state machine, action dispatch. Three unused locals (c1, c2, i1) are kept: the original 134-byte frame and its slot offsets require them. */
struct Rec54 { char b[54]; };
extern char G_h01_5E5E;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern long arc_file;
extern char difficulty_level;
extern long total_money;
extern short cave_cell_words[64];
extern long G_h01_7998;
extern unsigned int cave_player_cell_index;
extern unsigned int cave_wandering_actor_cell_index;
extern unsigned int cave_finish_cell_index;
extern short cave_player_to_finish_distance;
extern char G_h01_79A2;
extern char cave_elapsed_time_ticks;
extern char G_h01_79A5;
extern char G_h01_79A6;
extern char G_h01_79AA;
extern short G_h01_79AC;
extern short cave_time_limit;
extern short G_h01_79B0;
extern short cave_movement_animation_pending;
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
extern short cave_player_sprite_record;
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
extern long load_arc_record();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int fade_palette_to_black();
extern int draw_masked_sprite();
extern int draw_text();
extern int free_bitmap_planes();
extern int free_bitmap();
extern int free_text_block();
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
extern int draw_cave_map();
extern int reset_cave_direction_animations();
extern int draw_cave_actor_sprite();
extern int cave_column_delta();
extern int cave_row_delta();
extern int cave_cell_manhattan_distance();
extern int play_cave_traversal_event();
extern int draw_cave_cell_scene();
extern int play_cave_timeout_sequence();

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
        cave_cell_words[i] = 0;

    /* B: open cave map, parse 8 rows of 8 cell words. */
    request_disk(2);
    arc_file = Open("DT2:cavemaps.arc", 1005L);
    arc_read_index(arc_file);
    bitmap = load_arc_record(arg, 0L);
    text = *(char **)(bitmap + 2);
    for (i = 0; i < 64; i += 8) {
        text = (char *)F_h00_0976(text, line);
        sscanf(line, "%d %d %d %d %d %d %d %d",
                   &cave_cell_words[i], &cave_cell_words[i + 1], &cave_cell_words[i + 2], &cave_cell_words[i + 3],
                   &cave_cell_words[i + 4], &cave_cell_words[i + 5], &cave_cell_words[i + 6], &cave_cell_words[i + 7]);
    }
    free_text_block(bitmap);
    Close(arc_file);

    /* C: open exp.arc, draw static panels, set panel geometry. */
    request_disk(2);
    arc_file = Open("DT2:exp.arc", 1005L);
    arc_read_index(arc_file);
    exp_handle = arc_file;
    load_arc_record(17, &cave_player_sprite_record);
    cave_player_sprite_record = 82;
    G_h01_7310 = 38;
    if (G_h01_79AA != 0) {
        load_arc_record(18, G_h01_7344);
        load_arc_record(19, G_h01_737A);
        load_arc_record(20, G_h01_73E6);
        load_arc_record(21, G_h01_73B0);
    }
    load_arc_record(4, &G_h01_79B6);
    G_h01_79B6 = 220;
    G_h01_79B8 = 40;
    load_arc_record(5, &G_h01_79EC);
    G_h01_79EC = 0;
    G_h01_79EE = 144;
    load_arc_record(6, &G_h01_7A22);
    G_h01_7A22 = 240;
    G_h01_7A24 = 122;
    load_arc_record(3, &G_h01_7A58);
    G_h01_7A58 = 40;
    G_h01_7A5A = 24;
    load_arc_record(22, &G_h01_7452);
    G_h01_7452 = 71;
    G_h01_7454 = 141;
    load_arc_record(23, &G_h01_741C);
    G_h01_741C = 176;
    G_h01_741E = 110;
    load_arc_record(26, &G_h01_74F4);
    G_h01_74F4 = 141;
    G_h01_74F6 = 3;
    load_arc_record(37, &G_h01_7746);
    G_h01_7746 = 112;
    G_h01_7748 = 137;
    load_arc_record(38, &G_h01_777C);
    load_arc_record(39, &G_h01_77B2);
    load_arc_record(40, &G_h01_77E8);
    load_arc_record(41, &G_h01_781E);
    load_arc_record(42, &G_h01_7854);
    load_arc_record(43, &G_h01_788A);
    G_h01_777C = cave_player_sprite_record + 16;
    G_h01_77B2 = cave_player_sprite_record + 28;
    G_h01_77E8 = cave_player_sprite_record + 53;
    G_h01_781E = cave_player_sprite_record + 99;
    G_h01_7854 = cave_player_sprite_record + 112;
    G_h01_777E = G_h01_7310 + 61;
    G_h01_77B4 = G_h01_7310 + 39;
    G_h01_77EA = G_h01_7310 + 15;
    G_h01_7820 = G_h01_7310 + 41;
    G_h01_7856 = G_h01_7310 + 59;
    G_h01_788A = 160;
    G_h01_788C = 115;
    G_h01_7998 = 0;
    G_h01_7998 = load_arc_record(47, G_h01_7998);
    load_arc_record(14, G_h01_726C);
    G_h01_79AC = 14;
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(21);
    arc_file = exp_handle;
    request_disk(2);
    arc_read_index(arc_file);
    SetRast(screen_rast_port, 0L);
    draw_masked_sprite(&G_h01_7746);

    /* D: locate the marked start cell (bit 5) and the goal cell (bit 4). */
    grid_base = (long)(cell = cave_cell_words);
    draw_cave_map(cell);
    for (i = 0; i < 64; i++, cell++) {
        if (*cell & 0x20)
            cave_finish_cell_index = i;
        else if (*cell & 0x10)
            cave_player_cell_index = i;
    }
    for (;;) {
        if ((cave_wandering_actor_cell_index = F_h00_463E() & 63) != cave_player_cell_index)
            break;
    }
    cell = cave_cell_words + cave_player_cell_index;
    cave_movement_animation_pending = 1;
    kind = 0;
    kind2 = 0;
    G_h01_79A2 = 0;
    cave_elapsed_time_ticks = 0;
    G_h01_79A5 = 0;
    switch (difficulty_level) {
    case 0:
        flag81 = 20;
        cave_time_limit = 64;
        break;
    case 1:
        flag81 = 16;
        cave_time_limit = 48;
        break;
    case 2:
        flag81 = 7;
        cave_time_limit = 32;
        break;
    }
    G_h01_79B0 = cave_time_limit >> 2;
    play_sound(0);
    palette_cycle_callback_index = 0;
    palette_cycle_countdown_step = 0;
    fade_palette_to_black();
    clear_input_direction_and_fire_state();

    /* E: main input loop. Sentinel actions (-1, -2, -3) leave the loop for section F. */
    for (;;) {
        if (cave_player_cell_index == cave_finish_cell_index)
            break;
        cave_player_to_finish_distance = cave_cell_manhattan_distance(cave_finish_cell_index, cave_player_cell_index);
        if (cave_movement_animation_pending != 0) {
            cave_elapsed_time_ticks++;
            if (cave_elapsed_time_ticks == (cave_time_limit >> 1) && G_h01_79AC == 14) {
                free_bitmap_planes(&G_h01_727C, G_h01_7274, G_h01_7276);
                G_h01_79AC = 15;
                request_disk(2);
                load_arc_record(15, G_h01_72A2);
            } else if (cave_elapsed_time_ticks == (cave_time_limit - G_h01_79B0) && G_h01_79AC == 15) {
                free_bitmap_planes(G_h01_72B2, G_h01_72AA, G_h01_72AC);
                G_h01_79AC = 16;
                request_disk(2);
                load_arc_record(16, G_h01_72D8);
            }
            if ((*cell & 0x40) != 0)
                G_h01_79A6 = 1;
            phase++;
            fade_palette_to_black();
            request_disk(2);
            load_arc_record(0, archive_image_bitmap);
            draw_cave_cell_scene(cell, 1);
            if (kind == 0 || G_h01_79AA != 0)
                draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
            if (cave_elapsed_time_ticks > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0)
                draw_masked_sprite(&G_h01_788A);
            switch_display_buffer();
            draw_cave_cell_scene(cell, 0);
            if (kind == 0 || G_h01_79AA != 0)
                draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
            if (cave_elapsed_time_ticks > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0)
                draw_masked_sprite(&G_h01_788A);
            switch_display_buffer();
            palette_fade_target = G_h01_16A6;
            fade_palette_to_target(G_h01_16A6);
            cave_movement_animation_pending = 0;
            if (G_h01_79AA != 0) {
                if (cave_elapsed_time_ticks > 1 && (*cell & 0x10) == 0 && (*cell & 0x40) == 0) {
                    draw_cave_cell_scene(cell, 0);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    Delay(50L);
                    total_money += 50;
                    play_sound(32);
                    draw_text(132, 128, "$50", 14, 0, 0);
                    switch_display_buffer();
                    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
                    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
                }
            } else {
                if (kind == 1) {
                    load_arc_record(10, G_h01_7236);
                    play_cave_traversal_event(3, 13, G_h01_0476, 10, cell);
                } else if (kind == 2) {
                    load_arc_record(11, G_h01_7236);
                    play_cave_traversal_event(0, 12, G_h01_04DA, 11, cell);
                } else if (kind == 3) {
                    load_arc_record(12, G_h01_7236);
                    play_cave_traversal_event(0, 13, G_h01_053E, 12, cell);
                } else if (kind == 4) {
                    load_arc_record(13, G_h01_7236);
                    play_cave_traversal_event(3, 15, G_h01_059A, 13, cell);
                }
                for (i = 0; i < 2; i++) {
                    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
                }
            }
            *cell = *cell | 0x10;
            if ((*cell & 0x40) == 0x40) {
                action = -2;
                break;
            }
            if (cave_elapsed_time_ticks >= cave_time_limit) {
                action = -1;
                break;
            }
            if (G_h01_79AA == 0) {
                request_disk(2);
                if (*cell & 1) {
                    load_arc_record(18, G_h01_7344);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 4) {
                    load_arc_record(19, G_h01_737A);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 8) {
                    load_arc_record(20, G_h01_73E6);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
                    G_h01_79B4 |= 1;
                }
                if (*cell & 2) {
                    load_arc_record(21, G_h01_73B0);
                    draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                    switch_display_buffer();
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
                draw_cave_actor_sprite(&G_h01_73E6, 17, 5);
                flag82 = 0;
            } else {
                draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 3 || (action & 31) == 4) {
            if (*cell & 2) {
                draw_cave_actor_sprite(&G_h01_73B0, 17, 4);
                flag82 = 0;
            } else {
                draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 7 || (action & 31) == 8) {
            if (*cell & 1) {
                draw_cave_actor_sprite(&G_h01_7344, 17, 2);
                flag82 = 0;
            } else {
                draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else if ((action & 31) == 5 || (action & 31) == 6) {
            if (*cell & 4) {
                draw_cave_actor_sprite(&G_h01_737A, 17, 3);
                flag82 = 0;
            } else {
                draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
                if (flag82 == 0) {
                    play_sound(70);
                    flag82 = 1;
                }
            }
        } else {
            draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
            flag82 = 0;
            if ((F_h00_463E() & 0xff) > 230 && tile == 0) {
                tile = F_h00_463E() % 5;
                if (tile == 0)
                    draw_masked_sprite(&G_h01_777C);
                else if (tile == 1)
                    draw_masked_sprite(&G_h01_77B2);
                else if (tile == 2)
                    draw_masked_sprite(&G_h01_77E8);
                else if (tile == 3)
                    draw_masked_sprite(&G_h01_781E);
                else
                    draw_masked_sprite(&G_h01_7854);
                tile = 1;
            } else {
                tile = 0;
            }
            if (tick > 14) {
                cave_elapsed_time_ticks++;
                tick = 0;
                if (cave_elapsed_time_ticks == (cave_time_limit >> 1) && G_h01_79AC == 14) {
                    free_bitmap_planes(&G_h01_727C, G_h01_7274, G_h01_7276);
                    G_h01_79AC = 15;
                    request_disk(2);
                    load_arc_record(15, G_h01_72A2);
                } else if (cave_elapsed_time_ticks == (cave_time_limit - G_h01_79B0) && G_h01_79AC == 15) {
                    free_bitmap_planes(G_h01_72B2, G_h01_72AA, G_h01_72AC);
                    G_h01_79AC = 16;
                    request_disk(2);
                    load_arc_record(16, G_h01_72D8);
                }
                if (cave_elapsed_time_ticks >= cave_time_limit) {
                    action = -1;
                    break;
                }
            }
        }

        flag7f = 0;
        if (phase++ > flag81) {
            if ((cave_player_cell_index - 8 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 4))
                || (cave_player_cell_index - 1 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 2))
                || (cave_player_cell_index + 1 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 1))
                || (cave_player_cell_index + 8 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 8))
                || (cave_player_cell_index - 8 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 1))
                || cave_wandering_actor_cell_index == cave_player_cell_index) {
            if (cave_player_cell_index + 1 == cave_wandering_actor_cell_index || cave_wandering_actor_cell_index == cave_player_cell_index)
                cave_wandering_actor_cell_index = cave_player_cell_index - 8;
            else if (cave_player_cell_index + 8 == cave_wandering_actor_cell_index)
                cave_wandering_actor_cell_index = cave_player_cell_index - 1;
            G_h01_79A6 = 1;
            action = -3;
            break;
            }
            if ((unsigned int)cave_player_to_finish_distance <= 6) {
                dx = cave_column_delta();
                dy = cave_row_delta();
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
                if (cave_wandering_actor_cell_index > 0 && (cave_wandering_actor_cell_index & 7) != 0 && last + 1 != cave_wandering_actor_cell_index) {
                    if (cave_player_cell_index + 1 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 1) == 0)
                        ;
                    else {
                        last = cave_wandering_actor_cell_index;
                        cave_wandering_actor_cell_index--;
                        flag7f = 1;
                    }
                }
                break;
            case 1:
                if (cave_wandering_actor_cell_index + 1 <= 63 && (cave_wandering_actor_cell_index & 7) != 7 && cave_wandering_actor_cell_index + 1 != last) {
                    if (cave_player_cell_index == cave_wandering_actor_cell_index + 1 && (cave_cell_words[cave_wandering_actor_cell_index] & 2) == 0)
                        ;
                    else {
                        last = cave_wandering_actor_cell_index;
                        cave_wandering_actor_cell_index++;
                        flag7f = 1;
                    }
                }
                break;
            case 2:
                if (cave_wandering_actor_cell_index >= 8 && last + 8 != cave_wandering_actor_cell_index) {
                    if (cave_player_cell_index + 8 == cave_wandering_actor_cell_index && (cave_cell_words[cave_wandering_actor_cell_index] & 8) == 0)
                        ;
                    else {
                        last = cave_wandering_actor_cell_index;
                        cave_wandering_actor_cell_index -= 8;
                        flag7f = 1;
                    }
                }
                break;
            case 3:
                if (cave_wandering_actor_cell_index + 8 <= 63 && last != cave_wandering_actor_cell_index + 8) {
                    if (cave_player_cell_index == cave_wandering_actor_cell_index + 8 && (cave_cell_words[cave_wandering_actor_cell_index] & 4) == 0)
                        ;
                    else {
                        last = cave_wandering_actor_cell_index;
                        cave_wandering_actor_cell_index += 8;
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
        switch_display_buffer();
        if ((action & 128) && ((action & 31) == 1 || (action & 31) == 2)) {
            if (*cell & 8) {
                request_disk(2);
                play_sound(36);
                reset_cave_direction_animations(cell);
                cell -= 8;
                cave_player_cell_index -= 8;
                kind = 3;
                cave_movement_animation_pending = 1;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    load_arc_record(12, G_h01_7236);
                    kind2 = kind;
                    play_cave_traversal_event(0, 10, G_h01_0572, 12, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 5 || (action & 31) == 6)) {
            if (*cell & 4) {
                play_sound(36);
                reset_cave_direction_animations(cell);
                cell += 8;
                cave_player_cell_index += 8;
                cave_movement_animation_pending = 1;
                kind = 2;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    load_arc_record(11, G_h01_7236);
                    kind2 = kind;
                    play_cave_traversal_event(0, 13, G_h01_050A, 11, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 3 || (action & 31) == 4)) {
            if (*cell & 2) {
                play_sound(36);
                reset_cave_direction_animations(cell);
                cell += 1;
                cave_player_cell_index += 1;
                cave_movement_animation_pending = 1;
                kind = 1;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    load_arc_record(10, G_h01_7236);
                    kind2 = kind;
                    play_cave_traversal_event(1, 12, G_h01_04AA, 10, cell);
                }
            }
        } else if ((action & 128) && ((action & 31) == 7 || (action & 31) == 8)) {
            if (*cell & 1) {
                play_sound(36);
                reset_cave_direction_animations(cell);
                cell -= 1;
                cave_player_cell_index -= 1;
                cave_movement_animation_pending = 1;
                kind = 4;
                phase++;
                if (G_h01_79AA == 0) {
                    request_disk(2);
                    load_arc_record(13, G_h01_7236);
                    kind2 = kind;
                    play_cave_traversal_event(2, 13, G_h01_05D6, 13, cell);
                }
            }
        }
        action = 0;
    }

    /* F: action sentinels after the loop. */
    if (action == -1) {
        free_bitmap_planes(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        free_bitmap_planes(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        free_bitmap_planes(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        free_bitmap_planes(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        play_cave_timeout_sequence();
        free_bitmap(G_h01_7998);
        reset_cave_direction_animations(cell);
    } else if (action == -3) {
        free_bitmap_planes(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        free_bitmap_planes(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        free_bitmap_planes(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        free_bitmap_planes(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        request_disk(2);
        load_arc_record(46, &G_h01_792C);
        draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
        G_h01_792C = 102;
        G_h01_792E = 200 - G_h01_7932;
        load_arc_record(29, &G_h01_7596);
        draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
        G_h01_7596 = 76;
        G_h01_7598 = 43;
        draw_masked_sprite(&G_h01_792C);
        play_sound(83);
        switch_display_buffer();
        load_arc_record(30, &G_h01_75CC);
        draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
        G_h01_75CC = 70;
        G_h01_75CE = 43;
        draw_masked_sprite(&G_h01_792C);
        switch_display_buffer();
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        draw_masked_sprite(&G_h01_792C);
        BltBitMap(active_screen_bitmap, 0L, 0L, archive_image_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        for (i = 0; i < 16; i++) {
            BltBitMap(archive_image_bitmap, 64L, 5L, active_screen_bitmap, 64L, 5L, 176L, 195L, 192L, 255L, 0L);
            draw_masked_sprite((char *)((struct Rec54 *)&G_h01_7596 + (i & 1)));
            draw_masked_sprite(&G_h01_792C);
            switch_display_buffer();
        }
        free_bitmap_planes(&G_h01_75DC, G_h01_75D4, G_h01_75D6);
        free_bitmap_planes(&G_h01_75A6, G_h01_759E, G_h01_75A0);
        free_bitmap_planes(&G_h01_793C, G_h01_7934, G_h01_7936);
        reset_cave_direction_animations(cell);
        free_bitmap(G_h01_7998);
        fade_palette_to_black();
        while (G_h01_2A16 != 0)
            ;
    } else if (action == -2) {
        free_bitmap_planes(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        free_bitmap_planes(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        free_bitmap_planes(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        free_bitmap_planes(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 0;
        request_disk(2);
        load_arc_record(28, &G_h01_7560);
        for (i = 0; i < 2; i++) {
            BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            draw_cave_actor_sprite(&G_h01_7560, 17, 6);
            switch_display_buffer();
        }
        load_arc_record(29, &G_h01_7596);
        G_h01_7596 = 76;
        G_h01_7598 = 43;
        draw_cave_actor_sprite(&G_h01_7560, 17, 6);
        switch_display_buffer();
        load_arc_record(30, &G_h01_75CC);
        G_h01_75CC = 70;
        G_h01_75CE = 43;
        draw_cave_actor_sprite(&G_h01_7560, 17, 6);
        switch_display_buffer();
        load_arc_record(31, &G_h01_7602);
        G_h01_7602 = 88;
        G_h01_7604 = 43;
        draw_cave_actor_sprite(&G_h01_7560, 17, 6);
        switch_display_buffer();
        load_arc_record(32, &G_h01_7638);
        G_h01_7638 = 90;
        G_h01_763A = 43;
        draw_cave_actor_sprite(&G_h01_7560, 17, 6);
        switch_display_buffer();
        load_arc_record(33, &G_h01_766E);
        G_h01_766E = 88;
        G_h01_7670 = 64;
        draw_cave_actor_sprite(&G_h01_7560, 17, 6);
        switch_display_buffer();
        load_arc_record(34, &G_h01_76A4);
        G_h01_76A4 = 70;
        G_h01_76A6 = 73;
        draw_cave_actor_sprite(&G_h01_7560, 17, 6);
        switch_display_buffer();
        free_bitmap_planes(&G_h01_7570, G_h01_7568, G_h01_756A);
        free_bitmap(G_h01_7998);
        load_arc_record(35, &G_h01_76DA);
        G_h01_76DA = 61;
        G_h01_76DC = 54;
        load_arc_record(36, &G_h01_7710);
        G_h01_7710 = 70;
        G_h01_7712 = 42;
        play_sound(0);
        for (i = 0; i < 2; i++) {
            BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
            switch_display_buffer();
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
                    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
                else
                    BltBitMap(archive_image_bitmap, 64L, 40L, active_screen_bitmap, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
                draw_masked_sprite((char *)((struct Rec54 *)&G_h01_7596 + i));
                switch_display_buffer();
            }
            if (j == 0)
                BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            else
                BltBitMap(archive_image_bitmap, 64L, 40L, active_screen_bitmap, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
            draw_masked_sprite(&G_h01_75CC);
            switch_display_buffer();
        }
        for (i = 0; i < 3; i++) {
            BltBitMap(archive_image_bitmap, 64L, 40L, active_screen_bitmap, 64L, 40L, 176L, 160L, 192L, 255L, 0L);
            draw_masked_sprite((char *)((struct Rec54 *)&G_h01_7596 + i));
            switch_display_buffer();
        }
        F_h00_4EC6();
        request_disk(2);
        F_h00_4D04(40);
        request_disk(2);
        arc_read_index(arc_file);
        play_sound(71);
        for (i = 3; i < 8; i++) {
            BltBitMap(archive_image_bitmap, 64L, 10L, active_screen_bitmap, 64L, 10L, 176L, 190L, 192L, 255L, 0L);
            draw_masked_sprite((char *)((struct Rec54 *)&G_h01_7596 + i));
            switch_display_buffer();
            Delay(1L);
        }
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch_display_buffer();
        for (i = 0; i < 8; i++)
            free_bitmap_planes((char *)((struct Rec54 *)&G_h01_75A6 + i), *(short *)((struct Rec54 *)&G_h01_759E + i),
                       *(short *)((struct Rec54 *)&G_h01_75A0 + i));
        while (G_h01_2A16 != 0)
            ;
    } else {
        G_h01_79A6 = 1;
        reset_cave_direction_animations(cell);
        request_disk(2);
        load_arc_record(44, &G_h01_78C0);
        load_arc_record(45, &G_h01_78F6);
        G_h01_78F6 = 96;
        G_h01_78F8 = 94;
        fade_palette_to_black();
        load_arc_record(0, archive_image_bitmap);
        draw_cave_cell_scene(cell, 0);
        draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
        draw_masked_sprite(&G_h01_78F6);
        draw_masked_sprite(&G_h01_7452);
        switch_display_buffer();
        palette_fade_target = G_h01_16A6;
        fade_palette_to_target(G_h01_16A6);
        draw_cave_cell_scene(cell, 0);
        draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
        draw_masked_sprite(&G_h01_78F6);
        draw_masked_sprite(&G_h01_7452);
        switch_display_buffer();
        for (i = 0; i < 3; i++) {
            BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            draw_cave_actor_sprite(&cave_player_sprite_record, 17, 0);
            draw_masked_sprite(&G_h01_78F6);
            draw_masked_sprite(&G_h01_7452);
            switch_display_buffer();
        }
        G_h01_79A6 = 2;
        F_h00_4EC6();
        request_disk(2);
        F_h00_4D04(24);
        request_disk(2);
        arc_read_index(arc_file);
        play_sound(73);
        for (i = 0; i < 10; i++) {
            BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            draw_cave_actor_sprite(&G_h01_78C0, 17, 0);
            draw_masked_sprite(&G_h01_78F6);
            draw_masked_sprite(&G_h01_7452);
            switch_display_buffer();
        }
        free_bitmap_planes(&G_h01_78D0, G_h01_78C8, G_h01_78CA);
        free_bitmap_planes(&G_h01_7906, G_h01_78FE, G_h01_7900);
        free_bitmap_planes(&G_h01_79C6, G_h01_79BE, G_h01_79C0);
        free_bitmap_planes(&G_h01_79FC, G_h01_79F4, G_h01_79F6);
        free_bitmap_planes(&G_h01_7A68, G_h01_7A60, G_h01_7A62);
        free_bitmap_planes(&G_h01_7A32, G_h01_7A2A, G_h01_7A2C);
        res = 1;
        while (G_h01_2A16 != 0)
            ;
        F_h00_4EC6();
        free_bitmap(G_h01_7998);
    }

    /* G: teardown, restore the saved map handle, return the result word. */
    play_sound(0);
    switch (G_h01_79AC) {
    case 14:
        free_bitmap_planes(&G_h01_727C, G_h01_7274, G_h01_7276);
        break;
    case 15:
        free_bitmap_planes(&G_h01_72B2, G_h01_72AA, G_h01_72AC);
        break;
    case 16:
        free_bitmap_planes(&G_h01_72E8, G_h01_72E0, G_h01_72E2);
        break;
    }
    free_bitmap_planes(&G_h01_7462, G_h01_745A, G_h01_745C);
    free_bitmap_planes(&G_h01_742C, G_h01_7424, G_h01_7426);
    free_bitmap_planes(&G_h01_731E, G_h01_7316, G_h01_7318);
    if (G_h01_79AA != 0) {
        free_bitmap_planes(&G_h01_7354, G_h01_734C, G_h01_734E);
        free_bitmap_planes(&G_h01_738A, G_h01_7382, G_h01_7384);
        free_bitmap_planes(&G_h01_73C0, G_h01_73B8, G_h01_73BA);
        free_bitmap_planes(&G_h01_73F6, G_h01_73EE, G_h01_73F0);
    }
    free_bitmap_planes(&G_h01_7504, G_h01_74FC, G_h01_74FE);
    free_bitmap_planes(&G_h01_778C, G_h01_7784, G_h01_7786);
    free_bitmap_planes(&G_h01_77C2, G_h01_77BA, G_h01_77BC);
    free_bitmap_planes(&G_h01_77F8, G_h01_77F0, G_h01_77F2);
    free_bitmap_planes(&G_h01_782E, G_h01_7826, G_h01_7828);
    free_bitmap_planes(&G_h01_7864, G_h01_785C, G_h01_785E);
    free_bitmap_planes(&G_h01_7756, G_h01_774E, G_h01_7750);
    free_bitmap_planes(&G_h01_789A, G_h01_7892, G_h01_7894);
    Close(arc_file);
    arc_file = saved_handle;
    arc_read_index(arc_file);
    fade_palette_to_black();
    F_h00_4EC6();
    if (res == 0) {
        request_disk(1);
        arc_read_index(arc_file);
        fade_palette_to_black();
        load_arc_record(34, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        draw_text(176, 60, "Launchpad McQuack", 1, 0);
        draw_text(188, 76, "saves the day!", 1, 0);
        switch_display_buffer();
        palette_fade_target = G_h01_1726;
        fade_palette_to_target(G_h01_1726);
        if (wait_for_fire_input(20) != 0)
            play_sound(36);
        F_h00_4EC6();
    }
    return res;
}
