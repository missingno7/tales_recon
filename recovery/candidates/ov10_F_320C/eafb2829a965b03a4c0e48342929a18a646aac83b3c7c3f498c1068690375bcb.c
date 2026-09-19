/* Direct reconstruction candidate for ov10_F_320C. */
struct Flags { int value; char bits; };
extern int F_h00_0FDE();
extern int F_h00_34E0();
extern char G_h01_79B6;
extern char G_h01_79EC;
extern char G_h01_7A22;
extern char G_h01_7A58;

recovered(flags)
struct Flags *flags;
{
    while ((flags->value & 15) != 15) {
        F_h00_0FDE(2);
        if (!(flags->bits & 8)) F_h00_34E0(&G_h01_79B6);
        if (!(flags->bits & 4)) F_h00_34E0(&G_h01_79EC);
        if (!(flags->bits & 2)) F_h00_34E0(&G_h01_7A22);
        if (!(flags->bits & 1)) F_h00_34E0(&G_h01_7A58);
    }
}
