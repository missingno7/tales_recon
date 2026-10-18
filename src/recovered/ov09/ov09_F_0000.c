/* ov09_F_0000 v1: plain structured C; canonical declaration views where present. */
extern unsigned int F_h00_463E();
extern long Open();
extern int F_h00_4EC6();
extern int SetRast();
extern int request_disk();
extern int F_h00_4D04();
extern int arc_read_index();
extern int fade_palette_to_black();
extern int switch_display_buffer();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int BltBitMap();
extern int draw_masked_sprite();
extern int free_bitmap_planes();
extern int load_arc_record();
extern int play_sound();
extern int fade_palette_to_target();
extern int copy_palette_to_color_map();
extern int copy_palette_to_copper_lists();
extern int draw_text();
extern int draw_decimal_value();
extern int wait_for_fire_input();
extern int Close();
extern int load_timed_scene_route_indices();
extern int draw_timed_scene_status_panel();
extern int update_timed_scene_event_slots();
extern unsigned char get_timed_event_frame_limit();
extern int configure_timed_item_animation();
struct FlagEntry { char value; char pad[11]; };
struct Table { int first; int second; char pad[2]; };
struct State { unsigned char kind; char pad1; unsigned int type; unsigned char mode; unsigned char step; char ticks; char pad7; int first; int second; };
extern struct Table timed_scene_event_position_offsets[64];
extern struct State timed_scene_active_events[3];
extern struct FlagEntry player_treasure_collected[35];
extern unsigned char timed_scene_event_spawn_masks[96];
extern unsigned int timed_scene_route_point_indices[6];
extern char *palette_fade_target;
extern unsigned char timed_scene_elapsed_round_count;
extern unsigned char timed_scene_event_capture_thresholds[12];
extern char G_h01_4334[12];
extern int G_h01_1626;
extern int G_h01_1666;
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern int G_h01_3ACA;
extern int G_h01_3ACC;
extern int G_h01_3AD2;
extern int G_h01_3AD4;
extern int G_h01_3ADA;
extern int G_h01_3B00;
extern int G_h01_3B02;
extern int G_h01_3B08;
extern int G_h01_3B0A;
extern int G_h01_3B10;
extern int G_h01_3B36;
extern int G_h01_3B38;
extern int G_h01_3B3E;
extern int G_h01_3B40;
extern int G_h01_3B46;
extern int G_h01_3B6C;
extern int G_h01_3B6E;
extern int G_h01_3B74;
extern int G_h01_3B76;
extern int G_h01_3B7C;
extern int G_h01_3BA2;
extern int G_h01_3BA4;
extern int G_h01_3BAA;
extern int G_h01_3BAC;
extern int G_h01_3BB2;
extern int G_h01_3BD8;
extern int G_h01_3BDA;
extern int G_h01_3BE0;
extern int G_h01_3BE2;
extern int G_h01_3BE8;
extern int G_h01_3C0E;
extern int G_h01_3C10;
extern int G_h01_3C16;
extern int G_h01_3C18;
extern int G_h01_3C1E;
extern int G_h01_3C44;
extern int G_h01_3C46;
extern int G_h01_3C4C;
extern int G_h01_3C4E;
extern int G_h01_3C54;
extern int G_h01_3C7A;
extern int G_h01_3C7C;
extern int G_h01_3C82;
extern int G_h01_3C84;
extern int G_h01_3C8A;
extern int G_h01_3CB0;
extern int G_h01_3CB2;
extern int G_h01_3CB8;
extern int G_h01_3CBA;
extern int G_h01_3CC0;
extern int G_h01_3CE6;
extern int G_h01_3CE8;
extern int G_h01_3CEE;
extern int G_h01_3CF0;
extern int G_h01_3CF6;
extern int G_h01_3D1C;
extern int G_h01_3D1E;
extern int G_h01_3D24;
extern int G_h01_3D26;
extern int G_h01_3D2C;
extern int G_h01_3D52;
extern int G_h01_3D54;
extern int G_h01_3D5A;
extern int G_h01_3D5C;
extern int G_h01_3D62;
extern int G_h01_3D88;
extern int G_h01_3D8A;
extern int G_h01_3D90;
extern int G_h01_3D92;
extern int G_h01_3D98;
extern char G_h01_3DBC;
extern int G_h01_3DBE;
extern int G_h01_3DC0;
extern int G_h01_3DC6;
extern int G_h01_3DC8;
extern int G_h01_3DCE;
extern char G_h01_3DF2;
extern int G_h01_3DF4;
extern int G_h01_3DF6;
extern int G_h01_3DFC;
extern int G_h01_3DFE;
extern int G_h01_3E04;
extern char G_h01_3E28;
extern int G_h01_3E2A;
extern int G_h01_3E2C;
extern int G_h01_3E32;
extern int G_h01_3E34;
extern int G_h01_3E3A;
extern char G_h01_3E5E;
extern int G_h01_3E60;
extern int G_h01_3E62;
extern int G_h01_3E68;
extern int G_h01_3E6A;
extern int G_h01_3E70;
extern char G_h01_3E94;
extern int G_h01_3E96;
extern int G_h01_3E98;
extern int G_h01_3E9E;
extern int G_h01_3EA0;
extern int G_h01_3EA6;
extern char G_h01_3ECA;
extern int G_h01_3ECC;
extern int G_h01_3ECE;
extern int G_h01_3ED4;
extern int G_h01_3ED6;
extern int G_h01_3EDC;
extern char G_h01_3F00;
extern int G_h01_3F02;
extern int G_h01_3F04;
extern int G_h01_3F0A;
extern int G_h01_3F0C;
extern int G_h01_3F12;
extern char G_h01_3F36;
extern int G_h01_3F38;
extern int G_h01_3F3A;
extern int G_h01_3F40;
extern int G_h01_3F42;
extern int G_h01_3F48;
extern char G_h01_3F6C;
extern int G_h01_3F6E;
extern int G_h01_3F70;
extern int G_h01_3F76;
extern int G_h01_3F78;
extern int G_h01_3F7E;
extern char G_h01_3FA2;
extern int G_h01_3FA4;
extern int G_h01_3FA6;
extern int G_h01_3FAC;
extern int G_h01_3FAE;
extern int G_h01_3FB4;
extern char G_h01_3FD8;
extern int G_h01_3FDA;
extern int G_h01_3FDC;
extern int G_h01_3FE2;
extern int G_h01_3FE4;
extern int G_h01_3FEA;
extern char G_h01_400E;
extern int G_h01_4010;
extern int G_h01_4012;
extern int G_h01_4018;
extern int G_h01_401A;
extern int G_h01_4020;
extern char G_h01_4044;
extern int G_h01_4046;
extern int G_h01_4048;
extern int G_h01_404E;
extern int G_h01_4050;
extern int G_h01_4056;
extern char G_h01_407A;
extern int G_h01_407C;
extern int G_h01_407E;
extern int G_h01_4084;
extern int G_h01_4086;
extern int G_h01_408C;
extern char G_h01_40B0;
extern int G_h01_40B2;
extern int G_h01_40B4;
extern int G_h01_40BA;
extern int G_h01_40BC;
extern int G_h01_40C2;
extern char G_h01_40E6;
extern int G_h01_40E8;
extern int G_h01_40EA;
extern int G_h01_40F0;
extern int G_h01_40F2;
extern int G_h01_40F8;
extern char G_h01_411C;
extern int G_h01_411E;
extern int G_h01_4120;
extern int G_h01_4126;
extern int G_h01_4128;
extern int G_h01_412E;
extern char G_h01_4152;
extern int G_h01_4154;
extern int G_h01_4156;
extern int G_h01_415C;
extern int G_h01_415E;
extern int G_h01_4164;
extern unsigned char timed_scene_selected_option_index;
extern int G_h01_418A;
extern int G_h01_418C;
extern int G_h01_4192;
extern int G_h01_4194;
extern int G_h01_419A;
extern int G_h01_41C0;
extern int G_h01_41C2;
extern int G_h01_41C8;
extern int G_h01_41CA;
extern int G_h01_41D0;
extern int G_h01_41F6;
extern int G_h01_41F8;
extern int G_h01_41FE;
extern int G_h01_4200;
extern int G_h01_4206;
extern char G_h01_422A;
extern int G_h01_422C;
extern int G_h01_422E;
extern int G_h01_4234;
extern int G_h01_4236;
extern int G_h01_423C;
extern unsigned int timed_scene_bonus_event_type;
extern char timed_scene_actions_remaining;
extern int G_h01_4276;
extern int G_h01_427A;
extern int G_h01_427C;
extern int G_h01_4280;
extern int G_h01_4282;
extern int G_h01_4286;
extern int G_h01_4288;
extern int G_h01_428C;
extern int G_h01_428E;
extern int G_h01_4292;
extern int G_h01_4294;
extern int G_h01_4298;
extern int G_h01_429A;
extern int G_h01_429E;
extern int G_h01_42A0;
extern int G_h01_42A4;
extern int G_h01_42A6;
extern int G_h01_42AA;
extern int G_h01_42AC;
extern int G_h01_42B0;
extern int G_h01_42B2;
extern int G_h01_42B6;
extern int G_h01_42B8;
extern int G_h01_42BC;
extern int G_h01_42BE;
extern int G_h01_42C2;
extern int G_h01_42C4;
extern int G_h01_42C8;
extern int G_h01_42CA;
extern int G_h01_42CE;
extern int G_h01_42D0;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern long arc_file;
extern char difficulty_level;
extern char game_day;
extern char current_location;
extern long total_money;
extern long minigame_cash_winnings;
extern char G_h01_5E5E;

struct Pt { int x; int y; };
struct Rec { char kind; char pad; int first; int second; };

recovered(arg)
int arg;
{
    int w2;
    unsigned int c;
    char lim;
    int small[6];
    char flags[12];
    struct Pt pts[12];
    char sel;
    long saved;
    int cnt;
    char first;
    int t5a;
    char b5b;
    int idx;
    struct Rec *rp;
    int result;
    int changed;
    char newflag;

    result = 0;
    changed = 0;
    newflag = 0;
    first = 0;
    b5b = 0;
    idx = 0;
    sel = 0;

    minigame_cash_winnings = 0;
    F_h00_4EC6();
    SetRast(screen_rast_port, 0L);
    request_disk(2);
    F_h00_4D04(10);
    saved = arc_file;
    request_disk(2);
    arc_file = Open("DT2:ps.arc", 0x3edL);
    arc_read_index(arc_file);
    c = F_h00_463E() & 0xf;

    switch (arg) {
    case 1:
        if (c < 5) timed_scene_bonus_event_type = 0x1f;
        else if (c < 10) timed_scene_bonus_event_type = 0x2c;
        else timed_scene_bonus_event_type = 0x25;
        break;
    case 2:
        if (c < 2) timed_scene_bonus_event_type = 0x1e;
        else if (c < 4) timed_scene_bonus_event_type = 0x1f;
        else if (c < 6) timed_scene_bonus_event_type = 0x25;
        else if (c < 8) timed_scene_bonus_event_type = 0x23;
        else if (c < 10) timed_scene_bonus_event_type = 0x28;
        else if (c < 12) timed_scene_bonus_event_type = 0x2b;
        else timed_scene_bonus_event_type = 0x22;
        break;
    case 3:
        if (c & 1) timed_scene_bonus_event_type = 0x23;
        else timed_scene_bonus_event_type = 0x20;
        break;
    case 4:
        if (c < 3) timed_scene_bonus_event_type = 0x26;
        else if (c < 6) timed_scene_bonus_event_type = 0x27;
        else if (c < 9) timed_scene_bonus_event_type = 0x21;
        else if (c < 12) timed_scene_bonus_event_type = 0x22;
        else if (c < 15) timed_scene_bonus_event_type = 0x2a;
        else timed_scene_bonus_event_type = 0x2b;
        break;
    case 5:
        if (c < 3) timed_scene_bonus_event_type = 0x26;
        else if (c < 6) timed_scene_bonus_event_type = 0x27;
        else if (c < 9) timed_scene_bonus_event_type = 0x21;
        else if (c < 12) timed_scene_bonus_event_type = 0x22;
        else if (c < 15) timed_scene_bonus_event_type = 0x28;
        else timed_scene_bonus_event_type = 0x29;
        break;
    case 0:
    case 6:
    default:
        if (c < 5) timed_scene_bonus_event_type = 0x1e;
        else if (c < 10) timed_scene_bonus_event_type = 0x20;
        else if (c < 13) timed_scene_bonus_event_type = 0x28;
        else timed_scene_bonus_event_type = 0x29;
        break;
    }

    G_h01_5E5E = 1;
    cnt = 0;
    small[0] = 0x76; small[1] = 0x7e;
    small[2] = 0x78; small[3] = 0x7d;
    small[4] = 0xb2; small[5] = 0x70;
    pts[0].x = 0x46;  pts[0].y = 0x32;
    pts[1].x = 0x8e;  pts[1].y = 0x31;
    pts[2].x = 0xda;  pts[2].y = 0x33;
    pts[3].x = 0x11c; pts[3].y = 0x33;
    pts[4].x = 0x48;  pts[4].y = 0x6d;
    pts[5].x = 0x8e;  pts[5].y = 0x6c;
    pts[6].x = 0xd9;  pts[6].y = 0x6c;
    pts[7].x = 0x11e; pts[7].y = 0x6c;
    pts[8].x = 0x45;  pts[8].y = 0xa6;
    pts[9].x = 0x90;  pts[9].y = 0xa6;
    pts[10].x = 0xdb; pts[10].y = 0xa4;
    pts[11].x = 0x122; pts[11].y = 0xa4;

    for (c = 0; c < 12; c++)
        flags[c] = 0;
    for (c = 0; c < 6; c++)
        timed_scene_route_point_indices[c] = 0;

    request_disk(2);
    load_arc_record(0, archive_image_bitmap);
    load_arc_record(1, &G_h01_3ACA);
    G_h01_3ACA = 3;
    G_h01_3ACC = 0x3f;
    load_arc_record(2, &G_h01_3B00);
    G_h01_3B00 = 1;
    G_h01_3B02 = 0x5a;
    load_arc_record(3, &G_h01_3B36);
    G_h01_3B36 = 0x29;
    G_h01_3B38 = 0x78;
    load_arc_record(4, &G_h01_3B6C);
    G_h01_3B6C = 0x46;
    G_h01_3B6E = 0x2f;
    load_arc_record(5, &G_h01_3BA2);
    G_h01_3BA2 = 0x8c;
    G_h01_3BA4 = 0x2f;
    load_arc_record(6, &G_h01_3BD8);
    G_h01_3BD8 = 0x8d;
    G_h01_3BDA = 0x35;
    load_arc_record(7, &G_h01_3C0E);
    G_h01_3C0E = 0x8d;
    G_h01_3C10 = 0x63;
    load_arc_record(8, &G_h01_3C44);
    G_h01_3C44 = 0xb6;
    G_h01_3C46 = 0x3e;
    load_arc_record(9, &G_h01_3C7A);
    G_h01_3C7A = 0xf9;
    G_h01_3C7C = 0x47;
    load_arc_record(10, &G_h01_3CB0);
    G_h01_3CB0 = 0x112;
    G_h01_3CB2 = 0x43;
    load_arc_record(11, &G_h01_3CE6);
    G_h01_3CE6 = 0xe8;
    G_h01_3CE8 = 0x71;
    load_arc_record(12, &G_h01_3D1C);
    G_h01_3D1C = 0xd9;
    G_h01_3D1E = 0x8a;
    load_arc_record(13, &G_h01_3D52);
    G_h01_3D52 = 0xee;
    G_h01_3D54 = 0x1c;

    load_timed_scene_route_indices(arg);
    request_disk(2);

    for (c = 0; c < 6; c++) {
        if (c > 0 && timed_scene_route_point_indices[c] == timed_scene_route_point_indices[0])
            continue;
        switch (timed_scene_route_point_indices[c]) {
        case 14: load_arc_record(14, &G_h01_3D88); break;
        case 15: load_arc_record(15, &G_h01_3DBE); break;
        case 16: load_arc_record(16, &G_h01_3DF4); break;
        case 17: load_arc_record(17, &G_h01_3E2A); break;
        case 18: load_arc_record(18, &G_h01_3E60); break;
        case 19: load_arc_record(19, &G_h01_3E96); break;
        case 20: load_arc_record(20, &G_h01_3ECC); break;
        case 21: load_arc_record(21, &G_h01_3F02); break;
        case 22: load_arc_record(22, &G_h01_3F38); break;
        case 23: load_arc_record(23, &G_h01_3F6E); break;
        case 24: load_arc_record(24, &G_h01_3FA4); break;
        case 25: load_arc_record(25, &G_h01_3FDA); break;
        case 26: load_arc_record(26, &G_h01_4010); break;
        case 27: load_arc_record(27, &G_h01_4046); break;
        case 28: load_arc_record(28, &G_h01_407C); break;
        case 29: load_arc_record(29, &G_h01_40B2); break;
        }
    }

    load_arc_record(timed_scene_bonus_event_type, &G_h01_40E8);
    load_arc_record(0x2e, &G_h01_4154);
    G_h01_4154 = 0x75;
    G_h01_4156 = 0x70;
    timed_scene_selected_option_index = 1;
    load_arc_record(0x2f, &G_h01_418A);
    G_h01_418A = 8;
    G_h01_418C = 0xb0;
    load_arc_record(0x30, &G_h01_41C0);
    G_h01_41C0 = 8;
    G_h01_41C2 = 0xb0;
    timed_scene_elapsed_round_count = 0;
    load_arc_record(0x31, &G_h01_41F6);
    G_h01_422A = 1;
    G_h01_41F6 = small[timed_scene_selected_option_index * 2];
    G_h01_41F8 = small[timed_scene_selected_option_index * 2 + 1];
    load_arc_record(0x32, &G_h01_422C);
    G_h01_422C = 0x110;
    G_h01_422E = 0xb2;
    play_sound(0);
    timed_scene_actions_remaining = 0xc;

    for (c = 0; c < 3; c++) {
        timed_scene_active_events[c].kind = 0;
        timed_scene_active_events[c].type = 0;
    }

    rp = (struct Rec *)timed_scene_event_spawn_masks;
    for (c = 0; c <= 31; c++, rp++) {
        switch (c + 14) {
        case 14:
        case 30:
            rp->kind = 12; rp->first = 0x30; rp->second = 0x30; break;
        case 15:
        case 31:
            rp->kind = 12; rp->first = 0x30; rp->second = 0x2e; break;
        case 16:
        case 32:
            rp->kind = 12; rp->first = 0x20; rp->second = 0x20; break;
        case 17:
        case 33:
            rp->kind = 2; rp->first = 0x40; rp->second = 0x3e; break;
        case 18:
        case 34:
            rp->kind = 1; rp->first = 0x40; rp->second = 0x3e; break;
        case 19:
        case 35:
            rp->kind = 4; rp->first = 0x20; rp->second = 0x20; break;
        case 21:
        case 37:
            rp->kind = 2; rp->first = 0x30; rp->second = 0x30; break;
        case 22:
        case 38:
            rp->kind = 1; rp->first = 0x30; rp->second = 0x2d; break;
        case 23:
        case 39:
            rp->kind = 2; rp->first = 0x30; rp->second = 0x2d; break;
        case 24:
        case 26:
        case 40:
        case 42:
            rp->kind = 2; rp->first = 0x30; rp->second = 0x30; break;
        case 20:
        case 25:
        case 27:
        case 36:
        case 41:
        case 43:
            rp->kind = 1; rp->first = 0x30; rp->second = 0x30; break;
        case 28:
        case 44:
            rp->kind = 1; rp->first = 0x30; rp->second = 0x2c; break;
        case 29:
        case 45:
            rp->kind = 2; rp->first = 0x30; rp->second = 0x2c; break;
        default:
            break;
        }
    }

    if (difficulty_level == 0)
        lim = 0x32;
    else if (difficulty_level == 1)
        lim = 0x28;
    else
        lim = 0x1e;

    palette_cycle_callback_index = 0;
    palette_cycle_countdown_step = 0;
    fade_palette_to_black();
    SetRast(screen_rast_port, 0L);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xb0L,
               0xc0L, 0xffL, 0L);
    draw_timed_scene_status_panel((int)first);
    update_timed_scene_event_slots();
    draw_masked_sprite(&G_h01_4154);
    G_h01_422A = timed_scene_selected_option_index;
    G_h01_41F6 = small[timed_scene_selected_option_index * 2];
    G_h01_41F8 = small[timed_scene_selected_option_index * 2 + 1];
    draw_masked_sprite(&G_h01_41F6);
    switch_display_buffer();
    palette_fade_target = (char *)&G_h01_1626;
    fade_palette_to_target(&G_h01_1626);
    SetRast(screen_rast_port, 0L);
    clear_input_direction_and_fire_state();

    while (!changed) {
        w2 = 0;
        w2 = poll_controller_and_keyboard_input();
        clear_input_direction_and_fire_state();
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xb0L,
                   0xc0L, 0xffL, 0L);
        draw_timed_scene_status_panel((int)first);
        if (timed_scene_active_events[timed_scene_selected_option_index].kind == 0)
            newflag = 0;
        if (!newflag && (w2 & 0x80)) {
            w2 = 0;
            play_sound(0x6a);
            timed_scene_actions_remaining--;
            if (timed_scene_actions_remaining < 0)
                break;
            if (!newflag) {
                if (!(timed_scene_event_capture_thresholds[(long)timed_scene_selected_option_index * 12] >= get_timed_event_frame_limit(&timed_scene_active_events[timed_scene_selected_option_index]))) {
                    configure_timed_item_animation(&timed_scene_active_events[timed_scene_selected_option_index]);
                    flags[idx] = (char)timed_scene_active_events[timed_scene_selected_option_index].type;
                    if (flags[idx] == timed_scene_bonus_event_type)
                        play_sound(0x6c);
                    else if (flags[c] != 0)
                        play_sound(0x6b);
                    newflag = 1;
                }
            }
            idx++;
            t5a = timed_scene_active_events[timed_scene_selected_option_index].kind;
            for (c = 0; c < 4; c++) {
                SetRast(screen_rast_port, 0L);
                BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xb0L,
                           0xc0L, 0xffL, 0L);
                draw_timed_scene_status_panel((int)first);
                update_timed_scene_event_slots();
                draw_masked_sprite(&G_h01_4154);
                if (t5a) ;
                if (c == 0) {
                    copy_palette_to_color_map(&G_h01_1666);
                    copy_palette_to_copper_lists();
                    switch_display_buffer();
                    palette_fade_target = (char *)&G_h01_1626;
                    fade_palette_to_target(&G_h01_1626);
                } else {
                    switch_display_buffer();
                }
            }
            continue;
        }

        {
            if ((w2 & 0x3f) == 8 || (w2 & 0x3f) == 7) {
                w2 = 0;
                if (timed_scene_selected_option_index != 0)
                    play_sound(0x6d);
                timed_scene_selected_option_index = 0;
            } else if ((w2 & 0x3f) == 2 || (w2 & 0x3f) == 3) {
                w2 = 0;
                if (timed_scene_selected_option_index != 2)
                    play_sound(0x6d);
                timed_scene_selected_option_index = 2;
            } else if ((w2 & 0x3f) == 1) {
                w2 = 0;
                if (timed_scene_selected_option_index != 1)
                    play_sound(0x6d);
                timed_scene_selected_option_index = 1;
            }
        }
        update_timed_scene_event_slots();
        draw_masked_sprite(&G_h01_4154);
        G_h01_422A = timed_scene_selected_option_index;
        G_h01_41F6 = small[timed_scene_selected_option_index * 2];
        G_h01_41F8 = small[timed_scene_selected_option_index * 2 + 1];
        draw_masked_sprite(&G_h01_41F6);
        switch_display_buffer();
        {
            if (cnt++ > lim) {
                cnt = 0;
                if (first)
                    timed_scene_elapsed_round_count++;
                else
                    first = 1;
            }
        }
        if (timed_scene_actions_remaining <= 0 || timed_scene_elapsed_round_count > 10)
            changed = 1;
    }

    free_bitmap_planes(&G_h01_3ADA, G_h01_3AD2, G_h01_3AD4);
    free_bitmap_planes(&G_h01_3B10, G_h01_3B08, G_h01_3B0A);
    free_bitmap_planes(&G_h01_3B46, G_h01_3B3E, G_h01_3B40);
    free_bitmap_planes(&G_h01_3B7C, G_h01_3B74, G_h01_3B76);
    free_bitmap_planes(&G_h01_3BB2, G_h01_3BAA, G_h01_3BAC);
    free_bitmap_planes(&G_h01_3BE8, G_h01_3BE0, G_h01_3BE2);
    free_bitmap_planes(&G_h01_3C1E, G_h01_3C16, G_h01_3C18);
    free_bitmap_planes(&G_h01_3C54, G_h01_3C4C, G_h01_3C4E);
    free_bitmap_planes(&G_h01_3C8A, G_h01_3C82, G_h01_3C84);
    free_bitmap_planes(&G_h01_3CC0, G_h01_3CB8, G_h01_3CBA);
    free_bitmap_planes(&G_h01_3CF6, G_h01_3CEE, G_h01_3CF0);
    free_bitmap_planes(&G_h01_3D2C, G_h01_3D24, G_h01_3D26);
    free_bitmap_planes(&G_h01_3D62, G_h01_3D5A, G_h01_3D5C);
    F_h00_4EC6();
    SetRast(screen_rast_port, 0L);

    for (c = 0; c < 32; c++) {
        switch (c + 14) {
        case 16: case 17: case 18: case 19:
        case 32: case 33: case 34: case 35:
            break;
        default:
            timed_scene_event_position_offsets[c].first = 0x2c;
            timed_scene_event_position_offsets[c].second = 0x2c;
            break;
        }
    }

    for (c = 0; c < 12; c++) {
        if (flags[c] == timed_scene_bonus_event_type)
            sel = timed_scene_bonus_event_type - 16;
        else
            sel = flags[c];
        switch ((int)sel) {
        case 14:
            G_h01_3D88 = pts[c].x - timed_scene_event_position_offsets[0].first;
            G_h01_3D8A = pts[c].y - timed_scene_event_position_offsets[0].second;
            G_h01_3DBC = 0;
            draw_masked_sprite(&G_h01_3D88);
            break;
        case 15:
            G_h01_3DBE = pts[c].x - timed_scene_event_position_offsets[1].first;
            G_h01_3DC0 = pts[c].y - timed_scene_event_position_offsets[1].second;
            G_h01_3DF2 = 0;
            draw_masked_sprite(&G_h01_3DBE);
            break;
        case 16:
            G_h01_3DF4 = pts[c].x - timed_scene_event_position_offsets[2].first;
            G_h01_3DF6 = pts[c].y - timed_scene_event_position_offsets[2].second;
            G_h01_3E28 = 0;
            draw_masked_sprite(&G_h01_3DF4);
            break;
        case 17:
            G_h01_3E2A = pts[c].x - timed_scene_event_position_offsets[3].first + 8;
            G_h01_3E2C = pts[c].y - timed_scene_event_position_offsets[3].second + 8;
            G_h01_3E5E = 0;
            draw_masked_sprite(&G_h01_3E2A);
            break;
        case 18:
            G_h01_3E60 = pts[c].x - timed_scene_event_position_offsets[4].first + 8;
            G_h01_3E62 = pts[c].y - timed_scene_event_position_offsets[4].second + 8;
            G_h01_3E94 = 0;
            draw_masked_sprite(&G_h01_3E60);
            break;
        case 19:
            G_h01_3E96 = pts[c].x - timed_scene_event_position_offsets[5].first;
            G_h01_3E98 = pts[c].y - timed_scene_event_position_offsets[5].second;
            G_h01_3ECA = 0;
            draw_masked_sprite(&G_h01_3E96);
            break;
        case 20:
            G_h01_3ECC = pts[c].x - timed_scene_event_position_offsets[6].first;
            G_h01_3ECE = pts[c].y - timed_scene_event_position_offsets[6].second;
            G_h01_3F00 = 0;
            draw_masked_sprite(&G_h01_3ECC);
            break;
        case 21:
            G_h01_3F02 = pts[c].x - timed_scene_event_position_offsets[7].first;
            G_h01_3F04 = pts[c].y - timed_scene_event_position_offsets[7].second;
            G_h01_3F36 = 0;
            draw_masked_sprite(&G_h01_3F02);
            break;
        case 22:
            G_h01_3F38 = pts[c].x - timed_scene_event_position_offsets[8].first;
            G_h01_3F3A = pts[c].y - timed_scene_event_position_offsets[8].second;
            G_h01_3F6C = 0;
            draw_masked_sprite(&G_h01_3F38);
            break;
        case 23:
            G_h01_3F6E = pts[c].x - timed_scene_event_position_offsets[9].first;
            G_h01_3F70 = pts[c].y - timed_scene_event_position_offsets[9].second;
            G_h01_3FA2 = 0;
            draw_masked_sprite(&G_h01_3F6E);
            break;
        case 24:
            G_h01_3FA4 = pts[c].x - timed_scene_event_position_offsets[10].first;
            G_h01_3FA6 = pts[c].y - timed_scene_event_position_offsets[10].second;
            G_h01_3FD8 = 0;
            draw_masked_sprite(&G_h01_3FA4);
            break;
        case 25:
            G_h01_3FDA = pts[c].x - timed_scene_event_position_offsets[11].first;
            G_h01_3FDC = pts[c].y - timed_scene_event_position_offsets[11].second;
            G_h01_400E = 0;
            draw_masked_sprite(&G_h01_3FDA);
            break;
        case 26:
            G_h01_4010 = pts[c].x - timed_scene_event_position_offsets[12].first;
            G_h01_4012 = pts[c].y - timed_scene_event_position_offsets[12].second;
            G_h01_4044 = 0;
            draw_masked_sprite(&G_h01_4010);
            break;
        case 27:
            G_h01_4046 = pts[c].x - timed_scene_event_position_offsets[13].first;
            G_h01_4048 = pts[c].y - timed_scene_event_position_offsets[13].second;
            G_h01_407A = 0;
            draw_masked_sprite(&G_h01_4046);
            break;
        case 28:
            G_h01_407C = pts[c].x - timed_scene_event_position_offsets[14].first;
            G_h01_407E = pts[c].y - timed_scene_event_position_offsets[14].second;
            G_h01_40B0 = 0;
            draw_masked_sprite(&G_h01_407C);
            break;
        case 29:
            G_h01_40B2 = pts[c].x - timed_scene_event_position_offsets[15].first;
            G_h01_40B4 = pts[c].y - timed_scene_event_position_offsets[15].second;
            G_h01_40E6 = 0;
            draw_masked_sprite(&G_h01_40B2);
            break;
        default:
            break;
        }

        if (flags[c] == timed_scene_bonus_event_type) {
            G_h01_40E8 = pts[c].x - timed_scene_event_position_offsets[timed_scene_bonus_event_type - 14].first;
            G_h01_40EA = pts[c].y - timed_scene_event_position_offsets[timed_scene_bonus_event_type - 14].second;
            if (timed_scene_bonus_event_type == 0x21 || timed_scene_bonus_event_type == 0x22) {
                G_h01_40E8 += 8;
                G_h01_40EA += 8;
            }
            G_h01_411C = 0;
            if (timed_scene_bonus_event_type == 0x1e)
                G_h01_411C = 1;
            draw_masked_sprite(&G_h01_40E8);
        }
    }

    for (c = 0; c < 6; c++) {
        if (c > 0 && timed_scene_route_point_indices[c] == timed_scene_route_point_indices[0])
            continue;
        switch (timed_scene_route_point_indices[c]) {
        case 14: free_bitmap_planes(&G_h01_3D98, G_h01_3D90, G_h01_3D92); break;
        case 15: free_bitmap_planes(&G_h01_3DCE, G_h01_3DC6, G_h01_3DC8); break;
        case 16: free_bitmap_planes(&G_h01_3E04, G_h01_3DFC, G_h01_3DFE); break;
        case 17: free_bitmap_planes(&G_h01_3E3A, G_h01_3E32, G_h01_3E34); break;
        case 18: free_bitmap_planes(&G_h01_3E70, G_h01_3E68, G_h01_3E6A); break;
        case 19: free_bitmap_planes(&G_h01_3EA6, G_h01_3E9E, G_h01_3EA0); break;
        case 20: free_bitmap_planes(&G_h01_3EDC, G_h01_3ED4, G_h01_3ED6); break;
        case 21: free_bitmap_planes(&G_h01_3F12, G_h01_3F0A, G_h01_3F0C); break;
        case 22: free_bitmap_planes(&G_h01_3F48, G_h01_3F40, G_h01_3F42); break;
        case 23: free_bitmap_planes(&G_h01_3F7E, G_h01_3F76, G_h01_3F78); break;
        case 24: free_bitmap_planes(&G_h01_3FB4, G_h01_3FAC, G_h01_3FAE); break;
        case 25: free_bitmap_planes(&G_h01_3FEA, G_h01_3FE2, G_h01_3FE4); break;
        case 26: free_bitmap_planes(&G_h01_4020, G_h01_4018, G_h01_401A); break;
        case 27: free_bitmap_planes(&G_h01_4056, G_h01_404E, G_h01_4050); break;
        case 28: free_bitmap_planes(&G_h01_408C, G_h01_4084, G_h01_4086); break;
        case 29: free_bitmap_planes(&G_h01_40C2, G_h01_40BA, G_h01_40BC); break;
        }
    }

    free_bitmap_planes(&G_h01_40F8, G_h01_40F0, G_h01_40F2);
    free_bitmap_planes(&G_h01_4164, G_h01_415C, G_h01_415E);
    free_bitmap_planes(&G_h01_419A, G_h01_4192, G_h01_4194);
    free_bitmap_planes(&G_h01_41D0, G_h01_41C8, G_h01_41CA);
    free_bitmap_planes(&G_h01_4206, G_h01_41FE, G_h01_4200);
    free_bitmap_planes(&G_h01_423C, G_h01_4234, G_h01_4236);
    fade_palette_to_black();
    request_disk(2);
    load_arc_record(0x33, &G_h01_411E);
    G_h01_411E = 0;
    G_h01_4120 = 0;
    G_h01_4152 = 0;
    draw_masked_sprite(&G_h01_411E);
    free_bitmap_planes(&G_h01_412E, G_h01_4126, G_h01_4128);

    for (c = 0; c < 12; c++) {
        if (flags[c] == timed_scene_bonus_event_type) {
            draw_text(pts[c].x - 38, pts[c].y + 3, "$", 0, 0);
            draw_decimal_value(pts[c].x - 30, pts[c].y + 3, 0x1f4L, 0, 0, 0);
            minigame_cash_winnings += 0x1f4;
            result = 1;
        } else if (flags[c] != 0) {
            draw_text(pts[c].x - 38, pts[c].y + 3, "$", 0, 0);
            draw_decimal_value(pts[c].x - 30, pts[c].y + 3, 0x32L, 0, 0, 0);
            minigame_cash_winnings += 0x32;
        }
    }

    draw_text(0x90, 0xb8, "$", 0, 0);
    draw_decimal_value(0x98, 0xb8, minigame_cash_winnings, 0, 0, 0);
    total_money += minigame_cash_winnings;
    switch_display_buffer();
    palette_fade_target = (char *)&G_h01_1626;
    fade_palette_to_target(&G_h01_1626);
    clear_input_direction_and_fire_state();
    wait_for_fire_input(0x28);
    Close(arc_file);
    arc_file = saved;
    arc_read_index(arc_file);
    if (result)
        player_treasure_collected[current_location].value = 1;
    game_day++;
    return result;
}
