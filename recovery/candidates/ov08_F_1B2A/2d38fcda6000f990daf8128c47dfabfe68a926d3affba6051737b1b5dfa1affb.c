/* Direct reconstruction candidate for ov08_F_1B2A. */
extern int G_h01_34E0;
extern int G_h01_34D0[16];
extern int G_h01_34D4[16];
extern int G_h01_34D8[16];
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();

recovered()
{
    int x;
    int y;
    int height;
    int width;

    x = G_h01_34D0[G_h01_34E0] - 8;
    y = G_h01_34D4[G_h01_34E0];
    switch ((long)G_h01_34D8[G_h01_34E0]) {
    case 21:
    case 27:
        x -= 40;
        y -= 40;
        width = 128;
        height = 128;
        break;
    default:
        height = 40;
        width = 56;
        break;
    }
    if (y + height > 168)
        height = 168 - y;
    if (x < 0)
        x = 0;
    else if (x + width > 320)
        width = 320 - x;
    F_h00_8A46(G_h01_46CE, (long)x, (long)y, G_h01_46D2,
        (long)x, (long)y, (long)width, (long)height,
        (long)192, (long)255, 0L);
}
