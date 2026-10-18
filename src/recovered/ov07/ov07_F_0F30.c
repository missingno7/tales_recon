extern long screen_rast_port;
extern char *G_h01_5370;
extern int Draw();
extern int Move();
extern int SetAPen();

recovered(arg)
int arg;
{
    *G_h01_5370 = 12;
    switch (arg) {
    case 0xc0:
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xaeL);
        Draw(screen_rast_port, (long)(arg + 25), 0xaeL);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xc2L);
        Draw(screen_rast_port, (long)(arg + 25), 0xc2L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xaeL);
        Draw(screen_rast_port, (long)arg, 0xc2L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)(arg + 25), 0xaeL);
        Draw(screen_rast_port, (long)(arg + 25), 0xc2L);
        break;
    case 0xe0:
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xaeL);
        Draw(screen_rast_port, (long)(arg + 24), 0xaeL);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xc2L);
        Draw(screen_rast_port, (long)(arg + 24), 0xc2L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xaeL);
        Draw(screen_rast_port, (long)arg, 0xc2L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)(arg + 24), 0xaeL);
        Draw(screen_rast_port, (long)(arg + 24), 0xc2L);
        break;
    case 0x100:
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xaeL);
        Draw(screen_rast_port, (long)(arg + 24), 0xaeL);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xc2L);
        Draw(screen_rast_port, (long)(arg + 24), 0xc2L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xaeL);
        Draw(screen_rast_port, (long)arg, 0xc2L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)(arg + 24), 0xaeL);
        Draw(screen_rast_port, (long)(arg + 24), 0xc2L);
        break;
    case 0x120:
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xacL);
        Draw(screen_rast_port, (long)(arg + 24), 0xacL);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xc5L);
        Draw(screen_rast_port, (long)(arg + 24), 0xc5L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)arg, 0xacL);
        Draw(screen_rast_port, (long)arg, 0xc5L);
        SetAPen(screen_rast_port, (long)*G_h01_5370);
        Move(screen_rast_port, (long)(arg + 24), 0xacL);
        Draw(screen_rast_port, (long)(arg + 24), 0xc5L);
        break;
    default:
        break;
    }
}
