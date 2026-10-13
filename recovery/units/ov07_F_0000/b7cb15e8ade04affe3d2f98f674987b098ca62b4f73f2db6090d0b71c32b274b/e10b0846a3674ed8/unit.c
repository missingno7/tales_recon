/* Candidate v2 (v1 with the leading space of the third string restored) for ov07_F_0000: setup calls, 3+5 table-driven calls, key state machine, closing screen. */
struct Rec54 { char b[54]; };

extern char G_h01_33E2;
extern int G_h01_0A92[8];
extern char G_h01_3232;
extern char G_h01_323A;
extern char G_h01_323C;
extern char G_h01_3242;
extern char G_h01_329E;
extern int G_h01_1466;
extern char G_h01_1766[1];
extern char *G_h01_46D6;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46DA;
extern int F_h00_435E();
extern int F_h00_57D2();
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_8A46();
extern long F_h00_86DC();
extern int F_h00_2816();
extern int F_h00_868C();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_4376();
extern int F_h00_330E();
extern int F_h00_0640();
extern int F_h00_35DC();
extern int F_h00_134C();
extern int F_h00_3AE4();
extern int F_h00_86A8();
extern int F_h07_1424();
extern int F_h07_03CC();
extern int F_h07_04AC();
extern int F_h07_0612();

recovered()
{
    unsigned char key;
    int flag;
    int i;
    int cnt;
    int y;
    int x;
    int u0e;
    long saved;
    int u14;

    u14 = 0;
    G_h01_33E2 = 0;
    F_h00_435E();
    F_h00_57D2(0);
    F_h00_0FDE(1);
    F_h00_291E(0x14, G_h01_46CE);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    for (i = 0; i < 3; i++)
        F_h00_291E(G_h01_0A92[i], (char *)((struct Rec54 *)&G_h01_3232 + i));
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:invart.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    for (i = 3; i < 8; i++)
        F_h00_291E(G_h01_0A92[i], (char *)((struct Rec54 *)&G_h01_3232 + i));
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
    F_h00_57D2(30);
    F_h07_1424(&G_h01_3232, &G_h01_329E);
    cnt = 0;
    x = 10;
    y = 10;
    F_h07_03CC();
    F_h07_04AC(y, x);
    F_h00_307C();
    G_h01_46D6 = (char *)&G_h01_1466;
    F_h00_31AA((char *)&G_h01_1466);
    flag = 0;
    while (flag == 0) {
        key = F_h00_4376();
        if (key & 0x80) {
            F_h00_57D2(36);
            if (x == 15)
                flag = 1;
            else
                flag = F_h07_0612(x, &G_h01_3232);
            F_h07_03CC();
            F_h07_04AC(y, x);
            F_h00_307C();
        } else {
            key &= 0x3f;
            switch (key) {
            case 1:
                F_h00_57D2(36);
                x--;
                x &= 15;
                cnt--;
                if (cnt < 0) {
                    y--;
                    y &= 15;
                    cnt = 0;
                }
                F_h07_03CC();
                F_h07_04AC(y, x);
                F_h00_307C();
                F_h00_86A8(10L);
                break;
            case 5:
                F_h00_57D2(36);
                x++;
                x &= 15;
                cnt++;
                if (cnt > 5) {
                    y++;
                    y &= 15;
                    cnt = 5;
                }
                F_h07_03CC();
                F_h07_04AC(y, x);
                F_h00_307C();
                F_h00_86A8(10L);
                break;
            default:
                u14 = 0;
                break;
            }
        }
    }
    F_h00_330E();
    if (G_h01_33E2) {
        F_h00_0640(1);
        F_h00_35DC(176, 60, "I'll put that", 1, 0);
        F_h00_35DC(176, 76, "order through", 1, 0);
        F_h00_35DC(176, 92, " right away,  ", 1, 0);
        F_h00_35DC(176, 108, " Mr. McDuck!", 1, 0);
        F_h00_330E();
        F_h00_307C();
        G_h01_46D6 = G_h01_1766;
        F_h00_31AA(G_h01_1766);
        if (F_h00_134C(50))
            F_h00_57D2(36);
    }
    for (i = 0; i < 8; i++)
        F_h00_3AE4((char *)((struct Rec54 *)&G_h01_3242 + i),
                   *(short *)((struct Rec54 *)&G_h01_323A + i),
                   *(short *)((struct Rec54 *)&G_h01_323C + i));
}

/* Non-promoting ownership probe for ov07_F_03CC. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h07_0E06();
extern int F_h07_0E7C();
extern int F_h00_35DC();
extern char G_h01_3232;
extern char G_h01_329E;

F_h07_03CC()
{
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h07_0E06(&G_h01_3232);
    F_h07_0E7C(&G_h01_329E);
    F_h00_35DC(100, 8, "STOCK PORTFOLIO", 7, 15);
    F_h00_35DC(40, 22, "COMPANY NAME", 1, 7);
    F_h00_35DC(196, 22, "PRICE", 1, 7);
    F_h00_35DC(244, 22, "SHARES", 1, 7);
}

struct PortfolioRow {
    char name[34];
    int value;
    char rest[10];
};

extern int F_h00_35DC();
extern int F_h00_09C0();
extern int F_h07_0EC0();
extern struct PortfolioRow G_h01_4D62[16];

F_h07_04AC(start, selected)
int start;
int selected;
{
    int i;
    int slot;
    int value;
    char scratch[16];
    int y;
    unsigned char color;

    y = 40;
    for (i = start; i < start + 6; i++) {
        slot = i & 15;
        color = 0;
        if (slot == selected)
            color = 9;
        F_h00_35DC(32, y, "                                ", 1, color);
        if (slot == 15)
            F_h00_35DC(32, y, "RETURN TO OFFICE", 15, color);
        else {
            value = F_h07_0EC0(slot);
            F_h00_09C0(248, y, (long)value, 1, color, 1);
            F_h00_35DC(32, y, G_h01_4D62[slot].name, 1, color);
            F_h00_09C0(280, y, (long)G_h01_4D62[slot].value, 1, color, 1);
        }
        y += 20;
    }
}

/* Candidate for ov07_F_0612: state machine over key codes (historical reconstruction candidate). */
struct Input { char f0[2]; long text; };
struct Slot { int f0; int f2; char rest[50]; };
struct Holding { int shares; char rest[44]; };
struct Symbol { int code; char rest[44]; };
struct PortfolioRow { char data[46]; };

extern struct Input *G_h01_6EA8;
extern long G_h01_6EAC;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46DA;
extern long G_h01_46E6;
extern char G_h01_33E2;
extern struct PortfolioRow G_h01_4D62[16];
extern struct Holding G_h01_4D84[16];
extern struct Symbol G_h01_4D88[16];
extern int F_h00_0FDE();
extern int F_h00_2816();
extern long F_h00_86DC();
extern long F_h00_291E();
extern int F_h00_307C();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3C0E();
extern int F_h00_4376();
extern int F_h00_57D2();
extern int F_h00_868C();
extern int F_h00_8044();
extern int F_h00_8A46();
extern int F_h00_09C0();
extern int F_h07_0F30();
extern int F_h07_0E06();
extern int F_h07_0E7C();
extern int F_h07_0EC0();
extern int F_h07_18F8();

F_h07_0612(arg, p)
int arg;
struct Slot *p;
{
    char scratch[72];
    int s4a;
    int s4c;
    int xs[4];
    int s56;
    int s58;
    int u1;
    int key;
    int u2;
    int s60;
    int s62;
    int s64;
    int s66;
    int s68;
    char buf[2];

    buf[1] = 0;
    while ((F_h00_4376() & 0x80) == 0x80)
        ;
    s4a = 4;
    s4c = 7;
    xs[0] = 0xc0;
    xs[1] = 0xe0;
    xs[2] = 0x100;
    xs[3] = 0x120;
    s56 = 0;
    s62 = 0;
    s58 = 0;
    u1 = -1;
    u2 = 1;
    s64 = 1;
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    G_h01_6EAC = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:invest.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    G_h01_6EA8 = 0;
    G_h01_6EA8 = F_h00_291E(arg, G_h01_6EA8);

    while (s58 == 0) {
        key = (unsigned char)F_h00_4376();
        if (key & 0x40) {
            s58 = 1;
        } else if (key & 0x80) {
            if (s66 == 0) {
                F_h00_57D2(36);
                s66 = 1;
                switch (s56) {
                case 3:
                    s58 = 2;
                    break;
                case 0:
                    s58 = 1;
                    break;
                case 1:
                    s4a = 5;
                    if (s60 == 0) {
                        s62 = 5;
                    } else if (G_h01_4D84[arg].shares >= 99) {
                        s62 = 6;
                    } else if (G_h01_46E6 - s60 >= 0) {
                        G_h01_46E6 -= s60;
                        G_h01_4D84[arg].shares++;
                        s62 = 3;
                        G_h01_33E2 = 1;
                        s66 = 0;
                    } else {
                        s62 = 1;
                    }
                    break;
                case 2:
                    s4c = 6;
                    if (G_h01_4D84[arg].shares > 0) {
                        G_h01_46E6 += s60;
                        G_h01_4D84[arg].shares--;
                        s62 = 2;
                        G_h01_33E2 = 1;
                        s66 = 0;
                    } else {
                        s62 = 4;
                    }
                    break;
                default:
                    break;
                }
                s64 = 1;
            }
        } else {
            key &= 0x3f;
            switch (key) {
            case 7:
                if (s66 != 0)
                    break;
                F_h00_57D2(36);
                s66 = 1;
                s56 -= 1;
                if (s56 < 0)
                    s56 = 2;
                s64 = 1;
                break;
            case 3:
                if (s66 != 0)
                    break;
                s66 = 1;
                F_h00_57D2(36);
                s56 += 1;
                if (s56 > 2)
                    s56 = 0;
                s64 = 1;
                break;
            default:
                if (s66 != 0)
                    s64 = 1;
                s4a = 4;
                s4c = 7;
                s62 = 0;
                s66 = 0;
                break;
            }
        }
        if (s64 != 0) {
            p[3].f0 = 0xc0;
            p[3].f2 = 0xaf;
            F_h00_34E0(&p[3]);
            p[s4a].f0 = 0xe0;
            p[s4a].f2 = 0xaf;
            F_h00_34E0(&p[s4a]);
            p[s4c].f0 = 0x100;
            p[s4c].f2 = 0xaf;
            F_h00_34E0(&p[s4c]);
            F_h07_0F30(xs[s56]);
            s68 = F_h00_8044(&G_h01_4D62[arg]);
            F_h00_35DC(160 - s68 * 4, 8, &G_h01_4D62[arg], 7, 9);
            F_h07_0E06(p);
            F_h07_0E7C(&p[2]);
            F_h00_35DC(35, 23, "       COMPANY DESCRIPTION      ", 1, 7);
            F_h07_18F8(arg, 1, 32, 35);
            F_h00_35DC(32, 100, " TOTAL MONEY       CHART TYPE  ", 1, 7);
            buf[0] = G_h01_4D88[arg].code + 'A';
            F_h00_35DC(224, 113, buf, 1, 0);
            F_h00_35DC(96, 113, ".00", 14, 0);
            F_h00_09C0(96, 113, G_h01_46E6, 14, 0, 1);
            F_h00_35DC(32, 127, " PRICE PER SHARE  SHARES OWNED  ", 1, 7);
            F_h00_09C0(232, 140, (long)G_h01_4D84[arg].shares, 14, 0, 1);
            F_h00_35DC(96, 140, ".00", 1, 0);
            s60 = F_h07_0EC0(arg);
            F_h00_09C0(96, 140, (long)s60, 1, 0, 1);
            switch (s62) {
            case 1:
                F_h00_35DC(32, 150, "    NOT ENOUGH MONEY TO BUY     ", 1, 9);
                break;
            case 0:
                F_h00_35DC(35, 150, "                                ", 0, 0);
                break;
            case 3:
                F_h00_35DC(35, 150, "      ONE SHARE PURCHASED       ", 1, 15);
                F_h00_57D2(62);
                break;
            case 2:
                F_h00_35DC(35, 150, "         ONE SHARE SOLD         ", 1, 15);
                F_h00_57D2(63);
                break;
            case 4:
                F_h00_35DC(35, 150, "        NO SHARES TO SELL       ", 1, 9);
                break;
            case 5:
                F_h00_35DC(35, 150, "COMPANY BANKRUPT, NO MORE SHARES", 1, 9);
                break;
            case 6:
                F_h00_35DC(35, 150, "       SHARE LIMIT REACHED      ", 1, 9);
                break;
            default:
                break;
            }
            F_h00_307C();
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            s64 = 0;
        }
    }
    F_h00_3C0E(G_h01_6EA8);
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = G_h01_6EAC;
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    return s58 - 1;
}

struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern char G_h01_46E1;

F_h07_0E06(p)
struct Header *p;
{
    int unused1;
    int unused2;

    p->first = 8;
    p->second = 175;
    F_h00_34E0(p);
    if (G_h01_46E1 < 10)
        F_h00_09C0(18, 182, (long)G_h01_46E1, 7, 1, 0);
    else
        F_h00_09C0(14, 182, (long)G_h01_46E1, 7, 1, 0);
}

struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern long G_h01_46E6;

F_h07_0E7C(p)
struct Header *p;
{
    p->first = 40;
    p->second = 172;
    F_h00_34E0(p);
    F_h00_09C0(176, 175, G_h01_46E6, 1, 9, 1);
}

struct Record { int amount; char reserved[4]; int category; char rest[38]; };
extern struct Record G_h01_4D82[16];
extern unsigned char G_h01_5014[16][31];
extern char G_h01_46E1;
F_h07_0EC0(n) int n;
{
    int result, amount, percent;
    amount = G_h01_4D82[n].amount;
    percent = G_h01_5014[G_h01_4D82[n].category][G_h01_46E1-1];
    result = amount * percent / 100;
    if (result <= 0 && percent > 0) result = 1;
    return result;
}

extern long G_h01_46CA;
extern char *G_h01_5370;
extern int F_h00_8AA8();
extern int F_h00_8B4C();
extern int F_h00_8B88();

F_h07_0F30(arg)
int arg;
{
    *G_h01_5370 = 12;
    switch (arg) {
    case 0xc0:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 25), 0xaeL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 25), 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 25), 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 25), 0xc2L);
        break;
    case 0xe0:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        break;
    case 0x100:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        break;
    case 0x120:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xacL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xacL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc5L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc5L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xacL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc5L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 24), 0xacL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc5L);
        break;
    default:
        break;
    }
}

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

struct Input {
    char pad[2];
    long text;
};

extern struct Record G_h01_4D82[16];
extern int G_h01_1466;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern long G_h01_6EAC;
extern struct Input *G_h01_6EA8;
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_4376();
extern int F_h00_86A8();
extern int F_h00_3C0E();
extern int F_h00_868C();
extern int F_h00_35DC();
extern int F_h00_7A96();
extern int F_h07_1F6E();
extern int F_h07_18F8();
char *F_h07_2050();

F_h07_1424(x, y)
long x;
long y;
{
    long l1;
    int i1;
    int i;
    char *q;
    char *p;
    char buf1[32];
    char buf2[40];
    int r;

    for (i = 0; i < 15; i++) {
        if (G_h01_4D82[i].state == 0)
            continue;
        G_h01_6EAC = G_h01_46DA;
        F_h00_0FDE(1);
        G_h01_46DA = F_h00_86DC("DT1:invest.arc", 1005L);
        F_h00_2816(G_h01_46DA);
        G_h01_6EA8 = 0;
        G_h01_6EA8 = F_h00_291E(i, G_h01_6EA8);
        switch (G_h01_4D82[i].state) {
        case 1:
            F_h07_1F6E(i, x, y);
            F_h07_18F8(i, 2, 32, 35);
            buf1[0] = 0;
            p = F_h07_2050((long)G_h01_4D82[i].f12);
            F_h00_7A96(buf1, "STOCK IS UP BY ");
            F_h00_7A96(buf1, p);
            F_h00_7A96(buf1, "%");
            F_h00_35DC(80, 100, buf1, 14, 0);
            G_h01_4D82[i].state = 5;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = F_h00_4376();
                F_h00_86A8(5L);
            } while ((r & 0x80) == 0);
            break;
        case 2:
            F_h07_1F6E(i, x, y);
            F_h07_18F8(i, 3, 32, 35);
            buf1[0] = 0;
            p = F_h07_2050((long)G_h01_4D82[i].f12);
            F_h00_7A96(buf1, "STOCK IS DOWN BY ");
            F_h00_7A96(buf1, p);
            F_h00_7A96(buf1, "%");
            F_h00_35DC(80, 100, buf1, 14, 0);
            G_h01_4D82[i].state = 5;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = F_h00_4376();
                F_h00_86A8(5L);
            } while ((r & 0x80) == 0);
            break;
        case 3:
            F_h07_1F6E(i, x, y);
            F_h07_18F8(i, 2, 32, 35);
            F_h00_35DC(48, 100, "MAJOR PRICE CHANGE EXPECTED", 14, 0);
            buf2[0] = 0;
            q = F_h07_2050((long)G_h01_4D82[i].f10);
            F_h00_7A96(buf2, "ON OR AROUND DAY ");
            F_h00_7A96(buf2, q);
            F_h00_35DC(56, 110, buf2, 14, 0);
            G_h01_4D82[i].state = 0x83;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = F_h00_4376();
                F_h00_86A8(5L);
            } while ((r & 0x80) == 0);
            break;
        case 4:
            F_h07_1F6E(i, x, y);
            F_h07_18F8(i, 3, 32, 35);
            F_h00_35DC(48, 100, "MAJOR PRICE CHANGE EXPECTED", 14, 0);
            buf2[0] = 0;
            q = F_h07_2050((long)G_h01_4D82[i].f10);
            F_h00_7A96(buf2, "ON OR AROUND DAY ");
            F_h00_7A96(buf2, q);
            F_h00_35DC(56, 110, buf2, 14, 0);
            G_h01_4D82[i].state = 0x84;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = F_h00_4376();
                F_h00_86A8(5L);
            } while ((r & 0x80) == 0);
            break;
        default:
            break;
        }
        F_h00_3C0E(G_h01_6EA8);
        F_h00_868C(G_h01_46DA);
        G_h01_46DA = G_h01_6EAC;
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
    }
}

struct Input {
    char pad[2];
    long text;
};

extern struct Input *G_h01_6EA8;
extern long F_h00_0976();
extern int F_h00_35DC();

F_h07_18F8(unused, mode, x, y)
int unused;
int mode;
int x;
int y;
{
    int i;
    int limit;
    long unused_local;
    char data[60];
    long text;

    for (i = 0; i < 60; i++)
        data[i] = 0;
    text = G_h01_6EA8->text;
    text = F_h00_0976(text, data);
    text = F_h00_0976(text, data);
    if (mode == 1)
        limit = 6;
    else if (mode == 2) {
        for (i = 0; i < 6; i++)
            text = F_h00_0976(text, data);
        limit = 2;
    } else if (mode == 3) {
        for (i = 0; i < 8; i++)
            text = F_h00_0976(text, data);
        limit = 2;
    }
    for (i = 0; i < limit; i++) {
        text = F_h00_0976(text, data);
        F_h00_35DC(x, y, data, 1, 0);
        y += 10;
    }
}

extern int G_h01_4D8A;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h00_35DC();
extern int F_h00_7A96();
extern int F_h07_0E7C();
extern int F_h07_0E06();
char *F_h07_2050();

F_h07_1F6E(idx, x, y)
int idx;
long x;
long y;
{
    char buf[34];
    char *p;

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h07_0E7C(y);
    F_h07_0E06(x);
    F_h00_35DC(96, 8, "NEWS INFORMATION", 1, 15);
    buf[0] = 0;
    p = F_h07_2050((long)*(int *)((char *)&G_h01_4D8A + (long)idx * 46));
    F_h00_7A96(buf, "NEWS BULLETIN FROM DAY ");
    F_h00_7A96(buf, p);
    F_h00_35DC(56, 23, buf, 14, 0);
}

extern char G_h01_33E3[10];
extern char G_h01_33ED;

char *F_h07_2050(n)
long n;
{
    int i;

    G_h01_33ED = 0;
    i = 10;
    do {
        G_h01_33E3[--i] = n % 10 + '0';
    } while ((n = n / 10) > 0);
    return G_h01_33E3 + i;
}

