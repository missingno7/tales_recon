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

recovered(x, y)
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

