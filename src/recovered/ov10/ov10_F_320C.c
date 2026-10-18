/* Direct reconstruction candidate for ov10_F_320C. */
union Flags {
    int value;
    struct { char reserved; char bits; } bytes;
};
extern int request_disk();
extern int draw_masked_sprite();
extern char G_h01_79B6;
extern char G_h01_79EC;
extern char G_h01_7A22;
extern char G_h01_7A58;

recovered(flags)
union Flags *flags;
{
    if ((flags->value & 15) == 15)
        return;
    request_disk(2);
    if (!(flags->bytes.bits & 8)) draw_masked_sprite(&G_h01_79B6);
    if (!(flags->bytes.bits & 4)) draw_masked_sprite(&G_h01_79EC);
    if (!(flags->bytes.bits & 2)) draw_masked_sprite(&G_h01_7A22);
    if (!(flags->bytes.bits & 1)) draw_masked_sprite(&G_h01_7A58);
}
