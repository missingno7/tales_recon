extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();

recovered(y)
int y;
{
    *G_h01_5370 = 12;
    switch (y) {
    case 192:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 25), 174L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 194L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 25), 194L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)y, 194L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(y + 25), 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 25), 194L);
        break;
    case 224:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 174L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 174L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)y, 194L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 194L);
        break;
    case 256:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 174L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 194L);
        F_h00_8AA8(G_h01_46CA, (long)y, 194L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(y + 24), 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 194L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 174L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 194L);
        break;
    case 288:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 172L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 172L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 172L);
        F_h00_8AA8(G_h01_46CA, (long)y, 197L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)y, 172L);
        F_h00_8AA8(G_h01_46CA, (long)y, 197L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(y + 24), 172L);
        F_h00_8AA8(G_h01_46CA, (long)(y + 24), 197L);
        break;
    }
}
