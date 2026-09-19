struct Flags {
    char pad;
    unsigned char bits;
};
extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8C10();

recovered(x,y,flags,active)
int x,y;
struct Flags *flags;
int active;
{
    char i,j;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
            F_h00_8C10(G_h01_46CA,(long)(x+j),(long)(y+i));
        }
    if (!active)
        return;
    *G_h01_5370=3;
    if (flags->bits&8) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x+3),(long)(y-1));
    }
    if (flags->bits&4) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x-1),(long)(y+3));
    }
    if (flags->bits&2) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x+3),(long)(y+3));
    }
    if (flags->bits&1) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x-1),(long)(y-1));
    }
}
