extern long G_h01_46CA;
extern int F_h00_8044();
extern int F_h00_8B4C();
extern int F_h00_8B88();
extern int F_h00_8B98();
extern int F_h00_8BA8();
extern int F_h00_8BEA();

recovered(x, y, text, color, flag)
unsigned int x;
unsigned int y;
char *text;
unsigned char color;
unsigned char flag;
{
    F_h00_8B88(G_h01_46CA, (long)color);
    F_h00_8B98(G_h01_46CA, (long)flag);
    if (flag == 0) {
        F_h00_8BA8(G_h01_46CA, 0L);
    } else {
        F_h00_8BA8(G_h01_46CA, 1L);
    }
    F_h00_8B4C(G_h01_46CA, (long)x, (long)(y + 6));
    F_h00_8BEA(G_h01_46CA, text, (long)F_h00_8044(text));
}
