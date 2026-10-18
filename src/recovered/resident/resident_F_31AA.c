extern long screen_palette_words;
extern int copy_palette_to_copper_lists();
extern int Delay();

recovered(target)
unsigned int *target;
{
    int r, g, b, tr, tg, tb, c, i, j;

    for (i = 0; i < 16; i++) {
        for (j = 0; j < 32; j++) {
            c = ((short *)screen_palette_words)[j];
            tr = (target[j] >> 8) & 0xf;
            tg = (target[j] >> 4) & 0xf;
            tb = target[j] & 0xf;
            r = (c >> 8) & 0xf;
            g = (c >> 4) & 0xf;
            b = c & 0xf;
            if (r != tr)
                r = (r < tr) ? ++r : --r;
            if (g != tg)
                g = (g < tg) ? ++g : --g;
            if (b != tb)
                b = (b < tb) ? ++b : --b;
            ((short *)screen_palette_words)[j] = (r << 8) | (g << 4) | b;
        }
        copy_palette_to_copper_lists();
        Delay(2L);
    }
}
