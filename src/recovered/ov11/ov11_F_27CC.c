struct DrawRecord {
    int x;
    int y;
    char unused[48];
    char pen;
};

extern long screen_rast_port;
extern char game_day;
extern long total_money;
extern char *G_h01_5370;
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94AC;
extern int G_h01_94C0;
extern long G_h01_9F92;
extern long G_h01_9F96;
extern long G_h01_9F9A;
extern int draw_decimal_value();
extern int draw_masked_sprite();
extern int Draw();
extern int Move();
extern void RectFill();
extern int SetAPen();
extern int integer_within_inclusive_range();

void recovered()
{
    char saved;
    int i;
    int bottom;
    int redraw;

    bottom = 0xb0;
    redraw = 0;
    saved = *G_h01_5370;
    if (G_h01_94AE == 6 ||
        integer_within_inclusive_range(bottom, G_h01_94C0 + 0x20, 0xb0))
        redraw = 1;

    if (redraw || G_h01_8A3C) {
        *G_h01_5370 = 0;
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        RectFill(screen_rast_port, 0L, (long)bottom, 0x13fL, 0xc7L);
        *G_h01_5370 = 0x11;
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 0x13fL, (long)bottom);
        Draw(screen_rast_port, 0x13fL, 0xc7L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 0L, 0xc7L);
        Draw(screen_rast_port, 0x13fL, 0xc7L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, 0L, (long)bottom);
        Draw(screen_rast_port, 0L, 0xc7L);

        draw_masked_sprite(G_h01_9F96);
        draw_masked_sprite(G_h01_9F9A);
        ((struct DrawRecord *)G_h01_9F92)->pen = 2;
        ((struct DrawRecord *)G_h01_9F92)->x = 0xd8;
        ((struct DrawRecord *)G_h01_9F92)->y = 0xba;
        i = 0;
        for (; i <= 3 - G_h01_94AC; ++i) {
            draw_masked_sprite(G_h01_9F92);
            ((struct DrawRecord *)G_h01_9F92)->pen--;
            ((struct DrawRecord *)G_h01_9F92)->x += 0x20;
        }
        draw_decimal_value(0xae, 0xb5, total_money, 1, 0, 1);
        if (game_day < 10)
            draw_decimal_value(0x12, 0xb9, (long)game_day, 0, 0, 0);
        else
            draw_decimal_value(0xe, 0xb9, (long)game_day, 0, 0, 0);
    }

    *G_h01_5370 = 0x11;
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 0L, (long)bottom);
    Draw(screen_rast_port, 0x13fL, (long)bottom);
    *G_h01_5370 = saved;
}
