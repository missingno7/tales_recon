/* resident_F_34E0: sprite mask preparation and graphics register-ABI glue call.
   Record fields are access-derived offset views, not original names.
   The four unused word locals preserve the measured 18-byte C frame. */
struct SpriteBitmap {
    unsigned short field_0, field_2;
    char field_4;
    unsigned char field_5;
    char field_6[2];
    long field_8[8];
};
struct Sprite {
    short field_0, field_2, field_4, field_6;
    struct SpriteBitmap field_8;
    long field_30;
    unsigned char field_34;
};
extern long allocate_memory_or_report();
extern int free_memory_checked();
extern int F_h00_33E6();
extern void F_h00_4692();
extern long G_h01_542A;
extern long screen_rast_port;

recovered(p)
struct Sprite *p;
{
    short x, y, height, width, stride;
    short local_0C, local_0E, local_10, local_12;
    x = p->field_0;
    y = p->field_2;
    width = p->field_4 << 3;
    stride = width;
    height = p->field_6;
    p->field_30 = allocate_memory_or_report(&G_h01_542A,
        (long)(unsigned short)(p->field_8.field_0 * p->field_8.field_2));
    F_h00_33E6(&p->field_8, p->field_30);
    F_h00_4692(&p->field_8,
        (long)(unsigned short)(p->field_34 * stride), 0L, screen_rast_port,
        (long)x, (long)y, (long)width, (long)height, 0xe2L, p->field_30);
    free_memory_checked(&G_h01_542A, p->field_30,
        (long)(unsigned short)(p->field_8.field_0 * p->field_8.field_2));
}
