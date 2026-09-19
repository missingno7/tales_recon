struct Row { int values[5]; };
extern struct Row G_h01_12C0[32];
extern int G_h01_4262;
extern int G_h01_4264[6];
recovered(n) int n;
{
    unsigned int i;
    G_h01_4264[0] = G_h01_4262 - 16;
    i = 1;
    do {
        G_h01_4264[i] = G_h01_12C0[n-1].values[i-1];
        ++i;
    } while (i < 6);
}
