struct Point { char reserved[36]; unsigned int value; };
struct PointRef { struct Point *point; char reserved[8]; };

extern struct PointRef G_h01_4524[36];
extern unsigned char G_h01_46C8;
extern int F_h00_0FDE();
extern int F_h00_033E();
extern int F_h00_7978();
extern int F_h00_7522();
extern int F_h08_0000();
extern int F_h09_0000();
extern int F_h10_0000();
extern int F_h11_0000();

recovered(arg)
int arg;
{
    int result = 0;
    int unused;

    F_h00_0FDE(1);
    switch (G_h01_4524[arg].point->value & 0x000f) {
    case 1:
        F_h00_7978(F_h11_0000);
        F_h00_033E(1);
        G_h01_46C8 |= 1;
        result = F_h11_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h11_0000);
        break;
    case 2:
        F_h00_7978(F_h08_0000);
        F_h00_033E(2);
        G_h01_46C8 |= 2;
        result = F_h08_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h08_0000);
        break;
    case 8:
        F_h00_7978(F_h10_0000);
        F_h00_033E(4);
        G_h01_46C8 |= 4;
        result = F_h10_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h10_0000);
        break;
    case 4:
        F_h00_7978(F_h09_0000);
        F_h00_033E(8);
        G_h01_46C8 |= 8;
        result = F_h09_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h09_0000);
        break;
    default:
        break;
    }
    return result;
}
extern char G_h01_2C2C;
extern long G_h01_2C26;
extern long G_h01_2A16;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_1526;
extern char G_h01_0668;
extern char G_h01_068B;
extern char G_h01_06A6;
extern char G_h01_06BF;
extern char G_h01_06DB;
extern int F_h00_330E();
extern int F_h00_8BC8();
extern int F_h00_307C();
extern int F_h00_0FDE();
extern long F_h00_291E();
extern int F_h00_57D2();
extern int F_h00_4EC6();
extern int F_h00_4D04();
extern int F_h00_35DC();
extern int F_h00_31AA();
extern int F_h00_134C();
extern int F_h00_8A46();
extern int F_h00_04FE();

F_h00_033E(arg)
int arg;
{
    G_h01_2C2C = 0;
    G_h01_2C26 = 0;
    F_h00_330E();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_0FDE(1);
    F_h00_291E(0x1f, G_h01_46CE);
    F_h00_57D2(0x21);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(0x19);
    F_h00_57D2(0);
    F_h00_330E();
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_35DC(0x18, 0xc, &G_h01_0668, 0, 0);
    switch (arg) {
    case 1:
        F_h00_35DC(0x18, 0x18, &G_h01_06A6, 0, 0);
        F_h00_04FE(1);
        break;
    case 2:
        F_h00_35DC(0x18, 0x18, &G_h01_068B, 0, 0);
        F_h00_04FE(0);
        break;
    case 4:
        F_h00_35DC(0x18, 0x18, &G_h01_06DB, 0, 0);
        F_h00_04FE(3);
        break;
    case 8:
        F_h00_35DC(0x18, 0x18, &G_h01_06BF, 0, 0);
        F_h00_04FE(2);
        break;
    }
    F_h00_307C();
    G_h01_46D6 = &G_h01_1526;
    F_h00_31AA(&G_h01_1526);
    G_h01_2C26 = 4;
    G_h01_2C2C = 15;
    F_h00_57D2(0x71);
    while (G_h01_2A16 != 0)
        ;
    F_h00_4EC6();
    F_h00_134C(0x1e);
}

/* Candidate for resident_F_04FE: structure follows the ov04_F_0104 sibling. */
extern long G_h01_46DA;
extern unsigned int F_h00_463E();
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_35DC();
extern int F_h00_3C0E();
extern int F_h00_868C();

F_h00_04FE(a)
int a;
{
    long saved;
    long found;
    char buf[61];
    long state;
    unsigned int i;

    i = F_h00_463E() & 3;
    a = a * 4 + i;
    saved = G_h01_46DA;
    F_h00_0FDE(2);
    G_h01_46DA = F_h00_86DC("DT2:clues.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    found = 0;
    found = F_h00_291E(a, found);
    state = *(long *)((char *)found + 2);
    for (i = 0; i <= 61; i++)
        buf[i] = 0;
    state = F_h00_0976(state, buf);
    F_h00_35DC(20, 40, buf, 7, 0);
    state = F_h00_0976(state, buf);
    F_h00_35DC(20, 52, buf, 7, 0);
    state = F_h00_0976(state, buf);
    F_h00_35DC(20, 64, buf, 7, 0);
    F_h00_3C0E(found);
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

