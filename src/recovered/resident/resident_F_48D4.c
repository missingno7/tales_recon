struct Slot {
    char reserved[2];
    int mode;
    long buf;
};

extern struct Slot *G_h01_27E4[1];
extern long G_h01_B1F2;

recovered(a)
int a;
{
    int j, k;
    char *dst;
    struct Slot *slot;

    a = a * 6;
    slot = G_h01_27E4[a];
    slot->mode = 0x80;
    dst = (char *)((a << 8) + G_h01_B1F2);
    slot->buf = (long)dst;
    k = 1;
    do {
        j = 0;
        do {
            dst[(k << 8) + j] = dst[(j << k) & 0xff];
            j++;
        } while (j < 256);
        slot = G_h01_27E4[k + a];
        slot->buf = (k << 8) + (long)dst;
        slot->mode = 0x80;
        k++;
    } while (k < 6);
}
