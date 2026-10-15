extern long C_sink();
long C_reg6(p)
long *p;
{
    register long r0, r1, r2, r3, r4, r5;
    r0 = p[0] + 1;
    r1 = p[1] + 2;
    r2 = p[2] + 3;
    r3 = p[3] + 4;
    r4 = p[4] + 5;
    r5 = p[5] + 6;
    C_sink();
    return r0 + r1 + r2 + r3 + r4 + r5;
}
