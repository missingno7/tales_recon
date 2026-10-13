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
