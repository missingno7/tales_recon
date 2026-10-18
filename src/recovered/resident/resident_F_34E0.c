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
extern int build_sprite_mask();
extern void F_h00_4692();
extern long game_memory_header;
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
    p->field_30 = allocate_memory_or_report(&game_memory_header,
        (long)(unsigned short)(p->field_8.field_0 * p->field_8.field_2));
    build_sprite_mask(&p->field_8, p->field_30);
    F_h00_4692(&p->field_8,
        (long)(unsigned short)(p->field_34 * stride), 0L, screen_rast_port,
        (long)x, (long)y, (long)width, (long)height, 0xe2L, p->field_30);
    free_memory_checked(&game_memory_header, p->field_30,
        (long)(unsigned short)(p->field_8.field_0 * p->field_8.field_2));
}
