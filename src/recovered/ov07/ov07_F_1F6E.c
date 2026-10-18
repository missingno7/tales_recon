extern int G_h01_4D8A;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int BltBitMap();
extern int draw_text();
extern int strcat();
extern int invest_draw_total_money();
extern int invest_draw_game_day();
char *invest_format_unsigned_decimal();

recovered(idx, x, y)
int idx;
long x;
long y;
{
    char buf[34];
    char *p;

    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    invest_draw_total_money(y);
    invest_draw_game_day(x);
    draw_text(96, 8, "NEWS INFORMATION", 1, 15);
    buf[0] = 0;
    p = invest_format_unsigned_decimal((long)*(int *)((char *)&G_h01_4D8A + (long)idx * 46));
    strcat(buf, "NEWS BULLETIN FROM DAY ");
    strcat(buf, p);
    draw_text(56, 23, buf, 14, 0);
}
