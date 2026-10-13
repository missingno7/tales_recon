recovered(a, b, c, d)
int a, b, c, d;
{
    long dx, dy, sum;

    dx = (b - a < 0) ? -(b - a) : b - a;
    dy = (d - c < 0) ? -(d - c) : d - c;
    sum = dx * dx + dy * dy;
    return sum;
}
