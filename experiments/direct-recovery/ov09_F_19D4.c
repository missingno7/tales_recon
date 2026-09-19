extern char *G_h01_5370;
extern long G_h01_46CA;
extern char G_h01_418A;
extern char G_h01_41C0;
extern char G_h01_422C;
extern char G_h01_4270;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_34E0();
extern int F_h00_09C0();

recovered(a)
char a;
{
    *G_h01_5370=4;
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,0L,176L);
    F_h00_8AA8(G_h01_46CA,319L,176L);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,0L,199L);
    F_h00_8AA8(G_h01_46CA,319L,199L);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,0L,176L);
    F_h00_8AA8(G_h01_46CA,0L,199L);
    F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA,319L,176L);
    F_h00_8AA8(G_h01_46CA,319L,199L);
    F_h00_34E0(&G_h01_418A);
    if (a)
        F_h00_34E0(&G_h01_41C0);
    F_h00_34E0(&G_h01_422C);
    F_h00_09C0(300,183,(long)G_h01_4270,1,0,1);
}
