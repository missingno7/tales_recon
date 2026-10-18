/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
extern int G_h01_1422; /* 1x; w2 */
extern long screen_rast_port; /* 13x; w4 */
extern long archive_image_bitmap; /* 15x; w4 */
extern long active_screen_bitmap; /* 16x; w4 */
extern char *palette_fade_target; /* 3x; w4 */
extern long arc_file; /* 5x; w4 */
struct UiState;
extern struct UiState G_h01_50E6;
extern int G_h01_511C; /* 2x */
extern int G_h01_5152; /* 2x */
extern int G_h01_5188; /* 2x */
extern int G_h01_5338; /* 1x; w2 */
extern int G_h01_533A; /* 1x; w2 */
extern char G_h01_536C; /* 1x; w1 */
extern int request_disk(); /* 10x */
extern int arc_read_index(); /* 4x */
extern int load_arc_record(); /* 5x; alt long () x2 */
extern int switch_display_buffer(); /* 13x */
extern int fade_palette_to_target(); /* 3x */
extern int fade_palette_to_black(); /* 4x */
extern int draw_masked_sprite(); /* 20x; alt void () x2 */
extern int draw_text(); /* 9x */
extern int free_bitmap_planes(); /* 6x */
extern int clear_input_direction_and_fire_state(); /* 4x */
extern int poll_controller_and_keyboard_input(); /* 4x; alt char () x1 */
extern int F_h00_4D04(); /* 3x */
extern int F_h00_4EC6(); /* 5x */
extern int play_sound(); /* 19x */
extern int Delay(); /* 8x */
extern int BltBitMap(); /* 16x */
extern int SetRast(); /* 5x */
extern int initialize_office_menu_scene(); /* 1x */
/* invest_office_palette: no canonical view */
/* G_h01_2A16: no canonical view; w4 */
/* G_h01_5E5E: no canonical view; w1 */
/* G_h01_A6C6: inside G_h01_A6B0+22 (struct Record [36]); w2 */
/* G_h01_A6C8: inside G_h01_A6B0+24 (struct Record [36]); w2 */
/* G_h01_A6CE: inside G_h01_A6B0+30 (struct Record [36]); w2 */
/* G_h01_A6D0: inside G_h01_A6B0+32 (struct Record [36]); w2 */
/* G_h01_A6D6: inside G_h01_A6B0+38 (struct Record [36]) */
/* G_h01_A6FC: inside G_h01_A6B0+76 (struct Record [36]); w2 */
/* G_h01_A6FE: inside G_h01_A6B0+78 (struct Record [36]); w2 */
/* G_h01_A704: inside G_h01_A6B0+84 (struct Record [36]); w2 */
/* G_h01_A706: inside G_h01_A6B0+86 (struct Record [36]); w2 */
/* G_h01_A70C: inside G_h01_A6B0+92 (struct Record [36]) */
/* G_h01_A732: inside G_h01_A6B0+130 (struct Record [36]); w2 */
/* G_h01_A734: inside G_h01_A6B0+132 (struct Record [36]); w2 */
/* G_h01_A73A: inside G_h01_A6B0+138 (struct Record [36]); w2 */
/* G_h01_A73C: inside G_h01_A6B0+140 (struct Record [36]); w2 */
/* G_h01_A742: inside G_h01_A6B0+146 (struct Record [36]) */
/* F_h13_012E: no canonical view */
/* F_h13_0190: no canonical view */


extern long G_h01_2A16;
extern char invest_office_palette;
extern char G_h01_5E5E;
extern int G_h01_A6C6;
extern int G_h01_A6C8;
extern int G_h01_A6CE;
extern int G_h01_A6D0;
extern char G_h01_A6D6;
extern int G_h01_A6FC;
extern int G_h01_A6FE;
extern int G_h01_A704;
extern int G_h01_A706;
extern char G_h01_A70C;
extern int G_h01_A732;
extern int G_h01_A734;
extern int G_h01_A73A;
extern int G_h01_A73C;
extern char G_h01_A742;
extern int F_h13_012E();
extern int F_h13_0190();

recovered()
{
    int choice, result, done, i;
    unsigned char input;

    done = 0;
    play_sound(0x21);
    while (G_h01_2A16 != 0)
        ;
    SetRast(screen_rast_port, 0L);
    play_sound(0);
    initialize_office_menu_scene(0, 0, 1);
    F_h00_4EC6();
    request_disk(1);
    F_h00_4D04(1);
    request_disk(1);
    arc_read_index(arc_file);
    fade_palette_to_black();
    play_sound(6);
    switch_display_buffer();
    palette_fade_target = &invest_office_palette;
    fade_palette_to_target(&invest_office_palette);
    G_h01_5E5E = 0;
    result = 0x23;
    for (;;) {
        if (done)
            break;
        input = 0;
        choice = 0;
        for (;;) {
            if (input & 0x80)
                goto state_dispatch;
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
                    0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        draw_masked_sprite(&G_h01_50E6);
        draw_masked_sprite(&G_h01_511C);
        draw_masked_sprite(&G_h01_5152);
        draw_masked_sprite(&G_h01_5188);
        draw_masked_sprite(&G_h01_5338);
        input = poll_controller_and_keyboard_input();
        switch (input & 0x3f) {
                    case 1:
                        draw_text(0x76, 0x0b, "MONEY BIN", 0, 0);
                        draw_text(0x78, 0x0a, "MONEY BIN", 1, 0);
                        choice = 2;
                        switch_display_buffer();
                        break;
                    case 3:
                        draw_text(0xc6, 0x21, "CONTROL CENTER", 0, 0);
                        draw_text(0xc8, 0x20, "CONTROL CENTER", 1, 0);
                        choice = 1;
                        switch_display_buffer();
                        break;
                    case 7:
                        draw_text(0x0c, 0x21, "INVESTMENTS", 0, 0);
                        draw_text(0x0e, 0x20, "INVESTMENTS", 1, 0);
                        choice = 3;
                        switch_display_buffer();
                        break;
                    default:
                        choice = 0;
                        switch_display_buffer();
                        break;
                    }            Delay(1L);
        }
    state_dispatch:
        switch (choice) {
                case 1:
                    request_disk(1);
                    load_arc_record(0x11, &G_h01_A6C6);
                    load_arc_record(0x12, &G_h01_A6FC);
                    play_sound(0);
                    initialize_office_menu_scene(0, 0, 0);
                    G_h01_A6C6 = 0x108;
                    G_h01_A6C8 = 0;
                    draw_masked_sprite(&G_h01_A6C6);
                    G_h01_A6FC = 0xd0;
                    G_h01_A6FE = 0;
                    draw_masked_sprite(&G_h01_A6FC);
                    draw_masked_sprite(&G_h01_50E6);
                    switch_display_buffer();
                    free_bitmap_planes(&G_h01_A70C, G_h01_A704, G_h01_A706);
                    free_bitmap_planes(&G_h01_A6D6, G_h01_A6CE, G_h01_A6D0);
                    F_h13_012E();
                    play_sound(5);
                    result = 0x28;
                    done = 1;
                    break;
                case 2:
                    play_sound(0);
                    F_h13_0190();
                    F_h13_012E();
                    result = 0x26;
                    done = 1;
                    break;
                case 3:
                    request_disk(1);
                    load_arc_record(0x13, &G_h01_A732);
                    play_sound(0);
                    initialize_office_menu_scene(0, 0, 0);
                    G_h01_5338 = 0x21;
                    G_h01_533A = 0x30;
                    G_h01_536C = 0;
                    G_h01_A732 = 9;
                    G_h01_A734 = 0x10;
                    draw_masked_sprite(&G_h01_A732);
                    draw_masked_sprite(&G_h01_5338);
                    switch_display_buffer();
                    draw_masked_sprite(&G_h01_5338);
                    draw_masked_sprite(&G_h01_A732);
                    play_sound(3);
                    G_h01_1422 = 1;
                    i = 0;
                    do {
                        initialize_office_menu_scene(0, 0, 0);
                        draw_masked_sprite(&G_h01_A732);
                        G_h01_536C = i;
                        draw_masked_sprite(&G_h01_5338);
                        switch_display_buffer();
                        Delay(10L);
                        ++i;
                    } while (i <= 3);
                    initialize_office_menu_scene(0, 0, 0);
                    draw_masked_sprite(&G_h01_A732);
                    G_h01_536C = 3;
                    draw_masked_sprite(&G_h01_5338);
                    switch_display_buffer();
                    Delay(10L);
                    switch_display_buffer();
                    G_h01_1422 = 0;
                    free_bitmap_planes(&G_h01_A742, G_h01_A73A, G_h01_A73C);
                    F_h13_012E();
                    result = 0x27;
                    done = 1;
                    break;
                }
    }

    clear_input_direction_and_fire_state();
    G_h01_5E5E = 1;
    return result;
}