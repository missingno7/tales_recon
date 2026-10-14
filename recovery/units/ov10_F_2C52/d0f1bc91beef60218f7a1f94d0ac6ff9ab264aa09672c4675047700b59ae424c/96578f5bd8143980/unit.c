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
extern char G_h01_46E0;
extern char *G_h01_5370;
extern long G_h01_46D2;
extern int G_h01_7746;
extern int G_h01_7748;
extern int G_h01_774A;
extern int G_h01_774C;
extern char G_h01_774E;
extern int F_h10_1FDE();
extern int F_h00_8A46();

F_h10_2160(p)
struct Cell *p;
{
    unsigned i,x,y;
    int shift;

    shift=3;
    i=0;
    do {
        x=((56-(i&248))>>3)+(i&7);
        y=(i>>3)+(i&7);
        if (!G_h01_46E0 || (p->bits&16)) {
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
    F_h00_8A46(G_h01_46D2,(long)G_h01_7746,(long)G_h01_7748,
        &G_h01_774E,0L,0L,(long)(G_h01_774A<<shift),(long)G_h01_774C,
        192L,255L,0L);
}

struct BoardCell {
    char pad;
    unsigned char bits;
};

extern int F_h00_34E0();
extern int G_h01_7746;
extern char G_h01_46E0;
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A8;
extern unsigned int G_h01_79A0;

F_h10_22E6(p)
struct BoardCell *p;
{
    int unused;
    unsigned x,y;
    int shift;

    shift=3;
    F_h00_34E0(&G_h01_7746);
    if (G_h01_46E0) {
        x=((56-(G_h01_799E&248))>>3)+(G_h01_799E&7);
        y=(G_h01_799E>>3)+(G_h01_799E&7);
        if ((((unsigned short *)(p-1))[0]&64)==64 &&
            (G_h01_799E&7) && (p->bits&1) ||
            (((unsigned short *)(p+1))[0]&64)==64 &&
            (G_h01_799E&7)!=7 && (p->bits&2) ||
            (((unsigned short *)(p-8))[0]&64)==64 &&
            G_h01_799E>7 && (p->bits&8) ||
            (((unsigned short *)(p+8))[0]&64)==64 &&
            G_h01_799E<56 && (p->bits&4))
            *G_h01_5370=12;
        else
            *G_h01_5370=3;
        F_h10_1FDE(x*4+115,y*4+139,p+G_h01_799E,1);
        F_h00_8A46(G_h01_46D2,(long)G_h01_7746,(long)G_h01_7748,
            &G_h01_774E,0L,0L,(long)(G_h01_774A<<shift),(long)G_h01_774C,
            192L,255L,0L);
    }
    x=((56-(G_h01_799E&248))>>3)+(G_h01_799E&7);
    y=(G_h01_799E>>3)+(G_h01_799E&7);
    *G_h01_5370=22;
    F_h10_1FDE(x*4+115,y*4+139,p+G_h01_799E,1);
    if (G_h01_46E0!=2) {
        x=((56-(G_h01_79A8&248))>>3)+(G_h01_79A8&7);
        y=(G_h01_79A8>>3)+(G_h01_79A8&7);
        *G_h01_5370=14;
        F_h10_1FDE(x*4+115,y*4+139,p+G_h01_79A8,1);
    }
    x=((56-(G_h01_79A0&248))>>3)+(G_h01_79A0&7);
    y=(G_h01_79A0>>3)+(G_h01_79A0&7);
    *G_h01_5370=8;
    F_h10_1FDE(x*4+115,y*4+139,p+G_h01_79A0,0);
}

/* Direct reconstruction candidate for ov10_F_25A2. */
struct Flags { char pad; char bits; };
extern char G_h01_79AA;
extern char G_h01_79B4;
extern int G_h01_734C;
extern int G_h01_734E;
extern char G_h01_7354;
extern int G_h01_7382;
extern int G_h01_7384;
extern char G_h01_738A;
extern int G_h01_73B8;
extern int G_h01_73BA;
extern char G_h01_73C0;
extern int G_h01_73EE;
extern int G_h01_73F0;
extern char G_h01_73F6;
extern int F_h00_3AE4();

F_h10_25A2(flags)
struct Flags *flags;
{
    if (!G_h01_79AA && G_h01_79B4) {
        G_h01_79B4 = 0;
        if (flags->bits & 1) F_h00_3AE4(&G_h01_7354, G_h01_734C, G_h01_734E);
        if (flags->bits & 4) F_h00_3AE4(&G_h01_738A, G_h01_7382, G_h01_7384);
        if (flags->bits & 2) F_h00_3AE4(&G_h01_73C0, G_h01_73B8, G_h01_73BA);
        if (flags->bits & 8) F_h00_3AE4(&G_h01_73F6, G_h01_73EE, G_h01_73F0);
    }
}

extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_30F0();
extern int F_h00_34E0();
extern unsigned int F_h00_463E();
extern int F_h00_8A46();
extern int F_h00_8A68();
extern int F_h10_22E6();
extern short G_h01_060A[1];
extern short G_h01_0626[1];
extern short G_h01_0636[1];
extern short G_h01_0646[1];
extern short G_h01_0656[1];
extern char G_h01_4356[1];
extern char *G_h01_5392;
extern short G_h01_726C;
extern short G_h01_726E;
extern short G_h01_72A2;
extern short G_h01_72A4;
extern char G_h01_72D6;
extern short G_h01_72D8;
extern short G_h01_72DA;
extern char G_h01_730C;
extern char G_h01_741C[1];
extern char G_h01_7452[1];
extern char G_h01_74F4[1];
extern long G_h01_7998;
extern char G_h01_79A2;
extern char G_h01_79A3;
extern char G_h01_79A4;
extern char G_h01_79A6;
extern char G_h01_72A0;
extern short G_h01_79AE;
extern short G_h01_79B0;
extern short G_h01_79B2;

void F_h10_2634(obj, kind, frame)
short *obj;
int kind, frame;
{
    short *shape;
    int frame_index, x, y, width, height;

    if (kind == 17) {
        obj[0] = 0x52;
        obj[1] = 0x26;
        if (G_h01_79A6 == 2) {
            obj[0] = 0x53;
            obj[1] = 0x2f;
        }
        if (frame == 6) {
            obj[0] = 0x55;
            obj[1] = 0x30;
        }
        shape = G_h01_060A;
        x = obj[0] - 0x1e;
        y = obj[1] - 0x1e;
        width = 0xb4;
        height = 0xa0;
    } else if (kind == 10) {
        shape = G_h01_0626;
        x = obj[0] - 0x20;
        y = obj[1] - 0x26;
        width = 0xb4;
        height = 0x9e;
    } else if (kind == 11) {
        shape = G_h01_0636;
        x = obj[0];
        y = obj[1] - 0x26;
        width = 0xb4;
        height = 0xb4;
    } else if (kind == 13) {
        shape = G_h01_0656;
        x = obj[0];
        y = obj[1] - 0x28;
        width = 0xb4;
        height = 0xaa;
    } else {
        shape = G_h01_0646;
        x = obj[0] - 0x28;
        y = obj[1] - 0x12;
        width = 0xbe;
        height = 0x9e;
    }

    if (x < 0)
        x = 0;
    else if (x > 0x140)
        x = 0x140;
    if (y < 0)
        y = 0;
    else if (y > 0xc8)
        y = 0xc8;

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);

    frame_index = frame;
    F_h00_8A68(G_h01_7998, 0L, 0L, G_h01_46CA,
               (long)(shape[frame_index * 2] + obj[0] - 0x48),
               (long)(shape[frame_index * 2 + 1] + obj[1] - 0x40),
               0x90L, 0x87L, 0xeeL);

    if (G_h01_79B2 == 0) {
        switch (G_h01_79A2) {
        case 0:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x832;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xb20;
            break;
        case 1:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x842;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xb30;
            break;
        case 2:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x943;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xa30;
            break;
        case 3:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x843;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xa20;
            break;
        }
        F_h00_30F0();
    }

    if ((kind == 17 && frame_index != 5 && frame_index != 6) || kind == 11)
        F_h00_34E0(obj);

    if (G_h01_79A4 < (G_h01_79AE >> 1)) {
        G_h01_72A0 = G_h01_79A2;
        G_h01_726C = shape[frame_index * 2] + obj[0] - 0x0f;
        G_h01_726E = shape[frame_index * 2 + 1] + obj[1] - 0x40;
        if (G_h01_79A6 == 2) {
            G_h01_726C = shape[frame_index * 2] + 0x43;
            G_h01_726E = shape[frame_index * 2 + 1] - 0x1a;
        }
        F_h00_34E0(&G_h01_726C);
    } else if (G_h01_79A4 < G_h01_79AE - G_h01_79B0) {
        G_h01_72D6 = G_h01_79A2;
        G_h01_72A2 = shape[frame_index * 2] + obj[0] - 0x0b;
        G_h01_72A4 = shape[frame_index * 2 + 1] + obj[1] - 0x33;
        if (G_h01_79A6 == 2) {
            G_h01_72A2 = shape[frame_index * 2] + 0x47;
            G_h01_72A4 = shape[frame_index * 2 + 1] - 0x0d;
        }
        F_h00_34E0(&G_h01_72A2);
    } else {
        G_h01_730C = G_h01_79A2;
        G_h01_72D8 = shape[frame_index * 2] + obj[0] - 6;
        G_h01_72DA = shape[frame_index * 2 + 1] + obj[1] - 0x2a;
        if (G_h01_79A6 == 2) {
            G_h01_72D8 = shape[frame_index * 2] + 0x4c;
            G_h01_72DA = shape[frame_index * 2 + 1] - 4;
        }
        F_h00_34E0(&G_h01_72D8);
    }

    if (kind != 11 && (kind != 17 || (kind == 17 && (frame_index == 5 || frame_index == 6))))
        F_h00_34E0(obj);
    F_h00_34E0(G_h01_74F4);
    F_h00_34E0(G_h01_7452);
    F_h00_34E0(G_h01_741C);

    if (kind == 17 && G_h01_79A6 == 0)
        F_h10_22E6(G_h01_4356);

    G_h01_79A2 = F_h00_463E() & 3;
    if (G_h01_79A3 == G_h01_79A2) {
        G_h01_79A2++;
        if (G_h01_79A2 > 3)
            G_h01_79A2 = 0;
    }
    G_h01_79A3 = G_h01_79A2;
}
extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
F_h10_2B8A() { int d; d=(G_h01_799E&7)-(G_h01_79A0&7); return d; }

extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
F_h10_2BAC() { int d; d=(G_h01_799E>>3)-(G_h01_79A0>>3); return d; }

#define ABS(x) ((x) < 0 ? -(x) : (x))
F_h10_2BCA(a,b) int a,b;
{
    int rows, columns;
    rows = ABS((a >> 3) - (b >> 3));
    columns = ABS((a & 7) - (b & 7));
    return rows + columns;
}

extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
extern int G_h01_4356[1];
extern char G_h01_73E6[1];
extern char G_h01_7344[1];
extern char G_h01_73B0[1];
extern char G_h01_737A[1];
extern int F_h10_2634();
recovered() {
 if (G_h01_799E-8==G_h01_79A0 && ((char)G_h01_4356[G_h01_799E]&8))
  F_h10_2634(G_h01_73E6,17,5);
 else if (G_h01_799E-1==G_h01_79A0 && ((char)G_h01_4356[G_h01_799E]&1))
  F_h10_2634(G_h01_7344,17,2);
 else if (G_h01_799E-8==G_h01_79A0) F_h10_2634(G_h01_73B0,17,4);
 else F_h10_2634(G_h01_737A,17,3);
}

/* Direct recovery candidate for ov10_F_2CF4 (v2: inverted tail dispatch). */
struct Flags { char pad; char bits; };
extern char G_h01_79AA;
extern char G_h01_726A;
extern int G_h01_7236;
extern int G_h01_7238;
extern int G_h01_723E;
extern int G_h01_7240;
extern char G_h01_7246;
extern short G_h01_730E;
extern char G_h01_788A;
extern int G_h01_7962;
extern int G_h01_7964;
extern char G_h01_7972;
extern int G_h01_796A;
extern int G_h01_796C;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46E6;
extern short G_h01_0476;
extern short G_h01_04AA;
extern short G_h01_04DA;
extern short G_h01_050A;
extern short G_h01_053E;
extern short G_h01_0572;
extern short G_h01_059A;
extern short G_h01_05D6;
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3AE4();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h10_2634();

F_h10_2CF4(start, count, pairs, kind, flags)
int start, count;
short *pairs;
int kind;
struct Flags *flags;
{
    int i, frame;
    char draw;

    if (G_h01_79AA)
        return;
    draw = 0;
    frame = start;
    F_h00_0FDE(2);
    if (pairs == &G_h01_0476 || pairs == &G_h01_05D6) {
        draw = 1;
        F_h00_291E(24, &G_h01_7962);
        G_h01_7962 = 0;
        G_h01_7964 = 0;
    } else if (pairs == &G_h01_04DA || pairs == &G_h01_0572) {
        draw = 1;
        F_h00_291E(25, &G_h01_7962);
        G_h01_7962 = 240;
        G_h01_7964 = 0;
    }
    for (i = 0; i < count; i++, frame++) {
        if (frame > 3)
            frame = 0;
        G_h01_726A = frame;
        G_h01_7236 = pairs[2 * i];
        G_h01_7238 = pairs[2 * i + 1];
        F_h10_2634(&G_h01_7236, kind, frame);
        if (pairs == &G_h01_0476 || pairs == &G_h01_04DA ||
            pairs == &G_h01_053E || pairs == &G_h01_059A) {
            if (!(flags->bits & 0x10) && !(flags->bits & 0x40) && i < 8)
                F_h00_34E0(&G_h01_788A);
        }
        if (draw)
            F_h00_34E0(&G_h01_7962);
        F_h00_307C();
    }
    if (draw)
        F_h00_3AE4(&G_h01_7972, G_h01_796A, G_h01_796C);
    if (pairs != &G_h01_04AA && pairs != &G_h01_050A &&
        pairs != &G_h01_0572 && pairs != &G_h01_05D6) {
        if (!(flags->bits & 0x10) && !(flags->bits & 0x40)) {
            G_h01_46E6 += 50;
            F_h00_57D2(32);
        }
        for (i = 0; i < 4; i++) {
            F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
                0L, 0L, 320L, 200L, 192L, 255L, 0L);
            F_h10_2634(&G_h01_730E, 17, 0);
            if (!(flags->bits & 0x10) && !(flags->bits & 0x40))
                F_h00_35DC(132, 128, "$50", 14, 0, 0);
            F_h00_307C();
        }
    } else {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
    }
    F_h00_3AE4(&G_h01_7246, G_h01_723E, G_h01_7240);
}

