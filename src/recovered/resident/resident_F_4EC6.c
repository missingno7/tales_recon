/* Candidate v5 for resident_F_4EC6: as v4, with the byte-list walk written as a
   for loop whose increment follows the guarded call (one-factor change from v4). */
extern char G_h01_B1F0;
extern unsigned char *G_h01_1F9E[1];
extern long G_h01_B206[1];
extern int F_h00_3C0E();

recovered()
{
	int i;

	if (G_h01_B1F0 > -1) {
		for (i = 0; G_h01_1F9E[G_h01_B1F0][i] != 0xff; i++) {
			if (G_h01_B206[i])
				F_h00_3C0E(G_h01_B206[i]);
		}
		G_h01_B1F0 = -1;
	}
}
