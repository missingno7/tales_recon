extern char *G_h01_5370;
extern long screen_rast_port;
extern short G_h01_33EE;
extern short G_h01_3424;
extern unsigned char G_h01_348E;
extern short G_h01_345A;
extern short G_h01_345C;
extern unsigned char grid_lives_remaining;
extern long total_money;
extern char game_day;
extern void SetAPen();
extern void RectFill();
extern void Move();
extern void Draw();
extern void draw_masked_sprite();
extern void draw_decimal_value();

void recovered()
{
    char saved;
    int i;
    saved = *G_h01_5370;
    *G_h01_5370 = 0;
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    RectFill(screen_rast_port, 0L, 0xa8L, 0x13fL, 0xc7L);
    *G_h01_5370 = 0x15;
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 0L, 0xa8L);
    Draw(screen_rast_port, 0x13fL, 0xa8L);
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 0x13fL, 0xa8L);
    Draw(screen_rast_port, 0x13fL, 0xc7L);
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 0L, 0xc7L);
    Draw(screen_rast_port, 0x13fL, 0xc7L);
    SetAPen(screen_rast_port, (long)*G_h01_5370);
    Move(screen_rast_port, 0L, 0xa8L);
    Draw(screen_rast_port, 0L, 0xc7L);
    *G_h01_5370 = saved;
    draw_masked_sprite(&G_h01_33EE);
    draw_masked_sprite(&G_h01_3424);
    G_h01_348E = 2;
    G_h01_345A = 0xc8;
    G_h01_345C = 0xb2;
    for (i = 0; i < grid_lives_remaining; ++i) {
        draw_masked_sprite(&G_h01_345A);
        --G_h01_348E;
        G_h01_345A += 0x20;
    }
    draw_decimal_value(0xa8, 0xae, total_money, 1, 0x1a, 1);
    if (game_day < 10)
        draw_decimal_value(0x12, 0xb6, (long)game_day, 0x1b, 1, 0);
    else
        draw_decimal_value(0xe, 0xb6, (long)game_day, 0x1b, 1, 0);
}
