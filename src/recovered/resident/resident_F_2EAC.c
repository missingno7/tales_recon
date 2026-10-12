recovered(p)
register unsigned char *p;
{
    register unsigned char n;
    register unsigned char i;

    n = *p;
    for (i = 0; i < n; i++)
        p[i] = p[i + 1];
    p[i] = 0;
}
