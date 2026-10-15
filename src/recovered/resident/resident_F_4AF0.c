/* Mechanical access view. No storage/provider ownership is claimed. */
struct Slot { char reserved[2]; int mode; char *buf; };
extern long G_h01_5422;
extern char *G_h01_B1F2;
extern struct Slot *G_h01_28C4;
extern int F_h00_48D4();
extern int F_h00_559E();
extern int F_h00_49A0();
recovered()
{
    int i,j,k;
    unsigned int noise;
    struct Slot *slot;
    long off;
    G_h01_B1F2 = G_h01_5422;
    i=0;
    do { G_h01_B1F2[i]=0x5f; i++; } while(i<256);
    i=0;
    do { G_h01_B1F2[i]=0x90; i++; } while(i<32);
    i=128;
    do { G_h01_B1F2[i]=0x90; i++; } while(i<160);
    F_h00_48D4(0);
    k=1;
    off=k*0x600;
    i=0;
    do {
        ((char *)(G_h01_B1F2+(i>>1)))[off]=i<<1;
        (G_h01_B1F2+(i>>1)+off)[64]=(255-i)<<1;
        i++;
    } while(i<128);
    i=0;
    do {
        (G_h01_B1F2+(i>>1)+off)[128]=i<<1;
        (G_h01_B1F2+(i>>1)+off)[192]=(255-i)<<1;
        i++;
    } while(i<128);
    i=0;
    do {
        ((char *)(G_h01_B1F2+i))[off] = ((char *)(G_h01_B1F2+i))[off]<128 ? ((char *)(G_h01_B1F2+i))[off]+128 : ((char *)(G_h01_B1F2+i))[off]-128;
        i++;
    } while(i<256);
    F_h00_48D4(k);
    i=0;
    do {
        noise=F_h00_559E();
        noise+=F_h00_559E();
        noise>>=1;
        ((char *)((long)i+(long)G_h01_B1F2))[0xc00]=noise;
        i++;
    } while(i<0x700);
    slot=G_h01_28C4;
    slot->buf=G_h01_B1F2+0xc00;
    slot->mode=0x380;
    F_h00_49A0();
}
