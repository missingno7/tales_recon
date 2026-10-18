extern char *G_h01_5370;
extern long screen_rast_port;
extern char G_h01_418A;
extern char G_h01_41C0;
extern char G_h01_422C;
extern char G_h01_4270;
extern int SetAPen();
extern int Move();
extern int Draw();
extern int F_h00_34E0();
extern int F_h00_09C0();

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
    F_h00_34E0(&G_h01_418A);
    if (a)
        F_h00_34E0(&G_h01_41C0);
    F_h00_34E0(&G_h01_422C);
    F_h00_09C0(300,183,(long)G_h01_4270,1,0,1);
}
