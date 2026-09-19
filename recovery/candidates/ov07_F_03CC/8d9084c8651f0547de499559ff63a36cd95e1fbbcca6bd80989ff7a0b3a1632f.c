/* Non-promoting ownership probe for ov07_F_03CC. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h07_0E06();
extern int F_h07_0E7C();
extern int F_h00_35DC();
extern char G_h01_4C32;
extern char G_h01_4C9E;

recovered()
{
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h07_0E06(&G_h01_4C32);
    F_h07_0E7C(&G_h01_4C9E);
    F_h00_35DC(100, 8, "STOCK PORTFOLIO", 7, 15);
    F_h00_35DC(40, 22, "COMPANY NAME", 1, 7);
    F_h00_35DC(196, 22, "PRICE", 1, 7);
    F_h00_35DC(244, 22, "SHARES", 1, 7);
}
