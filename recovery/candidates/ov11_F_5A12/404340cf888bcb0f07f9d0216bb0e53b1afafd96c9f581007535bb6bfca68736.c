extern int G_h01_37F4[40];

recovered(n)
int n;
{
	int i;

	if (n) {
		for (i = 0; i < 40; i++)
			G_h01_37F4[i] = (i + 1) * 53 + 2;
	}
	return G_h01_37F4[n];
}
