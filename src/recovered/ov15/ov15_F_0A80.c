extern char *G_h01_5370;
extern long screen_rast_port;
extern int SetAPen();
extern int Move();
extern int Draw();

recovered(p,width,height)
int *p,width,height;
{
    int x,y;

    x=p[0]-1;
    y=p[1]-1;
    *G_h01_5370=1;
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x,(long)y);
    Draw(screen_rast_port,(long)x,(long)(y+height+1));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x+width+1),(long)y);
    Draw(screen_rast_port,(long)(x+width+1),(long)(y+height+1));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x,(long)y);
    Draw(screen_rast_port,(long)(x+width+1),(long)y);
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)x,(long)(y+height+1));
    Draw(screen_rast_port,(long)(x+width+1),(long)(y+height+1));
}
