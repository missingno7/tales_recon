/* Candidate v1 for resident_F_435E: discard the callee result, then clear the
   word global and the byte global in source order. */
extern int G_h01_1F34;
extern char G_h01_B1EB;
extern long F_h00_4F62();

recovered()
{
    F_h00_4F62();
    G_h01_1F34 = 0;
    G_h01_B1EB = 0;
}

extern int G_h01_B28C;
extern int G_h01_B28E;
extern char G_h01_B1EB;
extern char G_h01_B291[1];
extern char G_h01_1EA4[1];

long F_h00_4F62()
{
    char c;
    long l;
    long p;

    p = 0xbfe0fe;
    if (G_h01_B28E == G_h01_B28C)
        return 0;
    while (G_h01_B28E != G_h01_B28C) {
        c = G_h01_B291[G_h01_B28E++];
        if (c == 'D' || c == '@' || c == 'C')
            G_h01_B1EB = 1;
        else if (c == (char)0xC4 || c == (char)0xC0 || c == (char)0xC3)
            G_h01_B1EB = 0;
        G_h01_B28E &= 0x7f;
    }
    c &= 0xff;
    c = (c < 0x70 && c > 0) ? G_h01_1EA4[c] : -1;
    return c;
}

