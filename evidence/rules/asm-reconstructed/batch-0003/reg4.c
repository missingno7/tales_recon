extern long C_sink();
long C_reg4(p)
long *p;
{
    register long r0, r1, r2, r3;
    r0 = p[0] + 1;
    r1 = p[1] + 2;
    r2 = p[2] + 3;
    r3 = p[3] + 4;
    C_sink();
    return r0 + r1 + r2 + r3;
}
