struct entry_layout {
	unsigned short field_0;
	char *field_2;
};

extern long G_h01_46DA;
extern char G_h01_4D60;
extern char G_h01_4D62;
extern unsigned short G_h01_4D82;
extern unsigned short G_h01_4D84;
extern char G_h01_4D86;
extern unsigned short G_h01_4D88;
extern char G_h01_5014[154];

extern long F_h00_0FDE();
extern long F_h00_86DC();
extern long F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern long F_h00_463E();
extern long F_h00_3C0E();
extern long F_h00_868C();

void recovered()
{
	struct entry_layout *entry;
	char *text;
	long unknown_local_a[2];
	unsigned int index;
	int parsed;
	unsigned short unknown_local_b;
	unsigned short initial[15];
	unsigned short unknown_local_c;
	unsigned short field;
	long old_file;
	int column;
	char unknown_local_gap[3];
	char buffer[80];

	old_file = G_h01_46DA;
	G_h01_4D60 = 0;
	F_h00_0FDE(1);
	G_h01_46DA = F_h00_86DC("DT1:invest.arc", 1005L);
	F_h00_2816(G_h01_46DA);

	index = 0;
	do {
		initial[index] = -1;
	} while (++index < 15);

	index = 0;
	do {
		entry = 0;
		entry = (struct entry_layout *)F_h00_291E(index, entry);
		text = entry->field_2;
		field = entry->field_0;
		text[entry->field_0 - 1] = 0;
		text = (char *)F_h00_0976(text, (char *)&G_h01_4D62 + index * 46);
		text = (char *)F_h00_0976(text, buffer);
		F_h00_704E(buffer, "%d %d",
			(char *)&G_h01_4D82 + index * 46,
			(char *)&G_h01_4D88 + index * 46);
		*(unsigned short *)((char *)&G_h01_4D82 + index * 46) =
			((unsigned short)F_h00_463E(&G_h01_4D82, index * 46)) % 120;
		*(unsigned short *)((char *)&G_h01_4D88 + index * 46) =
			((unsigned short)F_h00_463E(&G_h01_4D88, index * 46)) % 5;
		*(char *)((char *)&G_h01_4D86 + index * 46) = 0;
		*(unsigned short *)((char *)&G_h01_4D84 + index * 46) = 0;
		F_h00_3C0E(entry);
	} while (++index < 15);

	F_h00_868C(G_h01_46DA);
	F_h00_0FDE(1);
	G_h01_46DA = F_h00_86DC("DT1:chart.arc", 1005L);
	F_h00_2816(G_h01_46DA);

	index = 0;
	do {
		entry = 0;
		entry = (struct entry_layout *)F_h00_291E(index, entry);
		text = entry->field_2;
		field = entry->field_0;
		text = (char *)F_h00_0976(text, buffer);
		parsed = 0;
		F_h00_704E(buffer, "%d", &parsed);
		column = 0;
		do {
			G_h01_5014[index * 31 + column] = parsed;
		} while (++column < 30);
		F_h00_3C0E(entry);
	} while (++index < 5);

	F_h00_868C(G_h01_46DA);
	F_h00_0FDE(1);
	G_h01_46DA = old_file;
	F_h00_2816(G_h01_46DA);
}







