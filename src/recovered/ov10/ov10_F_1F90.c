extern int F_h00_57D2();

recovered(a)
int a;
{
    if (a < 2)
        F_h00_57D2(0x51);
    else if (a < 4)
        F_h00_57D2(0x50);
    else if (a < 6)
        F_h00_57D2(0x4f);
    else
        F_h00_57D2(0x4e);
}
