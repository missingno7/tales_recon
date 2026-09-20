extern char G_h01_06FE[624];

extern int F_h00_435E();
extern int F_h00_134C();
extern int F_h00_57D2();
extern int F_h00_35DC();
extern int F_h00_307C();

F_h04_18A6()
{
    int i;
    int scratch;

    F_h00_435E();
    if (F_h00_134C(20)) {
        return F_h00_57D2(36);
    }
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    i = 0;
    do {
        F_h00_35DC(64, 192, G_h01_06FE + (long)i * 26, 1, 3);
        F_h00_307C();
        if (F_h00_134C(20)) {
            return F_h00_57D2(36);
        }
        ++i;
    } while (i < 24);
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
}
/* Direct reconstruction candidate for ov04_F_1A3A. */
extern long G_h01_46CA;
extern int F_h00_8BC8();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int F_h00_57D2();
extern int F_h00_435E();
extern int F_h00_134C();
extern int F_h00_307C();

F_h04_1A3A(choice)
int choice;
{
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(30);
    if (choice) F_h00_0640(13);
    else F_h00_0640(14);
    F_h00_57D2(119);
    F_h00_435E();
    F_h00_134C(100);
    F_h00_4EC6();
    F_h00_307C();
}

extern long F_h00_463E();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int F_h00_57D2();
extern int F_h00_2816();
extern int F_h00_134C();
extern long G_h01_46DA;

F_h04_1AA2(a)
int a;
{
    int value;

    if (a) {
        value=(unsigned)F_h00_463E()%3;
        F_h00_4EC6();
        F_h00_0FDE(2);
        switch (value) {
        case 0:
            F_h00_4D04(9);
            break;
        case 2:
            F_h00_4D04(17);
            break;
        case 3:
            F_h00_4D04(18);
            break;
        }
        F_h00_0640(12);
        F_h00_57D2(119);
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
    } else {
        value=(F_h00_463E()&1) ? 15 : 16;
        F_h00_4EC6();
        F_h00_0FDE(2);
        F_h00_4D04(value);
        F_h00_0640(11);
        F_h00_57D2(119);
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
    }
    F_h00_134C(100);
}

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

F_h04_1B94()
{
    int selection;
    unsigned char buttons;

    selection = 0;
    buttons = 0;
    F_h00_330E();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(0);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_57D2(1);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    F_h00_435E();
    buttons = F_h00_4376();
    while (!(buttons & 128)) {
        if ((buttons & 1) || (buttons & 5))
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
        if ((buttons & 1) || (buttons & 5)) {
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

extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_1826[1];
extern char G_h01_14A6[1];

extern int F_h00_57D2();
extern int F_h00_291E();
extern int F_h00_330E();
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_31AA();

extern int F_h00_134C();
extern int F_h00_4EC6();

recovered()
{
    F_h00_57D2(0);
    F_h00_291E(1, G_h01_46CE);
    F_h00_330E();
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_307C();
    G_h01_46D6 = G_h01_1826;
    F_h00_31AA(G_h01_1826);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h04_18A6();
    F_h00_291E(0, G_h01_46CE);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_330E();
    F_h00_307C();
    G_h01_46D6 = G_h01_14A6;
    F_h00_31AA(G_h01_14A6);
    if (F_h00_134C(40))
        F_h00_57D2(36);
    F_h00_57D2(0);
    F_h00_4EC6();
}

