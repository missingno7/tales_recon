/* ov03_F_001C: recovered source. */
/* Structured restructure of ov03_F_001C: switch/if/while control flow, no gotos. */
struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
struct PointRef { struct Point *point; char reserved[8]; };
extern char G_h01_1766[1];
extern char G_h01_17A6[1];
extern char G_h01_17E6[1];
extern char G_h01_1866[1];
extern char G_h01_18A6[1];
extern long G_h01_2A16;
extern long G_h01_2C26;
extern char G_h01_2C2C;
extern struct PointRef G_h01_4524[36];
extern struct LinkEntry G_h01_4528[35];
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern char G_h01_46E0;
extern char G_h01_46E1;
extern char G_h01_46E2;
extern char G_h01_46E3;
extern char G_h01_46E4;
extern char G_h01_46E5;
extern long G_h01_46E6;
extern long G_h01_46EA;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern int G_h01_46F6;
extern int G_h01_46FE;
extern char G_h01_46DF;
extern long G_h01_4700;
extern long G_h01_4706;
extern char G_h01_4704;
extern char G_h01_4705;
extern int F_h00_8AD2();
extern int F_h00_01BA();
extern int F_h00_09C0();
extern int F_h04_0000();
extern int F_h04_0536();
extern int F_h04_1302();
extern int F_h04_149C();
extern int F_h12_0000();
extern int F_h13_02BE();
extern int F_h15_0000();
extern int F_h00_0640();
extern int F_h00_0FDE();
extern int F_h00_134C();
extern int F_h00_2816();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
extern int F_h00_435E();
extern int F_h00_4376();
extern unsigned int F_h00_463E();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_7522();
extern int F_h00_7B00();
extern int F_h00_8044();
extern int F_h00_86A8();
extern long F_h00_86DC();
long F_h03_154E();
extern int F_h03_1500();
extern int F_h05_0000();
extern int F_h07_0000();
extern int F_h07_1A02();
extern int F_h14_0000();
extern int F_h14_03AE();
extern int F_h04_1A3A();
extern int F_h04_1AA2();
extern int F_h04_1B94();
extern int F_h04_1D32();

recovered()
{
    char st;
    int done;
    int flag2;
    int r8;
    int idx;
    int tmp;
    int rv;
    unsigned int mod;
    char tb[13];
    char tc;
    char f1f;

    rv = 0;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:main.arc", 1005L);
    G_h01_46F6++;
    F_h00_2816(G_h01_46DA);
    G_h01_4700 = G_h01_46DA;
    idx = 0;
    do {
        F_h00_8AD2((long)idx);
        idx++;
    } while (idx < 8);
    F_h04_1302();
    G_h01_4704 = 0;
    F_h00_4EC6();
    F_h00_7522(F_h04_1302);
    F_h04_149C();
    done = 0;
    while (!done) {

    G_h01_4705 = 0;
    G_h01_46E4 = 0;
    G_h01_46E5 = 0;
    ((char *)G_h01_452F)[409] = 0;
    G_h01_46E1 = 1;
    G_h01_46DF = 0;
    G_h01_46E6 = 0;
    G_h01_46EE = 0;
    G_h01_46EA = 0;
    G_h01_46F2 = 0;
    G_h01_46E2 = 1;
    F_h04_0536();
    F_h04_0000();
    F_h00_7522(F_h04_1302);
    G_h01_46E3 = 0x23;
    st = 0x23;
    tb[0] = 1;
    idx = 0;
    do {
        F_h00_8AD2((long)idx);
        idx++;
    } while (idx < 8);
    G_h01_46FE = 0;
    flag2 = 0;
    while (flag2 == 0) {
    switch (st) {
    case 0x23:
    G_h01_46E1 += F_h03_154E(G_h01_46E3, st);
        G_h01_46E3 = 0x23;
        if (G_h01_46E1 <= 0x1e) {
            st = F_h13_02BE();
            F_h00_7522(F_h13_02BE);
        } else {
            st = 0;
        }
        break;

    case 0:
    G_h01_46FE = 0;
        G_h01_46E1 += F_h03_154E(G_h01_46E3, st);
        G_h01_46E3 = 0;
        F_h03_1500();
        if (G_h01_46E1 >= 0x1e)
            flag2 = 1;
        else
            st = 0x24;
        break;

    case 0x25:
    G_h01_46E3 = 0x25;
        G_h01_46E1 = 0x1e;
        st = 0;
        break;

    case 0x24:
    st = F_h15_0000(0, tb);
        tc = 0x24;
        F_h00_7522(F_h15_0000);
        rv = -5;
        break;

    case 0x28:
    st = F_h15_0000(1, tb);
        tc = 0x28;
        F_h00_7522(F_h15_0000);
        break;

    case 0x26:
    rv = F_h12_0000();
        F_h00_0640(9);
        if (rv != 0) {
            F_h00_35DC(176, 60, "It must be", 1, 0);
            F_h00_35DC(176, 76, "your lucky day!", 1, 0);
            F_h00_35DC(176, 92, "That rare coin", 1, 0);
            F_h00_35DC(176, 108, "is worth $1000!", 1, 0);
            G_h01_46E6 += 1000;
        } else {
            F_h00_35DC(184, 60, "Mr. McDuck,", 1, 0);
            F_h00_35DC(184, 76, "don't forget", 1, 0);
            F_h00_35DC(184, 92, "about the", 1, 0);
            F_h00_35DC(184, 108, "contest!", 1, 0);
        }
        F_h00_307C();
        G_h01_46D6 = G_h01_1766;
        F_h00_31AA(G_h01_1766);
        if (F_h00_134C(0x32))
            F_h00_57D2(0x24);
        F_h00_330E();
        F_h00_7522(F_h12_0000);
        st = 0x23;
        break;

    case 0x27:
    F_h07_0000();
        F_h00_7522(F_h07_0000);
        st = 0x23;
        break;

    default:
        G_h01_46FE = 0;
        if (G_h01_452E[st].value != 0) {
        F_h00_0640(3);
        F_h00_35DC(168, 60, "Uh...", 1, 0);
        F_h00_35DC(168, 76, "Gee, Mr. McD,", 1, 0);
        F_h00_35DC(168, 92, "you already have", 1, 0);
        F_h00_35DC(168, 108, "that treasure.", 1, 0);
        F_h00_35DC(168, 132, "Why don't I", 1, 0);
        F_h00_35DC(168, 148, "take you to", 1, 0);
        F_h00_35DC(168, 164, "somewhere else?", 1, 0);
        F_h00_307C();
        G_h01_46D6 = G_h01_1866;
        F_h00_31AA(G_h01_1866);
        if (F_h00_134C(0x50))
            F_h00_57D2(0x24);
        F_h00_330E();
        st = tc;
        break;
        }
        if (G_h01_452F[st].value != 0) {
        F_h00_0640(10);
        F_h00_35DC(168, 60, "Hah! You're too", 1, 0);
        F_h00_35DC(168, 76, " late Scrooge!", 1, 0);
        F_h00_35DC(168, 100, " This treasure", 1, 0);
        F_h00_35DC(168, 116, "   is mine!", 1, 0);
        F_h00_57D2(0x6e);
        F_h00_307C();
        G_h01_46D6 = G_h01_17A6;
        F_h00_31AA(G_h01_17A6);
        F_h00_435E();
        idx = 0;
        while (G_h01_2A16 != 0) {
            idx = F_h00_4376();
            if (idx & 0x80)
                break;
            F_h00_86A8(5L);
            idx = 1;
        }
        if (idx == 0) {
            if (F_h00_134C(0x28))
                F_h00_57D2(0x24);
        }
        F_h00_330E();
        F_h00_57D2(0x21);
        while (G_h01_2A16 != 0)
            ;
        F_h00_57D2(0);
        st = tc;
        break;
        }
        idx = (char)F_h03_154E(G_h01_46E3, st);
        if (idx != 0) {
            if (G_h01_46E5 != 0) {
        mod = F_h00_463E() % 100;
        if ((unsigned int)mod > (unsigned int)((G_h01_46E0 + 1) << 3)) {
            G_h01_46E1 += F_h03_154E(G_h01_46E3, st);
            F_h00_57D2(0);
            F_h00_86A8(5L);
            F_h00_57D2(0x54);
        } else {
            F_h00_57D2(0);
            F_h00_86A8(5L);
            F_h00_57D2(0x45);
            while (G_h01_2A16 != 0)
                ;
            idx = 1;
            do {
                if (G_h01_452E[idx].value == 0 && G_h01_452F[idx].value == 0) {
                    st = idx;
                    break;
                }
                idx++;
            } while (idx < 35);
            F_h00_0640(2);
            F_h00_35DC(168, 60, "The Atomic Matter", 1, 0);
            F_h00_35DC(168, 76, "Transmitter ", 1, 0);
            F_h00_35DC(168, 92, "malfunctioned", 1, 0);
            F_h00_35DC(168, 108, "and sent you to", 1, 0);
            idx = F_h00_8044(G_h01_4524[st].point);
            idx = idx << 2;
            F_h00_35DC(232 - idx, 124, G_h01_4524[st].point, 1, 0);
            F_h00_35DC(idx + 232, 124, ".", 1, 0);
            F_h00_307C();
            G_h01_46D6 = G_h01_17E6;
            F_h00_31AA(G_h01_17E6);
            if (F_h00_134C(0x3c))
                F_h00_57D2(0x24);
            F_h00_330E();
            G_h01_46E1 += F_h03_154E(G_h01_46E3, st);
        }
            } else {
                r8 = (char)F_h03_154E(G_h01_46E3, st);
                F_h00_0640(3);
                F_h00_57D2(0x21);
                while (G_h01_2A16 != 0)
                    ;
                F_h00_57D2(0);
                F_h00_4EC6();
                F_h00_0FDE(1);
                idx = F_h00_463E() % 3;
                switch (idx) {
                case 0:
                    F_h00_4D04(3);
                    F_h00_35DC(168, 60, "Launchpad McQuack,", 1, 0);
                    F_h00_35DC(168, 76, "Flying Ace...", 1, 0);
                    F_h00_35DC(168, 92, "At your service!", 1, 0);
                    break;
                case 1:
                    F_h00_4D04(13);
                    F_h00_35DC(168, 60, "Ready to", 1, 0);
                    F_h00_35DC(168, 76, "hit the skies,", 1, 0);
                    F_h00_35DC(168, 92, "Mr. McD!", 1, 0);
                    break;
                case 2:
                    F_h00_4D04(14);
                    F_h00_35DC(168, 60, "Ready to", 1, 0);
                    F_h00_35DC(168, 76, "take off,", 1, 0);
                    F_h00_35DC(168, 92, "Mr. McD!", 1, 0);
                    break;
                }

                F_h00_0FDE(1);
                F_h00_2816(G_h01_46DA);
                F_h00_307C();
                G_h01_46D6 = G_h01_1866;
                F_h00_31AA(G_h01_1866);
                F_h00_57D2(0x77);
                while (G_h01_2A16 != 0)
                    ;
                F_h00_4EC6();
                switch (G_h01_46E0) {
                case 0:
                    idx = 25;
                    break;
                case 1:
                    idx = 50;
                    break;
                case 2:
                    idx = 75;
                    break;
                }
                mod = F_h00_463E() % 100;
                f1f = 0;
                if ((unsigned int)mod < (unsigned int)idx) {
                    if (G_h01_452F[st].value == 0) {
                        f1f = 1;
                        F_h14_03AE(G_h01_46E3, st);
                    }
                }

                F_h00_7522(F_h04_1302);
                F_h00_7522(F_h13_02BE);
                rv = F_h05_0000(r8, f1f);
                F_h00_7522(F_h05_0000);
                F_h00_330E();
                if (rv == 0 && f1f == 0) {
                    F_h00_0640(2);
                    F_h00_35DC(168, 60, "Sorry, Mr. McDuck,", 1, 0);
                    F_h00_35DC(168, 76, "but it will take", 1, 0);
                    F_h00_35DC(168, 92, "2 days to fix", 1, 0);
                    F_h00_35DC(168, 108, "the plane.", 1, 0);
                    G_h01_46E1 += 2;
                    F_h00_307C();
                    G_h01_46D6 = G_h01_17E6;
                    F_h00_31AA(G_h01_17E6);
                    if (F_h00_134C(0x3c))
                        F_h00_57D2(0x24);
                    F_h00_330E();
                    if (G_h01_46E6 > 0) {
                        mod = F_h00_463E();
                        mod = mod % 10;
                        switch (mod) {
                        case 0:
                        case 1:
                            mod = 0;
                            break;
                        case 2:
                        case 3:
                        case 4:
                            mod = G_h01_46E6 >> 3;
                            break;
                        case 5:
                        case 6:
                        case 7:
                            mod = G_h01_46E6 >> 2;
                            break;
                        case 8:
                        case 9:
                            mod = G_h01_46E6 >> 1;
                            break;
                        }
                        F_h00_0640(9);
                        F_h00_35DC(168, 44, "I've searched the", 1, 0);
                        F_h00_35DC(168, 60, "wreckage for your", 1, 0);
                        F_h00_35DC(168, 76, "treasure, and I'm", 1, 0);
                        if (mod == 0) {
                            F_h00_35DC(168, 92, "happy to report", 1, 0);
                            F_h00_35DC(168, 108, "that nothing", 1, 0);
                        } else {
                            F_h00_35DC(168, 92, "sorry to report", 1, 0);
                            F_h00_35DC(168, 108, "that $", 1, 0);
                            F_h00_09C0(216, 108, (long)mod, 1, 0, 0);
                            G_h01_46E6 -= mod;
                        }
                        F_h00_35DC(168, 124, "was lost in", 1, 0);
                        F_h00_35DC(168, 140, "the crash!", 1, 0);
                        F_h00_307C();
                        G_h01_46D6 = G_h01_1766;
                        F_h00_31AA(G_h01_1766);
                        if (F_h00_134C(0x64))
                            F_h00_57D2(0x24);
                        F_h00_330E();
                    }
                } else if (f1f != 0 && rv == 0) {
                    F_h14_0000(1);
                    F_h00_7522(F_h14_0000);
                    G_h01_46E3 = st;
                    st = 0x24;
                    rv = -5;
                    break;
                }
            }
        }
        G_h01_46E3 = st;
        if (G_h01_46E1 > 0x1e)
            break;
        rv = F_h00_01BA(G_h01_46E3);
        G_h01_46E1 += 1;
        if (rv != 0) {
            if (G_h01_4706 != 0) {
                G_h01_4706 = 0;
                F_h00_0FDE(1);
                F_h00_2816(G_h01_46DA);
            } else {
                F_h00_4EC6();
                tmp = F_h00_463E() % 3;
                F_h00_0FDE(2);
                switch (tmp) {
                case 0:
                    F_h00_4D04(11);
                    tmp = 0x77;
                    break;
                case 1:
                    F_h00_4D04(11);
                    tmp = 0x27;
                    break;
                case 2:
                    F_h00_4D04(24);
                    tmp = 0x49;
                    break;
                }
                G_h01_46DA = G_h01_4700;
                F_h00_0640(6);
                F_h00_35DC(168, 60, "Congratulations!", 1, 0);
                F_h00_35DC(168, 76, "You have acquired", 1, 0);
                F_h00_35DC(168, 92, "another valuable", 1, 0);
                F_h00_35DC(168, 108, "   treasure!", 1, 0);
                idx = *(int *)(G_h01_4528[G_h01_46E3].target + 2);
                G_h01_46E6 += idx;
                F_h00_35DC(208, 128, "$", 1, 0);
                F_h00_09C0(216, 128, (long)idx, 1, 0, 0);
                F_h00_330E();
                F_h00_307C();
                G_h01_46D6 = G_h01_18A6;
                F_h00_31AA(G_h01_18A6);
                F_h00_57D2(tmp);
                G_h01_2C26 = 1;
                G_h01_2C2C = 8;
                if (F_h00_134C(0x28))
                    F_h00_57D2(0x24);
                G_h01_2C2C = 0;
                G_h01_2C26 = 0;
                F_h00_4EC6();
            }
            F_h00_330E();
            G_h01_452E[G_h01_46E3].value = 1;
            if (G_h01_46E3 == G_h01_4705) {
                G_h01_46E4 = 1;
                F_h00_0640(2);
                F_h00_35DC(160, 16, "Now that you", 1, 0);
                F_h00_35DC(160, 32, "have found", 1, 0);
                F_h00_35DC(160, 48, "bombastium I", 1, 0);
                F_h00_35DC(160, 64, "can build you", 1, 0);
                F_h00_35DC(160, 80, "a matter transmitter", 1, 0);
                F_h00_35DC(160, 96, "you can use", 1, 0);
                F_h00_35DC(160, 112, "next time you're", 1, 0);
                F_h00_35DC(160, 128, "in the office", 1, 0);
                F_h00_35DC(160, 146, "to transport", 1, 0);
                F_h00_35DC(160, 162, "yourself to any", 1, 0);
                F_h00_35DC(160, 180, "destination.", 1, 0);
                F_h00_330E();
                F_h00_307C();
                G_h01_46D6 = G_h01_17E6;
                F_h00_31AA(G_h01_17E6);
                F_h00_57D2(0x54);
                if (F_h00_134C(0x64))
                    F_h00_57D2(0x24);
                F_h00_330E();
            }
        } else {
            F_h00_0FDE(1);
            G_h01_46DA = G_h01_4700;
            F_h00_2816(G_h01_46DA);
        }
        st = 0x24;
        break;
    }
    if (G_h01_46E1 > 0x1e) {
        st = 0;
        G_h01_46E3 = 0;
    } else if (rv != -5) {
        F_h14_0000(0);
        F_h00_7522(F_h14_0000);
        F_h07_1A02();
        F_h00_7522(F_h07_1A02);
    }
    }

    if (G_h01_46F2 > G_h01_46EE) {
        F_h04_1A3A(0);
        F_h04_1AA2(0);
    } else {
        F_h04_1A3A(1);
        F_h04_1AA2(1);
    }
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(0);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    done = F_h04_1B94();
    if (done == 0) {
        F_h04_149C();
    }
    F_h00_57D2(0);
    }
    F_h04_1D32();
    G_h01_46F6--;
}
