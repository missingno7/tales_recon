/* resident_F_0640: loads the screen asset selected by case a; cases 11-14 then also set palette_fade_target and call fade_palette_to_target with it. i1 is unused: the original 4-byte frame places flag at -3(a5). */
extern int SetRast();
extern int request_disk();
extern int arc_read_index();
extern int fade_palette_to_black();
extern int load_arc_record();
extern int BltBitMap();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int clear_input_direction_and_fire_state();
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern long arc_file;
extern char G_h01_1926;
extern char G_h01_1966;
extern char G_h01_19A6;

recovered(a)
int a;
{
    int i1;
    char flag;

    flag = 0;
    SetRast(screen_rast_port, 0L);
    request_disk(1);
    arc_read_index(arc_file);
    fade_palette_to_black();
    switch (a) {
    case 3:
        load_arc_record(30, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 1:
    case 9:
        load_arc_record(32, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 2:
        load_arc_record(41, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 6:
        load_arc_record(35, active_screen_bitmap);
        break;
    case 10:
        load_arc_record(33, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 11:
        load_arc_record(38, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch_display_buffer();
        palette_fade_target = &G_h01_1926;
        fade_palette_to_target(&G_h01_1926);
        break;
    case 12:
        load_arc_record(39, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch_display_buffer();
        palette_fade_target = &G_h01_1926;
        fade_palette_to_target(&G_h01_1926);
        break;
    case 13:
        load_arc_record(36, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch_display_buffer();
        palette_fade_target = &G_h01_1966;
        fade_palette_to_target(&G_h01_1966);
        break;
    case 14:
        load_arc_record(37, archive_image_bitmap);
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        switch_display_buffer();
        palette_fade_target = &G_h01_19A6;
        fade_palette_to_target(&G_h01_19A6);
        break;
    default:
        switch_display_buffer();
        break;
    }
    clear_input_direction_and_fire_state();
}
