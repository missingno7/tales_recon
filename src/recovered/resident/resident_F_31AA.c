extern long G_h01_5392;
extern int F_h00_30F0();
extern int F_h00_86A8();

recovered(target)
unsigned int *target;
{
    int r, g, b, tr, tg, tb, c, i, j;

    for (i = 0; i < 16; i++) {
        for (j = 0; j < 32; j++) {
            c = ((short *)G_h01_5392)[j];
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
            ((short *)G_h01_5392)[j] = (r << 8) | (g << 4) | b;
        }
        F_h00_30F0();
        F_h00_86A8(2L);
    }
}
