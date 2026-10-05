extern char G_h01_536E;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46D6;
extern long G_h01_46DA;
extern char G_h01_1426;
extern long G_h01_2A16;
extern char G_h01_4704;

extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_30F0();
extern int F_h00_31AA();
extern int F_h00_3178();
extern int F_h00_330E();
extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h00_8BC8();
extern int F_h04_1822();
extern int F_h04_0E44();

recovered()
{
    unsigned char key;

    F_h00_330E();
    G_h01_536E = 0;
    G_h01_4704 = 1;
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_0FDE(1);
    F_h00_291E(2, G_h01_46CE);
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_0FDE(1);
    F_h00_4D04(0);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_57D2(1);
    F_h00_307C();
    G_h01_46D6 = (long)&G_h01_1426;
    F_h00_31AA(&G_h01_1426);
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_3178(&G_h01_1426);
    F_h00_30F0();
    F_h04_1822();
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_435E();
    while (G_h01_2A16) {
        key = F_h00_4376();
        if (key & 0x80) {
            F_h00_57D2(0);
            F_h00_57D2(0x24);
            F_h00_330E();
            key = 0;
            G_h01_536E = 0;
            break;
        }
    }

    F_h00_4EC6();
    F_h00_435E();
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h04_0E44();
    G_h01_4704 = 0;
    if (G_h01_536E)
        F_h00_57D2(0x24);
    F_h00_330E();
}

