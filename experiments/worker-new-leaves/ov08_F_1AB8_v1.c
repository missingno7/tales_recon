extern short G_h01_34E0;
extern short G_h01_34DC[];
extern short G_h01_6F32;
extern int G_h01_46D0;
extern int G_h01_46D4;
extern int F_h00_014A();
extern int F_h08_1B2A();
extern int F_h08_354E();

recovered(arg)
int arg;
{
    if (G_h01_34DC[G_h01_34E0] != 5 && G_h01_34DC[G_h01_34E0] != 6)
        return F_h08_1B2A();
    if (G_h01_6F32 <= 0)
        return F_h08_1B2A();
    F_h00_014A(G_h01_46D0, 0, 0, G_h01_46D4, 0, 0, 0,
               0x140, 0xA8, 0xC0, 0xFF);
    --G_h01_6F32;
    return F_h08_354E(arg);
}
