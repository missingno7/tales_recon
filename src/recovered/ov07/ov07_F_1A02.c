struct Record {
    int amount;
    int flag;
    unsigned char state;
    char pad;
    int category;
    int f8;
    int f10;
    int f12;
    char rest[32];
};

extern struct Record G_h01_4D82[16];
extern unsigned char G_h01_5014[16][31];
extern char G_h01_46E0;
extern char G_h01_46E1;
extern long G_h01_46E6;
extern long G_h01_46EA;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern char G_h01_4D60;
extern int F_h00_463E();

recovered()
{
    int i;
    int t4;
    int cat;
    int v8;
    int q;
    int vC;
    int vE;
    int v10;
    int k;
    int v14;
    int t22;

    for (; G_h01_4D60 < G_h01_46E1; ) {
        G_h01_4D60++;
        for (i = 0; i < 15; i++) {
            if ((G_h01_4D82[i].state & 0x7f) == 3) {
                t22 = (F_h00_463E() & 3) * ((G_h01_46E0 >> 1) + 1);
                if ((F_h00_463E() & 0xff) > 127)
                    t22 = -t22;
                if (G_h01_4D60 >= (char)G_h01_4D82[i].f10 + t22) {
                    G_h01_4D82[i].state = 1;
                    G_h01_4D82[i].amount += G_h01_4D82[i].amount * G_h01_4D82[i].f12 / 100;
                    G_h01_4D82[i].f8 = G_h01_4D60;
                }
            }
            if ((G_h01_4D82[i].state & 0x7f) == 4) {
                if (G_h01_4D60 >= (char)G_h01_4D82[i].f10) {
                    G_h01_4D82[i].state = 2;
                    G_h01_4D82[i].amount += G_h01_4D82[i].amount * G_h01_4D82[i].f12 / 100;
                    G_h01_4D82[i].f12 *= -1;
                    G_h01_4D82[i].f8 = G_h01_4D60;
                    if (G_h01_4D82[i].amount < 0)
                        G_h01_4D82[i].amount = 0;
                }
            }
        }
        for (i = 0; i < 15; i++) {
            t4 = 0;
            q = 0;
            if (G_h01_4D82[i].state == 0) {
                cat = G_h01_4D82[i].category;
                if (G_h01_4D60 < 30) {
                    vC = G_h01_5014[cat][G_h01_4D60 - 1];
                    vE = G_h01_5014[cat][G_h01_4D60];
                    if (vC <= vE)
                        v8 = 1;
                    else
                        v8 = -1;
                    k = 0;
                    v10 = v8;
                    while (k < 15 && G_h01_4D60 + k < 31 && v8 == v10) {
                        if (G_h01_5014[cat][G_h01_4D60 + k - 1] <= G_h01_5014[cat][G_h01_4D60 + k])
                            v10 = 1;
                        else
                            v10 = -1;
                        k++;
                    }
                    if (v8 != v10 && v10 == 1) {
                        t4 = 5 * (3 - G_h01_46E0) + (G_h01_4D60 >> 2);
                        if (!G_h01_4D82[i].flag)
                            t4 = t4 >> 2;
                        if (t4 > (F_h00_463E() & 0xff)) {
                            if (G_h01_46EE + G_h01_46E6 < G_h01_46F2 + G_h01_46EA)
                                v14 = (F_h00_463E() & 0xf) + 110;
                            else
                                v14 = (F_h00_463E() & 7) + 105;
                            G_h01_4D82[i].f12 = v14 - G_h01_5014[cat][G_h01_4D60 - 1];
                            G_h01_4D82[i].state = 3;
                            G_h01_4D82[i].f8 = G_h01_4D60;
                            G_h01_4D82[i].f10 = (3 - G_h01_46E0) * 3 + G_h01_4D60 + (k >> 1);
                            if (G_h01_4D82[i].f10 > 30)
                                G_h01_4D82[i].f10 = 30;
                        }
                    }
                    if (v8 != v10 && v10 == -1) {
                        q = 5 * (G_h01_46E0 + 1) + (G_h01_4D60 >> 2);
                        if (!G_h01_4D82[i].flag)
                            q = q >> 2;
                        if (q > (F_h00_463E() & 0xff)) {
                            if (G_h01_46EE + G_h01_46E6 < G_h01_46F2 + G_h01_46EA)
                                v14 = (F_h00_463E() & 7) + 5;
                            else
                                v14 = (F_h00_463E() & 0xf) + 10;
                            G_h01_4D82[i].f12 = -(G_h01_5014[cat][G_h01_4D60 - 1] + v14);
                            G_h01_4D82[i].state = 4;
                            G_h01_4D82[i].f8 = G_h01_4D60;
                            G_h01_4D82[i].f10 = (3 - G_h01_46E0) * 3 + G_h01_4D60 + (k >> 1);
                            if (G_h01_4D82[i].f10 > 30)
                                G_h01_4D82[i].f10 = 30;
                        }
                    }
                }
            }
        }
    }
}
