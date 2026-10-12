struct resident_entry {
    unsigned short word0;
    unsigned char byte2;
    unsigned char byte3;
};

extern long F_h00_86F6();
extern int F_h00_3E9C();
extern int F_h00_4032();
extern unsigned short G_h01_1E2E;
extern unsigned short G_h01_B1D8;
extern unsigned short G_h01_B1DA;
extern unsigned short G_h01_B1DC;
extern unsigned short G_h01_B1E4;
extern unsigned short G_h01_B1E6;
extern long G_h01_B1E0;
extern long G_h01_ADCA;
extern long G_h01_544A;
extern char *G_h01_A9BE;
extern unsigned short G_h01_A9C2;
extern unsigned char G_h01_A9C3;
extern unsigned char G_h01_A9CA[1];
extern unsigned short G_h01_ADCE;
extern unsigned char G_h01_ADCF;
extern unsigned short G_h01_ADD0;
extern unsigned short G_h01_ADD2;
extern unsigned short G_h01_ADD4;
extern unsigned short G_h01_ADD6;
extern unsigned char G_h01_ADD8[1];
extern unsigned char G_h01_B1DE;

long recovered(p1, p2, p3, p4)
unsigned short p1;
long p2;
long p3;
unsigned short p4;
{
    G_h01_B1E6 = p4;
    G_h01_B1E4 = p1;
    G_h01_ADCA = p2;
    G_h01_B1E0 = p3;
    G_h01_A9BE = (char *)p3;
    G_h01_B1D8 = 0;
    G_h01_ADD4 = 0x102;
    G_h01_ADD6 = 0;
    G_h01_B1DA = 9;
    G_h01_B1DC = 0x200;
    G_h01_1E2E = 0;
    F_h00_86F6(G_h01_ADCA, G_h01_A9CA, (unsigned long)0x400);

    while ((G_h01_A9C2 = F_h00_3E9C()) != 0x101) {
        if (G_h01_A9C2 == 0x100) {
            G_h01_B1DA = 9;
            G_h01_B1DC = 0x200;
            G_h01_ADD4 = 0x102;
            G_h01_A9C2 = F_h00_3E9C();
            G_h01_ADD0 = G_h01_A9C2;
            G_h01_ADCE = G_h01_A9C2;
            G_h01_B1DE = G_h01_A9C3;
            F_h00_4032(G_h01_B1DE);
            continue;
        }
        G_h01_ADD2 = G_h01_A9C2;
        G_h01_ADCE = G_h01_A9C2;
        if (G_h01_A9C2 >= G_h01_ADD4) {
            G_h01_ADCE = G_h01_ADD0;
            G_h01_ADD8[G_h01_ADD6++] = G_h01_B1DE;
        }
        while (G_h01_ADCE > 0xff) {
            G_h01_ADD8[G_h01_ADD6++] = ((unsigned char *)(G_h01_544A + ((unsigned long)G_h01_ADCE << 2)))[2];
            G_h01_ADCE = ((struct resident_entry *)G_h01_544A)[G_h01_ADCE].word0;
        }
        G_h01_B1DE = G_h01_ADCF;
        G_h01_ADD8[G_h01_ADD6++] = G_h01_B1DE;
        while (G_h01_ADD6 != 0) {
            G_h01_ADD6--;
            F_h00_4032(G_h01_ADD8[G_h01_ADD6]);
        }
        ((unsigned char *)(G_h01_544A + ((unsigned long)G_h01_ADD4 << 2)))[2] = G_h01_B1DE;
        ((struct resident_entry *)G_h01_544A)[G_h01_ADD4].word0 = G_h01_ADD0;
        G_h01_ADD4++;
        G_h01_ADD0 = G_h01_ADD2;
        if (G_h01_ADD4 >= G_h01_B1DC && G_h01_B1DA < 0xc) {
            G_h01_B1DA++;
            G_h01_B1DC *= 2;
        }
    }
    return (long)G_h01_A9BE - G_h01_B1E0;
}
