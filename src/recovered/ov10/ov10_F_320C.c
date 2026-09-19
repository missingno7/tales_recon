/* Direct reconstruction candidate for ov10_F_320C. */
union Flags {
    int value;
    struct { char reserved; char bits; } bytes;
};
extern int F_h00_0FDE();
extern int F_h00_34E0();
extern char G_h01_79B6;
extern char G_h01_79EC;
extern char G_h01_7A22;
extern char G_h01_7A58;

recovered(flags)
union Flags *flags;
{
    if ((flags->value & 15) == 15)
        return;
    F_h00_0FDE(2);
    if (!(flags->bytes.bits & 8)) F_h00_34E0(&G_h01_79B6);
    if (!(flags->bytes.bits & 4)) F_h00_34E0(&G_h01_79EC);
    if (!(flags->bytes.bits & 2)) F_h00_34E0(&G_h01_7A22);
    if (!(flags->bytes.bits & 1)) F_h00_34E0(&G_h01_7A58);
}
