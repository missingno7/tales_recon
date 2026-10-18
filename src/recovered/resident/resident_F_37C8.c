/* Candidate for resident_F_37C8: the baseline with one extra long local declared
   before the int status local, so the status word sits at the lower frame slot.
   Callee and DATA names are mechanical. */
extern long AllocMem();
extern long G_h01_A9B2;
extern long G_h01_543A;
extern long G_h01_543E;
extern long G_h01_5442;
extern long G_h01_5446;
extern long G_h01_53E8;

int recovered(arg)
long arg;
{
    long tmp;
    int result;

    G_h01_A9B2 = AllocMem(arg, 0x10002L);
    if (G_h01_A9B2 == 0) {
        result = -1;
    } else {
        G_h01_543A = G_h01_A9B2;
        G_h01_543E = G_h01_A9B2;
        G_h01_5442 = (long)((char *)arg + G_h01_A9B2 + 1);
        G_h01_5446 = arg - 8;
        G_h01_53E8 = G_h01_A9B2;
        *(long *)G_h01_53E8 = 0L;
        *((long *)G_h01_53E8 + 1) = G_h01_5446;
        result = 0;
    }
    return result;
}
