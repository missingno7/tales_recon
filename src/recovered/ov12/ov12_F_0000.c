/* Candidate v2 for ov12_F_0000: v1 with the poll loop as a for loop (test at bottom after entry branch). */
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern char G_h01_18E6[1];
extern int G_h01_46FE;
extern char G_h01_396C;
extern char G_h01_38CA;
extern char G_h01_39A2;
extern char G_h01_3A0E;
extern char G_h01_3A7A;
extern char G_h01_3AB0;
extern int G_h01_3896;
extern int G_h01_3898;
extern int G_h01_389E;
extern int G_h01_38A0;
extern int G_h01_38A6;
extern int G_h01_38CC;
extern int G_h01_38CE;
extern int G_h01_38D4;
extern int G_h01_38D6;
extern int G_h01_38DC;
extern int G_h01_3902;
extern int G_h01_3904;
extern int G_h01_390A;
extern int G_h01_390C;
extern int G_h01_3912;
extern int G_h01_3938;
extern int G_h01_393A;
extern int G_h01_3940;
extern int G_h01_3942;
extern int G_h01_3948;
extern int G_h01_396E;
extern int G_h01_3970;
extern int G_h01_3976;
extern int G_h01_3978;
extern int G_h01_397E;
extern int G_h01_39A4;
extern int G_h01_39A6;
extern int G_h01_39AC;
extern int G_h01_39AE;
extern int G_h01_39B4;
extern int G_h01_39DA;
extern int G_h01_39DC;
extern int G_h01_39E2;
extern int G_h01_39E4;
extern int G_h01_39EA;
extern int G_h01_3A10;
extern int G_h01_3A12;
extern int G_h01_3A18;
extern int G_h01_3A1A;
extern int G_h01_3A20;
extern int G_h01_3A46;
extern int G_h01_3A48;
extern int G_h01_3A4E;
extern int G_h01_3A50;
extern int G_h01_3A56;
extern int G_h01_3A7C;
extern int G_h01_3A7E;
extern int G_h01_3A84;
extern int G_h01_3A86;
extern int G_h01_3A8C;
extern int F_h00_435E();
extern int F_h00_8BC8();
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern int F_h00_291E();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h00_330E();
extern int F_h00_57D2();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_86A8();
extern int F_h00_3AE4();
extern int F_h00_868C();
extern int F_h00_4376();

recovered()
{
    int i;
    int j;
    char flag;
    long saved;
    int ret;

    flag = 0;
    F_h00_435E();
    F_h00_8BC8(G_h01_46CA, 0L);
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:mbin.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    F_h00_291E(0, G_h01_46CE);
    F_h00_291E(1, &G_h01_3896);
    G_h01_3896 = 0xb2;
    G_h01_3898 = 0x35;
    F_h00_291E(2, &G_h01_38CC);
    F_h00_291E(3, &G_h01_3902);
    F_h00_291E(4, &G_h01_3938);
    G_h01_3938 = 0xba;
    G_h01_393A = 0x5e;
    G_h01_396C = 0;
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(12);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3896);
    F_h00_34E0(&G_h01_3938);
    F_h00_330E();
    F_h00_57D2(38);
    F_h00_307C();
    G_h01_46D6 = G_h01_18E6;
    F_h00_31AA(&G_h01_18E6);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);

    for (i = 0, j = 0; i < 6; i++, j++) {
        if (j > 1)
            j = 0;
        if (j == 0) {
            G_h01_3896 = 0xb2;
            G_h01_3898 = 0x35;
        } else if (j == 1) {
            G_h01_3896 = 0xb3;
            G_h01_3898 = 0x35;
        }
        G_h01_38CA = j;
        F_h00_8A46(G_h01_46CE, 160L, 0L, G_h01_46D2, 160L, 0L, 160L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_3896);
        F_h00_34E0(&G_h01_3938);
        F_h00_307C();
        F_h00_86A8(20L);
    }

    for (j = 2; !(F_h00_4376() & 0x80); j++) {
        if (j > 3)
            j = 2;
        if (j == 2) {
            G_h01_3896 = 0xb2;
            G_h01_3898 = 0x35;
            G_h01_396C = 0;
        } else if (j == 3) {
            G_h01_3896 = 0xb4;
            G_h01_3898 = 0x3c;
            G_h01_396C = 1;
        }
        G_h01_38CA = j;
        F_h00_8A46(G_h01_46CE, 160L, 0L, G_h01_46D2, 160L, 0L, 160L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_3896);
        F_h00_34E0(&G_h01_3938);
        F_h00_307C();
        F_h00_86A8(10L);
    }
    if (j == 3 && G_h01_46FE == 0) {
        flag = 1;
        G_h01_46FE = 1;
    }

    F_h00_57D2(37);
    G_h01_38CA = 4;
    G_h01_3896 = 0xb0;
    G_h01_3898 = 0x49;
    F_h00_8A46(G_h01_46CE, 160L, 0L, G_h01_46D2, 160L, 0L, 160L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3896);
    G_h01_396C = 2;
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_86A8(5L);
    G_h01_38CA = 5;
    G_h01_3896 = 0xa2;
    G_h01_3898 = 0x21;
    F_h00_8A46(G_h01_46CE, 160L, 0L, G_h01_46D2, 160L, 0L, 160L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3896);
    G_h01_396C = 3;
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_86A8(5L);
    G_h01_38CA = 5;
    G_h01_3896 = 0x9a;
    G_h01_3898 = 8;
    F_h00_8A46(G_h01_46CE, 160L, 0L, G_h01_46D2, 160L, 0L, 160L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3896);
    G_h01_396C = 0;
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_86A8(5L);

    for (i = 0; i < 5; i++) {
        if (i == 0) {
            G_h01_38CA = 6;
            G_h01_3896 = 0x83;
            G_h01_3898 = 1;
        } else if (i == 1) {
            G_h01_3896 = 0x70;
            G_h01_3898 = 1;
        } else if (i == 2) {
            G_h01_38CA = 7;
            G_h01_3896 = 0x6a;
            G_h01_3898 = 0x13;
        } else if (i == 3) {
            G_h01_3896 = 0x69;
            G_h01_3898 = 0x27;
        } else {
            G_h01_3896 = 0x69;
            G_h01_3898 = 0x41;
        }
        F_h00_8A46(G_h01_46CE, 104L, 0L, G_h01_46D2, 104L, 0L, 160L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_3896);
        F_h00_34E0(&G_h01_3938);
        F_h00_307C();
        F_h00_86A8(5L);
    }

    G_h01_38CA = 8;
    G_h01_3896 = 0x63;
    G_h01_3898 = 0x5c;
    F_h00_8A46(G_h01_46CE, 88L, 0L, G_h01_46D2, 88L, 0L, 80L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3896);
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_86A8(5L);
    G_h01_38CA = 9;
    G_h01_3896 = 0x71;
    G_h01_3898 = 0x59;
    F_h00_8A46(G_h01_46CE, 88L, 0L, G_h01_46D2, 88L, 0L, 80L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3896);
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_86A8(5L);
    G_h01_38CC = 0x6d;
    G_h01_38CE = 0x77;
    F_h00_8A46(G_h01_46CE, 88L, 0L, G_h01_46D2, 88L, 0L, 80L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_38CC);
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_86A8(5L);
    F_h00_57D2(7);

    for (i = 0; i < 6; i++) {
        if (i == 0) {
            G_h01_3902 = 0x6d;
            G_h01_3904 = 0x6e;
        } else if (i == 1) {
            G_h01_3902 = 0x68;
            G_h01_3904 = 0x72;
        } else if (i == 2) {
            G_h01_3902 = 0x65;
            G_h01_3904 = 0x77;
        } else if (i == 3) {
            G_h01_3902 = 0x60;
            G_h01_3904 = 0x78;
        } else if (i == 4) {
            G_h01_3902 = 0x5c;
            G_h01_3904 = 0x7c;
        } else {
            G_h01_3902 = 0x5e;
            G_h01_3904 = 0x85;
        }
        F_h00_8A46(G_h01_46CE, 88L, 0L, G_h01_46D2, 88L, 0L, 80L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_3902);
        F_h00_34E0(&G_h01_3938);
        F_h00_307C();
        F_h00_86A8(5L);
    }

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3938);
    F_h00_307C();
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_34E0(&G_h01_3938);
    F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_3AE4(&G_h01_38A6, G_h01_389E, G_h01_38A0);
    F_h00_3AE4(&G_h01_38DC, G_h01_38D4, G_h01_38D6);
    F_h00_3AE4(&G_h01_3948, G_h01_3940, G_h01_3942);
    F_h00_3AE4(&G_h01_3912, G_h01_390A, G_h01_390C);
    F_h00_0FDE(1);
    F_h00_291E(5, &G_h01_396E);
    F_h00_291E(6, &G_h01_39A4);
    F_h00_57D2(2);

    for (i = 0; i < 6; i++) {
        G_h01_39A2 = i;
        if (i == 0) {
            G_h01_396E = 0x27;
            G_h01_3970 = 0x68;
        } else if (i == 1) {
            G_h01_396E = 0x28;
            G_h01_3970 = 0x72;
        } else if (i == 2) {
            G_h01_396E = 0x2c;
            G_h01_3970 = 0x76;
        } else if (i == 3) {
            G_h01_396E = 0x30;
            G_h01_3970 = 0x62;
        } else if (i == 4) {
            G_h01_396E = 0x40;
            G_h01_3970 = 0x5b;
        } else {
            G_h01_396E = 0x44;
            G_h01_3970 = 0x5e;
        }
        F_h00_8A46(G_h01_46CE, 32L, 0L, G_h01_46D2, 32L, 0L, 160L, 200L, 192L, 255L, 0L);
        F_h00_34E0(&G_h01_396E);
        F_h00_307C();
        F_h00_86A8(5L);
    }

    F_h00_8A46(G_h01_46CE, 32L, 0L, G_h01_46D2, 32L, 0L, 160L, 200L, 192L, 255L, 0L);
    G_h01_39A4 = 0x4b;
    G_h01_39A6 = 0x60;
    F_h00_34E0(&G_h01_39A4);
    F_h00_307C();
    F_h00_86A8(5L);
    F_h00_3AE4(&G_h01_397E, G_h01_3976, G_h01_3978);

    if (flag) {
        F_h00_3AE4(&G_h01_39B4, G_h01_39AC, G_h01_39AE);
        F_h00_0FDE(1);
        F_h00_291E(7, &G_h01_39DA);
        G_h01_39DA = 0x4b;
        G_h01_39DC = 0x62;
        for (i = 0, j = 0; i < 14; i++, j++) {
            if (j > 1)
                j = 0;
            G_h01_3A0E = j;
            F_h00_8A46(G_h01_46CE, 32L, 0L, G_h01_46D2, 32L, 0L, 160L, 200L, 192L, 255L, 0L);
            F_h00_34E0(&G_h01_39DA);
            F_h00_307C();
            F_h00_86A8(5L);
        }
        F_h00_3AE4(&G_h01_39EA, G_h01_39E2, G_h01_39E4);
        ret = 1;
        F_h00_57D2(32);
    } else {
        F_h00_0FDE(1);
        F_h00_291E(8, &G_h01_3A10);
        F_h00_291E(9, &G_h01_3A46);
        F_h00_291E(10, &G_h01_3A7C);
        G_h01_3A10 = 0x51;
        G_h01_3A12 = 0x8b;
        G_h01_3A46 = 0x56;
        G_h01_3A48 = 0x49;
        G_h01_3A7C = 0x56;
        G_h01_3A7E = 0x4a;
        F_h00_57D2(64);
        for (i = 0; i < 14; i++) {
            F_h00_8A46(G_h01_46CE, 32L, 0L, G_h01_46D2, 32L, 0L, 160L, 200L, 192L, 255L, 0L);
            if (i < 7) {
                G_h01_3A7A = i;
                F_h00_34E0(&G_h01_3A46);
                F_h00_34E0(&G_h01_3A10);
            } else {
                G_h01_3AB0 = i;
                F_h00_34E0(&G_h01_3A7C);
                F_h00_34E0(&G_h01_3A10);
            }
            F_h00_307C();
        }
        F_h00_8A46(G_h01_46CE, 32L, 0L, G_h01_46D2, 32L, 0L, 160L, 200L, 192L, 255L, 0L);
        G_h01_39A4 = 0x4b;
        G_h01_39A6 = 0x60;
        F_h00_34E0(&G_h01_39A4);
        F_h00_307C();
        F_h00_3AE4(&G_h01_39B4, G_h01_39AC, G_h01_39AE);
        F_h00_86A8(5L);
        F_h00_3AE4(&G_h01_3A20, G_h01_3A18, G_h01_3A1A);
        F_h00_3AE4(&G_h01_3A56, G_h01_3A4E, G_h01_3A50);
        F_h00_3AE4(&G_h01_3A8C, G_h01_3A84, G_h01_3A86);
        ret = 0;
    }

    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_435E();
    F_h00_4EC6();
    return ret;
}
