extern long G_h01_5392;
extern int F_h00_30F0();
extern int F_h00_86A8();

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
            t = ((short *)G_h01_5392)[j];
            A = (t >> 8) & 15;
            B = (t >> 4) & 15;
            C = t & 15;
            ((short *)G_h01_5392)[j] = ((A ? --A : A) << 8) | ((B ? --B : B) << 4) | (C ? --C : C);
        }
        F_h00_30F0();
        F_h00_86A8(2L);
    }
}
