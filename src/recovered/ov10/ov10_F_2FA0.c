extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern unsigned short G_h01_7194;
extern unsigned short G_h01_7196;
extern unsigned short G_h01_719C;
extern unsigned short G_h01_719E;
extern unsigned short G_h01_71A4;
extern unsigned short G_h01_71CA;
extern unsigned short G_h01_71CC;
extern unsigned short G_h01_71D2;
extern unsigned short G_h01_71D4;
extern unsigned short G_h01_71DA;
extern unsigned short G_h01_7200;
extern unsigned short G_h01_7202;
extern unsigned short G_h01_7208;
extern unsigned short G_h01_720A;
extern unsigned short G_h01_7210;
extern unsigned short G_h01_7488;
extern unsigned short G_h01_748A;
extern unsigned short G_h01_7490;
extern unsigned short G_h01_7492;
extern unsigned short G_h01_7498;
extern unsigned short G_h01_74BE;
extern unsigned short G_h01_74C0;
extern unsigned short G_h01_74C6;
extern unsigned short G_h01_74C8;
extern unsigned short G_h01_74CE;
extern unsigned short cave_player_to_finish_distance;
extern unsigned short cave_player_cell_index;
extern int BltBitMap();
extern int F_h10_320C();
extern int request_disk();
extern int load_arc_record();
extern int draw_masked_sprite();
extern int free_bitmap_planes();
extern int play_sound();
extern int play_cave_distance_cue();

void recovered(p, flag)
char *p;
char flag;
{
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h10_320C(p);
    request_disk(2);

    if ((*((unsigned short *)p) & 0x40) == 0x40) {
        load_arc_record(2, &G_h01_74BE);
        G_h01_74BE = 0x1a;
        G_h01_74C0 = 0x5c;
        draw_masked_sprite(&G_h01_74BE);
        free_bitmap_planes(&G_h01_74CE, G_h01_74C6, G_h01_74C8);
    }

    if (cave_player_to_finish_distance < 2) {
        load_arc_record(9, &G_h01_7200);
        G_h01_7200 = 0x68;
        G_h01_7202 = 0x8;
        draw_masked_sprite(&G_h01_7200);
        free_bitmap_planes(&G_h01_7210, G_h01_7208, G_h01_720A);
    } else if (cave_player_to_finish_distance < 4) {
        load_arc_record(8, &G_h01_71CA);
        G_h01_71CA = 0x68;
        G_h01_71CC = 0x8;
        draw_masked_sprite(&G_h01_71CA);
        free_bitmap_planes(&G_h01_71DA, G_h01_71D2, G_h01_71D4);
    } else if (cave_player_to_finish_distance < 6) {
        load_arc_record(7, &G_h01_7194);
        G_h01_7194 = 0x68;
        G_h01_7196 = 0x41;
        draw_masked_sprite(&G_h01_7194);
        free_bitmap_planes(&G_h01_71A4, G_h01_719C, G_h01_719E);
    }

    if (((*((unsigned short *)(p - 2)) & 0x40) == 0x40 &&
         ((cave_player_cell_index & 7) != 0) && ((p[1] & 1) != 0)) ||
        ((*((unsigned short *)(p + 2)) & 0x40) == 0x40 &&
         ((cave_player_cell_index & 7) != 7) && (p[1] & 2)) ||
        ((*((unsigned short *)(p - 0x10)) & 0x40) == 0x40 &&
         (cave_player_cell_index > 7) && (p[1] & 8)) ||
        ((*((unsigned short *)(p + 0x10)) & 0x40) == 0x40 &&
         (cave_player_cell_index < 0x38) && (p[1] & 4))) {
        load_arc_record(1, &G_h01_7488);
        G_h01_7488 = 0x57;
        G_h01_748A = 0xe;
        draw_masked_sprite(&G_h01_7488);
        if (flag != 0)
            play_sound(0x4d);
        free_bitmap_planes(&G_h01_7498, G_h01_7490, G_h01_7492);
    } else if (flag != 0) {
        play_cave_distance_cue(cave_player_to_finish_distance);
    }
    BltBitMap(active_screen_bitmap, 0L, 0L, archive_image_bitmap, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
}









