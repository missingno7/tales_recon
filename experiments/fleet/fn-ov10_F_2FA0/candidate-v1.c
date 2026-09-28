extern long G_h01_46CE;
extern long G_h01_46D2;
extern unsigned short G_h01_7194;
extern unsigned short G_h01_7196;
extern unsigned short G_h01_719C;
extern unsigned short G_h01_719E;
extern unsigned short G_h01_71A4;
extern unsigned short G_h01_71CA;
extern unsigned short G_h01_71CC;
extern unsigned short G_h01_71D2;
extern unsigned short G_h01_71D4;
extern unsigned short G_h01_71DA;
extern unsigned short G_h01_7200;
extern unsigned short G_h01_7202;
extern unsigned short G_h01_7208;
extern unsigned short G_h01_720A;
extern unsigned short G_h01_7210;
extern unsigned short G_h01_7488;
extern unsigned short G_h01_748A;
extern unsigned short G_h01_7490;
extern unsigned short G_h01_7492;
extern unsigned short G_h01_7498;
extern unsigned short G_h01_74BE;
extern unsigned short G_h01_74C0;
extern unsigned short G_h01_74C6;
extern unsigned short G_h01_74C8;
extern unsigned short G_h01_74CE;
extern unsigned short G_h01_799C;
extern unsigned short G_h01_799E;
extern int F_h00_8A46();
extern int F_h10_320C();
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_34E0();
extern int F_h00_3AE4();
extern int F_h00_57D2();
extern int F_h10_1F90();

void recovered(p, flag)
char *p;
char flag;
{
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h10_320C(p);
    F_h00_0FDE(2);

    if ((*((unsigned short *)p) & 0x40) == 0x40) {
        F_h00_291E(2, &G_h01_74BE);
        G_h01_74BE = 0x1a;
        G_h01_74C0 = 0x5c;
        F_h00_34E0(&G_h01_74BE);
        F_h00_3AE4(&G_h01_74CE, G_h01_74C6, G_h01_74C8);
    }

    if (G_h01_799C < 2) {
        F_h00_291E(9, &G_h01_7200);
        G_h01_7200 = 0x68;
        G_h01_7202 = 0x8;
        F_h00_34E0(&G_h01_7200);
        F_h00_3AE4(&G_h01_7210, G_h01_720A, G_h01_7208);
    } else if (G_h01_799C < 4) {
        F_h00_291E(8, &G_h01_71CA);
        G_h01_71CA = 0x68;
        G_h01_71CC = 0x8;
        F_h00_34E0(&G_h01_71CA);
        F_h00_3AE4(&G_h01_71DA, G_h01_71D4, G_h01_71D2);
    } else if (G_h01_799C < 6) {
        F_h00_291E(7, &G_h01_7194);
        G_h01_7194 = 0x68;
        G_h01_7196 = 0x41;
        F_h00_34E0(&G_h01_7194);
        F_h00_3AE4(&G_h01_71A4, G_h01_719E, G_h01_719C);
    }

    if (((*((unsigned short *)(p - 2)) & 0x40) == 0x40 &&
         ((G_h01_799E & 7) != 0) && ((p[1] & 1) != 0)) ||
        ((*((unsigned short *)(p + 2)) & 0x40) == 0x40 &&
         ((G_h01_799E & 7) != 7) && (p[1] & 2)) ||
        ((*((unsigned short *)(p - 0x10)) & 0x40) == 0x40 &&
         (G_h01_799E > 7) && (p[1] & 8)) ||
        ((*((unsigned short *)(p + 0x10)) & 0x40) == 0x40 &&
         (G_h01_799E < 0x38) && (p[1] & 4))) {
        F_h00_291E(1, &G_h01_7488);
        G_h01_7488 = 0x57;
        G_h01_748A = 0xe;
        F_h00_34E0(&G_h01_7488);
        if (flag == 0)
            F_h00_57D2(0x4d);
        F_h00_3AE4(&G_h01_7498, G_h01_7492, G_h01_7490);
    } else if (flag != 0) {
        F_h10_1F90(G_h01_799C);
    }
    F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
}




