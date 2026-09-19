extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();

recovered(p,width,height)
int *p,width,height;
{
    int x,y;

    x=p[0]-1;
    y=p[1]-1;
    *G_h01_5370=1;
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x,(long)y);
    F_h00_8AA8(G_h01_46CA,(long)x,(long)(y+height+1));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)(x+width+1),(long)y);
    F_h00_8AA8(G_h01_46CA,(long)(x+width+1),(long)(y+height+1));
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x,(long)y);
    F_h00_8AA8(G_h01_46CA,(long)(x+width+1),(long)y);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,(long)x,(long)(y+height+1));
    F_h00_8AA8(G_h01_46CA,(long)(x+width+1),(long)(y+height+1));
}
