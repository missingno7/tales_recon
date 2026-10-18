extern int G_h01_B1E8;
char arc_next_byte();

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
                    token = arc_next_byte();
                    remaining = token;
                    remaining &= 127;
                    if (token & 128)
                        literal = 1;
                    else {
                        literal = 0;
                        value = arc_next_byte();
                    }
                }
                --remaining;
                if (literal) {
                    token = arc_next_byte();
                    *out = token;
                } else
                    *out = value;
                out += stride;
            }
        }
    }
}
