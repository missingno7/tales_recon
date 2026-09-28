extern int G_h01_1708;
extern int G_h01_170A;
extern int G_h01_170C;
extern int G_h01_170E;
extern int G_h01_94AC;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B2;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94C2;
extern int G_h01_94C4;
extern int G_h01_94C6;
extern int G_h01_94C8;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int G_h01_94D8;
extern int F_h00_30F0();
extern int F_h11_5BC4();
extern int F_h11_4B0C();

recovered(flag)
int flag;
{
    int selector;
    if (flag)
        G_h01_94AC = 1;
    else
        G_h01_94AC++;

    selector = 3 - G_h01_94AC + 1;
    switch (selector) {
    case 3:
        G_h01_1708 = 0x62;
        G_h01_170A = 0x82;
        G_h01_170C = 0xb3;
        G_h01_170E = 0x4d8;
        break;
    case 2:
        G_h01_1708 = 5;
        G_h01_170A = 8;
        G_h01_170C = 0x11c;
        G_h01_170E = 0x44d;
        break;
    case 1:
        G_h01_1708 = 0x500;
        G_h01_170A = 0x800;
        G_h01_170C = 0xc00;
        G_h01_170E = 0xd44;
        break;
    }

    F_h00_30F0(0);
    G_h01_94AE = 5;
    G_h01_94B0 = 1;
    G_h01_94B2 = 0;
    G_h01_94B6 = 0;
    G_h01_94B4 = 0;
    G_h01_94D4 = 0;
    G_h01_94D6 = 0;
    G_h01_94D8 = 0;
    F_h11_5BC4(&G_h01_94BA, &G_h01_94BC);
    G_h01_94BE = G_h01_94BA * 53 + 8;
    G_h01_94C0 = (G_h01_94BC << 5) + 16;
    G_h01_94C2 = G_h01_94C6 = G_h01_94BE - (G_h01_94B0 ? 16 : 0);
    G_h01_94C8 = G_h01_94C0;
    G_h01_94C4 = G_h01_94C0;
    F_h11_4B0C(G_h01_94AE);
}




