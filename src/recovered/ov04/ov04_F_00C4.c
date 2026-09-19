recovered(a,b)
int a,b;
{
    a += b;
    if (a >= 35) a -= 35;
    return a;
}
