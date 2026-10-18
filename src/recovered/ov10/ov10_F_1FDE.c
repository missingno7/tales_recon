struct Flags {
    char pad;
    unsigned char bits;
};
extern char *G_h01_5370;
extern long screen_rast_port;
extern int SetAPen();
extern int WritePixel();

recovered(x,y,flags,active)
int x,y;
struct Flags *flags;
int active;
{
    char i,j;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            SetAPen(screen_rast_port,(long)*G_h01_5370);
            WritePixel(screen_rast_port,(long)(x+j),(long)(y+i));
        }
    if (active) {
    *G_h01_5370=3;
    if (flags->bits&8) {
        SetAPen(screen_rast_port,(long)*G_h01_5370);
        WritePixel(screen_rast_port,(long)(x+3),(long)(y-1));
    }
    if (flags->bits&4) {
        SetAPen(screen_rast_port,(long)*G_h01_5370);
        WritePixel(screen_rast_port,(long)(x-1),(long)(y+3));
    }
    if (flags->bits&2) {
        SetAPen(screen_rast_port,(long)*G_h01_5370);
        WritePixel(screen_rast_port,(long)(x+3),(long)(y+3));
    }
    if (flags->bits&1) {
        SetAPen(screen_rast_port,(long)*G_h01_5370);
        WritePixel(screen_rast_port,(long)(x-1),(long)(y-1));
    }
    }
}
