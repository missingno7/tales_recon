/* Direct recovery candidate for ov04_F_07CA. */
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int G_h01_511C; extern int G_h01_511E; extern char G_h01_5150;
extern int G_h01_5124; extern int G_h01_5126; extern char G_h01_512C;
extern int G_h01_5338; extern int G_h01_533A; extern char G_h01_536C;
extern int G_h01_5340; extern int G_h01_5342; extern char G_h01_5348;
extern int G_h01_5152; extern int G_h01_5154; extern char G_h01_5186;
extern int G_h01_515A; extern int G_h01_515C; extern char G_h01_5162;
extern int G_h01_5188; extern int G_h01_518A; extern char G_h01_51BC;
extern int G_h01_5190; extern int G_h01_5192; extern char G_h01_5198;
extern int request_disk();
extern int load_arc_record();
extern int BltBitMap();
extern int draw_masked_sprite();
extern int free_bitmap_planes();

recovered()
{
    request_disk(1);
    load_arc_record(3, archive_image_bitmap);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);

    load_arc_record(4, &G_h01_511C);
    G_h01_511C = 120;
    G_h01_511E = 8;
    G_h01_5150 = 0;
    draw_masked_sprite(&G_h01_511C);
    free_bitmap_planes(&G_h01_512C, G_h01_5124, G_h01_5126);

    load_arc_record(5, &G_h01_5338);
    G_h01_5338 = 32;
    G_h01_533A = 48;
    G_h01_536C = 0;
    draw_masked_sprite(&G_h01_5338);
    free_bitmap_planes(&G_h01_5348, G_h01_5340, G_h01_5342);

    load_arc_record(6, &G_h01_5152);
    G_h01_5152 = 136;
    G_h01_5154 = 32;
    G_h01_5186 = 0;
    draw_masked_sprite(&G_h01_5152);
    free_bitmap_planes(&G_h01_5162, G_h01_515A, G_h01_515C);

    load_arc_record(7, &G_h01_5188);
    G_h01_5188 = 120;
    G_h01_518A = 48;
    G_h01_51BC = 0;
    draw_masked_sprite(&G_h01_5188);
    free_bitmap_planes(&G_h01_5198, G_h01_5190, G_h01_5192);

    BltBitMap(active_screen_bitmap, 0L, 0L, archive_image_bitmap,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
}
