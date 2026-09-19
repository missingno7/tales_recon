struct Flags {
    char pad;
    unsigned char bits;
};
extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8C10();

F_h10_1FDE(x,y,flags,active)
int x,y;
struct Flags *flags;
int active;
{
    char i,j;

    for (i=0;i<=2;++i)
        for (j=0;j<=2;++j) {
            F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
            F_h00_8C10(G_h01_46CA,(long)(x+j),(long)(y+i));
        }
    if (active) {
    *G_h01_5370=3;
    if (flags->bits&8) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x+3),(long)(y-1));
    }
    if (flags->bits&4) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x-1),(long)(y+3));
    }
    if (flags->bits&2) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x+3),(long)(y+3));
    }
    if (flags->bits&1) {
        F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
        F_h00_8C10(G_h01_46CA,(long)(x-1),(long)(y-1));
    }
    }
}

struct Cell {
    char pad;
    unsigned char bits;
};
extern char G_h01_014A;
extern char *G_h01_5370;
extern long G_h01_46D2;
extern int G_h01_7746;
extern int G_h01_7748;
extern int G_h01_774A;
extern int G_h01_774C;
extern char G_h01_774E;

extern int F_h00_8A46();

recovered(p)
struct Cell *p;
{
    unsigned i,x,y,shift;

    shift=3;
    i=0;
    do {
        x=((56-(i&248))>>3)+(i&7);
        y=(i>>3)+(i&7);
        if (!G_h01_014A || (p->bits&16)) {
            if ((((unsigned short *)(p-1))[0]&64)==64 &&
                (i&7) && (p->bits&1) ||
                (((unsigned short *)(p+1))[0]&64)==64 &&
                (i&7)!=7 && (p->bits&2) ||
                (((unsigned short *)(p-8))[0]&64)==64 &&
                i>7 && (p->bits&8) ||
                (((unsigned short *)(p+8))[0]&64)==64 &&
                i<56 && (p->bits&4))
                *G_h01_5370=12;
            else
                *G_h01_5370=3;
            F_h10_1FDE(x*4+115,y*4+139,p,1);
        }
        ++i;
        ++p;
    } while (i<64);
    F_h00_8A46(G_h01_46D2,(long)G_h01_774C,(long)G_h01_774A,
        &G_h01_774E,0L,0L,(long)(G_h01_7748<<shift),(long)G_h01_7746,
        192L,255L,0L);
}

