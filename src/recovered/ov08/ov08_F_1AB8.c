extern int G_h01_34E0;
extern int G_h01_34DC[16];
extern int grid_full_screen_restore_countdown;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int BltBitMap();
extern int restore_grid_background_region();
extern int draw_grid_visible_entities();

recovered(P)
int P;
{
    int x;

    if (G_h01_34DC[G_h01_34E0] == 5 || G_h01_34DC[G_h01_34E0] == 6 || grid_full_screen_restore_countdown > 0) {
        BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
        grid_full_screen_restore_countdown--;
    } else {
        restore_grid_background_region();
        draw_grid_visible_entities(P);
    }
}
