extern unsigned short G_h01_3AB8;

unsigned short recovered()
{
    unsigned short t;

    t = 0x9248;
    t += G_h01_3AB8;
    t = (t >> 3) ^ (t << 13);
    G_h01_3AB8 = t;
    return t;
}
