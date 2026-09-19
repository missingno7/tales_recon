extern int G_h01_5026[64];

int recovered(n) unsigned n;
{
    return G_h01_5026[(n >> 2) & 63];
}
