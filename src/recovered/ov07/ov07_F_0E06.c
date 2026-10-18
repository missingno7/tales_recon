struct Header {
    int first;
    int second;
};

extern int draw_masked_sprite();
extern int draw_decimal_value();
extern char game_day;

recovered(p)
struct Header *p;
{
    int unused1;
    int unused2;

    p->first = 8;
    p->second = 175;
    draw_masked_sprite(p);
    if (game_day < 10)
        draw_decimal_value(18, 182, (long)game_day, 7, 1, 0);
    else
        draw_decimal_value(14, 182, (long)game_day, 7, 1, 0);
}
