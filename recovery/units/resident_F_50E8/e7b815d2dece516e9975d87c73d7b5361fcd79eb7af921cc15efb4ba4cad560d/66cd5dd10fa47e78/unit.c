extern long F_h00_8708();
extern long F_h00_2DBA();
extern long F_h00_2D66();
extern long G_h01_A7EE[104];
extern long G_h01_A7D6;
extern int G_h01_A7DA;
extern int G_h01_A7DC;
extern int G_h01_A7DE;
extern int G_h01_A7E0;
extern int G_h01_A7E2;
extern int G_h01_A7E4;

F_h00_287C(index, fh)
int index;
long fh;
{
    long offset;
    offset = G_h01_A7EE[index];
    F_h00_8708(fh, offset, -1L);
    F_h00_2DBA(fh, &G_h01_A7D6);
    F_h00_2D66(fh, &G_h01_A7DA);
    F_h00_2D66(fh, &G_h01_A7DC);
    F_h00_2D66(fh, &G_h01_A7DE);
    F_h00_2D66(fh, &G_h01_A7E0);
    F_h00_2D66(fh, &G_h01_A7E2);
    F_h00_2D66(fh, &G_h01_A7E4);
    return 0;
}


extern long F_h00_86F6();
extern short G_h01_A7E8;

F_h00_2D66(fh, buf)
long fh;
char *buf;
{
    char *p;
    char c;

    F_h00_86F6(fh, buf, 2L);
    G_h01_A7E8 = *(short *)buf;
    p = buf;
    c = *p;
    *p = p[1];
    p[1] = c;
    G_h01_A7E8 = *(short *)buf;
}

extern long F_h00_86F6();
extern long G_h01_A7EA;

long F_h00_2DBA(fh, buf)
long fh;
char *buf;
{
    char *p;
    char c;

    F_h00_86F6(fh, buf, 4L);
    G_h01_A7EA = *(long *)buf;
    p = buf;
    c = *p;
    p[0] = p[3];
    p[3] = c;
    c = p[1];
    p[1] = p[2];
    p[2] = c;
    G_h01_A7EA = *(long *)buf;
}

/* Worker candidate fn-resident_F_46CE v4 variant: v4 index: (long)q + (long)(L16*p). */
struct Level {
    unsigned int u0;
    unsigned int w2;
    char *p4;
};

extern struct Level *G_h01_27E4[1];
extern unsigned int G_h01_A7DE;
extern unsigned int G_h01_A7E0;
extern unsigned int G_h01_A7E2;
extern unsigned int G_h01_A7E4;

F_h00_46CE(n, base)
unsigned int n;
char *base;
{
    unsigned int p, q;
    unsigned int r;
    unsigned int L8;
    char *lv[3];
    unsigned int L16;
    char *src, *dst;
    struct Level *hdr, *plane, *pT;

    L8 = n * 3;
    hdr = G_h01_27E4[L8];
    plane = G_h01_27E4[L8] + 1;
    src = base + G_h01_A7DE;
    L16 = G_h01_A7E0 << G_h01_A7E2;
    dst = base + G_h01_A7E4 - (long)L16 * 3;
    hdr->w2 = G_h01_A7DE >> 1;
    hdr->p4 = base;
    for (p = 0; p < 3; p++) {
        plane = G_h01_27E4[L8 + p] + 1;
        plane->w2 = L16 >> 1;
        plane->p4 = dst + (long)L16 * p;
        for (q = 0; q < L16; q++)
            dst[(long)q + (long)(L16 * p)] = src[(q << p) % G_h01_A7E0];
    }
    lv[1] = base + G_h01_A7DE;
    lv[2] = base + ((G_h01_A7DE >> 1) + G_h01_A7DE);
    for (q = 1; q < 3; q++) {
        pT = G_h01_27E4[L8 + q];
        pT->w2 = G_h01_A7DE >> (q + 1);
        pT->p4 = lv[q];
        for (p = 0; p < (G_h01_A7DE >> q); p++)
            pT->p4[p] = hdr->p4[(p << q)];
    }
}

struct Slot {
    char reserved[2];
    int mode;
    long buf;
};

extern struct Slot *G_h01_27E4[1];
extern long G_h01_B1F2;

F_h00_48D4(a)
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

struct Sample {
    unsigned int field0;
    unsigned int length;
    char *data;
};
/* This function accesses entries 48..54; the complete table extent is unknown. */
extern struct Sample *G_h01_27E4[55];
extern long G_h01_A7CE;
extern unsigned long G_h01_A7D6;
extern int G_h01_A7D8;
extern int G_h01_A7E4;
extern int G_h01_B1FE;
extern char *G_h01_5426;
extern char *G_h01_5422;
extern long F_h00_2816();
extern int F_h00_287C();
extern int F_h00_46CE();
extern long F_h00_86F6();

F_h00_49A0()
{
    int i;
    int state;
    int offset;
    int count;
    struct Sample *sample;

    offset = 0;
    F_h00_2816(G_h01_A7CE);
    for (i = 0; i < 7; i++) {
        sample = G_h01_27E4[i + 48];
        if (F_h00_287C(i + 11, G_h01_A7CE)) ;
        sample->length = G_h01_A7D6 >> 1;
        sample->data = G_h01_5426 + offset;
        offset += G_h01_A7D8;
        F_h00_86F6(G_h01_A7CE, sample->data, G_h01_A7D6);
    }
    if (F_h00_287C(18, G_h01_A7CE)) ;
    count = F_h00_86F6(G_h01_A7CE, G_h01_5426 + offset, G_h01_A7D6);
    F_h00_46CE(8, G_h01_5426 + offset);
    offset += G_h01_A7E4;
    G_h01_B1FE = offset;
    if (F_h00_287C(19, G_h01_A7CE)) ;
    count = F_h00_86F6(G_h01_A7CE, G_h01_5422 + 4864, G_h01_A7D6);
    F_h00_46CE(9, G_h01_5422 + 4864);
    return 0;
}

/* Mechanical access view. No storage/provider ownership is claimed. */
struct Slot { char reserved[2]; int mode; char *buf; };
extern long G_h01_5422;
extern char *G_h01_B1F2;
extern struct Slot *G_h01_28C4;
extern int F_h00_48D4();
extern int F_h00_559E();
extern int F_h00_49A0();
F_h00_4AF0()
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

struct Event { long next; char kind; char reserved[2]; char value; };
struct Ring { int head,tail; char quit; char bytes[128]; };
extern int F_h00_8970();
extern int F_h00_89E4();
F_h00_5064(first,ring)
long first;
struct Ring *ring;
{
 struct Event *event;
 int next;
 event=(struct Event *)first;
 do {
  if(event->kind==1) {
   F_h00_8970();
   next=(ring->head+1)&127;
   if(ring->tail!=next) {
    ring->bytes[ring->head]=event->value;
    ring->head=next;
   }
   F_h00_89E4();
  } else if(event->kind==16) ring->quit=1;
 } while(event=(struct Event *)event->next);
 return 0;
}

/* Declaration views recover accesses only; no DATA provider is defined. */
struct Request { char reserved_00[28]; short command; char reserved_1e[10]; long data; };
extern long F_h00_8794();
extern long F_h00_887E();
extern long F_h00_89BA();
extern int F_h00_57B6();
extern int F_h00_5868();
extern int F_h00_4AF0();
extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_579E();
extern int F_h00_55D6();
extern int F_h00_5646();
extern int F_h00_56B6();
extern int F_h00_5726();
extern int F_h00_615E();
extern char G_h01_B1F0;
extern long G_h01_B284;
extern long G_h01_B288;
extern long G_h01_B336;
extern long G_h01_B33A;
extern char G_h01_B331;
extern long G_h01_B328;
extern int G_h01_B28C;
extern int G_h01_B28E;
extern long G_h01_B348;
extern char G_h01_B346;
extern char G_h01_B347;
extern long G_h01_B34C;
extern long G_h01_B350;
extern long G_h01_B33E;
extern long G_h01_2B4E;
extern long G_h01_B35E;
extern char G_h01_B35C;
extern char G_h01_B35D;
extern long G_h01_B362;
extern long G_h01_B366;
extern long G_h01_B354;
extern long G_h01_2B56;
extern long G_h01_B374;
extern char G_h01_B372;
extern char G_h01_B373;
extern long G_h01_B378;
extern long G_h01_B37C;
extern long G_h01_B36A;
extern long G_h01_2B5E;
extern long G_h01_B38A;
extern char G_h01_B388;
extern char G_h01_B389;
extern long G_h01_B38E;
extern long G_h01_B392;
extern long G_h01_B380;
extern long G_h01_2B66;
extern long G_h01_B31C;
extern char G_h01_B31A;
extern char G_h01_B31B;
extern long G_h01_B320;
extern long G_h01_B324;
extern long G_h01_B27E;
extern long G_h01_B312;
extern long G_h01_A7CE;
extern long G_h01_46DA;
extern long G_h01_B39A;
extern long G_h00_6200;
extern long F_h00_86DC();
extern int F_h00_8820();
extern int F_h00_894A();
extern int F_h00_8A1E();
extern int F_h00_8728();
recovered()
{
 long err,i,j,k,l,m;
 F_h00_57B6();
 G_h01_B1F0=-1;
 if(!(G_h01_B284=F_h00_8794(0L,0L))) return 0;
 G_h01_B288=F_h00_887E(G_h01_B284);
 if(!G_h01_B288) { F_h00_8820(G_h01_B284); return 0; }
 G_h01_B336=(long)&G_h01_B28C;
 G_h01_B33A=(long)F_h00_579E;
 G_h01_B331=0x33;
 err=F_h00_89BA("input.device",0L,G_h01_B288,0L);
 if(err) return 0;
 ((struct Request *)G_h01_B288)->command=9;
 ((struct Request *)G_h01_B288)->data=(long)&G_h01_B328;
 F_h00_894A(G_h01_B288);
 G_h01_B28E=0;
 G_h01_B28C=0;
 G_h01_B348=(long)"Audio 0";
 G_h01_B346=2;
 G_h01_B347=0;
 G_h01_B34C=(long)&G_h01_2B4E;
 G_h01_B350=(long)F_h00_55D6;
 F_h00_8A1E(7L,&G_h01_B33E);
 G_h01_B35E=(long)"Audio 1";
 G_h01_B35C=2;
 G_h01_B35D=0;
 G_h01_B362=(long)&G_h01_2B56;
 G_h01_B366=(long)F_h00_5646;
 F_h00_8A1E(8L,&G_h01_B354);
 G_h01_B374=(long)"Audio 2";
 G_h01_B372=2;
 G_h01_B373=0;
 G_h01_B378=(long)&G_h01_2B5E;
 G_h01_B37C=(long)F_h00_56B6;
 F_h00_8A1E(9L,&G_h01_B36A);
 G_h01_B38A=(long)"Audio 3";
 G_h01_B388=2;
 G_h01_B389=0;
 G_h01_B38E=(long)&G_h01_2B66;
 G_h01_B392=(long)F_h00_5726;
 F_h00_8A1E(10L,&G_h01_B380);
 F_h00_5868();
 G_h01_B31C=(long)"IT V Blank";
 G_h01_B31A=2;
 G_h01_B31B=0;
 G_h01_B320=(long)&G_h01_B27E;
 G_h01_B324=(long)F_h00_615E;
 F_h00_8728(5L,&G_h01_B312);
 i=0;
 do { i++; } while(i<100000L);
 F_h00_0FDE(1);
 G_h01_A7CE=F_h00_86DC("dt1:dt1.as",1005L);
 F_h00_0FDE(1);
 G_h01_46DA=G_h01_A7CE;
 F_h00_2816(G_h01_46DA);
 F_h00_4AF0();
 G_h01_B39A=(long)&G_h00_6200;
}

