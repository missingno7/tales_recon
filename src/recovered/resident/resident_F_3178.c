extern long G_h01_5392;

recovered(src)
short *src;
{
    short *dst;
    unsigned int i;

    dst = (short *)G_h01_5392;
    for (i = 0; i < 0x20; i++)
        *dst++ = *src++;
}
