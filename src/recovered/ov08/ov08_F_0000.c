struct Entry { unsigned char kind; char active; char rest[4]; };
struct Slot { int x; int y; int t; char pad[46]; char st; char tail; };
struct Sprite { int x; int y; int t; int u; int w; int h; long p; char data[36]; char st; char tail; };
extern char *grid_collision_map;
extern struct Entry *grid_entity_state_table;
extern char *G_h01_6EB4;
extern char G_h01_6EB8[54];
extern char G_h01_6EEE[54];
extern char G_h01_6EFE[1];
extern int G_h01_6EF6;
extern int G_h01_6EF8;
extern int G_h01_6EC0;
extern int G_h01_6EC2;
extern char G_h01_6EC8[1];
extern char G_h01_0AA2[32];
extern char G_h01_0AC4[1];
extern char G_h01_0CD2[1];
extern char G_h01_0EE0[1];
extern char G_h01_10F2[1];
extern char G_h01_1188[1];
extern char G_h01_121E[1];
extern char G_h01_15E6[1];
extern int G_h01_1608;
extern int G_h01_160A;
extern int G_h01_160C;
extern int G_h01_160E;
extern char palette_cycle_countdown_step;
extern long palette_cycle_callback_index;
extern char G_h01_12BB;
extern char G_h01_34CE;
extern int G_h01_349A;
extern int G_h01_349C;
extern int G_h01_345A;
extern int G_h01_3424;
extern int G_h01_33EE;
extern int G_h01_34D0[16];
extern int G_h01_34D4[16];
extern int G_h01_34D8[16];
extern int G_h01_34DC[16];
extern int G_h01_34E0;
extern char G_h01_34E1;
extern int grid_player_screen_x;
extern int grid_player_screen_y;
extern int G_h01_6F28;
extern int grid_player_map_row;
extern int grid_player_map_column;
extern int grid_player_action_state;
extern int grid_player_facing_direction;
extern int grid_player_action_countdown;
extern char G_h01_6F36;
extern char G_h01_6F37;
extern int G_h01_6F38;
extern unsigned char G_h01_6F3A;
extern unsigned char grid_lives_remaining;
extern unsigned char grid_stationary_hazard_counter;
extern long grid_background_bitmap;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern long arc_file;
extern long total_money;
extern char difficulty_level;
extern char *G_h01_5370;
extern int clear_input_direction_and_fire_state();
extern int play_sound();
extern int request_disk();
extern long Open();
extern int arc_read_index();
extern long load_arc_record();
extern int load_grid_archive_records();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int fade_palette_to_black();
extern int reset_grid_entity_activity_for_game();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int BltBitMap();
extern int draw_grid_map_rows();
extern int draw_grid_status_panel();
extern int advance_grid_player_and_entities();
extern int draw_masked_sprite();
extern int copy_palette_to_copper_lists();
extern int reset_grid_entity_activity_for_life();
extern int poll_controller_and_keyboard_input();
extern int mul36();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int draw_decimal_value();
extern int refresh_grid_view();
extern int free_bitmap_planes();
extern int free_bitmap();
extern int F_h08_3F70();
extern int Close();
extern int G_h01_3426;
extern int G_h01_33F0;
extern int G_h01_33F6;
extern int G_h01_33F8;
extern int G_h01_33FE;
extern int G_h01_342C;
extern int G_h01_342E;
extern int G_h01_3434;
extern int G_h01_3462;
extern int G_h01_3464;
extern int G_h01_346A;
extern int G_h01_34A2;
extern int G_h01_34A4;
extern int G_h01_34AA;
extern int G_h01_349C;
extern char G_h01_6F29;
extern int G_h01_6F38;

recovered(P)
int P;
{
    long saved;
    long handle;
    struct Sprite spr;
    int local40, local42, local44, local46, local48, local4a, local4c, local4e;
    int local50, local52, local54, local56, local58, local5a;
    unsigned char c5b, c5c, c5d, c5e, c5f, c60, c61;
    unsigned char dummy62;
    unsigned char c63;
    char c64;
    unsigned char c65;
    int local68, local6a;
    int ret;

    c5d = 0;
    dummy62 = 1;
    clear_input_direction_and_fire_state();
    play_sound(0x21);
    saved = arc_file;
    request_disk(2);
    handle = Open("DT2:mt.arc", 1005L);
    arc_file = handle;
    arc_read_index(arc_file);
    load_arc_record(0x11, &G_h01_3424);
    load_arc_record(0x10, &G_h01_33EE);
    G_h01_3424 = 0x28;
    G_h01_3426 = 0xab;
    G_h01_33EE = 8;
    G_h01_33F0 = 0xaf;
    grid_background_bitmap = 0;
    grid_background_bitmap = load_arc_record(0, grid_background_bitmap);
    load_arc_record(1, &G_h01_349A);
    load_arc_record(2, G_h01_6EB8);
    load_arc_record(3, G_h01_6EEE);
    load_arc_record(4, &spr);
    load_arc_record(12, &G_h01_345A);
    load_grid_archive_records();
    switch (P) {
    case 0:
        grid_collision_map = G_h01_0AC4;
        grid_entity_state_table = (struct Entry *)G_h01_10F2;
        break;
    case 1:
        grid_collision_map = G_h01_0CD2;
        grid_entity_state_table = (struct Entry *)G_h01_1188;
        break;
    case 2:
        grid_collision_map = G_h01_0EE0;
        grid_entity_state_table = (struct Entry *)G_h01_121E;
        break;
    default:
        grid_collision_map = G_h01_0AC4;
        grid_entity_state_table = (struct Entry *)G_h01_10F2;
        break;
    }
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(4);
    request_disk(2);
    arc_read_index(arc_file);
    palette_cycle_countdown_step = 0;
    palette_cycle_callback_index = 0;
    fade_palette_to_black();
    G_h01_12BB = 0;
    grid_lives_remaining = 3;
    c65 = 0;
    reset_grid_entity_activity_for_game();
    clear_input_direction_and_fire_state();
    while (grid_lives_remaining > 0 && !c65) {
        grid_player_map_row = 0;
        for (local42 = 1; grid_collision_map[local42] == 'F'; local42++)
            ;
        G_h01_6EB4 = G_h01_6EB8;
        grid_player_map_column = local42;
        grid_player_screen_x = grid_player_map_column * 16;
        grid_player_screen_y = 0x83;
        G_h01_6F28 = 0x14;
        grid_player_action_state = 0;
        G_h01_34D0[0] = grid_player_screen_x;
        G_h01_34D4[0] = grid_player_screen_y;
        G_h01_34D8[0] = G_h01_6F28;
        G_h01_34DC[0] = grid_player_action_state;
        G_h01_34D0[1] = grid_player_screen_x;
        G_h01_34D4[1] = grid_player_screen_y;
        G_h01_34D8[1] = G_h01_6F28;
        G_h01_34DC[1] = grid_player_action_state;
        G_h01_6EB4[0x34] = 20;
        grid_player_facing_direction = 0;
        c63 = 0;
        G_h01_6F36 = 0;
        local40 = 0;
        c5d = 0;
        reset_grid_entity_activity_for_life();
        switch (grid_lives_remaining) {
        case 3:
            G_h01_1608 = 0x500;
            G_h01_160A = 0x800;
            G_h01_160C = 0xc00;
            G_h01_160E = 0xd44;
            break;
        case 2:
            G_h01_1608 = 5;
            G_h01_160A = 8;
            G_h01_160C = 0x11c;
            G_h01_160E = 0x44d;
            break;
        case 1:
            G_h01_1608 = 0x62;
            G_h01_160A = 0x82;
            G_h01_160C = 0xb3;
            G_h01_160E = 0x4d8;
            break;
        }
        copy_palette_to_copper_lists(0);
        *(int *)G_h01_6EB4 = grid_player_screen_x;
        ((int *)G_h01_6EB4)[1] = grid_player_screen_y;
        draw_grid_map_rows(c5d);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
        draw_grid_status_panel();
        advance_grid_player_and_entities(c5d, 0);
        draw_masked_sprite(G_h01_6EB4);
        switch_display_buffer();
        palette_fade_target = G_h01_15E6;
        fade_palette_to_target(G_h01_15E6);
        draw_grid_map_rows(c5d);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
        draw_grid_status_panel();
        advance_grid_player_and_entities(c5d, 0);
        draw_masked_sprite(G_h01_6EB4);
        switch_display_buffer();
        c5e = 0;
        while (!c5e) {
            c5b = 0;
            c5b = poll_controller_and_keyboard_input();
            c5c = (c5b & 0x80) ? 1 : 0;
            if (--local40 <= 0) {
                local40 = 0;
                switch (grid_player_action_state) {
                case 0:
                    G_h01_6EB4 = G_h01_6EB8;
                    if (c5c) {
                        if (grid_player_facing_direction == 0) {
                            G_h01_6F28 = 0x15;
                            c64 = 0;
                            local48 = 0xb;
                            local4a = 0xe;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + grid_player_screen_x + 0xb;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + grid_player_screen_y + 0xe;
                        } else {
                            G_h01_6F28 = 0x1b;
                            c64 = 8;
                            local48 = 0x17;
                            local4a = 0xe;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + grid_player_screen_x + 0x17;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + grid_player_screen_y + 0xe;
                        }
                        grid_player_action_state = 4;
                        play_sound(0x10);
                        grid_player_action_countdown = 10;
                        G_h01_6F36 = 1;
                    } else {
                        G_h01_6F36 = 0;
                        switch ((unsigned char)c5b) {
                        case 1:
                            if (G_h01_6F37 != 0) {
                                grid_player_action_state = 10;
                                play_sound(0x13);
                            } else {
                                if (grid_player_facing_direction == 0) {
                                    if (grid_collision_map[(long)(grid_player_map_row + 1) * 21 + (grid_player_map_column + 1)] == '0') {
                                        G_h01_6F28 = 0x16;
                                        grid_player_screen_x += 0x10;
                                        grid_player_action_state = 3;
                                        play_sound(0x19);
                                        grid_player_action_countdown = 0;
                                        local40 = 1;
                                    } else {
                                        G_h01_6F28 = 0x16;
                                        grid_player_screen_x += 0x10;
                                        grid_player_action_state = 2;
                                        local40 = 1;
                                        grid_player_action_countdown = 1;
                                    }
                                } else if (grid_player_facing_direction == 1) {
                                    if (grid_collision_map[(long)(grid_player_map_row + 1) * 21 + (grid_player_map_column - 1)] == '8') {
                                        G_h01_6F28 = 0x1c;
                                        grid_player_screen_x -= 16;
                                        grid_player_action_state = 3;
                                        play_sound(0x19);
                                        grid_player_action_countdown = 0;
                                        local40 = 1;
                                    } else {
                                        G_h01_6F28 = 0x1c;
                                        grid_player_screen_x -= 16;
                                        grid_player_action_state = 2;
                                        local40 = 1;
                                        grid_player_action_countdown = 1;
                                    }
                                }
                            }
                            break;
                        case 5:
                            if (grid_player_facing_direction == 0) {
                                if (G_h01_6F28 == 0x14)
                                    grid_player_screen_x += 16;
                                G_h01_6F28 = 0x16;
                                local40 = 5;
                            } else if (grid_player_facing_direction == 1) {
                                if (G_h01_6F28 == 0x1a)
                                    grid_player_screen_x -= 16;
                                G_h01_6F28 = 0x1c;
                                local40 = 5;
                            }
                            break;
                        case 7:
                            if (grid_player_facing_direction == 0) {
                                G_h01_6F28 = 0x1a;
                                grid_player_facing_direction = 1;
                                grid_player_screen_x += 16;
                                local40 = 2;
                            } else {
                                if (c63 == 0)
                                    G_h01_6F28 = 0xa;
                                else
                                    G_h01_6F28 = 0xf;
                                c63 ^= 1;
                                grid_player_screen_x -= 16;
                                grid_player_action_state = 1;
                                grid_player_action_countdown = 0;
                            }
                            break;
                        case 3:
                            if (grid_player_facing_direction == 1) {
                                G_h01_6F28 = 0x14;
                                grid_player_facing_direction = 0;
                                grid_player_screen_x -= 16;
                                local40 = 2;
                            } else {
                                if (c63 == 0)
                                    G_h01_6F28 = 0;
                                else
                                    G_h01_6F28 = 5;
                                c63 ^= 1;
                                grid_player_screen_x += 16;
                                grid_player_action_state = 1;
                                grid_player_action_countdown = 0;
                            }
                            break;
                        default:
                            if (G_h01_6F28 == 0x16)
                                grid_player_screen_x -= 16;
                            else if (G_h01_6F28 == 0x1c)
                                grid_player_screen_x += 16;
                            G_h01_6F28 = (grid_player_facing_direction == 0) ? 0x14 : 0x1a;
                            break;
                        }
                    }
                    break;
                case 1:
                    G_h01_6EB4 = G_h01_6EB8;
                    local40 = 0;
                    grid_player_action_countdown++;
                    if (grid_player_action_countdown == 3)
                        play_sound(10);
                    if (grid_player_facing_direction == 0) {
                        if (grid_player_action_countdown < 5)
                            G_h01_6F28++;
                        else
                            grid_player_action_state = 0;
                    } else {
                        if (grid_player_action_countdown < 5)
                            G_h01_6F28++;
                        else
                            grid_player_action_state = 0;
                    }
                    break;
                case 2:
                    if (grid_player_action_countdown != 0) {
                        G_h01_6EB4 = G_h01_6EEE;
                        if (grid_player_facing_direction == 0)
                            G_h01_6F28 = 0;
                        else
                            G_h01_6F28 = 6;
                        local40 = 1;
                        grid_player_screen_y -= 8;
                        grid_player_action_countdown = 0;
                    } else {
                        G_h01_6EB4 = G_h01_6EB8;
                        play_sound(10);
                        if (grid_player_facing_direction == 0) {
                            G_h01_6F28 = 0x14;
                            grid_player_screen_x += 16;
                        } else {
                            G_h01_6F28 = 0x1a;
                            grid_player_screen_x -= 16;
                        }
                        grid_player_screen_y += 8;
                        local40 = 0;
                        grid_player_action_state = 0;
                    }
                    break;
                case 3:
                    grid_player_action_countdown++;
                    G_h01_6EB4 = G_h01_6EEE;
                    if (grid_player_facing_direction == 0) {
                        switch (grid_player_action_countdown) {
                        case 1:
                            G_h01_6F28 = 0;
                            grid_player_screen_x -= 8;
                            grid_player_screen_y -= 16;
                            break;
                        case 2:
                            G_h01_6F28 = 1;
                            grid_player_screen_x += 8;
                            grid_player_screen_y -= 10;
                            local40 = 2;
                            break;
                        case 3:
                            G_h01_6F28 = 2;
                            local40 = 2;
                            break;
                        case 4:
                            G_h01_6F28 = 3;
                            grid_player_screen_y++;
                            local40 = 2;
                            break;
                        case 0:
                        case 5:
                        default:
                            G_h01_6F28 = 0x14;
                            G_h01_6EB4 = G_h01_6EB8;
                            grid_player_screen_y -= 15;
                            grid_player_action_state = 0;
                            grid_player_map_row++;
                            local40 = 0;
                            break;
                        }
                    } else {
                        switch (grid_player_action_countdown) {
                        case 1:
                            G_h01_6F28 = 6;
                            grid_player_screen_y -= 16;
                            break;
                        case 2:
                            G_h01_6F28 = 7;
                            grid_player_screen_x -= 8;
                            grid_player_screen_y -= 10;
                            local40 = 2;
                            break;
                        case 3:
                            G_h01_6F28 = 8;
                            local40 = 2;
                            break;
                        case 4:
                            G_h01_6F28 = 9;
                            grid_player_screen_y += 1;
                            local40 = 2;
                            break;
                        case 0:
                        case 5:
                        default:
                            G_h01_6F28 = 0x1a;
                            G_h01_6EB4 = G_h01_6EB8;
                            grid_player_screen_x += 8;
                            grid_player_screen_y -= 15;
                            grid_player_action_state = 0;
                            grid_player_map_row++;
                            local40 = 0;
                            break;
                        }
                    }
                    break;
                case 4:
                    local40 = 0;
                    if (!c5c && grid_player_action_countdown > 0)
                        c5c = 1;
                    if (c5c) {
                        if (grid_player_facing_direction == 0) {
                            c64--;
                            c64 &= 0xf;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + grid_player_screen_x + 11;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + grid_player_screen_y + 14;
                        } else {
                            c64++;
                            c64 &= 0xf;
                            local4c = G_h01_0AA2[c64 * 2] * 4 + grid_player_screen_x + 0x17;
                            local4e = G_h01_0AA2[c64 * 2 + 1] * 4 + grid_player_screen_y + 14;
                        }
                        grid_player_action_countdown--;
                        if (c64 == 4)
                            play_sound(0x10);
                        else if (c64 == 12)
                            play_sound(0x1d);
                    } else {
                        if (grid_player_facing_direction == 0) {
                            local50 = -G_h01_0AA2[2 * (15 - c64) + 1];
                            local52 = -G_h01_0AA2[2 * (15 - c64)];
                            c64 -= 2;
                            c64 &= 0xf;
                        } else {
                            local50 = -G_h01_0AA2[2 * c64 + 1];
                            local52 = G_h01_0AA2[2 * c64];
                            c64 += 2;
                            c64 &= 0xf;
                        }
                        local4c += local50;
                        local4e += local52;
                        grid_player_action_countdown = (4 >> (difficulty_level)) + 8;
                        grid_player_action_state = 5;
                        play_sound(12);
                    }
                    break;
                case 5:
                    if (grid_player_action_countdown > 0) {
                        grid_player_action_countdown--;
                        local4c += local50;
                        local4e += local52;
                        if (local4e <= 0 || ((local4e + 8) % 40 < 16 && local4e < grid_player_screen_y + 16)) {
                            if (local4e < 0)
                                local4e = 0;
                            if (local4c < 0)
                                local4c = 0;
                            if (local4c > 320)
                                local4c = 320;
                            c5f = c5d + (160 - (local4e + 8)) / 40 + 1;
                            if (c5f < 25) {
                                c60 = (int)grid_collision_map[(long)c5f * 21 + (local4c >> 4)];
                                switch (c60) {
                                case '0': case '8':
                                    if (local4c > grid_player_screen_x + 12) {
                                        local56 = (local4c - (grid_player_screen_x + 12) >> 1) + grid_player_screen_y + 16;
                                        local58 = (local4c - (grid_player_screen_x + 12) >> 2) - 8;
                                        local5a = 0;
                                        c61 = 1;
                                        grid_player_screen_x += 24;
                                    } else {
                                        local56 = (grid_player_screen_x + 12 - local4c >> 1) + grid_player_screen_y + 16;
                                        local58 = (grid_player_screen_x + 12 - local4c >> 2) - 8;
                                        local5a = 0;
                                        c61 = 0;
                                        grid_player_screen_x -= 24;
                                    }
                                    if (local56 > 128)
                                        local56 = 128;
                                    if (c60 == '0') {
                                        G_h01_6F28 = 0x18;
                                        grid_player_facing_direction = 0;
                                        local48 = 0x15;
                                        local4c = (local4c & 0xfff0) + 5;
                                        local54 = local4c - 0x15;
                                    } else {
                                        G_h01_6F28 = 0x1e;
                                        grid_player_facing_direction = 1;
                                        local48 = 0xb;
                                        local4c = (local4c & 0xfff0) + 0xb;
                                        local54 = local4c - 0xb;
                                    }
                                    local4e = 160 - (c5f - c5d) * 40;
                                    local4a = 0;
                                    play_sound(0x11);
                                    grid_player_action_state = 6;
                                    break;
                                case 1: case 2: case 3: case 4: case 5: case 6: case 7:
                                    if (local52 > 0) {
                                        local52 = -4;
                                        local4e -= 16;
                                    } else {
                                        local52 = 4;
                                        local4e += 16;
                                    }
                                    break;
                                case 'F':
                                default:
                                    break;
                                }
                            }
                        }
                    } else {
                        play_sound(0x16);
                        G_h01_6F36 = 0;
                        grid_player_action_state = 0;
                        if (grid_player_facing_direction == 0)
                            G_h01_6F28 = 0x14;
                        else
                            G_h01_6F28 = 0x1a;
                    }
                    break;
                case 6:
                    if (local54 > grid_player_screen_x) {
                        if (c61 == 1) {
                            grid_player_screen_x += 8;
                            grid_player_screen_y += 2;
                        } else {
                            grid_player_screen_x -= 8;
                            grid_player_screen_y -= 2;
                        }
                    } else {
                        if (c61 == 1) {
                            grid_player_screen_x += 8;
                            grid_player_screen_y -= 2;
                        } else {
                            grid_player_screen_x -= 8;
                            grid_player_screen_y += 2;
                        }
                    }
                    if (grid_player_screen_y > 128)
                        grid_player_screen_y = 128;
                    if (grid_player_screen_x < 0) {
                        grid_player_screen_x = 0;
                        local58--;
                    } else if (grid_player_screen_y > 0x118) {
                        grid_player_screen_x = 0x118;
                        local58--;
                    }
                    local5a++;
                    if (local5a >= local58) {
                        local58 -= 8;
                        local5a = 0;
                        c61 ^= 1;
                        play_sound(c61 ? 0x5a : 0x5d);
                    }
                    if (local58 <= 0) {
                        grid_player_screen_x = local54;
                        grid_player_action_state = 7;
                        play_sound(0);
                        grid_player_action_countdown = 0;
                        local40 = 1;
                    }
                    break;
                case 7:
                    if (grid_player_screen_y - 16 < local4e) {
                        G_h01_6EB4 = G_h01_6EEE;
                        switch (grid_player_action_countdown) {
                        case 0:
                            G_h01_6F36 = 0;
                            grid_player_screen_y = local4e - 16;
                            if (grid_player_facing_direction == 0)
                                G_h01_6F28 = 1;
                            else
                                G_h01_6F28 = 7;
                            local40 = 3;
                            break;
                        case 1:
                            G_h01_6F28 = grid_player_facing_direction == 0 ? 2 : 8;
                            local40 = 3;
                            break;
                        case 2:
                            play_sound(0x77);
                            G_h01_6F28 = grid_player_facing_direction == 0 ? 3 : 9;
                            local40 = 3;
                            break;
                        case 3:
                        default:
                            grid_player_screen_x = local4c & 0xfff0;
                            if (grid_player_facing_direction == 1)
                                grid_player_screen_y -= 16;
                            grid_player_screen_y = local4e - 29;
                            grid_player_action_state = 0;
                            G_h01_6EB4 = G_h01_6EB8;
                            if (grid_player_facing_direction == 0)
                                G_h01_6F28 = 0x14;
                            else
                                G_h01_6F28 = 0x1a;
                            local40 = 0;
                            break;
                        }
                        grid_player_action_countdown++;
                    } else {
                        G_h01_6EB4 = G_h01_6EB8;
                        switch (G_h01_6F28) {
                        case 30:
                            grid_player_screen_y -= 9;
                            G_h01_6F28 = 0x1f;
                            local40 = 2;
                            break;
                        case 31:
                            grid_player_screen_y -= 6;
                            G_h01_6F28 = 0x1e;
                            local40 = 3;
                            break;
                        case 24:
                            grid_player_screen_y -= 9;
                            G_h01_6F28 = 0x19;
                            local40 = 2;
                            break;
                        case 25:
                            grid_player_screen_y -= 6;
                            G_h01_6F28 = 0x18;
                            local40 = 3;
                            break;
                        }
                    }
                    break;
                case 8:
                    if (grid_player_screen_y > 128) {
                        grid_lives_remaining--;
                        c5e = 1;
                        continue;
                    }
                    G_h01_6EB4 = G_h01_6EEE;
                    if (grid_collision_map[(long)grid_player_map_row * 21 + grid_player_map_column] != 'F' && grid_player_screen_y % 40 < 16) {
                        G_h01_6F28 = grid_player_facing_direction == 0 ? 5 : 11;
                        local40 = 0;
                    } else {
                        G_h01_6F28 = grid_player_facing_direction == 0 ? 4 : 10;
                        local40 = 1;
                    }
                    grid_player_screen_y += 8;
                    G_h01_6F36 = 0;
                    break;
                case 9:
                    G_h01_6EB4 = G_h01_6EEE;
                    if (grid_player_screen_y > 120) {
                        G_h01_6EB4 = G_h01_6EB8;
                        G_h01_6F28 = grid_player_facing_direction == 0 ? 20 : 26;
                        grid_player_screen_y = 0x83;
                        grid_player_action_state = 0;
                        play_sound(0x77);
                        local40 = 0;
                    } else if (grid_collision_map[(long)grid_player_map_row * 21 + grid_player_map_column] != 'F' && grid_player_screen_y % 40 > 16 && grid_player_action_countdown > 10) {
                        G_h01_6EB4 = G_h01_6EB8;
                        G_h01_6F28 = grid_player_facing_direction == 0 ? 20 : 26;
                        grid_player_screen_y = 160 - (grid_player_map_row - c5d) * 40 - 29;
                        grid_player_action_state = 0;
                        play_sound(0x77);
                        local40 = 0;
                    } else {
                        grid_player_screen_y += 8;
                        G_h01_6F28 = 10;
                        grid_player_action_countdown++;
                    }
                    G_h01_6F36 = 0;
                    break;
                case 10:
                    if (grid_player_map_row < G_h01_6F3A)
                        grid_player_screen_y -= 40;
                    else if (grid_player_map_row > G_h01_6F3A)
                        grid_player_screen_y += 40;
                    else {
                        grid_player_screen_x = G_h01_6F38;
                        grid_player_action_state = 0;
                        play_sound(0x14);
                        G_h01_6EB4 = G_h01_6EB8;
                        G_h01_6F28 = grid_player_facing_direction == 0 ? 20 : 26;
                    }
                    G_h01_6F36 = 0;
                    break;
                }
            }
            if (grid_player_screen_x < 0)
                grid_player_screen_x = 0;
            if (grid_player_screen_x > 0x120)
                grid_player_screen_x = 0x120;
            grid_player_map_row = c5d + (160 - (grid_player_screen_y + 16)) / 40;
            grid_player_map_column = (grid_player_screen_x >> 4) - grid_player_facing_direction + 1;
            if (G_h01_6F28 == 0x16)
                grid_player_map_column--;
            else if (G_h01_6F28 == 0x1c)
                grid_player_map_column++;
            if (grid_player_map_column == local68 && grid_player_map_row == local6a && (G_h01_6F28 == 0x14 || G_h01_6F28 == 0x1a))
                grid_stationary_hazard_counter++;
            else {
                local68 = grid_player_map_column;
                local6a = grid_player_map_row;
                grid_stationary_hazard_counter = 0;
            }
            if (grid_player_action_state == 0 && grid_collision_map[(long)grid_player_map_row * 21 + grid_player_map_column] == 'F' && grid_player_map_row != 0) {
                if (grid_collision_map[(long)(grid_player_map_row - 1) * 21 + grid_player_map_column] != 'F') {
                    grid_player_map_row--;
                    grid_player_screen_y = 160 - (grid_player_map_row - c5d) * 40 - 29;
                    G_h01_6EB4 = G_h01_6EB8;
                    if (grid_player_facing_direction == 0) {
                        G_h01_6F28 = 0x16;
                        grid_player_screen_x += 16;
                    } else {
                        G_h01_6F28 = 0x1c;
                        grid_player_screen_x -= 16;
                    }
                    local40 = 2;
                } else {
                    grid_player_action_state = 8;
                    play_sound(0xf);
                    grid_player_screen_y += 8;
                    grid_player_action_countdown = 0;
                }
            }
            if (grid_player_map_row > c5d + 2) {
                local42 = 10;
                do {
                    grid_player_screen_y += 10;
                    local4e += 10;
                    local46 = (((unsigned int)(c5d + 5)) % 5) * 40;
                    BltBitMap(grid_background_bitmap, 0L, (long)(local46 + 40 - local42), active_screen_bitmap, 0L, 0L, 320L, (long)local42, 192L, 255L, 0L);
                    if (c5d + 5 < 25) {
                        local44 = 0;
                        do {
                            if (grid_collision_map[(long)(c5d + 5) * 21 + local44] != 'F') {
                                G_h01_34CE = grid_collision_map[(long)(c5d + 5) * 21 + local44] - '0';
                                G_h01_349A = local44 * 16;
                                G_h01_349C = local42 - 40;
                                draw_masked_sprite(&G_h01_349A);
                            }
                            local44++;
                        } while (local44 < 20);
                    }
                    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, (long)local42, 320L, (long)(168 - local42), 192L, 255L, 0L);
                    advance_grid_player_and_entities(c5d, local42);
                    *(int *)G_h01_6EB4 = grid_player_screen_x;
                    ((int *)G_h01_6EB4)[1] = grid_player_screen_y;
                    G_h01_6EB4[0x34] = G_h01_6F29;
                    if (grid_player_action_state != 10)
                        draw_masked_sprite(G_h01_6EB4);
                    if (G_h01_6F36 != 0) {
                        if (local4c < 0)
                            local4c = 0;
                        else if (local4c > 0x136)
                            local4c = 0x136;
                        if (local4e < 0)
                            local4e = 0;
                        else if (local4e > 0xbe)
                            local4e = 0xbe;
                        *G_h01_5370 = 0x10;
                        SetAPen(screen_rast_port, (long)*G_h01_5370);
                        Move(screen_rast_port, (long)(grid_player_screen_x + local48), (long)(grid_player_screen_y + local4a));
                        Draw(screen_rast_port, (long)local4c, (long)local4e);
                    }
                    draw_grid_status_panel();
                    G_h01_34D0[G_h01_34E0] = grid_player_screen_x;
                    G_h01_34D4[G_h01_34E0] = grid_player_screen_y;
                    G_h01_34D8[G_h01_34E0] = G_h01_6F28;
                    G_h01_34DC[G_h01_34E0] = grid_player_action_state;
                    G_h01_34E1 ^= 1;
                    switch_display_buffer();
                    local42 += 10;
                } while (local42 <= 40);
                c5d++;
                draw_grid_map_rows(c5d);
                BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
            } else {
                if (grid_player_map_row <= c5d && c5d > 0 && grid_player_action_state != 8 && grid_player_action_state != 6 && grid_player_action_state != 7) {
                    local42 = 10;
                    do {
                        grid_player_screen_y -= 10;
                        local4e -= 10;
                        BltBitMap(archive_image_bitmap, 0L, (long)local42, active_screen_bitmap, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
                        if (local42 > 32 && c5d > 0) {
                            local46 = ((unsigned int)(c5d - 1) % 5) * 40;
                            BltBitMap(grid_background_bitmap, 0L, (long)local46, active_screen_bitmap, 0L, (long)(200 - local42), 320L, (long)(local42 - 32), 192L, 255L, 0L);
                            local44 = 0;
                            do {
                                if (grid_collision_map[(long)(c5d - 1) * 21 + local44] != 'F') {
                                    G_h01_34CE = grid_collision_map[(long)(c5d - 1) * 21 + local44] - '0';
                                    G_h01_349A = local44 * 16;
                                    G_h01_349C = 200 - local42;
                                    draw_masked_sprite(&G_h01_349A);
                                }
                                local44++;
                            } while (local44 < 20);
                        }
                        advance_grid_player_and_entities(c5d, -local42);
                        *(int *)G_h01_6EB4 = grid_player_screen_x;
                        ((int *)G_h01_6EB4)[1] = grid_player_screen_y;
                        G_h01_6EB4[0x34] = G_h01_6F29;
                        if (grid_player_action_state != 10)
                            draw_masked_sprite(G_h01_6EB4);
                        if (G_h01_6F36 != 0) {
                            if (local4c < 0)
                                local4c = 0;
                            else if (local4c > 0x136)
                                local4c = 0x136;
                            if (local4e < 0)
                                local4e = 0;
                            else if (local4e > 0xbe)
                                local4e = 0xbe;
                            *G_h01_5370 = 0x10;
                            SetAPen(screen_rast_port, (long)*G_h01_5370);
                            Move(screen_rast_port, (long)(grid_player_screen_x + local48), (long)(grid_player_screen_y + local4a));
                            Draw(screen_rast_port, (long)local4c, (long)local4e);
                        }
                        draw_grid_status_panel();
                        G_h01_34D0[G_h01_34E0] = grid_player_screen_x;
                        G_h01_34D4[G_h01_34E0] = grid_player_screen_y;
                        G_h01_34D8[G_h01_34E0] = G_h01_6F28;
                        G_h01_34DC[G_h01_34E0] = grid_player_action_state;
                        G_h01_34E1 ^= 1;
                        switch_display_buffer();
                        local42 += 10;
                    } while (local42 <= 40);
                    c5d--;
                    draw_grid_map_rows(c5d);
                    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
                } else {
                    refresh_grid_view(c5d);
                    draw_masked_sprite(&G_h01_3424);
                    draw_decimal_value(168, 174, total_money, 1, 26, 1);
                }
            }
            if (grid_player_map_row == 24 && grid_player_action_state == 0) {
                c65 = 1;
                c5e = 1;
            }
            advance_grid_player_and_entities(c5d, 0);
            *(int *)G_h01_6EB4 = grid_player_screen_x;
            ((int *)G_h01_6EB4)[1] = grid_player_screen_y;
            G_h01_6EB4[0x34] = G_h01_6F29;
            if (grid_player_action_state != 10)
                draw_masked_sprite(G_h01_6EB4);
            if (G_h01_6F36 != 0) {
                *G_h01_5370 = 0x10;
                if (local4c < 0)
                    local4c = 0;
                else if (local4c > 0x136)
                    local4c = 0x136;
                if (local4e < 0)
                    local4e = 0;
                else if (local4e > 0xbe)
                    local4e = 0xbe;
                SetAPen(screen_rast_port, (long)*G_h01_5370);
                Move(screen_rast_port, (long)(grid_player_screen_x + local48), (long)(grid_player_screen_y + local4a));
                Draw(screen_rast_port, (long)local4c, (long)local4e);
            }
            if (grid_player_action_state == 4 || grid_player_action_state == 5) {
                spr.x = local4c;
                spr.y = local4e - 3;
                spr.st = c64;
                draw_masked_sprite(&spr);
                if (spr.y > 160)
                    draw_grid_status_panel();
            }
            G_h01_34D0[G_h01_34E0] = grid_player_screen_x;
            G_h01_34D4[G_h01_34E0] = grid_player_screen_y;
            G_h01_34D8[G_h01_34E0] = G_h01_6F28;
            G_h01_34DC[G_h01_34E0] = grid_player_action_state;
            G_h01_34E1 ^= 1;
            switch_display_buffer();
        }
        play_sound(0);
        ret = c65;
        fade_palette_to_black();
    }
    fade_palette_to_black();
    F_h00_4EC6();
    free_bitmap_planes(&G_h01_6EC8, G_h01_6EC0, G_h01_6EC2);
    free_bitmap_planes(&G_h01_6EFE, G_h01_6EF6, G_h01_6EF8);
    free_bitmap_planes(&G_h01_34AA, G_h01_34A2, G_h01_34A4);
    free_bitmap_planes(&G_h01_3434, G_h01_342C, G_h01_342E);
    free_bitmap_planes(&G_h01_33FE, G_h01_33F6, G_h01_33F8);
    free_bitmap_planes(&G_h01_346A, G_h01_3462, G_h01_3464);
    free_bitmap_planes(spr.data, spr.w, spr.h);
    free_bitmap(grid_background_bitmap);
    F_h08_3F70();
    Close(handle);
    arc_file = saved;
    arc_read_index(arc_file);
    return ret;
}
