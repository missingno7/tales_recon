extern long F_h00_4F62();
extern int F_h00_57D2();
extern int F_h00_0A44();
extern int F_h00_0D36();
extern unsigned char G_h01_1F14[32];
extern int G_h01_1F34;
extern char G_h01_1F36;
extern char G_h01_4704;
extern char G_h01_536E;
extern char G_h01_A7CC;
extern char G_h01_A7CD;
extern char G_h01_B1EA;
extern char G_h01_B1EB;
extern int G_h01_096E;

int recovered()
{
    unsigned int s;
    long p0;
    long p1;
    unsigned int c;
    int e;

    p0 = 0xdff00c;
    p1 = 0xbfe0fe;
    s = ((*(unsigned short *)p1 & 0x80) ^ 0x80) >> 3;
    s |= (*(unsigned short *)p0 & 0x2) << 2;
    s |= (*(unsigned short *)p0 & 0x200) >> 7;
    s |= ((*(unsigned short *)p0 & 0x1) << 1) ^ (*(unsigned short *)p0 & 0x2);
    s |= ((*(unsigned short *)p0 & 0x200) >> 9) ^ ((*(unsigned short *)p0 & 0x100) >> 8);
    e = G_h01_1F14[s];
    c = F_h00_4F62();
    switch (c & 0x7f) {
    case 27:
    case 113:
        G_h01_B1EA = 1;
        if (G_h01_A7CC == 0 && G_h01_A7CD == 0) {
            F_h00_0A44();
            e = 0;
        } else {
            e = 0x71;
        }
        break;
    case 13:
    case 32:
        e = G_h01_1F34;
        break;
    case 1:
        e = 6;
        G_h01_1F34 = 6;
        break;
    case 2:
    case 109:
        e = 5;
        G_h01_1F34 = 5;
        break;
    case 3:
        e = 4;
        G_h01_1F34 = 4;
        break;
    case 4:
    case 106:
        e = 7;
        G_h01_1F34 = 7;
        break;
    case 5:
        e = 0;
        G_h01_1F34 = 0;
        break;
    case 6:
    case 107:
        e = 3;
        G_h01_1F34 = 3;
        break;
    case 7:
        e = 8;
        G_h01_1F34 = 8;
        break;
    case 8:
    case 105:
        e = 1;
        G_h01_1F34 = 1;
        break;
    case 9:
        e = 2;
        G_h01_1F34 = 2;
        break;
    case 112:
        if (G_h01_A7CD == 0 && G_h01_A7CC == 0) {
            F_h00_0D36();
            e = 0;
        } else {
            e = 0x70;
        }
        break;
    case 115:
        if (G_h01_096E == 0) {
            G_h01_096E = 1;
            F_h00_57D2(0x7f);
        } else {
            G_h01_096E = 0;
            F_h00_57D2(0x7e);
        }
        break;
    case 78:
    case 89:
    case 110:
    case 121:
        e = c;
        break;
    default:
        G_h01_1F34 = 0;
        break;
    }
    if (G_h01_1F36 == 0)
        G_h01_1F34 = 0;
    if (G_h01_B1EB)
        e |= 0x80;
    if (G_h01_4704 && (e & 0x80))
        G_h01_536E = 1;
    return e;
}
