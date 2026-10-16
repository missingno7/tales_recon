/* resident_F_33E6 candidate v1 (baseline).
   Mechanical access view: the argument record supplies a word at +0 and +2,
   a byte at +5 and a long table at +8; the custom-chip registers are absolute
   constant addresses. Field names are offsets, not provenance. */
struct BlitSrc {
	short field_0;
	short field_2;
	char field_4;
	unsigned char field_5;
	char field_6[2];
	long field_8[1];
};

extern int F_h00_8A8A();

F_h00_33E6(p, n)
struct BlitSrc *p;
long n;
{
	unsigned int b, a, count, size, mod, i;

	a = p->field_0;
	b = p->field_2;
	count = p->field_5;
	mod = 0;
	*(unsigned short *)0xdff096 = 0x8600;
	while (*(unsigned char *)0xdff002 & 0x40)
		;
	F_h00_8A8A(n, (long)(b * a), 1L);
	size = (b << 6) | (a >> 1);
	*(unsigned short *)0xdff040 = 0xdfc;
	*(unsigned short *)0xdff042 = 0;
	*(unsigned short *)0xdff044 = 0xffff;
	*(unsigned short *)0xdff046 = 0xffff;
	*(unsigned short *)0xdff060 = 0;
	*(unsigned short *)0xdff062 = mod;
	*(unsigned short *)0xdff064 = 0;
	*(unsigned short *)0xdff066 = mod;
	for (i = 0; i < count; i++) {
		*(unsigned long *)0xdff048 = 0;
		*(long *)0xdff04c = n;
		*(long *)0xdff050 = p->field_8[i];
		*(long *)0xdff054 = n;
		*(unsigned short *)0xdff058 = size;
	}
	*(unsigned short *)0xdff096 = 0x400;
}

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
extern long F_h00_3870();
extern int F_h00_3930();
extern int F_h00_33E6();
extern void F_h00_4692();
extern long G_h01_542A;
extern long G_h01_46CA;

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
    p->field_30 = F_h00_3870(&G_h01_542A,
        (long)(unsigned short)(p->field_8.field_0 * p->field_8.field_2));
    F_h00_33E6(&p->field_8, p->field_30);
    F_h00_4692(&p->field_8,
        (long)(unsigned short)(p->field_34 * stride), 0L, G_h01_46CA,
        (long)x, (long)y, (long)width, (long)height, 0xe2L, p->field_30);
    F_h00_3930(&G_h01_542A, p->field_30,
        (long)(unsigned short)(p->field_8.field_0 * p->field_8.field_2));
}

