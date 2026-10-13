extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int F_h11_5FB2();
extern int F_h11_405A();
extern int F_h11_4B0C();
extern int F_h11_415A();
extern int F_h11_40E0();

recovered()
{
    if (G_h01_94B4) {
        F_h11_5FB2(G_h01_94D6, &G_h01_94C0);
    } else if (G_h01_94B6) {
        if (F_h11_405A(G_h01_94D4)) {
            G_h01_94AE = 2;
            F_h11_4B0C(2);
            G_h01_94B6 = 0;
        } else {
            F_h11_415A(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            F_h11_40E0(G_h01_94D4, 10);
        }
    }
}
