extern int G_h01_B1E8;
char F_h00_411E();

struct View404A {
    unsigned int width, rows;
    unsigned char flags, depth;
    int reserved;
    char *planes[8];
};

void recovered(bitmap)
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

