struct BoardCell {
    char pad;
    unsigned char bits;
};

extern int F_h00_34E0();
extern int G_h01_0054;
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
extern unsigned int G_h01_79A8;

recovered(p)
struct BoardCell *p;
{
    int x,y,shift;

    shift=3;
    F_h00_34E0(&G_h01_0054);
    if (G_h01_014A) {
        x=56-((G_h01_799E&248)>>3)+(G_h01_799E&7);
        y=(G_h01_799E>>3)+(G_h01_799E&7);
        if ((((unsigned short *)(p-1))[0]&64)==64 &&
            (G_h01_799E&7) && (p->bits&1))
            *G_h01_5370=12;
        else if ((((unsigned short *)(p+1))[0]&64)==64 &&
                 (G_h01_799E&7)!=7 && (p->bits&2))
            *G_h01_5370=12;
        else if ((((unsigned short *)(p-8))[0]&64)==64 &&
                 G_h01_799E>7 && (p->bits&8))
            *G_h01_5370=12;
        else if ((((unsigned short *)(p+8))[0]&64)==64 &&
                 G_h01_799E<56 && (p->bits&4))
            *G_h01_5370=12;
        else
            *G_h01_5370=3;
        F_h10_1FDE(x*4+115,y*4+139,p+G_h01_799E,1);
        F_h00_8A46(G_h01_46D2,(long)G_h01_7746,(long)G_h01_7748,
            &G_h01_774E,0L,0L,(long)(G_h01_774A<<shift),(long)G_h01_774C,
            192L,255L,0L);
    }
    x=56-((G_h01_799E&248)>>3)+(G_h01_799E&7);
    y=(G_h01_799E>>3)+(G_h01_799E&7);
    *G_h01_5370=22;
    F_h10_1FDE(x*4+115,y*4+139,p+G_h01_799E,1);
    if (G_h01_014A!=2) {
        x=56-((G_h01_79A0&248)>>3)+(G_h01_79A0&7);
        y=(G_h01_79A0>>3)+(G_h01_79A0&7);
        *G_h01_5370=14;
        F_h10_1FDE(x*4+115,y*4+139,p+G_h01_79A0,1);
    }
    x=56-((G_h01_79A8&248)>>3)+(G_h01_79A8&7);
    y=(G_h01_79A8>>3)+(G_h01_79A8&7);
    *G_h01_5370=8;
    F_h10_1FDE(x*4+115,y*4+139,p+G_h01_79A8,0);
}