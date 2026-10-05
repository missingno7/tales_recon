extern int F_h04_000C();

F_h04_0000()
{
    F_h04_000C();
}

struct LinkEntry {
    char *target;
    char pad[8];
};

struct TargetEntry {
    char pad[40];
};

struct ShortTargetEntry {
    char pad[6];
};

struct FlagEntry {
    char value;
    char pad[11];
};

extern struct LinkEntry G_h01_4524[35];
extern struct LinkEntry G_h01_4528[35];
extern char G_h01_470A;
extern char G_h01_4C82;
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];
extern int F_h04_0104();
extern int F_h04_037E();

F_h04_000C()
{
    int i;

    for (i = 0; i < 35; i++) {
        G_h01_4524[i].target = (char *)&G_h01_470A + (long)i * 40;
        G_h01_4528[i].target = (char *)&G_h01_4C82 + (long)i * 6;
        G_h01_452E[i].value = 0;
        G_h01_452F[i].value = 0;
    }
    F_h04_0104();
    F_h04_037E();
}

F_h04_0088(n,p) int n,*p; { char i; if(n>=35)return 0; for(i=0;i<35;i++)if(*p++==n)return 0; return 1; }

F_h04_00C4(a,b)
int a,b;
{
    a += b;
    if (a >= 35) a -= 35;
    return a;
}

F_h04_00E6(a)
int a;
{
    ++a;
    if (a >= 35) a = 1;
    return a;
}

/* Direct recovery candidate for ov04_F_0104. */
struct Location {
    char pad[30];
    int selected;
    int a;
    int b;
    int c;
    int d;
};

extern long G_h01_46DA;
extern char G_h01_470A;
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_7AF0();
extern int F_h00_3C0E();
extern unsigned int F_h00_463E();
extern int F_h00_868C();
extern int F_h04_0088();
extern int F_h04_00C4();
extern int F_h04_00E6();

F_h04_0104()
{
    int count;
    struct Location *location;
    long state;
    long page;
    long saved;
    int choices[35];
    char text[81];
    int row;
    int picked;

    page = 0;
    row = 0;
    picked = 0;
    for (count = 1; count < 35; ++count)
        choices[count] = 36;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loc.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    page = 0;
    page = F_h00_291E(0, page);
    choices[0] = 0;
    location = (struct Location *)&G_h01_470A;
    state = *(long *)((char *)page + 2);
    state = F_h00_0976(state, text);
    F_h00_704E(text, "%d %d %d %d", &location->a, &location->b,
        &location->c, &location->d);
    location->selected = 0;
    state = F_h00_0976(state, text);
    F_h00_7AF0(location, text);
    F_h00_3C0E(page);
    row = F_h00_463E();
    row = (unsigned)row % 30;
    picked = F_h00_463E();
    picked = (unsigned)picked % 5;
    for (count = 1; count < 35; ++count) {
        while (!F_h04_0088(row, choices))
            row = F_h04_00E6(row);
        choices[(unsigned)row] = row;
        location = (struct Location *)(&G_h01_470A + (long)count * 40);
        page = 0;
        page = F_h00_291E(row, page);
        state = *(long *)((char *)page + 2);
        state = F_h00_0976(state, text);
        F_h00_704E(text, "%d %d %d %d", &location->a, &location->b,
            &location->c, &location->d);
        state = F_h00_0976(state, text);
        F_h00_7AF0(location, text);
        location->selected = row;
        F_h00_3C0E(page);
        row = F_h04_00C4(row, picked);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

struct Loot {
    char padding[38];
    int value;
};

struct Slot {
    int value;
    char text[4];
};

struct Object {
    char padding[2];
    long name;
};

extern long G_h01_46DA;
extern char G_h01_4705;
extern char G_h01_470A;
extern struct Loot G_h01_4732[35];
extern char G_h01_4C82;

extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern unsigned int F_h00_463E();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_3C0E();
extern int F_h00_868C();

F_h04_037E()
{
    int i;
    int probe;
    struct Slot *slot;
    struct Loot *loot;
    long unused;
    long name;
    long result;
    long saved;
    char buffer[81];
    int value;

    result = 0;
    value = 0;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loot.arc", 0x3edL);
    F_h00_2816(G_h01_46DA);
    slot = (struct Slot *)&G_h01_4C82;
    slot->value = 0;
    for (i = 1; i < 35; ++i) {
        loot = (struct Loot *)((char *)&G_h01_470A + (long)i * 40);
        if (loot->value)
            value = loot->value;
        else {
            value = (unsigned)F_h00_463E() % 37 + 1;
again:
            loot = G_h01_4732;
            probe = 1;
            do {
                if (loot->value == value)
                    break;
                ++probe;
                ++loot;
            } while (probe < 35);
            if (probe >= 35) {
                loot = (struct Loot *)((char *)&G_h01_470A + (long)i * 40);
                loot->value = value;
            }
            else {
                if ((unsigned)(value + 1) >= 37)
                    value = 1;
                else
                    ++value;
                goto again;
            }
        }
        slot = (struct Slot *)((char *)&G_h01_4C82 + (long)i * 6);
        if (value == 9)
            G_h01_4705 = ((char *)&i)[1];
        --value;
        result = 0;
        result = F_h00_291E(value, result);
        name = ((struct Object *)result)->name;
        name = F_h00_0976(name, buffer);
        F_h00_704E(buffer, "%d", slot->text);
        slot->value = value;
        F_h00_3C0E(result);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

struct ArcEntry {
    unsigned int length;
    char *text;
};

extern long G_h01_46DA;
extern char G_h01_4D60;
extern char G_h01_4D62;
extern char G_h01_4D82;
extern char G_h01_4D84;
extern char G_h01_4D86;
extern char G_h01_4D88;
extern char G_h01_5014;

extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_463E();
extern int F_h00_3C0E();
extern int F_h00_868C();

F_h04_0536()
{
    struct ArcEntry *item;
    char *name;
    long unused1;
    long unused2;
    unsigned int i;
    int value;
    int spare_top;
    int state[15];
    int spare_after_state;
    int id;
    long saved;
    int j;
    int lower[3];
    char buffer[77];

    saved = G_h01_46DA;
    G_h01_4D60 = 0;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:invest.arc", 1005L);
    F_h00_2816(G_h01_46DA);

    for (i = 0; i < 15; ++i)
        state[i] = -1;

    for (i = 0; i < 15; ++i) {
        item = 0;
        item = (struct ArcEntry *)F_h00_291E(i, (long)item);
        name = item->text;
        id = item->length;
        item->text[item->length - 1] = 0;
        name = (char *)F_h00_0976(name,
            (char *)&G_h01_4D62 + (long)i * 46L);
        name = (char *)F_h00_0976(name, buffer);
        F_h00_704E(buffer, "%d %d",
            (int *)((char *)&G_h01_4D82 + (long)i * 46L),
            (int *)((char *)&G_h01_4D88 + (long)i * 46L));
        *((unsigned int *)((char *)&G_h01_4D82 + (long)i * 46L)) =
            (unsigned int)F_h00_463E() % 120;
        *((unsigned int *)((char *)&G_h01_4D88 + (long)i * 46L)) =
            (unsigned int)F_h00_463E() % 5;
        *((unsigned char *)((char *)&G_h01_4D86 + (long)i * 46L)) = 0;
        *((unsigned int *)((char *)&G_h01_4D84 + (long)i * 46L)) = 0;
        F_h00_3C0E(item);
    }

    F_h00_868C(G_h01_46DA);
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:chart.arc", 1005L);
    F_h00_2816(G_h01_46DA);

    for (i = 0; i < 5; ++i) {
        item = 0;
        item = (struct ArcEntry *)F_h00_291E(i, (long)item);
        name = item->text;
        id = item->length;
        j = 0;
        do {
            name = (char *)F_h00_0976(name, buffer);
            F_h00_704E(buffer, "%d", &value);
            *((char *)&G_h01_5014 + (long)i * 31L + j) = ((char *)&value)[1];
            ++j;
        } while (j < 30);
        F_h00_3C0E(item);
    }

    F_h00_868C(G_h01_46DA);
    F_h00_0FDE(1);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

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

F_h04_0E44()
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

    G_h01_46D6 = (char *)&G_h01_1466;
    F_h00_31AA((char *)&G_h01_1466);
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
            G_h01_46CE, 0L, 0x14L,
            G_h01_46D2, 0L, 0x14L,
            0x140L, 0x82L, 0xc0L, 0xffL, 0L);
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
        F_h00_86A8(10L);
        ++state;
        ++index;
frame_test:
    if (index < 5)
        goto frame_body;

    F_h00_8A46(
        G_h01_46CE, 0L, 0x14L,
        G_h01_46D2, 0L, 0x14L,
        0x140L, 0x82L, 0xc0L, 0xffL, 0L);
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

    F_h04_0B50(11, 14, 6);
    F_h04_0B50(15, 19, 6);
    F_h04_0B50(20, 23, 5);
    F_h04_0B50(24, 26, 5);
    F_h00_4376();
    if (G_h01_536E) {
        F_h04_0DBE();
        F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
        F_h00_57D2(0);
        return;
    }

    F_h04_0926(7, 9, 5);
    F_h04_0926(10, 12, 5);
    F_h04_0926(13, 13, 1);
    F_h04_0926(13, 14, 1);
    F_h04_0926(13, 15, 1);
    F_h04_0DBE();
    F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
}

extern char G_h01_536E;
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46D6;
extern long G_h01_46DA;
extern char G_h01_1426;
extern long G_h01_2A16;
extern char G_h01_4704;

extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_291E();
extern int F_h00_307C();
extern int F_h00_30F0();
extern int F_h00_31AA();
extern int F_h00_3178();
extern int F_h00_330E();
extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h00_8BC8();
extern int F_h04_1822();
extern int F_h04_0E44();

F_h04_1302()
{
    unsigned char key;

    F_h00_330E();
    G_h01_536E = 0;
    G_h01_4704 = 1;
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_0FDE(1);
    F_h00_291E(2, G_h01_46CE);
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_0FDE(1);
    F_h00_4D04(0);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_57D2(1);
    F_h00_307C();
    G_h01_46D6 = (long)&G_h01_1426;
    F_h00_31AA(&G_h01_1426);
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_3178(&G_h01_1426);
    F_h00_30F0();
    F_h04_1822();
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
    F_h00_435E();
    while (G_h01_2A16) {
        key = F_h00_4376();
        if (key & 0x80) {
            F_h00_57D2(0);
            F_h00_57D2(0x24);
            F_h00_330E();
            key = 0;
            G_h01_536E = 0;
            break;
        }
    }

    F_h00_4EC6();
    F_h00_435E();
    F_h00_4376();
    if (G_h01_536E) {
        F_h00_57D2(0);
        return;
    }

    F_h04_0E44();
    G_h01_4704 = 0;
    if (G_h01_536E)
        F_h00_57D2(0x24);
    F_h00_330E();
}


extern char G_h01_1766[1];
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_46E0;

extern int F_h00_0640();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_330E();
extern int F_h00_35DC();
extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h00_4676();
extern int F_h00_57D2();
extern int F_h00_8A46();
extern int F_h00_8BC8();
extern int F_h00_86A8();

F_h04_149C()
{
    int unused;
    unsigned char buttons;

    unused = 0;
    buttons = 0;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    G_h01_46E0 = 0;
    F_h00_0640(9);
    F_h00_35DC(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
    F_h00_35DC(176, 80, "Easy Money", 24, 0);
    F_h00_35DC(176, 100, "Standard Wages", 1, 0);
    F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    F_h00_435E();
    while (!(buttons & 0x80)) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 176L, 200L, 192L, 255L, 0L);
        F_h00_35DC(168, 60, "CHOOSE DIFFICULTY:", 1, 0);
        buttons &= 0x3f;
        if (buttons & 0x40)
            return 0x25;
        if (buttons == 1) {
            if (G_h01_46E0 == 0)
                G_h01_46E0 = 2;
            else
                --G_h01_46E0;
            F_h00_57D2(36);
        } else if (buttons == 5) {
            if (G_h01_46E0 == 2)
                G_h01_46E0 = 0;
            else
                ++G_h01_46E0;
            F_h00_57D2(36);
        }

        switch (G_h01_46E0) {
        case 0:
            F_h00_35DC(168, 80, ">Easy Money", 24, 0);
            F_h00_35DC(176, 100, "Standard Wages", 1, 0);
            F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
            break;
        case 2:
            F_h00_35DC(176, 80, "Easy Money", 1, 0);
            F_h00_35DC(176, 100, "Standard Wages", 1, 0);
            F_h00_35DC(168, 120, ">Hard Earned Cash", 24, 0);
            break;
        default:
            F_h00_35DC(176, 80, "Easy Money", 1, 0);
            F_h00_35DC(168, 100, ">Standard Wages", 24, 0);
            F_h00_35DC(176, 120, "Hard Earned Cash", 1, 0);
            break;
        }
        F_h00_307C();
        F_h00_86A8((long)5);
        buttons = F_h00_4376();
    }

    F_h00_57D2(36);
    F_h00_4676();
    F_h00_8BC8(G_h01_46CA, 0L);
    return F_h00_330E();
}

/* Direct reconstruction candidate for ov04_F_1822. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_4376();
extern int F_h00_86A8();

F_h04_1822()
{
    int inset;

    inset = 80;
    do {
        F_h00_8A46(G_h01_46CE, (long)inset, (long)inset,
            G_h01_46D2, (long)inset, (long)inset,
            (long)(320 - inset - inset), (long)(200 - inset - inset),
            (long)192, (long)255, 0L);
        F_h00_307C();
        F_h00_4376();
        F_h00_86A8(2L);
        inset -= 8;
    } while (inset >= 0);
}

extern char G_h01_06FE[624];

extern int F_h00_435E();
extern int F_h00_134C();
extern int F_h00_57D2();
extern int F_h00_35DC();
extern int F_h00_307C();

F_h04_18A6()
{
    int i;
    int scratch;

    F_h00_435E();
    if (F_h00_134C(20)) {
        return F_h00_57D2(36);
    }
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    i = 0;
    do {
        F_h00_35DC(64, 192, G_h01_06FE + (long)i * 26, 1, 3);
        F_h00_307C();
        if (F_h00_134C(20)) {
            return F_h00_57D2(36);
        }
        ++i;
    } while (i < 24);
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
}
/* Direct reconstruction candidate for ov04_F_1A3A. */
extern long G_h01_46CA;
extern int F_h00_8BC8();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int F_h00_57D2();
extern int F_h00_435E();
extern int F_h00_134C();
extern int F_h00_307C();

F_h04_1A3A(choice)
int choice;
{
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(30);
    if (choice) F_h00_0640(13);
    else F_h00_0640(14);
    F_h00_57D2(119);
    F_h00_435E();
    F_h00_134C(100);
    F_h00_4EC6();
    F_h00_307C();
}

extern long F_h00_463E();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int F_h00_57D2();
extern int F_h00_2816();
extern int F_h00_134C();
extern long G_h01_46DA;

F_h04_1AA2(a)
int a;
{
    int value;

    if (a) {
        value=(unsigned)F_h00_463E()%3;
        F_h00_4EC6();
        F_h00_0FDE(2);
        switch (value) {
        case 0:
            F_h00_4D04(9);
            break;
        case 2:
            F_h00_4D04(17);
            break;
        case 3:
            F_h00_4D04(18);
            break;
        }
        F_h00_0640(12);
        F_h00_57D2(119);
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
    } else {
        value=(F_h00_463E()&1) ? 15 : 16;
        F_h00_4EC6();
        F_h00_0FDE(2);
        F_h00_4D04(value);
        F_h00_0640(11);
        F_h00_57D2(119);
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
    }
    F_h00_134C(100);
}

extern long G_h01_46CA;
extern long G_h01_46DA;
extern char G_h01_1766[1];
extern char *G_h01_46D6;
extern int F_h00_330E();
extern int F_h00_8BC8();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_2816();
extern int F_h00_57D2();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_435E();
extern char F_h00_4376();
extern int F_h00_35DC();
extern int F_h00_86A8();

F_h04_1B94()
{
    int selection;
    unsigned char buttons;

    selection = 0;
    buttons = 0;
    F_h00_330E();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(1);
    F_h00_4D04(0);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_57D2(1);
    F_h00_307C();
    G_h01_46D6 = G_h01_1766;
    F_h00_31AA(G_h01_1766);
    F_h00_435E();
    buttons = F_h00_4376();
    while (!(buttons & 128)) {
        if ((buttons & 1) || (buttons & 5))
            selection ^= 1;
        F_h00_8BC8(G_h01_46CA, 0L);
        F_h00_35DC(112, 70, "PLAY AGAIN?", 1, 0);
        if (!selection) {
            F_h00_35DC(136, 100, ">YES", 24, 0);
            F_h00_35DC(144, 120, "NO", 1, 0);
        } else {
            F_h00_35DC(144, 100, "YES", 1, 0);
            F_h00_35DC(136, 120, ">NO", 24, 0);
        }
        F_h00_307C();
        if ((buttons & 1) || (buttons & 5)) {
            F_h00_435E();
            F_h00_86A8((long)10);
        }
        buttons = F_h00_4376();
    }
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_57D2(0);
    F_h00_4EC6();
    return selection;
}

extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_1826[1];
extern char G_h01_14A6[1];

extern int F_h00_57D2();
extern int F_h00_291E();
extern int F_h00_330E();
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h04_18A6();
extern int F_h00_134C();
extern int F_h00_4EC6();

F_h04_1D32()
{
    int unused;

    F_h00_57D2(0);
    F_h00_291E(1, G_h01_46CE);
    F_h00_330E();
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_307C();
    G_h01_46D6 = G_h01_1826;
    F_h00_31AA(G_h01_1826);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h04_18A6();
    F_h00_291E(0, G_h01_46CE);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_330E();
    F_h00_307C();
    G_h01_46D6 = G_h01_14A6;
    F_h00_31AA(G_h01_14A6);
    if (F_h00_134C(40))
        F_h00_57D2(36);
    F_h00_57D2(0);
    F_h00_4EC6();
}

struct RootBitMapView { unsigned short BytesPerRow; unsigned short Rows; unsigned char Flags; unsigned char Depth; unsigned short pad; unsigned char *Planes[8]; };
struct RootRasInfoView { struct RootRasInfoView *Next; struct RootBitMapView *BitMap; short RxOffset; short RyOffset; };
struct BitmapScreenRecord { char pad0[4]; long field_4; char pad8[16]; char field_18; char field_19; char field_1a; char field_1b; char field_1c; char pad1d[5]; short field_22; };
struct BitmapLayout { char pad0[8]; long planes[8]; };
struct ScreenInfo { char pad0[12]; struct BitmapScreenRecord *field_c; };
struct S53B8 { long field_0; long field_4; };

extern long G_h01_0036;
extern long G_h01_004E;
extern long G_h01_0066;
extern long G_h01_0072;
extern long G_h01_0078;
extern long G_h01_00AE;
extern long G_h01_00C0;
extern long G_h01_010E;
extern long G_h01_0126;
extern long G_h01_012C;
extern long G_h01_0132;
extern long G_h01_0138;
extern long G_h01_013E;
extern long G_h01_0144;
extern long G_h01_0174;
extern long G_h01_0180;
extern long G_h01_0186;
extern long G_h01_018C;
extern long G_h01_0192;
extern long G_h01_0198;
extern long G_h01_019E;
extern long G_h01_01AA;
extern long G_h01_01B0;
extern long G_h01_01BC;
extern long G_h01_01C2;
extern long G_h01_01C8;
extern long G_h01_01CE;
extern long G_h01_01E0;
extern long G_h01_01E6;
extern long G_h01_01F2;
extern long G_h01_01F8;
extern long G_h01_020A;

extern short G_h01_0970;
extern struct RootRasInfoView G_h01_2EB4;
extern struct RootBitMapView G_h01_2EC0;
extern struct RootBitMapView G_h01_2EE8;
extern struct BitmapScreenRecord *G_h01_46CA;
extern struct BitmapLayout *G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46F8;
extern long G_h01_5370;
extern long G_h01_5374;
extern long G_h01_5378;
extern long G_h01_537C;
extern long G_h01_5380;
extern struct ScreenInfo *G_h01_5384;
extern long G_h01_5388;
extern long G_h01_538C;
extern unsigned char G_h01_5390;
extern long G_h01_5392;
extern long G_h01_5396;
extern short G_h01_539A;
extern char G_h01_539C;
extern char G_h01_539D;
extern long G_h01_53A2;
extern long G_h01_53A6;
extern long G_h01_53B4;
extern long G_h01_53B8;
extern short G_h01_53CC;
extern short G_h01_53CE;
extern long G_h01_53D8;
extern long G_h01_53DC;
extern long G_h01_53E0;
extern long G_h01_53E4;
extern long G_h01_53E8;
extern long G_h01_53EC;
extern long G_h01_53F0;
extern long G_h01_53F4;
extern char G_h01_53F8;
extern long G_h01_5422;
extern long G_h01_5426;
extern long G_h01_542A;
extern long G_h01_544A;

struct GraphicsBaseView { char pad[34]; long view; };
struct S3 { char pad[8]; long field_8; long field_c; };
struct S2 { char pad[4]; struct S3 *field_4; };
struct S1 { char pad[36]; struct S2 *field_24; };
struct S0 { struct S1 *field_0; };
struct InitBlock { char first; char pad[11]; long field_c; long field_10; };
struct Layer { char pad[0xb8]; long field_b8; };

extern long F_h00_89D0();
extern int F_h04_27FE();
extern long F_h00_876C();
extern int F_h04_26F0();
extern int F_h00_37C8();
extern int F_h00_8C66();
extern long F_h00_8926();
extern long F_h00_8CD0();
extern long F_h00_8C98();
extern long F_h00_8960();
extern long F_h00_3870();
extern int F_h00_8C6E();
extern int F_h00_8C86();
extern int F_h00_3930();
extern int F_h00_8AF6();
extern int F_h00_8534();
extern int F_h00_8B08();
extern int F_h00_8B14();
extern long F_h00_8AEA();
extern int F_h00_8B3E();
extern int F_h00_8B5E();
extern int F_h00_8B32();
extern long F_h00_8B6A();
extern int F_h00_8BB8();
extern int F_h00_8BA8();
extern int F_h00_8B88();
extern int F_h00_8BC8();
extern int F_h00_307C();
extern int F_h00_330E();
extern int F_h00_8AD2();
extern int F_h00_4676();
extern int F_h00_50E8();
extern int F_h00_897C();
extern int F_h00_8784();

recovered()
{
    unsigned int i;
    long memory;
    struct Layer *layer;
    long size;
    long unused_slot;
    long probe;

    G_h01_5374 = F_h00_89D0("graphics.library", 0L);
    if (!G_h01_5374)
        F_h04_27FE("InitAV:\tcannot open graphics library\n");
    G_h01_53DC = ((struct GraphicsBaseView *)G_h01_5374)->view;
    G_h01_5378 = F_h00_89D0("intuition.library", 0L);
    if (!G_h01_5378)
        F_h04_27FE("InitAV:\tcannot open intuition library\n");

    size = F_h00_876C(2L);
    if (size < 0x45948L)
        F_h04_26F0("Insufficient Chip Memory!");
    i = F_h00_37C8(0x40f10L);
    if (i < 0)
        F_h04_26F0("Memory Fragmentation:  Can't allocate enough contiguous chip memory.");

    i = F_h00_8C66();
    if (i)
        G_h01_53F8 = 1;
    else
        G_h01_53F8 = 0;
    if (G_h01_53F8) {
        G_h01_5422 = F_h00_8926(0x3e80L, 0x10002L);
        G_h01_5426 = F_h00_8926(0x3e80L, 0x10002L);
        if (!G_h01_5422 || !G_h01_5426)
            F_h04_26F0("Insufficient Chip Memory!");
    } else {
        G_h01_5422 = ((struct S0 *)G_h01_53DC)->field_0->field_24->field_4->field_8;
        G_h01_5426 = ((struct S0 *)G_h01_53DC)->field_0->field_24->field_4->field_c;
    }

    size = F_h00_876C(2L);
    if (size < 0x4a38L) {
        F_h04_26F0("Insufficient Chip Memory!");
    } else {
        size = 0x4a38L;
        do {
            probe = F_h00_8926(size, 2L);
            if (!probe)
                size -= 0x1f4L;
        } while (!probe);
        F_h00_897C(probe, size);
        if (size < 0x4a38L)
            F_h04_26F0("Memory Fragmentation:  Can't allocate enough contiguous chip memory.");
    }

    G_h01_537C = F_h00_89D0("layers.library", 0L);
    if (!G_h01_537C)
        F_h04_27FE("InitAV:\tcannot open layers library\n");
    G_h01_5380 = F_h00_8CD0();
    if (!G_h01_5380)
        F_h04_27FE("InitAV:\tcannot allocate Layer_Info");

    G_h01_5384 = F_h00_8C98(G_h01_5380, &G_h01_2EC0, 0L, 0L, 0x13fL, 0xc7L, 1L);
    layer = (struct Layer *)F_h00_8960(0L);
    layer->field_b8 = 0xffffffffL;
    G_h01_53EC = F_h00_3870(&G_h01_542A, 0xe8L);
    F_h00_8C6E(G_h01_53EC, 0xe8L);
    ((struct InitBlock *)G_h01_53EC)->first = 8;
    G_h01_53F0 = ((struct InitBlock *)G_h01_53EC)->field_c;
    ((struct InitBlock *)G_h01_53EC)->field_c = 0L;
    G_h01_53F4 = ((struct InitBlock *)G_h01_53EC)->field_10;
    ((struct InitBlock *)G_h01_53EC)->field_10 = 10L;
    F_h00_8C86(G_h01_53EC, 0xe8L, 1L);
    F_h00_3930(&G_h01_542A, G_h01_53EC, 0xe8L);
    F_h00_8784(G_h01_5378);

    G_h01_544A = F_h00_3870(&G_h01_542A, 0x4000L);
    if (!G_h01_544A)
        F_h00_8534(-1);
    F_h00_8B08(&G_h01_53A2);
    F_h00_8B14(&G_h01_53B4);
    G_h01_53A2 = &G_h01_53B4;

    F_h00_8AF6(&G_h01_2EC0, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = F_h00_3870(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_2EC0.Planes[i] = (unsigned char *)memory + (long)i * 0x1f40L;

    F_h00_8AF6(&G_h01_2EE8, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = F_h00_3870(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_2EE8.Planes[i] = (unsigned char *)memory + (long)i * 0x1f40L;

    G_h01_46CE = F_h00_3870(&G_h01_542A, 0x28L);
    F_h00_8AF6(G_h01_46CE, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = F_h00_3870(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_46CE->planes[i] = memory + (long)i * 0x1f40L;

    G_h01_2EB4.BitMap = &G_h01_2EC0;
    G_h01_2EB4.RxOffset = 0;
    G_h01_2EB4.RyOffset = 0;
    G_h01_2EB4.Next = 0L;
    G_h01_53CC = 0x140;
    G_h01_53CE = 0xc8;
    G_h01_53D8 = &G_h01_2EB4;
    G_h01_53E8 = F_h00_8AEA(0x20L);
    G_h01_53B8 = G_h01_53E8;
    G_h01_5392 = ((struct S53B8 *)G_h01_53B8)->field_4;
    F_h00_8B3E(&G_h01_53A2, &G_h01_53B4);
    F_h00_8B5E(&G_h01_53A2);
    G_h01_53E0 = G_h01_53A6;
    G_h01_53A6 = 0L;
    G_h01_2EB4.BitMap = &G_h01_2EE8;
    G_h01_53B8 = G_h01_53E8;
    F_h00_8B3E(&G_h01_53A2, &G_h01_53B4);
    F_h00_8B5E(&G_h01_53A2);
    G_h01_53E4 = G_h01_53A6;
    F_h00_8B32(&G_h01_53A2);

    G_h01_46CA = G_h01_5384->field_c;
    G_h01_46CA->field_4 = (long)&G_h01_2EC0;
    G_h01_46CA->field_18 = 0xff;
    G_h01_46CA->field_19 = 0x1f;
    G_h01_46CA->field_1a = 2;
    G_h01_46CA->field_1b = 1;
    G_h01_46CA->field_1c = 0;
    G_h01_46CA->field_22 = -1;

    G_h01_5396 = "topaz.font";
    G_h01_539A = 8;
    G_h01_539C = 0;
    G_h01_539D = 0;
    G_h01_46F8 = F_h00_8B6A(&G_h01_5396);
    if (!G_h01_46F8)
        F_h04_27FE("InitAV:\tcannot open font");
    F_h00_8BB8(G_h01_46CA, G_h01_46F8);
    F_h00_8BA8(G_h01_46CA, 0L);
    F_h00_8B88(G_h01_46CA, 0x1fL);
    G_h01_5370 = (long)((char *)G_h01_46CA + 0x19L);
    G_h01_5388 = &G_h01_2EC0;
    G_h01_538C = &G_h01_2EE8;
    G_h01_5390 = 0;
    G_h01_46D2 = ((long *)&G_h01_5388)[G_h01_5390];
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_330E();
    for (i = 0; i < 8; ++i)
        F_h00_8AD2((long)i);
    F_h00_4676();
    F_h00_50E8();
}

extern long G_h01_5422;
extern long G_h01_5426;
extern char G_h01_53F8;
extern char G_h01_53FA;
extern char G_h01_53FB;
extern char G_h01_53FC;
extern int G_h01_53FE;
extern int G_h01_5400;
extern long G_h01_5402;
extern long G_h01_5406;
extern long G_h01_540A;
extern char G_h01_540E;
extern char G_h01_540F;
extern char G_h01_5410;
extern int G_h01_5412;
extern int G_h01_5414;
extern long G_h01_5416;
extern char *G_h01_541A;
extern long G_h01_541E;
extern long G_h01_5374;
extern long G_h01_5378;

extern int F_h00_897C();
extern int F_h00_3850();
extern int F_h00_8C7E();
extern int F_h00_8C48();
extern int F_h00_8784();
extern int F_h00_8534();

F_h04_26F0(arg)
long arg;
{
    if (G_h01_5422)
        F_h00_897C(G_h01_5422, 0x3e80L);
    if (G_h01_5426)
        F_h00_897C(G_h01_5426, 0x3e80L);
    F_h00_3850(0x40f10L);
    if (G_h01_53F8)
        F_h00_8C7E();
    G_h01_53FA = 0;
    G_h01_53FB = 1;
    G_h01_53FC = 1;
    G_h01_53FE = 6;
    G_h01_5400 = 3;
    G_h01_5402 = 0;
    G_h01_5406 = arg;
    G_h01_540A = 0;
    G_h01_540E = 0;
    G_h01_540F = 1;
    G_h01_5410 = 1;
    G_h01_5412 = 6;
    G_h01_5414 = 3;
    G_h01_5416 = 0;
    G_h01_541A = "OK";
    G_h01_541E = 0;
    F_h00_8C48(0L, &G_h01_53FA, 0L, &G_h01_540E, 0L, 0L, 0x280L, 0x28L);
    F_h00_8784(G_h01_5374);
    F_h00_8784(G_h01_5378);
    F_h00_8534(0);
}

extern long G_h01_5374;
extern long G_h01_5378;
extern long G_h01_537C;
extern long G_h01_5380;
extern long G_h01_5384;
extern long G_h01_53B4;
extern long G_h01_53E0;
extern long G_h01_53E4;
extern long G_h01_53E8;
extern long G_h01_53F0;
extern long G_h01_53F4;
extern char G_h01_53F8;
extern long G_h01_5422;
extern long G_h01_5426;
extern long G_h01_542A;
extern long G_h01_46DA;
extern long G_h01_46F8;

struct InitBlock { char pad[12]; long field_c; long field_10; };
struct S3 { char pad[8]; long field_8; long field_c; };
struct S2 { char pad[4]; struct S3 *field_4; };
struct S1 { char pad[36]; struct S2 *field_24; };
struct S0 { struct S1 *field_0; };
extern struct InitBlock *G_h01_53EC;
extern struct S0 *G_h01_53DC;

extern int F_h00_4EC6();
extern int F_h00_53E6();
extern int F_h00_330E();
extern long F_h00_89D0();
extern long F_h00_3870();
extern int F_h00_8C6E();
extern int F_h00_8C86();
extern int F_h00_3930();
extern int F_h00_3850();
extern int F_h00_897C();
extern int F_h00_8A8A();
extern int F_h00_868C();
extern int F_h00_8A9C();
extern int F_h00_8CB6();
extern int F_h00_8CC4();
extern int F_h00_8B32();
extern int F_h00_8ABA();
extern int F_h00_8ADE();
extern int F_h00_8AC6();
extern int F_h00_8C66();
extern int F_h00_8C7E();
extern int F_h00_8784();
extern int F_h00_8534();

F_h04_27FE()
{
    int unused;

    F_h00_4EC6();
    F_h00_53E6();
    F_h00_330E();
    G_h01_5378 = F_h00_89D0("intuition.library", 0L);
    if (!G_h01_5378)
        F_h04_27FE("InitAV:\tcannot open intuition library\n");
    G_h01_53EC = F_h00_3870(&G_h01_542A, 0xe8L);
    F_h00_8C6E(G_h01_53EC, 0xe8L);
    G_h01_53EC->field_c = G_h01_53F0;
    G_h01_53EC->field_10 = G_h01_53F4;
    F_h00_8C86(G_h01_53EC, 0xe8L, 1L);
    F_h00_3930(&G_h01_542A, G_h01_53EC, 0xe8L);
    F_h00_3850(0x40f10L);
    if (G_h01_53F8) {
        if (G_h01_5422)
            F_h00_897C(G_h01_5422, 0x3e80L);
        if (G_h01_5426)
            F_h00_897C(G_h01_5426, 0x3e80L);
    } else {
        F_h00_8A8A(G_h01_53DC->field_0->field_24->field_4->field_8, 0x3e80L, 0L);
        F_h00_8A8A(G_h01_53DC->field_0->field_24->field_4->field_c, 0x3e80L, 0L);
    }
    F_h00_868C(G_h01_46DA);
    F_h00_8A9C(G_h01_46F8);
    F_h00_8CB6(G_h01_5380, G_h01_5384);
    F_h00_8CC4(G_h01_5380);
    F_h00_8B32(G_h01_53DC);
    F_h00_8ABA(G_h01_53E8);
    F_h00_8ADE(&G_h01_53B4);
    F_h00_8AC6(G_h01_53E0);
    F_h00_8AC6(G_h01_53E4);
    F_h00_8C66();
    F_h00_8C7E();
    F_h00_8784(G_h01_537C);
    F_h00_8784(G_h01_5378);
    F_h00_8784(G_h01_5374);
    F_h00_8534(0);
}

