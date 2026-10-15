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
