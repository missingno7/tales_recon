recovered() {
    int i;
    short *a0, *a1, *a6;
    long d0, d1;
    long *a4;
    i = 0;
    do {
        a4 = (long *)G_h01_A554;
        a0 = (short *)a4;
        a1 = (short *)a4;
        a6 = (short *)a4;
        d0 = *(short *)((char *)a0 + 0xc);
        d1 = *(short *)((char *)a6 + 0x10);
        d0 += d1;
        *(short *)((char *)a1 + 0x14) = (short)d0;
        a0 = (short *)a4;
        a1 = (short *)a4;
        d0 = *(short *)((char *)a0 + 0x12);
        *(short *)((char *)a1 + 0x6) = (short)d0;
        a1 = (short *)a4;
        d0 = *(short *)((char *)a0 + 0x12);
        *(short *)((char *)a1 + 0x4) = (short)d0;
        a0 = (short *)a4;
        a1 = (short *)a4;
        d0 = *(short *)((char *)a0 + 0x14);
        *(short *)((char *)a1 + 0xa) = (short)d0;
        a1 = (short *)a4;
        d0 = *(short *)((char *)a0 + 0x14);
        *(short *)((char *)a1 + 0x8) = (short)d0;
        *(short *)((char *)a0 + 0x16) = 0xc0;
        a0 = (short *)a4;
        *(short *)((char *)a0 + 0x1e) = 0x8;
        a0 = (short *)a4;
        *(short *)((char *)a0 + 0x20) = 0x1;
        i++;
    } while (i < 10);
}
