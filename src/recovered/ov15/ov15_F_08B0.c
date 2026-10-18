extern char *G_h01_5370;
extern long screen_rast_port;
extern int SetAPen();
extern int Move();
extern int Draw();
extern int WritePixel();

recovered(x,y)
int x,y;
{
    char i,j;
    int x0,y0;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            SetAPen(screen_rast_port,(long)*G_h01_5370);
            WritePixel(screen_rast_port,(long)(x+j),(long)(y+i));
        }
    x0=x-1;
    y0=y-1;
    *G_h01_5370=0;
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x0,(long)y0);
    Draw(screen_rast_port,(long)(x0+4),(long)y0);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x0,(long)(y0+1));
    Draw(screen_rast_port,(long)x0,(long)(y0+4));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x0+4),(long)(y0+1));
    Draw(screen_rast_port,(long)(x0+4),(long)(y0+4));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x0,(long)(y0+4));
    Draw(screen_rast_port,(long)(x0+4),(long)(y0+4));
}
