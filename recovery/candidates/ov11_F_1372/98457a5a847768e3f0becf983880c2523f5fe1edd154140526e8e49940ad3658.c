/* Direct reconstruction candidate for ov11_F_1372. */
struct Target { int x; int y; };
extern int G_h01_94C2;
extern int G_h01_94C4;
extern int G_h01_94C6;
extern int G_h01_94C8;
extern long G_h01_94CA;
extern long G_h01_94CE;
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Target *G_h01_94DA;
extern int G_h01_94AE;
extern int G_h01_8A3E;
extern int F_h00_34E0();

recovered()
{
    int shift;

    G_h01_94C2 = G_h01_94C6;
    G_h01_94C4 = G_h01_94C8;
    G_h01_94CE = G_h01_94CA;
    if (G_h01_94B0)
        shift = 16;
    else
        shift = 0;
    G_h01_94C6 = G_h01_94BE - shift;
    G_h01_94C8 = G_h01_94C0;
    G_h01_94CA = G_h01_94DA;
    G_h01_94DA->x = G_h01_94C6 - G_h01_8A3E;
    G_h01_94DA->y = G_h01_94C0 + 1;
    if (G_h01_94AE != 45)
        F_h00_34E0(G_h01_94DA);
}
