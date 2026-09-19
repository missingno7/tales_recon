extern char *G_h01_5370;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_307C();

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
    F_h00_8A46(G_h01_46CE,0L,0L,G_h01_46D2,
        0L,0L,320L,200L,192L,255L,0L);
    *G_h01_5370=12;
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x-1),(long)y);
    F_h00_8AA8(G_h01_46CA,(long)(x-1),(long)(y+7));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x+32),(long)y);
    F_h00_8AA8(G_h01_46CA,(long)(x+32),(long)(y+7));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x-1),(long)(y-1));
    F_h00_8AA8(G_h01_46CA,(long)(x+32),(long)(y-1));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x-1),(long)(y+7));
    F_h00_8AA8(G_h01_46CA,(long)(x+32),(long)(y+7));
    F_h00_307C();
}
