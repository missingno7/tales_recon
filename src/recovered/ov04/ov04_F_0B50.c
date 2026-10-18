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
extern char input_fire_action_pending;

extern int Delay();
extern int BltBitMap();
extern int F_h00_34E0();
extern int F_h00_463E();
extern int F_h00_307C();
extern int poll_controller_and_keyboard_input();
extern int play_sound();
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

	for (pass = 0; pass < limit; ++pass) {
		BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
			0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
		F_h00_34E0(&G_h01_50E6);
		F_h00_34E0(&G_h01_51BE);
		F_h00_34E0(&G_h01_522A);
		if ((unsigned int)(F_h00_463E() & 0x100) < 0x80)
			F_h00_34E0(&G_h01_52CC);
		else
			F_h00_34E0(&G_h01_5302);
		F_h00_34E0(&G_h01_5260);

		for (row = first - 1; row < last; ++row)
			F_h00_35DC(*((int *)((char *)G_h01_0398 + ((long)row << 3))),
				*((int *)((char *)G_h01_039A + ((long)row << 3))),
				*((long *)((char *)G_h01_039C + ((long)row << 3))), 0, 1);
    F_h00_307C();
		poll_controller_and_keyboard_input();
		if (input_fire_action_pending) {
			play_sound(0);
			return;
		}

		Delay(5L);
		poll_controller_and_keyboard_input();
		if (input_fire_action_pending) {
			play_sound(0);
			return;
		}

		BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
			0L, 0L, 0x140L, 0xc8L, 0xc0L, 0xffL, 0L);
		F_h00_34E0(&G_h01_50E6);
		F_h00_34E0(&G_h01_51BE);
		F_h00_34E0(&G_h01_522A);
		if ((unsigned int)(F_h00_463E() & 0x100) < 0x80)
			F_h00_34E0(&G_h01_52CC);
		else
			F_h00_34E0(&G_h01_5302);
		F_h00_34E0(&G_h01_5296);

		for (row = first - 1; row < last; ++row)
			F_h00_35DC(*((int *)((char *)G_h01_0398 + ((long)row << 3))),
				*((int *)((char *)G_h01_039A + ((long)row << 3))),
				*((long *)((char *)G_h01_039C + ((long)row << 3))), 0, 1);
    F_h00_307C();
		poll_controller_and_keyboard_input();
		if (input_fire_action_pending) {
			play_sound(0);
			return;
		}

		Delay((unsigned long)((((unsigned)F_h00_463E() & 2) + 1) * 5));
		poll_controller_and_keyboard_input();
		if (input_fire_action_pending) {
			play_sound(0);
			return;
		}
	}
	Delay(15L);
}