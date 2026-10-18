extern long screen_palette_words;
extern int copy_palette_to_copper_lists();
extern int Delay();

recovered()
{
    int A;
    int B;
    int C;
    int k0;
    int k1;
    int k2;
    short t;
    int i;
    int j;

    for (i = 0; i < 16; i++) {
        for (j = 0; j < 32; j++) {
            t = ((short *)screen_palette_words)[j];
            A = (t >> 8) & 15;
            B = (t >> 4) & 15;
            C = t & 15;
            ((short *)screen_palette_words)[j] = ((A ? --A : A) << 8) | ((B ? --B : B) << 4) | (C ? --C : C);
        }
        copy_palette_to_copper_lists();
        Delay(2L);
    }
}
