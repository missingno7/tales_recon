/* Direct recovery candidate for ov09_F_26C6 (plain structured C, h1 baseline). */
extern int draw_masked_sprite();

struct ov09_a {
    unsigned char f0;
    char f1_3[3];
    unsigned char f4;
    char f5_7[3];
    int f8;
    int f10;
};

struct ov09_b {
    int x;
    int y;
    char f4_33[48];
    unsigned char flag34;
};

recovered(a, b)
struct ov09_a *a;
struct ov09_b *b;
{
    int x;
    int y;

    switch (a->f0) {
    case 1:
        x = 8;
        y = 80 - a->f10;
        break;
    case 2:
        x = 14;
        y = 108 - a->f10;
        break;
    case 3:
        x = 44;
        y = 124 - a->f10;
        break;
    case 4:
        x = 78 - a->f8;
        y = 124 - a->f10;
        break;
    case 5:
        x = 140;
        y = 106 - a->f10;
        break;
    case 6:
        x = 146;
        y = 64 - a->f10;
        break;
    case 7:
        x = 144;
        y = 106 - a->f10;
        break;
    case 8:
        x = 206 - a->f8;
        y = 106 - a->f10;
        break;
    case 9:
        x = 271 - a->f8;
        y = 121 - a->f10;
        break;
    case 10:
        x = 272;
        y = 70 - a->f10;
        break;
    case 11:
        x = 232;
        y = 121 - a->f10;
        break;
    case 12:
        x = 217;
        y = 151 - a->f10;
        break;
    case 13:
        x = 240;
        y = 36;
        break;
    case 14:
        x = 0;
        y = 176 - a->f10;
        break;
    default:
        x = 100;
        y = 100;
        break;
    }
    b->flag34 = a->f4;
    b->x = x;
    b->y = y;
    draw_masked_sprite(b);
}
