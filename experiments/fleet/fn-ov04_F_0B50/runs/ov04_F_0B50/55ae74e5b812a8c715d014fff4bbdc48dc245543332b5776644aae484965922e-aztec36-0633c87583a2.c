extern int G_h01_0398[1]; extern int G_h01_039A[1]; extern long G_h01_039C[1];
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int G_h01_51BE;
extern int G_h01_51C0;
extern int G_h01_5260;
extern int G_h01_5262;
extern int G_h01_52CC;
extern int G_h01_52CE;
extern char G_h01_511A;
extern int G_h01_50E6;
extern int G_h01_522A;
extern int G_h01_5296;
extern int G_h01_5302;
extern char G_h01_536E;

extern int F_h00_86A8();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h00_463E();
extern int F_h00_307C();
extern int F_h00_4376();
extern int F_h00_57D2();
extern int F_h00_35DC();

recovered(first, last, limit)
int first;
int last;
int limit;
{
	int row;
	int pass;

	G_h01_51BE = 0;
	G_h01_51C0 = 0;
	G_h01_5260 = 0x97;
	G_h01_5262 = 0x22;
	G_h01_52CC = 0xc1;
	G_h01_52CE = 0x52;
	G_h01_511A = 2;

	pass = 0;
	while (++pass < limit) {
		F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
			0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
		F_h00_34E0(&G_h01_50E6);
		F_h00_34E0(&G_h01_51BE);
		F_h00_34E0(&G_h01_522A);
		if ((unsigned int)(F_h00_463E() & 0x100) < 0x80)
			F_h00_34E0(&G_h01_52CC);
		else
			F_h00_34E0(&G_h01_5302);
		F_h00_34E0(&G_h01_5260);

		row = first - 1;
		while (row < last) {
			F_h00_35DC(G_h01_0398[(long)row * 4],
				G_h01_039A[(long)row * 4],
				G_h01_039C[(long)row * 2], 0, 1);
			++row;
		}
		F_h00_307C();
		F_h00_4376();
		if (G_h01_536E) {
			F_h00_57D2(0);
			return;
		}

		F_h00_86A8(5L);
		F_h00_4376();
		if (G_h01_536E) {
			F_h00_57D2(0);
			return;
		}

		F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
			0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
		F_h00_34E0(&G_h01_50E6);
		F_h00_34E0(&G_h01_51BE);
		F_h00_34E0(&G_h01_522A);
		if ((unsigned int)(F_h00_463E() & 0x100) < 0x80)
			F_h00_34E0(&G_h01_52CC);
		else
			F_h00_34E0(&G_h01_5302);
		F_h00_34E0(&G_h01_5296);

		row = first - 1;
		while (row < last) {
			F_h00_35DC(G_h01_0398[(long)row * 4],
				G_h01_039A[(long)row * 4],
				G_h01_039C[(long)row * 2], 0, 1);
			++row;
		}
		F_h00_307C();
		F_h00_4376();
		if (G_h01_536E) {
			F_h00_57D2(0);
			return;
		}

		F_h00_86A8((unsigned long)(((F_h00_463E() & 2) + 1) * 5));
		F_h00_4376();
		if (G_h01_536E) {
			F_h00_57D2(0);
			return;
		}
	}
	F_h00_86A8(15L);
}