/* ov05_F_3836: record and float-threshold updates; float math through m.lib FFP. */
extern int G_h01_0A84;
extern int G_h01_5E42;
extern char *G_h01_5370;
extern long G_h01_46CA;
extern char G_h01_46E1;
extern int G_h01_5E56;
extern int G_h01_5E52;
extern char G_h01_5E58;
extern int G_h01_593E;
extern int G_h01_5974;
extern int G_h01_59AA;
extern int G_h01_59AC;
extern int G_h01_5C9E;
extern int G_h01_5CA0;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_34E0();
extern int F_h00_09C0();

recovered()
{
    float a;
    float b;

    a = (float)G_h01_0A84;
    b = (float)G_h01_5E42;
    *G_h01_5370 = 4;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xb0L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xb0L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xc7L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xb1L);
    F_h00_8AA8(G_h01_46CA, 0L, 0xc7L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0x13fL, 0xb1L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
    F_h00_34E0(&G_h01_593E);
    if (G_h01_5E56 + 42 <= G_h01_0A84) {
        G_h01_46E1++;
        G_h01_5E56 += 42;
    }
    if (G_h01_46E1 < 10)
        F_h00_09C0(18, 184, (long)(G_h01_46E1 > 30 ? 30 : G_h01_46E1), 7, 1, 0);
    else
        F_h00_09C0(14, 184, (long)(G_h01_46E1 > 30 ? 30 : G_h01_46E1), 7, 1, 0);
    F_h00_34E0(&G_h01_5974);
    if (G_h01_5E58) {
        G_h01_59AA = (int)(a / b * 208.0 + 72.0);
        G_h01_59AC = 0xb1;
        F_h00_34E0(&G_h01_59AA);
        G_h01_5C9E = (int)((float)G_h01_5E52 / b * 208.0 + 72.0);
        G_h01_5CA0 = 0xba;
        F_h00_34E0(&G_h01_5C9E);
    } else {
        G_h01_59AA = (int)(a / b * 208.0 + 72.0);
        G_h01_59AC = 0xb6;
        F_h00_34E0(&G_h01_59AA);
    }
}
