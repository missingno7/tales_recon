extern char *G_h01_5370;
extern long G_h01_46CA;
extern short G_h01_33EE;
extern short G_h01_3424;
extern unsigned char G_h01_348E;
extern short G_h01_345A;
extern short G_h01_345C;
extern unsigned char G_h01_6F3B;
extern long G_h01_46E6;
extern char G_h01_46E1;
extern void F_h00_8B88();
extern void F_h00_8B76();
extern void F_h00_8B4C();
extern void F_h00_8AA8();
extern void F_h00_34E0();
extern void F_h00_09C0();

void recovered()
{
    char saved;
    int i;
    saved = *G_h01_5370;
    *G_h01_5370 = 0;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B76(G_h01_46CA, 0L, 0xa8L, 0x13fL, 0xc7L);
    *G_h01_5370 = 0x15;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xa8L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xa8L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0x13fL, 0xa8L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xc7L);
    F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, 0xa8L);
    F_h00_8AA8(G_h01_46CA, 0L, 0xc7L);
    *G_h01_5370 = saved;
    F_h00_34E0(&G_h01_33EE);
    F_h00_34E0(&G_h01_3424);
    G_h01_348E = 2;
    G_h01_345A = 0xc8;
    G_h01_345C = 0xb2;
    for (i = 0; i < G_h01_6F3B; ++i) {
        F_h00_34E0(&G_h01_345A);
        --G_h01_348E;
        G_h01_345A += 0x20;
    }
    F_h00_09C0(0xa8, 0xae, G_h01_46E6, 1, 0x1a, 1);
    if (G_h01_46E1 < 10)
        F_h00_09C0(0x12, 0xb6, (long)G_h01_46E1, 0x1b, 1, 0);
    else
        F_h00_09C0(0xe, 0xb6, (long)G_h01_46E1, 0x1b, 1, 0);
}
