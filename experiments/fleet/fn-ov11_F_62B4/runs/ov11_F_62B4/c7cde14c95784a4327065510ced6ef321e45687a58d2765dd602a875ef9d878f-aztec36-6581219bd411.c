struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37EC;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int G_h01_37F2;
extern char G_h01_46E0[3];
extern struct ClusterRecord G_h01_8BEC[1];
extern short G_h01_940C[1];
extern int F_h11_5962();
extern int F_h11_5A12();
extern int F_h11_5A62();
extern int F_h11_5C42();
extern int F_h11_41F6();
extern unsigned int F_h00_463E();

recovered(mode)
int mode;
{
    int i, selected, result;

    G_h01_37F2 = 1;
    switch (G_h01_46E0[0]) {
    case 0:
        selected = 35;
        break;
    case 1:
        selected = 25;
        break;
    case 2:
        selected = 15;
        break;
    }

    for (i = 1; i < G_h01_37EC; i++) {
        F_h11_5962(i, 2);
        if (G_h01_8BEC[i].value8 != 0) {
            ((int *)&G_h01_8BEC[i])[24] = 1;
            G_h01_8BEC[i].value2c =
                ((int *)&G_h01_8BEC[i])[0] * 53 +
                ((((((int *)&G_h01_8BEC[i])[0] & 1) ^ 1) == 0) ? 4 : -8) - 1;
            G_h01_8BEC[i].value2e = ((int *)&G_h01_8BEC[i])[1] * 32 + 48;
            F_h11_5C42(i, 3);
            F_h11_41F6(24, G_h01_8BEC[i].pad18, 1,
                       G_h01_8BEC[i].value2c,
                       G_h01_8BEC[i].value2e);
        }
        else if (mode && F_h00_463E() % 100 < 25)
            *(G_h01_940C + 1 + i) = 1;
    }

    G_h01_37F0 = 0;
    G_h01_37EE = 0;
    if (mode) {
        result = F_h11_5A62(1, 0);
        result = F_h11_5A12(1, 0);
    }
}
