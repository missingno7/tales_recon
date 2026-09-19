extern int G_h1322_OFFSET[];

int recovered(n)
unsigned n;
{
    return G_h1322_OFFSET[(n >> 2) & 63];
}
