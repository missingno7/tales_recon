extern char G_h01_33E3[10];
extern char G_h01_33ED;

char *recovered(n)
long n;
{
    int i;

    G_h01_33ED = 0;
    i = 10;
    do {
        G_h01_33E3[--i] = n % 10 + '0';
    } while ((n = n / 10) > 0);
    return G_h01_33E3 + i;
}
