extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern int G_h01_50E6;
extern int G_h01_50F0;
extern int G_h01_51BE;
extern int G_h01_51F4;
extern int G_h01_522A;
extern int G_h01_5234;
extern int G_h01_5260;
extern int G_h01_526A;
extern int G_h01_5296;
extern int G_h01_52A0;
extern int G_h01_52CC;
extern int G_h01_52D6;
extern int G_h01_5302;
extern int G_h01_530C;
extern char G_h01_536E;
extern int G_h01_50B0;
extern int G_h01_50B8;
extern int G_h01_50C0;
extern char G_h01_50E4;
extern int G_h01_50EE;
extern char G_h01_50F6;
extern char G_h01_511A;
extern int G_h01_5232;
extern char G_h01_523A;
extern int G_h01_529E;
extern char G_h01_52A6;
extern int G_h01_5268;
extern char G_h01_5270;
extern int G_h01_52D4;
extern char G_h01_52DC;
extern int G_h01_530A;
extern char G_h01_5312;
extern int G_h01_1466;
extern int G_h01_511C;
extern int G_h01_50B2;
extern int G_h01_50B4;
extern int G_h01_50E8;
extern int G_h01_50EA;
extern int G_h01_50F2;
extern int G_h01_50F8;
extern int G_h01_50BA;
extern int G_h01_50BC;
extern int G_h01_50C2;
extern int G_h01_522C;
extern int G_h01_522E;
extern int G_h01_5236;
extern int G_h01_523C;
extern int G_h01_5298;
extern int G_h01_529A;
extern int G_h01_52A2;
extern int G_h01_52A8;
extern int G_h01_5262;
extern int G_h01_526C;
extern int G_h01_52D8;
extern int G_h01_530E;
extern int G_h01_5272;
extern int G_h01_52CE;
extern int G_h01_52DE;
extern int G_h01_5304;
extern int G_h01_5306;
extern int G_h01_5314;

extern int F_h00_0FDE();
extern int F_h00_86A8();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_34E0();
extern int F_h00_3AE4();
extern int F_h00_4376();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h04_07CA();
extern int F_h04_0B50();
extern int F_h04_0926();
extern int F_h04_0DBE();

recovered()
{
    int state;
    int index;
    char coordinates[10];
    coordinates[0] = -57;
    coordinates[1] = 29;
    coordinates[2] = -23;
    coordinates[3] = 25;
    coordinates[4] = 36;
    coordinates[5] = 30;
    coordinates[6] = 49;
    coordinates[7] = 29;
    coordinates[8] = 99;
    coordinates[9] = 29;

    F_h04_07CA();
    F_h00_0FDE(1);
    F_h00_291E(8, &G_h01_50E6);
    F_h00_4376();
    G_h01_50E6 = 0xd8;
    G_h01_50E8 = 0x20;
    G_h01_511A = 0;
    F_h00_34E0(&G_h01_50E6);
    F_h00_330E();
    F_h00_4376();
    F_h00_307C();

    G_h01_46D6 = (char *)&G_h01_1466;
    F_h00_31AA((char *)&G_h01_1466);
    F_h00_8A46(
        G_h01_46CE, 0L, 0L,
        G_h01_46D2, 0L, 0L,
        0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_34E0(&G_h01_50E6);
    F_h00_307C();

    F_h00_291E(9, &G_h01_50B0);
    F_h00_291E(11, &G_h01_522A);
    F_h00_291E(12, &G_h01_5296);
    F_h00_291E(13, &G_h01_5260);
    F_h00_291E(14, &G_h01_52CC);
    F_h00_291E(15, &G_h01_5302);
    F_h00_4376();
    G_h01_522A = 0x7f;
    G_h01_522C = 0x22;
    G_h01_5296 = 0x97;
    G_h01_5298 = 0x22;
    G_h01_5302 = 0xba;
    G_h01_5304 = 0x67;
    F_h00_57D2(0x6e);

    state = 2;
    index = 0;
    goto frame_test;
frame_body:
        if (state == 4)
            state = 0;
        G_h01_50B0 = coordinates[index * 2];
        G_h01_50B2 = coordinates[index * 2 + 1];
        G_h01_50E4 = state;
        F_h00_8A46(
            G_h01_46CE, 0L, 0x14L,
            G_h01_46D2, 0L, 0x14L,
            0x140L, 0x82L, 0xc0L, 0xffL, 0L);
        if (index == 0)
            G_h01_511A = 1;
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_50B0);
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
            F_h00_3AE4(&G_h01_50C0, G_h01_50B8, G_h01_50BA);
            F_h00_3AE4(&G_h01_523A, G_h01_5232, G_h01_5234);
            F_h00_3AE4(&G_h01_52A6, G_h01_529E, G_h01_52A0);
            F_h00_3AE4(&G_h01_5270, G_h01_5268, G_h01_526A);
            F_h00_3AE4(&G_h01_52DC, G_h01_52D4, G_h01_52D6);
            F_h00_3AE4(&G_h01_5312, G_h01_530A, G_h01_530C);
            F_h00_57D2(0);
            return;
        }
        F_h00_307C();
        F_h00_86A8(10L);
        ++state;
        ++index;
frame_test:
    if (index < 5)
        goto frame_body;

    F_h00_8A46(
        G_h01_46CE, 0L, 0x14L,
        G_h01_46D2, 0L, 0x14L,
        0x140L, 0x82L, 0xc0L, 0xffL, 0L);
    F_h00_34E0(&G_h01_522A);
    F_h00_34E0(&G_h01_5302);
    F_h00_34E0(&G_h01_5296);
    F_h00_34E0(&G_h01_50E6);
    F_h00_307C();
    F_h00_3AE4(&G_h01_50C0, G_h01_50B8, G_h01_50BA);
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h00_0FDE(1);
    F_h00_291E(10, &G_h01_51BE);
    F_h00_4376();
    F_h04_0B50(1, 5, 8);
    F_h04_0B50(6, 10, 8);
    F_h00_291E(16, &G_h01_51F4);
    F_h04_0926(1, 3, 5);
    F_h04_0926(4, 6, 4);
    F_h00_4376();
    if (G_h01_536E) {
        F_h04_0DBE();
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h04_0B50(11, 14, 6);
    F_h04_0B50(15, 19, 6);
    F_h04_0B50(20, 23, 5);
    F_h04_0B50(24, 26, 5);
    F_h00_4376();
    if (G_h01_536E) {
        F_h04_0DBE();
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h04_0926(7, 9, 5);
    F_h04_0926(10, 12, 5);
    F_h04_0926(1, 13, 13);
    F_h04_0926(13, 14, 1);
    F_h04_0926(13, 15, 1);
    F_h04_0DBE();
    F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
}
