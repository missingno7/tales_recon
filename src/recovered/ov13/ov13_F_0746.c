extern char *G_h01_5370;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int BltBitMap();
extern int SetAPen();
extern int Move();
extern int Draw();
extern int switch_display_buffer();

recovered(a)
int a;
{
    int x,y;

    *G_h01_5370=1;
    x=(a&1) ? 168 : 120;
    if (a<2)
        y=88;
    else if (a<4)
        y=96;
    else if (a<6)
        y=104;
    else if (a<8)
        y=112;
    else
        y=120;
    BltBitMap(archive_image_bitmap,0L,0L,active_screen_bitmap,
        0L,0L,320L,200L,192L,255L,0L);
    *G_h01_5370=12;
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x-1),(long)y);
    Draw(screen_rast_port,(long)(x-1),(long)(y+7));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x+32),(long)y);
    Draw(screen_rast_port,(long)(x+32),(long)(y+7));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x-1),(long)(y-1));
    Draw(screen_rast_port,(long)(x+32),(long)(y-1));
    SetAPen(screen_rast_port,(long)*G_h01_5370);
    Move(screen_rast_port,(long)(x-1),(long)(y+7));
    Draw(screen_rast_port,(long)(x+32),(long)(y+7));
    switch_display_buffer();
}
