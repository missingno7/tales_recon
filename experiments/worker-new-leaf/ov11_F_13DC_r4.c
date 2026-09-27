extern char *G_h01_94CE;
extern char *G_h01_9F4E;
extern char *G_h01_9F56;
extern char *G_h01_9F52;
extern char *G_h01_9F8E;
extern int G_h01_94C4;
extern int G_h01_94C2;
extern int F_h11_4696();
extern int F_h11_583A();

recovered()
{
    if (G_h01_94CE == G_h01_9F4E || G_h01_94CE == G_h01_9F56) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 40, 33, 22);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 40, 33, 10);
    } else if (G_h01_94CE == G_h01_9F52) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 48, 41, 22);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 48, 41, 10);
    } else if (G_h01_94CE == G_h01_9F8E) {
        F_h11_4696(G_h01_94C2, G_h01_94C4, 88, 34, 22);
        F_h11_583A(G_h01_94C2, G_h01_94C4, 88, 34, 10);
    }
}
