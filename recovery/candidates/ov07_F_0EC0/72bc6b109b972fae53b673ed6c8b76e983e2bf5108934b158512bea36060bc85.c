#define G_h01_46E1 ((short*)0x46E1)
#define G_h01_4D82 ((short*)0x4D82)
#define G_h01_4D88 ((short*)0x4D88)
#define G_h01_5014 ((char*)0x5014)
long recovered(a, b) short a, b; {
    short *p;
    short d;
    long c;
    p = (short*)((char*)G_h01_46E1 - 0x327c);
    d = p[a * 0x2e];
    p = (short*)((char*)G_h01_4D82 - 0x3276);
    c = p[b * 0x2e] * 0x1f;
    c += (long)(unsigned char)G_h01_5014[0x391d];
    c -= 1L;
    c += d;
    p = (short*)((char*)G_h01_4D88 - 0x2fea);
    d = p[c];
    if (d < 0) {
        d = 0;
    }
    if (d > 0) {
        d = 1;
    }
    return (long)d;
}
