extern long screen_rast_port;
extern int strlen();
extern int Move();
extern int SetAPen();
extern int SetBPen();
extern int SetDrMd();
extern int Text();

recovered(x, y, text, color, flag)
unsigned int x;
unsigned int y;
char *text;
unsigned char color;
unsigned char flag;
{
    SetAPen(screen_rast_port, (long)color);
    SetBPen(screen_rast_port, (long)flag);
    if (flag == 0) {
        SetDrMd(screen_rast_port, 0L);
    } else {
        SetDrMd(screen_rast_port, 1L);
    }
    Move(screen_rast_port, (long)x, (long)(y + 6));
    Text(screen_rast_port, text, (long)strlen(text));
}
