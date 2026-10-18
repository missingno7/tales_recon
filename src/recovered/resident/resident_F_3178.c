extern long screen_palette_words;

recovered(src)
short *src;
{
    short *dst;
    unsigned int i;

    dst = (short *)screen_palette_words;
    for (i = 0; i < 0x20; i++)
        *dst++ = *src++;
}
