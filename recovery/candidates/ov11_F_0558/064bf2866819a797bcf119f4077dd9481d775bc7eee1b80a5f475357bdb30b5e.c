/* Direct reconstruction candidate for ov11_F_0558. */
extern int G_h01_8A42;
extern int G_h01_8A44;
extern int G_h01_8A48;
extern int G_h01_8A3E;
extern int G_h01_8A4A;
extern int G_h01_94BE;
extern int G_h01_94AE;
extern int G_h01_1300[16];

recovered()
{
    if (G_h01_8A42) {
        if (G_h01_8A48 == 1) {
            G_h01_8A3E += 8;
            if (G_h01_8A3E >= G_h01_8A4A) {
                G_h01_8A3E = G_h01_8A4A;
                G_h01_8A42 = 0;
                G_h01_8A44 = 1;
            }
        } else {
            G_h01_8A3E -= 8;
            if (G_h01_8A3E <= G_h01_8A4A) {
                G_h01_8A3E = G_h01_8A4A;
                G_h01_8A42 = 0;
                G_h01_8A44 = 1;
            }
        }
        return;
    }
    if (G_h01_94BE > G_h01_8A3E + 240 && G_h01_8A3E < 856) {
        G_h01_8A42 = 1;
        G_h01_8A4A = G_h01_1300[G_h01_94BE / 104 - 1];
        G_h01_8A48 = 1;
    } else if (G_h01_94BE < G_h01_8A3E + 72 && G_h01_94AE != 8 && G_h01_94AE != 6 && G_h01_8A3E > 0) {
        G_h01_8A42 = 1;
        G_h01_8A4A = G_h01_1300[G_h01_94BE / 104 - 1];
        G_h01_8A48 = 0;
    }
}
