F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

struct DrawRecord {
    int x;
    int y;
    char unused[48];
    char pen;
};

extern long G_h01_46CA;
extern char G_h01_46E1;
extern long G_h01_46E6;
extern char *G_h01_5370;
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int G_h01_94AC;
extern int G_h01_94C0;
extern long G_h01_9F92;
extern long G_h01_9F96;
extern long G_h01_9F9A;
extern int F_h00_09C0();
extern int F_h00_34E0();
extern int F_h00_8AA8();
extern int F_h00_8B4C();
extern void F_h00_8B76();
extern int F_h00_8B88();
extern int F_h11_25D6();

void recovered()
{
    char saved;
    int i;
    int bottom;
    int redraw;

    bottom = 0xb0;
    redraw = 0;
    saved = *G_h01_5370;
    if (G_h01_94AE == 6 ||
        F_h11_25D6(bottom, G_h01_94C0 + 0x20, 0xb0))
        redraw = 1;

    if (redraw || G_h01_8A3C) {
        *G_h01_5370 = 0;
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B76(G_h01_46CA, 0L, (long)bottom, 0x13fL, 0xc7L);
        *G_h01_5370 = 0x11;
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, 0x13fL, (long)bottom);
        F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, 0L, 0xc7L);
        F_h00_8AA8(G_h01_46CA, 0x13fL, 0xc7L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, 0L, (long)bottom);
        F_h00_8AA8(G_h01_46CA, 0L, 0xc7L);

        F_h00_34E0(G_h01_9F96);
        F_h00_34E0(G_h01_9F9A);
        ((struct DrawRecord *)G_h01_9F92)->pen = 2;
        ((struct DrawRecord *)G_h01_9F92)->x = 0xd8;
        ((struct DrawRecord *)G_h01_9F92)->y = 0xba;
        i = 0;
        for (; i <= 3 - G_h01_94AC; ++i) {
            F_h00_34E0(G_h01_9F92);
            ((struct DrawRecord *)G_h01_9F92)->pen--;
            ((struct DrawRecord *)G_h01_9F92)->x += 0x20;
        }
        F_h00_09C0(0xae, 0xb5, G_h01_46E6, 1, 0, 1);
        if (G_h01_46E1 < 10)
            F_h00_09C0(0x12, 0xb9, (long)G_h01_46E1, 0, 0, 0);
        else
            F_h00_09C0(0xe, 0xb9, (long)G_h01_46E1, 0, 0, 0);
    }

    *G_h01_5370 = 0x11;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, 0L, (long)bottom);
    F_h00_8AA8(G_h01_46CA, 0x13fL, (long)bottom);
    *G_h01_5370 = saved;
}

