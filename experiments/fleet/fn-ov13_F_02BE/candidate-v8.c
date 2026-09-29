/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
extern int G_h01_1422; /* 1x; w2 */
extern long G_h01_46CA; /* 13x; w4 */
extern long G_h01_46CE; /* 15x; w4 */
extern long G_h01_46D2; /* 16x; w4 */
extern char *G_h01_46D6; /* 3x; w4 */
extern long G_h01_46DA; /* 5x; w4 */
struct UiState;
extern struct UiState G_h01_50E6;
extern int G_h01_511C; /* 2x */
extern int G_h01_5152; /* 2x */
extern int G_h01_5188; /* 2x */
extern int G_h01_5338; /* 1x; w2 */
extern int G_h01_533A; /* 1x; w2 */
extern char G_h01_536C; /* 1x; w1 */
extern int F_h00_0FDE(); /* 10x */
extern int F_h00_2816(); /* 4x */
extern int F_h00_291E(); /* 5x; alt long () x2 */
extern int F_h00_307C(); /* 13x */
extern int F_h00_31AA(); /* 3x */
extern int F_h00_330E(); /* 4x */
extern int F_h00_34E0(); /* 20x; alt void () x2 */
extern int F_h00_35DC(); /* 9x */
extern int F_h00_3AE4(); /* 6x */
extern int F_h00_435E(); /* 4x */
extern int F_h00_4376(); /* 4x; alt char () x1 */
extern int F_h00_4D04(); /* 3x */
extern int F_h00_4EC6(); /* 5x */
extern int F_h00_57D2(); /* 19x */
extern int F_h00_86A8(); /* 8x */
extern int F_h00_8A46(); /* 16x */
extern int F_h00_8BC8(); /* 5x */
extern int F_h13_0000(); /* 1x */
/* G_h01_1466: no canonical view */
/* G_h01_2A16: no canonical view; w4 */
/* G_h01_5E5E: no canonical view; w1 */
/* G_h01_A6C6: inside G_h01_A6B0+22 (struct Record [36]); w2 */
/* G_h01_A6C8: inside G_h01_A6B0+24 (struct Record [36]); w2 */
/* G_h01_A6CE: inside G_h01_A6B0+30 (struct Record [36]); w2 */
/* G_h01_A6D0: inside G_h01_A6B0+32 (struct Record [36]); w2 */
/* G_h01_A6D6: inside G_h01_A6B0+38 (struct Record [36]) */
/* G_h01_A6FC: inside G_h01_A6B0+76 (struct Record [36]); w2 */
/* G_h01_A6FE: inside G_h01_A6B0+78 (struct Record [36]); w2 */
/* G_h01_A704: inside G_h01_A6B0+84 (struct Record [36]); w2 */
/* G_h01_A706: inside G_h01_A6B0+86 (struct Record [36]); w2 */
/* G_h01_A70C: inside G_h01_A6B0+92 (struct Record [36]) */
/* G_h01_A732: inside G_h01_A6B0+130 (struct Record [36]); w2 */
/* G_h01_A734: inside G_h01_A6B0+132 (struct Record [36]); w2 */
/* G_h01_A73A: inside G_h01_A6B0+138 (struct Record [36]); w2 */
/* G_h01_A73C: inside G_h01_A6B0+140 (struct Record [36]); w2 */
/* G_h01_A742: inside G_h01_A6B0+146 (struct Record [36]) */
/* F_h13_012E: no canonical view */
/* F_h13_0190: no canonical view */


extern long G_h01_2A16;
extern char G_h01_1466;
extern char G_h01_5E5E;
extern int G_h01_A6C6;
extern int G_h01_A6C8;
extern int G_h01_A6CE;
extern int G_h01_A6D0;
extern char G_h01_A6D6;
extern int G_h01_A6FC;
extern int G_h01_A6FE;
extern int G_h01_A704;
extern int G_h01_A706;
extern char G_h01_A70C;
extern int G_h01_A732;
extern int G_h01_A734;
extern int G_h01_A73A;
extern int G_h01_A73C;
extern char G_h01_A742;
extern char G_h13_06FC;
extern char G_h13_0706;
extern char G_h13_0710;
extern char G_h13_071F;
extern char G_h13_072E;
extern char G_h13_073A;
extern int F_h13_012E();
extern int F_h13_0190();

recovered()
{
    int choice, result, done, i;
    unsigned char input;

    done = 0;
    F_h00_57D2(0x21);
    while (G_h01_2A16 != 0)
        ;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_57D2(0);
    F_h13_0000(0, 0, 1);
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(1);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_330E();
    F_h00_57D2(6);
    F_h00_307C();
    G_h01_46D6 = &G_h01_1466;
    F_h00_31AA(&G_h01_1466);
    G_h01_5E5E = 0;
    result = 0x23;
    for (;;) {
        if (done)
            break;
        input = 0;
        choice = 0;
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
                    0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_511C);
        F_h00_34E0(&G_h01_5152);
        F_h00_34E0(&G_h01_5188);
        F_h00_34E0(&G_h01_5338);
        input = F_h00_4376();
        for (;;) {
        if ((input & 0x80) == 0) {
            switch (input & 0x3f) {
            case 1:
                F_h00_35DC(0x76, 0x0b, &G_h13_06FC, 0, 0);
                F_h00_35DC(0x78, 0x0a, &G_h13_0706, 1, 0);
                choice = 2;
                F_h00_307C();
                break;
            case 3:
                F_h00_35DC(0xc6, 0x21, &G_h13_0710, 0, 0);
                F_h00_35DC(0xc8, 0x20, &G_h13_071F, 1, 0);
                choice = 1;
                F_h00_307C();
                break;
            case 7:
                F_h00_35DC(0x0c, 0x21, &G_h13_072E, 0, 0);
                F_h00_35DC(0x0e, 0x20, &G_h13_073A, 1, 0);
                choice = 3;
                F_h00_307C();
                break;
            default:
                choice = 0;
                F_h00_307C();
                break;
            }
            F_h00_86A8(1L);
            continue;
        }

        switch (choice) {
        case 1:
            F_h00_0FDE(1);
            F_h00_291E(0x11, &G_h01_50E6);
            F_h00_291E(0x12, &G_h01_511C);
            F_h00_57D2(0);
            F_h13_0000(0, 0, 0);
            G_h01_A6C6 = 0x108;
            G_h01_A6C8 = 0;
            F_h00_34E0(&G_h01_A6C6);
            G_h01_A6FC = 0xd0;
            G_h01_A6FE = 0;
            F_h00_34E0(&G_h01_A6FC);
            F_h00_34E0(&G_h01_50E6);
            F_h00_307C();
            F_h00_3AE4(&G_h01_A70C, G_h01_A704, G_h01_A706);
            F_h00_3AE4(&G_h01_A6D6, G_h01_A6CE, G_h01_A6D0);
            F_h13_012E();
            F_h00_57D2(5);
            result = 0x28;
            done = 1;
            break;
        case 2:
            F_h00_57D2(0);
            F_h13_0190();
            F_h13_012E();
            result = 0x26;
            done = 1;
            break;
        case 3:
            F_h00_0FDE(1);
            F_h00_291E(0x13, &G_h01_A732);
            F_h00_57D2(0);
            F_h13_0000(0, 0, 0);
            G_h01_5338 = 0x21;
            G_h01_533A = 0x30;
            G_h01_536C = 0;
            G_h01_A732 = 9;
            G_h01_A734 = 0x10;
            F_h00_34E0(&G_h01_A732);
            F_h00_34E0(&G_h01_5338);
            F_h00_307C();
            G_h01_A6C6 = 1;
            i = 0;
            do {
                F_h00_34E0(&G_h01_A732);
                G_h01_536C = i;
                F_h00_34E0(&G_h01_5338);
                F_h00_307C();
                F_h00_86A8(10L);
                ++i;
            } while (i <= 3);
            F_h13_0000(0, 0, 0);
            F_h00_34E0(&G_h01_A732);
            G_h01_536C = 3;
            F_h00_34E0(&G_h01_5338);
            F_h00_307C();
            F_h00_86A8(10L);
            F_h00_307C();
            G_h01_A6C6 = 0;
            F_h00_3AE4(&G_h01_A742, G_h01_A73A, G_h01_A73C);
            F_h13_012E();
            result = 0x27;
            done = 1;
            break;
        }        break;
        }
    }

    F_h00_435E();
    G_h01_5E5E = 1;
    return result;
}