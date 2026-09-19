/* Host-written toolchain probe. This is not recovered game source. */
int add(a, b)
int a, b;
{
    return a + b;
}

int main()
{
    return add(2, 3) == 5 ? 0 : 10;
}
