/* Non-promoting ownership probe for ov07_F_03CC. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h07_0E06();
extern int F_h07_0E7C();
extern int F_h00_35DC();
extern char G_h01_3232;
extern char G_h01_329E;

recovered()
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

