/* resident_F_0D36: GAME PAUSED box; waits for p/P, then restores the screen. l1 is stored but never read, as in the original (clr.l -6(a5)). */
extern long G_h01_46CA;
extern long G_h01_46D2;
extern char *G_h01_5370;
extern unsigned int G_h01_A7A4;
extern unsigned int G_h01_A7A6;
extern char G_h01_A7A9;
extern long G_h01_A7AC;
extern char G_h01_A7CD;
extern int F_h00_3A6E();
extern int F_h00_3AE4();
extern int F_h00_307C();
extern int F_h00_8A46();
extern int F_h00_35DC();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_86A8();
extern int F_h00_435E();
extern int F_h00_4376();

recovered()
{
    char c;
    long l1;

    l1 = 0L;
    G_h01_A7CD = 1;
    G_h01_A7A4 = 14;
    G_h01_A7A6 = 24;
    G_h01_A7A9 = 5;
    G_h01_A7AC = 0L;
    F_h00_3A6E(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    F_h00_307C();
    F_h00_8A46(G_h01_46D2, 104L, 80L, &G_h01_A7A4, 0L, 0L, 104L, 24L, 192L, 255L, 0L);
    F_h00_35DC(104, 80, "             ", 15, 1);
    F_h00_35DC(104, 88, " GAME PAUSED ", 15, 1);
    F_h00_35DC(104, 96, "             ", 15, 1);
    *G_h01_5370 = 15;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 104L, 80L);
    F_h00_8AA8(G_h01_46CA, 207L, 80L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 104L, 80L);
    F_h00_8AA8(G_h01_46CA, 104L, 103L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 104L, 103L);
    F_h00_8AA8(G_h01_46CA, 207L, 103L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 207L, 80L);
    F_h00_8AA8(G_h01_46CA, 207L, 103L);
    F_h00_307C();
    F_h00_86A8(25L);
    F_h00_435E();
    c = F_h00_4376();
    for (;;) {
        if (c == 'p' || c == 'P') {
            break;
        }
        c = F_h00_4376();
    }
    F_h00_8A46(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 104L, 80L, 104L, 24L, 192L, 255L, 0L);
    F_h00_307C();
    F_h00_8A46(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 104L, 80L, 104L, 24L, 192L, 255L, 0L);
    F_h00_307C();
    F_h00_3AE4(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    G_h01_A7CD = 0;
    F_h00_86A8(5L);
    F_h00_435E();
}
