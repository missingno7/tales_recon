extern char *G_h01_5370;
extern long screen_rast_port;
extern char G_h01_418A;
extern char G_h01_41C0;
extern char G_h01_422C;
extern char timed_scene_actions_remaining;
extern int SetAPen();
extern int Move();
extern int Draw();
extern int draw_masked_sprite();
extern int draw_decimal_value();

recovered(a)
char a;
{
    *G_h01_5370=4;
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,0L,176L);
    Draw(screen_rast_port,319L,176L);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,0L,199L);
    Draw(screen_rast_port,319L,199L);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,0L,176L);
    Draw(screen_rast_port,0L,199L);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,319L,176L);
    Draw(screen_rast_port,319L,199L);
    draw_masked_sprite(&G_h01_418A);
    if (a)
        draw_masked_sprite(&G_h01_41C0);
    draw_masked_sprite(&G_h01_422C);
    draw_decimal_value(300,183,(long)timed_scene_actions_remaining,1,0,1);
}
