/* resident_F_0A44: "Do you wish to quit the game?" Y/N box; on Y releases the screen and calls the ov04 exit path. l1 is stored but never read, as in the original. */
extern int F_h00_3A6E();
extern int F_h00_307C();
extern int F_h00_8A46();
extern int F_h00_35DC();
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_4376();
extern int F_h00_330E();
extern int F_h00_3AE4();
extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_435E();
extern int F_h04_1D32();
extern int F_h04_27FE();
extern long G_h01_2C26;
extern char G_h01_2C2C;
extern unsigned int G_h01_A7A4;
extern unsigned int G_h01_A7A6;
extern char G_h01_A7A9;
extern char G_h01_A7CC;
extern long G_h01_A7AC;
extern long G_h01_46CA;
extern long G_h01_46D2;
extern long G_h01_46DA;
extern long G_h01_4700;
extern char *G_h01_5370;

recovered()
{
    char key;
    int quit;
    long l1;

    quit = 0;
    l1 = 0;
    G_h01_A7CC = 1;
    G_h01_A7A4 = 32;
    G_h01_A7A6 = 32;
    G_h01_A7A9 = 5;
    G_h01_2C2C = 0;
    G_h01_2C26 = 0;
    G_h01_A7AC = 0;
    F_h00_3A6E(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    F_h00_307C();
    F_h00_8A46(G_h01_46D2, 32L, 80L, &G_h01_A7A4, 0L, 0L, 248L, 32L, 192L, 255L, 0L);
    F_h00_35DC(40, 88, "Do you wish to quit the game?", 15, 1);
    F_h00_35DC(40, 96, "     Type 'Y' or 'N'.        ", 15, 1);
    *G_h01_5370 = 15;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 39L, 87L);
    F_h00_8AA8(G_h01_46CA, 272L, 87L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 39L, 104L);
    F_h00_8AA8(G_h01_46CA, 272L, 104L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 39L, 87L);
    F_h00_8AA8(G_h01_46CA, 39L, 104L);
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 272L, 87L);
    F_h00_8AA8(G_h01_46CA, 272L, 104L);
    F_h00_307C();
    key = F_h00_4376();
    for (;;) {
        if (key == 'y' || key == 'Y') {
            quit = 1;
            break;
        }
        if (key == 'n' || key == 'N') {
            break;
        }
        key = F_h00_4376();
    }
    if (quit) {
        F_h00_330E();
        F_h00_3AE4(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
        F_h00_0FDE(1);
        G_h01_46DA = G_h01_4700;
        F_h00_2816(G_h01_46DA);
        F_h04_1D32();
        F_h04_27FE("");
    } else {
        F_h00_8A46(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 32L, 80L, 248L, 32L, 192L, 255L, 0L);
        F_h00_307C();
        F_h00_8A46(&G_h01_A7A4, 0L, 0L, G_h01_46D2, 32L, 80L, 248L, 32L, 192L, 255L, 0L);
        F_h00_307C();
        F_h00_3AE4(&G_h01_A7AC, G_h01_A7A4, G_h01_A7A6);
    }
    G_h01_A7CC = 0;
    F_h00_435E();
}
