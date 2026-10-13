extern char G_h01_2C2C;
extern long G_h01_2C26;
extern long G_h01_2A16;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_1526;
extern char G_h01_0668;
extern char G_h01_068B;
extern char G_h01_06A6;
extern char G_h01_06BF;
extern char G_h01_06DB;
extern int F_h00_330E();
extern int F_h00_8BC8();
extern int F_h00_307C();
extern int F_h00_0FDE();
extern long F_h00_291E();
extern int F_h00_57D2();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_35DC();
extern int F_h00_31AA();
extern int F_h00_134C();
extern int F_h00_8A46();
extern int F_h00_04FE();

F_h00_033E(arg)
int arg;
{
    G_h01_2C2C = 0;
    G_h01_2C26 = 0;
    F_h00_330E();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_0FDE(1);
    F_h00_291E(0x1f, G_h01_46CE);
    F_h00_57D2(0x21);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(0x19);
    F_h00_57D2(0);
    F_h00_330E();
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_35DC(0x18, 0xc, &G_h01_0668, 0, 0);
    switch (arg) {
    case 1:
        F_h00_35DC(0x18, 0x18, &G_h01_06A6, 0, 0);
        F_h00_04FE(1);
        break;
    case 2:
        F_h00_35DC(0x18, 0x18, &G_h01_068B, 0, 0);
        F_h00_04FE(0);
        break;
    case 4:
        F_h00_35DC(0x18, 0x18, &G_h01_06DB, 0, 0);
        F_h00_04FE(3);
        break;
    case 8:
        F_h00_35DC(0x18, 0x18, &G_h01_06BF, 0, 0);
        F_h00_04FE(2);
        break;
    }
    F_h00_307C();
    G_h01_46D6 = &G_h01_1526;
    F_h00_31AA(&G_h01_1526);
    G_h01_2C26 = 4;
    G_h01_2C2C = 15;
    F_h00_57D2(0x71);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    F_h00_134C(0x1e);
}
