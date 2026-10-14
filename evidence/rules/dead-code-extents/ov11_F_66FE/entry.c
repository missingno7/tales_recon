/* Plain structured transcription of ov11_F_0000 (worker haiku-fn-ov11_F_0000). */
struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };

extern int G_h01_12FE;
extern long G_h01_2C26;
extern char G_h01_2C2C;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern int G_h01_7A94;
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern int G_h01_8A42;
extern struct Record G_h01_8A66[1];
extern int G_h01_8B1C[41][4];
extern short G_h01_940C[1];
extern int G_h01_94AC;
extern int G_h01_94AE;
extern int G_h01_94B8;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94E6;
extern long G_h01_9FA6;
extern char G_h01_16E6[1];

extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_435E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_868C();
extern int F_h00_86A8();
extern int F_h00_8A46();
extern int F_h00_8BC8();

recovered(arg)
int arg;
{
    int i;
    int aux;
    int j;
    int lim;
    struct Record *p;
    int flag;
    char scratch[200];

    flag = 1;
    G_h01_7A94 = arg;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h11_15C8(1);
    F_h11_2A3A();
    F_h11_4EC6();
    F_h11_69A4();
    F_h11_3A24();
    F_h11_21F8();
    F_h11_68B0();
    F_h11_6FFE();
    F_h11_14BA(1);
    G_h01_2C26 = 0;
    G_h01_2C2C = 0;
    F_h00_330E();
    G_h01_12FE = 0;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xC8L, 0xC0L, 0xFFL, 0L);
    F_h11_62B4(1);
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(8);
    F_h00_57D2(0x5C);
    G_h01_940C[G_h01_8B1C[G_h01_94BA][G_h01_94BC]] = 0;
    G_h01_94B8 = 0;
    F_h00_435E();

    while (G_h01_12FE == 0) {
        if (G_h01_8A3C == 0) {
            F_h11_13DC();
        }
        G_h01_94E6 = 0;
        F_h11_063A();
        F_h11_0BB6();
        if (G_h01_12FE != 0) continue;
        if (G_h01_94AE == 7) {
            F_h00_57D2(0);
            F_h00_86A8(0x32L);
            F_h00_330E();
            if (G_h01_94AC < 3) {
                G_h01_8A3C = 3;
                flag = 1;
                F_h11_49CE();
                F_h11_15C8(0);
                F_h11_14BA(0);
                F_h11_2A3A();
                F_h11_62B4(0);
                F_h11_3A24();
                F_h11_21F8();
                F_h00_86A8(0x64L);
                G_h01_94B8 = 0;
                F_h00_57D2(0x5C);
            } else {
                break;
            }
        }
        F_h11_0558();
        if (G_h01_8A42) {
            G_h01_8A3C = 3;
        }
        j = G_h01_8A3E / 104;
        lim = (G_h01_8A42 ? 4 : 3) + j;

        for (i = j; i < lim; i++) {
            p = &G_h01_8A66[i];
            if (p->ignored) {
                F_h11_5D14(p->ignored);
            }
            if (p->value1) {
                F_h11_51C0(p->value1);
            }
            if (p->value2) {
                F_h11_6CFE(p->value2);
                if (p->value3) {
                    F_h11_6CFE(p->value3);
                }
            }
            if (p->value5) {
                F_h11_2EEA(p->value5);
            }
            if (p->value5) {
                F_h11_3532(p->value5);
            }
            if (p->value4) {
                F_h11_6486(p->value4);
                F_h11_6582(p->value4);
            }
            if (p->value6) {
                F_h11_70DC(p->value6);
            }
        }

        F_h11_3D9A();
        F_h11_2272();
        F_h11_0B4C();
        F_h11_0D8E();
        if (G_h01_8A3C > 1) {
            F_h11_4848();
        }
        if (G_h01_8A3C > 0) {
            F_h11_487E(G_h01_8A3E, 0, 0x140, G_h01_8A3C == 1);
            G_h01_8A3C--;
        } else {
            F_h11_4790();
        }

        for (i = j; i < lim; i++) {
            p = &G_h01_8A66[i];
            if (p->ignored) {
                F_h11_5C1A(p->ignored);
            }
            if (p->value5) {
                F_h11_2DBA(p->value5);
            }
        }

        F_h11_3B92();

        for (i = j; i < lim; i++) {
            p = &G_h01_8A66[i];
            if (p->value1) {
                F_h11_519C(p->value1);
            }
            if (p->value5) {
                F_h11_36F8(p->value5);
                F_h11_37E4(p->value5);
            }
            if (p->value2) {
                F_h11_6C3A(p->value2);
                if (p->value3) {
                    F_h11_6C3A(p->value3);
                }
            }
            if (p->value4 && G_h01_94AE == 45) {
                F_h11_645E(p->value4);
            }
            if (p->value6) {
                F_h11_706C(p->value6);
            }
        }

        F_h11_1372();
        F_h11_23F4();
        F_h11_27CC();
        if (flag) {
            F_h00_330E();
            F_h00_307C();
            G_h01_46D6 = G_h01_16E6;
            F_h00_31AA(G_h01_16E6);
            flag = 0;
            F_h00_435E();
        } else {
            F_h00_307C();
        }
    }

    F_h11_049C();
    F_h11_4A92();
    F_h00_330E();
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = G_h01_9FA6;
    F_h00_2816(G_h01_46DA);
    F_h00_57D2(0);
    F_h00_4EC6();
    return G_h01_12FE;
}
