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


struct TextBlock {
    unsigned int length;
    char *data;
};
extern long G_h01_46DA;
extern unsigned int G_h01_A7DA;
extern unsigned int G_h01_A7DC;
extern unsigned int G_h01_A7DE;
extern unsigned int G_h01_A7E0;
extern unsigned int G_h01_A7E4;
extern unsigned int G_h01_A7D8;
extern long G_h01_A7D6;
extern long G_h01_542A;
extern char G_h01_0971;
extern int F_h00_287C();
extern int F_h00_3674();
extern long F_h00_3B16();
extern long F_h00_3870();
extern int F_h00_3A6E();
extern void F_h00_404A();
extern void F_h00_4184();
extern int F_h00_3C4C();
extern int F_h04_27FE();
extern long F_h00_86F6();
extern int F_h00_7BD8();

long recovered(index, destination)
int index;
char *destination;
{
    unsigned int width;
    unsigned int stride;
    unsigned int height;
    unsigned int multiplier;
    int mode;
    unsigned int length;
    char *result;
    char *bitmap;
    char *graphic;
    struct TextBlock *block;

    if (F_h00_287C(index, G_h01_46DA))
        F_h00_3674(index + 1000);
    switch (G_h01_A7DA) {
    case 1:
        bitmap = destination;
        width = G_h01_A7DC;
        height = G_h01_A7DE;
        if (bitmap == 0) {
            bitmap = F_h00_3B16(width, height);
            if (bitmap == 0)
                F_h00_3674(index + 2000);
        }
        F_h00_404A(bitmap);
        result = bitmap;
        break;
    case 2:
        graphic = destination;
        width = G_h01_A7DC;
        height = G_h01_A7DE;
        multiplier = G_h01_A7E0;
        if (graphic == 0) {
            graphic = F_h00_3870(&G_h01_542A, 54L);
            if (graphic == 0)
                F_h00_3674(index + 3000);
        }
        stride = width >> 3;
        *(int *)graphic = 0;
        *(int *)(graphic + 2) = 0;
        *(unsigned int *)(graphic + 4) = stride;
        *(unsigned int *)(graphic + 6) = height;
        *(unsigned int *)(graphic + 8) = stride * multiplier;
        *(unsigned int *)(graphic + 10) = height;
        *(char *)(graphic + 13) = G_h01_0971;
        F_h00_3A6E(graphic + 16, stride * multiplier, height);
        if (*(long *)(graphic + 16) == 0)
            F_h00_3674(index + 4000);
        *(char *)(graphic + 52) = 0;
        F_h00_404A(graphic + 8);
        result = graphic;
        break;
    case 3:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7D8;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        F_h00_86F6(G_h01_46DA, block->data, G_h01_A7D6);
        break;
    case 4:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7DC;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        mode = 1;
        F_h00_3C4C(mode, G_h01_46DA, block->data, length);
        break;
    case 5:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7DC;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        F_h00_4184(G_h01_A7D6, block->data);
        break;
    case 6:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7E4;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        F_h00_86F6(G_h01_46DA, block->data, G_h01_A7D6);
        break;
    default:
        F_h00_7BD8("LIT: #%d\n", index);
        F_h00_3674(G_h01_A7DA + 5000);
        break;
    }
    return result;
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

/* resident_F_3870 candidate: alloc-side sibling of resident_F_3930. The allocation
   result is a long; the failure report prints the range and size. Callee and DATA
   names are mechanical. */
extern int F_h00_701A();
extern long F_h00_875C();
extern int F_h00_3A06();
extern int F_h04_27FE();
extern long G_h01_5446;

long F_h00_3870(a, c)
long a;
long c;
{
    long r;

    r = F_h00_875C(a, c);
    if (r == 0) {
        F_h00_701A("alloc: %lx - %lx,  %ld ($%lx)\n", r, r + c, c, c);
        F_h00_701A("FAILED:  %ld ($%lx) bytes free\n", G_h01_5446, G_h01_5446);
        F_h00_3A06();
        F_h04_27FE("Memory Alloc Failure");
    }
    return r;
}

/* resident_F_3930 candidate: pointer range argument, long arithmetic for the end address; callees and DATA names are mechanical. */
extern int F_h00_701A();
extern int F_h00_8938();
extern int F_h04_27FE();
extern long G_h01_543E;
extern long G_h01_5442;

F_h00_3930(a, b, c)
long a;
char *b;
long c;
{
    if (b < G_h01_543E || b > G_h01_5442) {
        F_h00_701A("dealloc: %lx - %lx,  %ld ($%lx)\n", b, (long)b + c, c, c);
        F_h04_27FE("BAD POINTER\n");
    } else {
        F_h00_8938(a, b, c);
    }
}

extern long G_h01_5446;
extern int F_h00_701A();
F_h00_39C0(label)
long label;
{
 F_h00_701A("%s  mem=%ld (%lx)\n",label,G_h01_5446,G_h01_5446);
}

extern long G_h01_5446;
long F_h00_39F8()
{
 return G_h01_5446;
}

/* Candidate for resident_F_3A06: the two referenced printable runs are written as
   string literals (PC-relative in the code hunk), the list head stays an absolute
   long global. Callee and DATA names are mechanical. */
extern long G_h01_543A;
extern int F_h00_701A();

F_h00_3A06()
{
    long node;

    F_h00_701A("\nMEM LIST\n");
    node = G_h01_543A;
    while (node != 0) {
        F_h00_701A("%lx:  %ld ($%lx)\n", node, *(long *)((char *)node + 4), *(long *)((char *)node + 4));
        node = *(long *)node;
    }
}

extern long F_h00_3870();
extern int F_h00_3674();
extern long G_h01_542A;
extern int G_h01_0970;

F_h00_3A6E(p, c, e)
long *p;
unsigned int c;
unsigned int e;
{
    int i;
    long r;

    r = F_h00_3870(&G_h01_542A, (long)(unsigned int)(c * e * G_h01_0970));
    if (r == 0)
        F_h00_3674(6000);
    for (i = 0; i < G_h01_0970; i++)
        p[i] = r + (unsigned int)(i * c * e);
}

struct resident_entry {
    unsigned short word0;
    unsigned char byte2;
    unsigned char byte3;
};

extern long F_h00_86F6();
extern int F_h00_3E9C();
extern int F_h00_4032();
extern unsigned short G_h01_1E2E;
extern unsigned short G_h01_B1D8;
extern unsigned short G_h01_B1DA;
extern unsigned short G_h01_B1DC;
extern unsigned short G_h01_B1E4;
extern unsigned short G_h01_B1E6;
extern long G_h01_B1E0;
extern long G_h01_ADCA;
extern long G_h01_544A;
extern char *G_h01_A9BE;
extern unsigned short G_h01_A9C2;
extern unsigned char G_h01_A9C3;
extern unsigned char G_h01_A9CA[1];
extern unsigned short G_h01_ADCE;
extern unsigned char G_h01_ADCF;
extern unsigned short G_h01_ADD0;
extern unsigned short G_h01_ADD2;
extern unsigned short G_h01_ADD4;
extern unsigned short G_h01_ADD6;
extern unsigned char G_h01_ADD8[1];
extern unsigned char G_h01_B1DE;

long F_h00_3C4C(p1, p2, p3, p4)
unsigned short p1;
long p2;
long p3;
unsigned short p4;
{
    G_h01_B1E6 = p4;
    G_h01_B1E4 = p1;
    G_h01_ADCA = p2;
    G_h01_B1E0 = p3;
    G_h01_A9BE = (char *)p3;
    G_h01_B1D8 = 0;
    G_h01_ADD4 = 0x102;
    G_h01_ADD6 = 0;
    G_h01_B1DA = 9;
    G_h01_B1DC = 0x200;
    G_h01_1E2E = 0;
    F_h00_86F6(G_h01_ADCA, G_h01_A9CA, (unsigned long)0x400);

    while ((G_h01_A9C2 = F_h00_3E9C()) != 0x101) {
        if (G_h01_A9C2 == 0x100) {
            G_h01_B1DA = 9;
            G_h01_B1DC = 0x200;
            G_h01_ADD4 = 0x102;
            G_h01_A9C2 = F_h00_3E9C();
            G_h01_ADD0 = G_h01_A9C2;
            G_h01_ADCE = G_h01_A9C2;
            G_h01_B1DE = G_h01_A9C3;
            F_h00_4032(G_h01_B1DE);
            continue;
        }
        G_h01_ADD2 = G_h01_A9C2;
        G_h01_ADCE = G_h01_A9C2;
        if (G_h01_A9C2 >= G_h01_ADD4) {
            G_h01_ADCE = G_h01_ADD0;
            G_h01_ADD8[G_h01_ADD6++] = G_h01_B1DE;
        }
        while (G_h01_ADCE > 0xff) {
            G_h01_ADD8[G_h01_ADD6++] = ((unsigned char *)(G_h01_544A + ((unsigned long)G_h01_ADCE << 2)))[2];
            G_h01_ADCE = ((struct resident_entry *)G_h01_544A)[G_h01_ADCE].word0;
        }
        G_h01_B1DE = G_h01_ADCF;
        G_h01_ADD8[G_h01_ADD6++] = G_h01_B1DE;
        while (G_h01_ADD6 != 0) {
            G_h01_ADD6--;
            F_h00_4032(G_h01_ADD8[G_h01_ADD6]);
        }
        ((unsigned char *)(G_h01_544A + ((unsigned long)G_h01_ADD4 << 2)))[2] = G_h01_B1DE;
        ((struct resident_entry *)G_h01_544A)[G_h01_ADD4].word0 = G_h01_ADD0;
        G_h01_ADD4++;
        G_h01_ADD0 = G_h01_ADD2;
        if (G_h01_ADD4 >= G_h01_B1DC && G_h01_B1DA < 0xc) {
            G_h01_B1DA++;
            G_h01_B1DC *= 2;
        }
    }
    return (long)G_h01_A9BE - G_h01_B1E0;
}

extern long F_h00_86F6();
extern unsigned short G_h01_1E26[1];
extern unsigned short G_h01_1E2E;
extern unsigned short G_h01_A9C2;
extern unsigned short G_h01_A9C4;
extern unsigned short G_h01_A9C6;
extern unsigned short G_h01_A9C8;
extern unsigned char G_h01_A9CA[1];
extern unsigned char G_h01_A9CB;
extern unsigned char G_h01_A9CC[1];
extern unsigned char G_h01_A9CD;
extern long G_h01_ADCA;
extern unsigned short G_h01_B1DA;

F_h00_3E9C()
{
    unsigned long bits;

    G_h01_A9C2 = G_h01_1E2E >> 3;
    G_h01_A9C8 = G_h01_1E2E & 7;
    G_h01_1E2E += G_h01_B1DA;
    if (G_h01_A9C2 >= 0x3fd) {
        G_h01_1E2E = G_h01_A9C8 + G_h01_B1DA;
        G_h01_A9C6 = 0x400 - G_h01_A9C2;
        G_h01_A9CA[0] = G_h01_A9CA[G_h01_A9C2];
        G_h01_A9CB = G_h01_A9CA[G_h01_A9C2 + 1];
        G_h01_A9CC[0] = G_h01_A9CA[G_h01_A9C2 + 2];
        G_h01_A9CD = G_h01_A9CA[G_h01_A9C2 + 3];
        F_h00_86F6(G_h01_ADCA, G_h01_A9CA + G_h01_A9C6, (unsigned long)G_h01_A9C2);
        G_h01_A9C2 = 0;
    }
    G_h01_A9C4 = G_h01_A9CA[G_h01_A9C2 + 1];
    G_h01_A9C4 <<= 8;
    G_h01_A9C4 += G_h01_A9CA[G_h01_A9C2];
    G_h01_A9C2 = G_h01_A9CC[G_h01_A9C2];
    bits = (((unsigned long)G_h01_A9C2 << 16) + G_h01_A9C4) >> G_h01_A9C8;
    return G_h01_1E26[(unsigned short)(G_h01_B1DA - 9)] & (unsigned short)bits;
}

/* Baseline for resident_F_4032: a byte-sized argument is stored through an
   absolute-data char pointer that is post-incremented in place. */
extern char *G_h01_A9BE;

F_h00_4032(arg)
char arg;
{
    *G_h01_A9BE++ = arg;
}

extern int G_h01_B1E8;
char F_h00_411E();

struct View404A {
    unsigned int width, rows;
    unsigned char flags, depth;
    int reserved;
    char *planes[8];
};

void F_h00_404A(bitmap)
register struct View404A *bitmap;
{
    register unsigned int plane, row, remaining;
    register char token;
    register char *out;
    char value;
    int literal;
    unsigned int count, column;
    unsigned char stride;

    G_h01_B1E8 = 1024;
    stride = (char)bitmap->width;
    remaining = 0;
    count = bitmap->rows * bitmap->width / stride;
    for (column = 0; column < stride; ++column) {
        for (plane = 0; plane < bitmap->depth; ++plane) {
            out = bitmap->planes[plane] + column;
            for (row = 0; row < count; ++row) {
                if (remaining == 0) {
                    token = F_h00_411E();
                    remaining = token;
                    remaining &= 127;
                    if (token & 128)
                        literal = 1;
                    else {
                        literal = 0;
                        value = F_h00_411E();
                    }
                }
                --remaining;
                if (literal) {
                    token = F_h00_411E();
                    *out = token;
                } else
                    *out = value;
                out += stride;
            }
        }
    }
}

extern int G_h01_B1E8;
extern char *G_h01_3AB4;
extern long G_h01_46DA;
extern char G_h01_A9CA[1024];
extern long F_h00_86F6();
extern int F_h00_3674();

char
F_h00_411E()
{
    long amount;

    if (++G_h01_B1E8 >= 1024) {
        amount = F_h00_86F6(G_h01_46DA, G_h01_A9CA, 1024L);
        if (amount <= 0)
            F_h00_3674(8000);
        G_h01_B1E8 = 0;
        G_h01_3AB4 = G_h01_A9CA;
    } else
        ++G_h01_3AB4;
    return *G_h01_3AB4;
}

extern int G_h01_B1E8;
extern int G_h01_1E32[8];
extern int G_h01_1E42[49];
extern char F_h00_411E();

void F_h00_4184(length, out)
long length;
char *out;
{
    register int nibble, delta, bit1, bit2, bit4;
    int sample, index, half, step, quarter, magnitude, i;
    unsigned char packed;

    sample = 0;
    index = 1;
    G_h01_B1E8 = 1024;
    for (i = 0; i < length; ++i) {
        packed = F_h00_411E();
        nibble = (packed >> 4) & 15;
        magnitude = (bit4 = nibble & 4) + (bit2 = nibble & 2) + (bit1 = nibble & 1);
        step = G_h01_1E42[index - 1];
        half = step >> 1;
        quarter = half >> 1;
        delta = quarter >> 1;
        index += G_h01_1E32[magnitude];
        if (index > 0 && index <= 49) {
        } else
            index = index < 1 ? 1 : 49;
        if (bit1) delta += quarter;
        if (bit2) delta += half;
        if (bit4) delta += step;
        sample += nibble & 8 ? -delta : delta;
        *out = sample >> 4;
        out++;

        nibble = packed;
        nibble &= 15;
        magnitude = (bit4 = nibble & 4) + (bit2 = nibble & 2) + (bit1 = nibble & 1);
        step = G_h01_1E42[index - 1];
        half = step >> 1;
        quarter = half >> 1;
        delta = quarter >> 1;
        index += G_h01_1E32[magnitude];
        if (index > 0 && index <= 49) {
        } else
            index = index < 1 ? 1 : 49;
        if (bit1) delta += quarter;
        if (bit2) delta += half;
        if (bit4) delta += step;
        sample += nibble & 8 ? -delta : delta;
        *out = sample >> 4;
        out++;
    }
}

