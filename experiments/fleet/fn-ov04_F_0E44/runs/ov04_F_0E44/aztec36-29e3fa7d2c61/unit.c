/* Direct recovery candidate for ov04_F_07CA. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int G_h01_511C; extern int G_h01_511E; extern char G_h01_5150;
extern int G_h01_5124; extern int G_h01_5126; extern char G_h01_512C;
extern int G_h01_5338; extern int G_h01_533A; extern char G_h01_536C;
extern int G_h01_5340; extern int G_h01_5342; extern char G_h01_5348;
extern int G_h01_5152; extern int G_h01_5154; extern char G_h01_5186;
extern int G_h01_515A; extern int G_h01_515C; extern char G_h01_5162;
extern int G_h01_5188; extern int G_h01_518A; extern char G_h01_51BC;
extern int G_h01_5190; extern int G_h01_5192; extern char G_h01_5198;
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h00_3AE4();

F_h04_07CA()
{
    F_h00_0FDE(1);
    F_h00_291E(3, G_h01_46CE);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);

    F_h00_291E(4, &G_h01_511C);
    G_h01_511C = 120;
    G_h01_511E = 8;
    G_h01_5150 = 0;
    F_h00_34E0(&G_h01_511C);
    F_h00_3AE4(&G_h01_512C, G_h01_5124, G_h01_5126);

    F_h00_291E(5, &G_h01_5338);
    G_h01_5338 = 32;
    G_h01_533A = 48;
    G_h01_536C = 0;
    F_h00_34E0(&G_h01_5338);
    F_h00_3AE4(&G_h01_5348, G_h01_5340, G_h01_5342);

    F_h00_291E(6, &G_h01_5152);
    G_h01_5152 = 136;
    G_h01_5154 = 32;
    G_h01_5186 = 0;
    F_h00_34E0(&G_h01_5152);
    F_h00_3AE4(&G_h01_5162, G_h01_515A, G_h01_515C);

    F_h00_291E(7, &G_h01_5188);
    G_h01_5188 = 120;
    G_h01_518A = 48;
    G_h01_51BC = 0;
    F_h00_34E0(&G_h01_5188);
    F_h00_3AE4(&G_h01_5198, G_h01_5190, G_h01_5192);

    F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
}

/* Direct recovery candidate for ov04_F_0926. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int G_h01_0320;
extern int G_h01_0322;
extern long G_h01_0324;
extern int G_h01_50E6;
extern int G_h01_522A;
extern int G_h01_5296;
extern int G_h01_5302;
extern int G_h01_51F4;
extern int G_h01_51F6;
extern char G_h01_511A;
extern char G_h01_536E;
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_307C();
extern int F_h00_4376();
extern int F_h00_57D2();
extern int F_h00_86A8();
extern unsigned int F_h00_463E();

F_h04_0926(first,last,rounds)
int first,last,rounds;
{
    int i;
    int round;

    G_h01_51F4 = 128;
    G_h01_51F6 = 0;
    for (round = 0; round < rounds; ++round) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        G_h01_511A = 3;
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_522A);
        F_h00_34E0(&G_h01_5296);
        F_h00_34E0(&G_h01_5302);
        F_h00_34E0(&G_h01_51F4);
        for (i = first - 1; i < last; ++i)
            F_h00_35DC(*((int *)((char *)&G_h01_0320 + ((long)i << 3))),
                *((int *)((char *)&G_h01_0322 + ((long)i << 3))),
                *((long *)((char *)&G_h01_0324 + ((long)i << 3))), 0, 1);
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
            0L, 0L, 320L, 200L, 192L, 255L, 0L);
        G_h01_511A = 2;
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_522A);
        F_h00_34E0(&G_h01_5296);
        F_h00_34E0(&G_h01_5302);
        F_h00_34E0(&G_h01_51F4);
        for (i = first - 1; i < last; ++i)
            F_h00_35DC(*((int *)((char *)&G_h01_0320 + ((long)i << 3))),
                *((int *)((char *)&G_h01_0322 + ((long)i << 3))),
                *((long *)((char *)&G_h01_0324 + ((long)i << 3))), 0, 1);
        F_h00_307C();
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_57D2(0);
            return;
        }
        F_h00_86A8((long)(unsigned)(((F_h00_463E() & 2) + 1) * 5));
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_57D2(0);
            return;
        }
    }
    F_h00_86A8(15L);
}

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

F_h04_0B50(first, last, limit)
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
	goto outer_check;
outer_body:
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
    goto row_check_one;
row_body_one:
			F_h00_35DC(*((int *)((char *)G_h01_0398 + ((long)row << 3))),
				*((int *)((char *)G_h01_039A + ((long)row << 3))),
				*((long *)((char *)G_h01_039C + ((long)row << 3))), 0, 1);
			++row;
row_check_one:
    if (row < last)
        goto row_body_one;
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
    goto row_check_two;
row_body_two:
			F_h00_35DC(*((int *)((char *)G_h01_0398 + ((long)row << 3))),
				*((int *)((char *)G_h01_039A + ((long)row << 3))),
				*((long *)((char *)G_h01_039C + ((long)row << 3))), 0, 1);
			++row;
row_check_two:
    if (row < last)
        goto row_body_two;
    F_h00_307C();
		F_h00_4376();
		if (G_h01_536E) {
			F_h00_57D2(0);
			return;
		}

		F_h00_86A8((unsigned long)((((unsigned)F_h00_463E() & 2) + 1) * 5));
		F_h00_4376();
		if (G_h01_536E) {
			F_h00_57D2(0);
			return;
		}
++pass;
outer_check:
if (pass < limit)
	goto outer_body;
	F_h00_86A8(15L);
}
/* Direct reconstruction candidate for ov04_F_0DBE. */
extern int G_h01_51FC; extern int G_h01_51FE; extern char G_h01_5204;
extern int G_h01_5232; extern int G_h01_5234; extern char G_h01_523A;
extern int G_h01_529E; extern int G_h01_52A0; extern char G_h01_52A6;
extern int G_h01_52D4; extern int G_h01_52D6; extern char G_h01_52DC;
extern int G_h01_5268; extern int G_h01_526A; extern char G_h01_5270;
extern int G_h01_51C6; extern int G_h01_51C8; extern char G_h01_51CE;
extern int G_h01_530A; extern int G_h01_530C; extern char G_h01_5312;
extern int F_h00_3AE4();
F_h04_0DBE()
{
 F_h00_3AE4(&G_h01_5204,G_h01_51FC,G_h01_51FE);
 F_h00_3AE4(&G_h01_523A,G_h01_5232,G_h01_5234);
 F_h00_3AE4(&G_h01_52A6,G_h01_529E,G_h01_52A0);
 F_h00_3AE4(&G_h01_52DC,G_h01_52D4,G_h01_52D6);
 F_h00_3AE4(&G_h01_5270,G_h01_5268,G_h01_526A);
 F_h00_3AE4(&G_h01_51CE,G_h01_51C6,G_h01_51C8);
 F_h00_3AE4(&G_h01_5312,G_h01_530A,G_h01_530C);
}

extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern int G_h01_50E6;
extern int G_h01_50F0;
extern int G_h01_51BE;
extern int G_h01_51F4;
extern int G_h01_522A;
extern int G_h01_5234;
extern int G_h01_5260;
extern int G_h01_526A;
extern int G_h01_5296;
extern int G_h01_52A0;
extern int G_h01_52CC;
extern int G_h01_52D6;
extern int G_h01_5302;
extern int G_h01_530C;
extern char G_h01_536E;
extern int G_h01_50B0;
extern int G_h01_50B8;
extern int G_h01_50C0;
extern char G_h01_50E4;
extern int G_h01_50EE;
extern char G_h01_50F6;
extern char G_h01_511A;
extern int G_h01_5232;
extern char G_h01_523A;
extern int G_h01_529E;
extern char G_h01_52A6;
extern int G_h01_5268;
extern char G_h01_5270;
extern int G_h01_52D4;
extern char G_h01_52DC;
extern int G_h01_530A;
extern char G_h01_5312;
extern int G_h01_1466;
extern int G_h01_511C;
extern int G_h01_50B2;
extern int G_h01_50B4;
extern int G_h01_50E8;
extern int G_h01_50EA;
extern int G_h01_50F2;
extern int G_h01_50F8;
extern int G_h01_50BA;
extern int G_h01_50BC;
extern int G_h01_50C2;
extern int G_h01_522C;
extern int G_h01_522E;
extern int G_h01_5236;
extern int G_h01_523C;
extern int G_h01_5298;
extern int G_h01_529A;
extern int G_h01_52A2;
extern int G_h01_52A8;
extern int G_h01_5262;
extern int G_h01_526C;
extern int G_h01_52D8;
extern int G_h01_530E;
extern int G_h01_5272;
extern int G_h01_52CE;
extern int G_h01_52DE;
extern int G_h01_5304;
extern int G_h01_5306;
extern int G_h01_5314;

extern int F_h00_0FDE();
extern int F_h00_86A8();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_34E0();
extern int F_h00_3AE4();
extern int F_h00_4376();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h04_07CA();
extern int F_h04_0B50();
extern int F_h04_0926();
extern int F_h04_0DBE();

recovered()
{
    int state;
    int index;
    char coordinates[10];
    coordinates[0] = -57;
    coordinates[1] = 29;
    coordinates[2] = -23;
    coordinates[3] = 25;
    coordinates[4] = 36;
    coordinates[5] = 30;
    coordinates[6] = 49;
    coordinates[7] = 29;
    coordinates[8] = 99;
    coordinates[9] = 29;

    F_h04_07CA();
    F_h00_0FDE(1);
    F_h00_291E(8, &G_h01_50E6);
    F_h00_4376();
    G_h01_50E6 = 0xd8;
    G_h01_50E8 = 0x20;
    G_h01_511A = 0;
    F_h00_34E0(&G_h01_50E6);
    F_h00_330E();
    F_h00_4376();
    F_h00_307C();

    F_h00_31AA(
        G_h01_46D6 = (char *)&G_h01_1466);
    F_h00_8A46(
        G_h01_46CE, 0L, 0L,
        G_h01_46D2, 0L, 0L,
        0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_34E0(&G_h01_50E6);
    F_h00_307C();

    F_h00_291E(9, &G_h01_50B0);
    F_h00_291E(11, &G_h01_522A);
    F_h00_291E(12, &G_h01_5296);
    F_h00_291E(13, &G_h01_5260);
    F_h00_291E(14, &G_h01_52CC);
    F_h00_291E(15, &G_h01_5302);
    F_h00_4376();
    G_h01_522A = 0x7f;
    G_h01_522C = 0x22;
    G_h01_5296 = 0x97;
    G_h01_5298 = 0x22;
    G_h01_5302 = 0xba;
    G_h01_5304 = 0x67;
    F_h00_57D2(0x6e);

    state = 2;
    index = 0;
    goto frame_test;
frame_body:
        if (state == 4)
            state = 0;
        G_h01_50B0 = coordinates[index * 2];
        G_h01_50B2 = coordinates[index * 2 + 1];
        G_h01_50E4 = state;
        F_h00_8A46(
            G_h01_46CE, 0L, 0L,
            G_h01_46D2, 0L, 0L,
            0x140L, 0xc8L, 0x82L, 0x14L, 0L);
        if (index == 0)
            G_h01_511A = 1;
        F_h00_34E0(&G_h01_50E6);
        F_h00_34E0(&G_h01_50B0);
        F_h00_4376();
        if (G_h01_536E) {
            F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
            F_h00_3AE4(&G_h01_50C0, G_h01_50B8, G_h01_50BA);
            F_h00_3AE4(&G_h01_523A, G_h01_5232, G_h01_5234);
            F_h00_3AE4(&G_h01_52A6, G_h01_529E, G_h01_52A0);
            F_h00_3AE4(&G_h01_5270, G_h01_5268, G_h01_526A);
            F_h00_3AE4(&G_h01_52DC, G_h01_52D4, G_h01_52D6);
            F_h00_3AE4(&G_h01_5312, G_h01_530A, G_h01_530C);
            F_h00_57D2(0);
            return;
        }
        F_h00_307C();
        F_h00_86A8(10);
        ++state;
        ++index;
frame_test:
    if (index < 5)
        goto frame_body;

    F_h00_8A46(
        G_h01_46CE, 0L, 0L,
        G_h01_46D2, 0L, 0L,
        0x140L, 0xc8L, 0x82L, 0x14L, 0L);
    F_h00_34E0(&G_h01_522A);
    F_h00_34E0(&G_h01_5302);
    F_h00_34E0(&G_h01_5296);
    F_h00_34E0(&G_h01_50E6);
    F_h00_307C();
    F_h00_3AE4(&G_h01_50C0, G_h01_50B8, G_h01_50BA);
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h00_0FDE(1);
    F_h00_291E(10, &G_h01_51BE);
    F_h00_4376();
    F_h04_0B50(1, 5, 8);
    F_h04_0B50(6, 10, 8);
    F_h00_291E(16, &G_h01_51F4);
    F_h04_0926(1, 3, 5);
    F_h04_0926(4, 6, 4);
    F_h00_4376();
    if (G_h01_536E) {
        F_h04_0DBE();
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h04_0B50(6, 14, 11);
    F_h04_0B50(6, 19, 15);
    F_h04_0B50(5, 23, 20);
    F_h04_0B50(5, 26, 24);
    F_h00_4376();
    if (G_h01_536E) {
        F_h04_0DBE();
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h04_0926(5, 9, 7);
    F_h04_0926(5, 12, 10);
    F_h04_0926(1, 13, 13);
    F_h04_0926(1, 14, 13);
    F_h04_0926(1, 15, 13);
    F_h04_0DBE();
    F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
}

