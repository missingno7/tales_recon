extern int G_h01_1322[64];

unsigned recovered(n)
unsigned n;
{
    return G_h01_1322[(n >> 2) & 63];
}
