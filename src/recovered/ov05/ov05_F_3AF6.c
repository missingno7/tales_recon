/* Direct reconstruction candidate for ov05_F_3AF6. */
struct Lookup { int index; int pad; };
struct Record { char pad[4]; int value; char pad2[8]; };
extern int G_h01_5E42;
extern struct Lookup G_h01_5E66[16];
extern struct Record G_h01_606C[16];
extern int G_h01_5500;
extern char G_h01_54FE;
extern int draw_masked_sprite();
extern int switch_display_buffer();

recovered()
{
    int i;
    struct Record *record;
    int value;

    record = &G_h01_606C[G_h01_5E66[G_h01_5E42].index];
    value = record->value;
    for (i = 0; i < 26; i++) {
        G_h01_5500 = value - 2;
        draw_masked_sprite(&G_h01_54FE);
        switch_display_buffer();
        G_h01_5500 = value + 2;
        draw_masked_sprite(&G_h01_54FE);
        switch_display_buffer();
    }
    G_h01_5500 = value;
}
