extern int G_h01_13A2[64];

int recovered(n) unsigned n;
{
    return G_h01_13A2[(n >> 2) & 63];
}
