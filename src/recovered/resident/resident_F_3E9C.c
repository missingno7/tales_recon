extern long Read();
extern unsigned short G_h01_1E26[1];
extern unsigned short G_h01_1E2E;
extern unsigned short G_h01_A9C2;
extern unsigned short G_h01_A9C4;
extern unsigned short G_h01_A9C6;
extern unsigned short G_h01_A9C8;
extern unsigned char G_h01_A9CA[1];
extern unsigned char G_h01_A9CB;
extern unsigned char G_h01_A9CC[1];
extern unsigned char G_h01_A9CD;
extern long G_h01_ADCA;
extern unsigned short G_h01_B1DA;

recovered()
{
    unsigned long bits;

    G_h01_A9C2 = G_h01_1E2E >> 3;
    G_h01_A9C8 = G_h01_1E2E & 7;
    G_h01_1E2E += G_h01_B1DA;
    if (G_h01_A9C2 >= 0x3fd) {
        G_h01_1E2E = G_h01_A9C8 + G_h01_B1DA;
        G_h01_A9C6 = 0x400 - G_h01_A9C2;
        G_h01_A9CA[0] = G_h01_A9CA[G_h01_A9C2];
        G_h01_A9CB = G_h01_A9CA[G_h01_A9C2 + 1];
        G_h01_A9CC[0] = G_h01_A9CA[G_h01_A9C2 + 2];
        G_h01_A9CD = G_h01_A9CA[G_h01_A9C2 + 3];
        Read(G_h01_ADCA, G_h01_A9CA + G_h01_A9C6, (unsigned long)G_h01_A9C2);
        G_h01_A9C2 = 0;
    }
    G_h01_A9C4 = G_h01_A9CA[G_h01_A9C2 + 1];
    G_h01_A9C4 <<= 8;
    G_h01_A9C4 += G_h01_A9CA[G_h01_A9C2];
    G_h01_A9C2 = G_h01_A9CC[G_h01_A9C2];
    bits = (((unsigned long)G_h01_A9C2 << 16) + G_h01_A9C4) >> G_h01_A9C8;
    return G_h01_1E26[(unsigned short)(G_h01_B1DA - 9)] & (unsigned short)bits;
}
