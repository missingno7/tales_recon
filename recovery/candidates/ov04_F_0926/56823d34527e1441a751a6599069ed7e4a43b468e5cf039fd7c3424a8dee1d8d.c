/* Direct recovery candidate for ov04_F_0926. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int G_h01_0320;
extern int G_h01_0322;
extern long G_h01_0324;
extern int G_h01_50E6;
extern int G_h01_522A;
extern int G_h01_5296;
extern int G_h01_5302;
extern int G_h01_51F4;
extern int G_h01_51F6;
extern char G_h01_511A;
extern char G_h01_536E;
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_307C();
extern int F_h00_4376();
extern int F_h00_57D2();
extern int F_h00_86A8();
extern unsigned int F_h00_463E();

recovered(first,last,rounds)
int first,last,rounds;
{
    int i;
    int round;

    G_h01_51F4 = 128;
    G_h01_51F6 = 0;
    for (round = 0; round < rounds; ++round) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        G_h01_511A = 3;
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_522A);
        F_h00_34E0(&G_h01_5296);
        F_h00_34E0(&G_h01_5302);
        F_h00_34E0(&G_h01_51F4);
        for (i = first - 1; i < last; ++i)
            F_h00_35DC(*((int *)((char *)&G_h01_0320 + ((long)i << 3))),
                *((int *)((char *)&G_h01_0322 + ((long)i << 3))),
                *((long *)((char *)&G_h01_0324 + ((long)i << 3))), 0, 1);
        F_h00_307C();
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_57D2(0);
            return;
        }
        F_h00_86A8(5L);
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_57D2(0);
            return;
        }
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        G_h01_511A = 2;
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_522A);
        F_h00_34E0(&G_h01_5296);
        F_h00_34E0(&G_h01_5302);
        F_h00_34E0(&G_h01_51F4);
        for (i = first - 1; i < last; ++i)
            F_h00_35DC(*((int *)((char *)&G_h01_0320 + ((long)i << 3))),
                *((int *)((char *)&G_h01_0322 + ((long)i << 3))),
                *((long *)((char *)&G_h01_0324 + ((long)i << 3))), 0, 1);
        F_h00_307C();
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_57D2(0);
            return;
        }
        F_h00_86A8((long)(unsigned)(((F_h00_463E() & 2) + 1) * 5));
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_57D2(0);
            return;
        }
    }
    F_h00_86A8(15L);
}
