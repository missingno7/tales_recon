/* Direct reconstruction candidate for ov10_F_25A2. */
struct Flags { char pad; char bits; };
extern char G_h01_79AA;
extern char G_h01_79B4;
extern int G_h01_734C, G_h01_734E;
extern char G_h01_7354;
extern int G_h01_7382, G_h01_7384;
extern char G_h01_738A;
extern int G_h01_73B8, G_h01_73BA;
extern char G_h01_73C0;
extern int G_h01_73EE, G_h01_73F0;
extern char G_h01_73F6;
extern int F_h00_3AE4();

recovered(flags)
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
