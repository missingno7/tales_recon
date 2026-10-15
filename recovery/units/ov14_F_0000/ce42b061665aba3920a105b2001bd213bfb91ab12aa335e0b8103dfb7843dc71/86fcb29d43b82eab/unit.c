struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
struct StringEntry { char *text; char pad[8]; };
extern struct FlagEntry G_h01_452F[35];
extern struct LinkEntry G_h01_4528[35];
extern struct StringEntry G_h01_4524[36];
extern char G_h01_1424;
extern char G_h01_17A6[1];
extern long G_h01_2A16;
extern char G_h01_3AB2;
extern unsigned char G_h01_46C8;
extern long G_h01_46CA;
extern char *G_h01_46D6;
extern char G_h01_46E0;
extern char G_h01_46E1;
extern char G_h01_46E2;
extern long G_h01_46EA;
extern long G_h01_46F2;
extern int F_h00_0640();
extern int F_h00_134C();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
extern int F_h00_435E();
extern int F_h00_4376();
extern unsigned int F_h00_463E();
extern int F_h00_57D2();
extern int F_h00_7B00();
extern int F_h00_8044();
extern int F_h00_86A8();
extern int F_h00_8BC8();
extern int F_h14_03C2();
extern char F_h14_0412();
extern char F_h14_04A8();
extern char F_h14_0540();
extern char F_h03_154E();

recovered(a)
char a;
{
    unsigned int local_02;
    int local_04;
    int local_06;
    int local_08;
    int local_0a;
    int local_0c;
    int local_0e;
    int local_10;
    int local_12;

    if (G_h01_46E2 > G_h01_46E1 || G_h01_46E1 <= 1 || G_h01_46C8 == 0) {
        if (a == 0)
            return;
    }

    F_h00_8BC8(G_h01_46CA, 0L);

    if (a == 0) {
        switch ((long)G_h01_46E0) {
        case 0:
            if (G_h01_46EA > 1000L)
                G_h01_3AB2 = 0;
            else
                G_h01_3AB2 = F_h14_03C2(G_h01_1424);
            break;
        case 1:
            if (G_h01_46EA > 5000L) {
                G_h01_3AB2 = 0;
            } else if (G_h01_46E2 & 1) {
                G_h01_3AB2 = F_h14_04A8(G_h01_1424);
            } else {
                G_h01_3AB2 = F_h14_0412(G_h01_1424);
            }
            break;
        case 2:
            if (G_h01_46EA > 10000L)
                G_h01_3AB2 = 0;
            else
                G_h01_3AB2 = F_h14_0540(G_h01_1424);
            break;
        }
    }

    G_h01_46E2 += F_h03_154E(G_h01_1424, G_h01_3AB2);
    if (G_h01_3AB2 != 0) {
    local_02 = F_h00_463E() % 100;
    if (local_02 < 25)
        --G_h01_46E2;
    else if (local_02 < 50)
        ++G_h01_46E2;
    else if (local_02 < 55 && a == 0)
        G_h01_46EA = 0L;

    local_02 = F_h00_463E();
    if ((local_02 & 1) || a) {
        ((struct FlagEntry *)((char *)&G_h01_452F + (long)G_h01_3AB2 * 12L))->value = 1;
        G_h01_46EA += ((int *)(((struct LinkEntry *)((char *)&G_h01_4528 + (long)G_h01_3AB2 * 12L))->target))[1];
        F_h00_0640(10);

        local_02 = F_h00_463E();
        if (local_02 & 1) {
            F_h00_35DC(0xa8, 0x3c, "Give it up,", 1, 0);
            F_h00_35DC(0xa8, 0x4c, "Scrooge!", 1, 0);
        } else {
            F_h00_35DC(0xa8, 0x3c, "You don't have a", 1, 0);
            F_h00_35DC(0xa8, 0x4c, "chance, McDuck!", 1, 0);
        }
        F_h00_35DC(0xa8, 0x64, "I've taken the", 1, 0);
        F_h00_35DC(0xa8, 0x74, "treasure from", 1, 0);

        local_10 = F_h00_8044(((struct StringEntry *)((char *)&G_h01_4524 + (long)G_h01_3AB2 * 12L))->text);
        local_10 <<= 2;
        F_h00_35DC(0xe0 - local_10, 0x84,
                   ((struct StringEntry *)((char *)&G_h01_4524 + (long)G_h01_3AB2 * 12L))->text,
                   1, 0);
        F_h00_35DC(0xe0 + local_10, 0x84, ".", 1, 0);
        F_h00_57D2(0x6e);
        F_h00_307C();
        G_h01_46D6 = &G_h01_17A6[0];
        F_h00_31AA(&G_h01_17A6[0]);
        F_h00_435E();

        local_12 = 0;
        while (G_h01_2A16 != 0L) {
            local_12 = F_h00_4376();
            if (local_12 & 0x80)
                break;
            F_h00_86A8(10L);
            local_12 = 1;
        }
        if (local_12 == 0 && F_h00_134C(0x28))
            F_h00_57D2(0x24);
        F_h00_330E();
        F_h00_57D2(0x21);
    }
    } else {
        G_h01_46F2 += G_h01_46EA;
        G_h01_46EA = 0L;
    }
    G_h01_1424 = G_h01_3AB2;
}

struct Record { char a,b; char reserved[10]; };
extern struct Record G_h01_452E[36];
F_h14_03C2(a)
char a;
{
 int i;
 for(i=1;i<35;++i) { if (i==a || G_h01_452E[i].a || G_h01_452E[i].b) continue; break; }
 return i;
}

struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
extern struct LinkEntry G_h01_4528[35];
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];

char
F_h14_0412(excluded)
char excluded;
{
    char i;
    char winner;
    int best;
    int value;

    best = 0;
    winner = 35;
    for (i = 1; i < 35; i++) {
        if (i != excluded && !G_h01_452E[i].value && !G_h01_452F[i].value) {
            value = ((int *)G_h01_4528[i].target)[1];
            if (value > best) {
                best = value;
                winner = i;
            }
        }
    }
    return winner;
}

struct FlagEntry { char value; char pad[11]; };
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];
extern char F_h03_154E();

char
F_h14_04A8(excluded)
char excluded;
{
    char i;
    char winner;
    int best;
    int cost;

    winner = 35;
    best = 16000;
    for (i = 1; i < 35; i++) {
        if (i != excluded && !G_h01_452E[i].value && !G_h01_452F[i].value) {
            cost = F_h03_154E(excluded, i);
            if (cost < best) {
                best = cost;
                winner = i;
            }
        }
    }
    return winner;
}

struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
extern struct LinkEntry G_h01_4528[35];
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];
extern char F_h03_154E();

char
F_h14_0540(excluded)
char excluded;
{
    char i;
    char winner;
    int best;
    int ratio;
    int cost;
    int value;

    winner = 35;
    best = 0;
    for (i = 1; i < 35; i++) {
        if (i != excluded && !G_h01_452E[i].value && !G_h01_452F[i].value) {
            cost = F_h03_154E(excluded, i);
            value = ((int *)G_h01_4528[i].target)[1];
            ratio = value / cost;
            if (ratio > best) {
                best = ratio;
                winner = i;
            }
        }
    }
    return winner;
}

