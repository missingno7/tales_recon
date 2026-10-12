extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern short G_h01_752A;
extern short G_h01_752C;
extern short G_h01_7532;
extern short G_h01_7534;
extern short G_h01_753A;
extern char G_h01_755E;
extern short G_h01_730E;
extern char G_h01_730C;
extern short G_h01_72D8;
extern char G_h01_74F4[1];
extern char G_h01_7452[1];
extern char G_h01_741C[1];

extern void F_h10_2634();
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_34E0();
extern int F_h00_0FDE();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_291E();
extern int F_h00_86A8();
extern int F_h00_57D2();
extern int F_h00_8BC8();
extern int F_h00_330E();
extern int F_h00_3AE4();

void recovered()
{
    int i;

    for (i = 0; i < 4; i++) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h10_2634(&G_h01_730E, 17, 0);
        F_h00_307C();
    }
    for (i = 0; i < 6; i++) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_730E);
        if ((i & 1) && i < 4)
            G_h01_730C = 3;
        else if (i < 4)
            G_h01_730C = 4;
        else
            G_h01_730C = 4;
        F_h00_34E0(&G_h01_72D8);
        F_h00_34E0(G_h01_74F4);
        F_h00_34E0(G_h01_7452);
        F_h00_34E0(G_h01_741C);
        F_h00_307C();
    }
    F_h00_0FDE(2);
    F_h00_4EC6();
    F_h00_4D04(7);
    F_h00_291E(0x1b, &G_h01_752A);
    G_h01_752A = 0x62;
    G_h01_752C = 0x37;
    G_h01_755E = 4;
    F_h00_34E0(&G_h01_752A);
    F_h00_307C();
    F_h00_86A8(0x32L);
    G_h01_755E = 1;
    F_h00_34E0(&G_h01_752A);
    F_h00_307C();
    F_h00_86A8(5L);
    for (i = 0; i < 6; i++) {
        if (i == 4) {
            F_h00_57D2(0x4b);
        } else {
            F_h00_8BC8(G_h01_46CA, 0L);
            G_h01_755E = i;
            F_h00_34E0(&G_h01_752A);
            F_h00_307C();
            if (i == 1) {
                F_h00_86A8(5L);
            } else {
                if (i & 1)
                    F_h00_86A8(0x32L);
                else
                    F_h00_86A8(0x19L);
                if (i > 1 && i < 6) {
                    G_h01_755E = 1;
                    F_h00_34E0(&G_h01_752A);
                    F_h00_307C();
                    F_h00_86A8(3L);
                }
            }
        }
    }
    G_h01_755E = 0;
    F_h00_34E0(&G_h01_752A);
    F_h00_307C();
    F_h00_86A8(0x96L);
    F_h00_330E();
    F_h00_4EC6();
    F_h00_3AE4(&G_h01_753A, G_h01_7532, G_h01_7534);
}
