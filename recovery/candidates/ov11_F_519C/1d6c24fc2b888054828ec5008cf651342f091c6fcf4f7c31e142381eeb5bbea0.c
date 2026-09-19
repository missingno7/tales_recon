extern char G_h01_3724[];
extern int F_h11_4610();

recovered(n)
int n;
{
	return F_h11_4610(&G_h01_3724[40 * n]);
}
