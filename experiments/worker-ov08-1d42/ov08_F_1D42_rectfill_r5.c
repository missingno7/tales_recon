extern char *G_h01_5370;
extern long G_h01_01BC;
extern long G_h01_01B6;
extern long G_h01_01A4;
extern long G_h01_0162;
extern long G_h01_46CA;
extern char G_h01_33EE;
extern char G_h01_3424;
extern unsigned char G_h01_348E;
extern int G_h01_345A;
extern int G_h01_345C;
extern char G_h01_46E1;
extern long G_h01_46E6;
extern int F_h00_8B88();
extern int F_h00_8B76();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_34E0();
extern int F_h00_09C0();

recovered()
{
    char saved;
    int i;

    saved = *G_h01_5370;
    *G_h01_5370 = 0;
    F_h00_8B88(G_h01_01BC, (long)*G_h01_5370);
    F_h00_8B76(G_h01_46CA, 0L, 168L, 319L, 199L);
    *G_h01_5370 = 21;
    F_h00_8B88(G_h01_01BC, (long)*G_h01_5370);

    F_h00_8B4C(G_h01_01A4, 0L, 168L);
    F_h00_8AA8(G_h01_0162, 319L, 168L);
    F_h00_8B88(G_h01_01BC, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_01A4, 319L, 168L);
    F_h00_8AA8(G_h01_0162, 319L, 199L);
    F_h00_8B88(G_h01_01BC, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_01A4, 0L, 199L);
    F_h00_8AA8(G_h01_0162, 319L, 199L);
    F_h00_8B88(G_h01_01BC, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_01A4, 0L, 199L);
    F_h00_8AA8(G_h01_0162, 0L, 199L);
    *G_h01_5370 = saved;
    F_h00_34E0(&G_h01_33EE);
    F_h00_34E0(&G_h01_3424);
    G_h01_348E = 2;
    G_h01_345A = 200;
    G_h01_345C = 178;
    for (i = 0; i < G_h01_46E1; ++i) {
        F_h00_34E0(&G_h01_345A);
        --G_h01_348E;
        G_h01_345A += 32;
    }
    F_h00_09C0(168, 174, (long)G_h01_46E6, 1, 26, 1);
    if (G_h01_46E1 < 10) {
        F_h00_09C0(18, 182, (long)G_h01_46E1, 27, 1, 0);
    } else {
        F_h00_09C0(14, 182, (long)G_h01_46E1, 27, 1, 0);
    }
}
