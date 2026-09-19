extern int G_h1322_OFFSET[64];

int recovered(n)
unsigned n;
{
    return G_h1322_OFFSET[(n >> 2) & 63];
}
