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

recovered(p, n)
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
