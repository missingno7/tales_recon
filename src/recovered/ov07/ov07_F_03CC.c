/* Non-promoting ownership probe for ov07_F_03CC. */
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int BltBitMap();
extern int invest_draw_game_day();
extern int invest_draw_total_money();
extern int draw_text();
extern char G_h01_3232;
extern char G_h01_329E;

recovered()
{
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    invest_draw_game_day(&G_h01_3232);
    invest_draw_total_money(&G_h01_329E);
    draw_text(100, 8, "STOCK PORTFOLIO", 7, 15);
    draw_text(40, 22, "COMPANY NAME", 1, 7);
    draw_text(196, 22, "PRICE", 1, 7);
    draw_text(244, 22, "SHARES", 1, 7);
}
