extern long G_h01_46CA;
extern long G_h01_46DA;
extern char G_h01_1766[1];
extern char *G_h01_46D6;
extern int F_h00_330E();
extern int F_h00_8BC8();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_2816();
extern int F_h00_57D2();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_435E();
extern char F_h00_4376();
extern int F_h00_35DC();
extern int F_h00_86A8();

recovered()
{
    int selection;
    char buttons;

    selection = 0;
    F_h00_330E();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(0);
    F_h00_0FDE(1);
    F_h00_2816();
    F_h00_57D2(1);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    F_h00_435E();
    buttons = F_h00_4376();
    while (!(buttons & 128)) {
        if ((buttons & 1) || !(buttons & 5))
            selection ^= 1;
        F_h00_8BC8(G_h01_46CA, 0L);
        F_h00_35DC(112, 70, "PLAY AGAIN?", 1, 0);
        if (!selection) {
            F_h00_35DC(136, 100, ">YES", 24, 0);
            F_h00_35DC(144, 120, "NO", 1, 0);
        } else {
            F_h00_35DC(144, 100, "YES", 1, 0);
            F_h00_35DC(136, 120, ">NO", 24, 0);
        }
        F_h00_307C();
        if ((buttons & 1) || !(buttons & 5)) {
            F_h00_435E();
            F_h00_86A8((long)10);
        }
        buttons = F_h00_4376();
    }
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_57D2(0);
    F_h00_4EC6();
    return selection;
}
