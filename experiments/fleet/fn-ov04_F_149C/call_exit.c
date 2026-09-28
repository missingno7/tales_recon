extern char G_h01_1766[1];
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_46E0;

extern int F_h00_0640();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h00_4676();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h00_8BC8();
extern int F_h00_86A8();

recovered()
{
    int unused;
    unsigned char buttons;

    unused = 0;
    buttons = 0;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    G_h01_46E0 = 0;
    F_h00_0640(9);
    F_h00_35DC(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
    F_h00_35DC(176, 80, "Easy Money", 24, 0);
    F_h00_35DC(176, 100, "Standard Wages", 1, 0);
    F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    F_h00_435E();
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 176L, 200L, 192L, 255L, 0L);

    while (!(buttons & 0x80)) {
        F_h00_35DC(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
        buttons &= 0x3f;
        if (buttons & 0x40)
            return 0x25;
        if (buttons == 1) {
            if (G_h01_46E0 == 0)
                G_h01_46E0 = 2;
            else
                --G_h01_46E0;
            F_h00_57D2(36);
        } else if (buttons == 5) {
            if (G_h01_46E0 == 2)
                G_h01_46E0 = 0;
            else
                ++G_h01_46E0;
            F_h00_57D2(36);
        }

        switch (G_h01_46E0) {
        case 0:
            F_h00_35DC(168, 80, ">Easy Money", 24, 0);
            F_h00_35DC(176, 100, "Standard Wages", 1, 0);
            F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
            break;
        case 2:
            F_h00_35DC(176, 80, "Easy Money", 1, 0);
            F_h00_35DC(176, 100, "Standard Wages", 1, 0);
            F_h00_35DC(168, 120, ">Hard Earned Cash", 24, 0);
            break;
        default:
            F_h00_35DC(176, 80, "Easy Money", 1, 0);
            F_h00_35DC(168, 100, ">Standard Wages", 24, 0);
            F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
            break;
        }
        F_h00_307C();
        F_h00_86A8((long)5);
        buttons = F_h00_4376();
    }

    F_h00_57D2(36);
    F_h00_4676();
    F_h00_8BC8(G_h01_46CA, 0L);
    return F_h00_4676();
}
