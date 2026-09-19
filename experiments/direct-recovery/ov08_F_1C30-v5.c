extern long G_h01_10EE;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_6EB0;
extern int G_h01_349A;
extern int G_h01_349C;
extern char G_h01_34CE;
extern int F_h00_8A46();
extern int F_h00_34E0();

recovered(a)
int a;
{
    int block, digit, y, x;
    char *p;

    x=160;
    y=(a%5)*40;
    block=0;
    do {
        F_h00_8A46(G_h01_10EE,0L,(long)y,G_h01_46D2,
            0L,0L,320L,40L,192L,255L,0L);
        if (a+block<25) {
            p=(char *)(G_h01_6EB0+((long)(a+block))*21);
            G_h01_349A=0;
            digit=0;
            do {
                if (*p!='F') {
                    G_h01_34CE=*p-'0';
                    G_h01_349C=0;
                    F_h00_34E0(&G_h01_349A);
                }
                ++p;
                G_h01_349A+=16;
            } while (++digit<20);
        }
        F_h00_8A46(G_h01_46D2,0L,0L,G_h01_46CE,
            0L,(long)x,320L,40L,192L,255L,0L);
        x-=40;
        y+=40;
        if (y>160)
            y=0;
    } while (++block<5);
}