extern char *G_h01_5370;
extern long screen_rast_port;
extern int SetAPen();
extern int Move();
extern int Draw();
recovered(x,y,w,h,pen) int x,y,w,h; char pen; {
 *G_h01_5370=pen;
 SetAPen(screen_rast_port,(long)*G_h01_5370);
 Move(screen_rast_port,(long)x,(long)y);
 Draw(screen_rast_port,(long)(x+w),(long)y);
 SetAPen(screen_rast_port,(long)*G_h01_5370);
 Move(screen_rast_port,(long)x,(long)(y+h));
 Draw(screen_rast_port,(long)(x+w),(long)(y+h));
 SetAPen(screen_rast_port,(long)*G_h01_5370);
 Move(screen_rast_port,(long)x,(long)y);
 Draw(screen_rast_port,(long)x,(long)(y+h));
 SetAPen(screen_rast_port,(long)*G_h01_5370);
 Move(screen_rast_port,(long)(x+w),(long)y);
 Draw(screen_rast_port,(long)(x+w),(long)(y+h));
}
