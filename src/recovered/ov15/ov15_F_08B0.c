extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_8C10();

recovered(x,y)
int x,y;
{
    char i,j;
    int x0,y0;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
            F_h00_8C10(G_h01_46CA,(long)(x+j),(long)(y+i));
        }
    x0=x-1;
    y0=y-1;
    *G_h01_5370=0;
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x0,(long)y0);
    F_h00_8AA8(G_h01_46CA,(long)(x0+4),(long)y0);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x0,(long)(y0+1));
    F_h00_8AA8(G_h01_46CA,(long)x0,(long)(y0+4));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x0+4),(long)(y0+1));
    F_h00_8AA8(G_h01_46CA,(long)(x0+4),(long)(y0+4));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x0,(long)(y0+4));
    F_h00_8AA8(G_h01_46CA,(long)(x0+4),(long)(y0+4));
}
