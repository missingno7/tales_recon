#define ABS(x) ((x) < 0 ? -(x) : (x))
recovered(a,b) int a,b;
{
    int rows, columns;
    rows = ABS((a >> 3) - (b >> 3));
    columns = ABS((a & 7) - (b & 7));
    return rows + columns;
}
