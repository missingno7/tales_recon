struct Pair {
    int first;
    int second;
};

extern char G_h01_5E5E;
extern char G_h01_451B;
extern int G_h01_451A;
extern int G_h01_451C;
extern int G_h01_451E;
extern int G_h01_4520;
extern int G_h01_4522;
extern struct Pair G_h01_A768;

extern int F_h00_4376();
extern int F_h00_34E0();
extern int F_h00_435E();

int recovered(px, py)
int *px, *py;
{
    G_h01_5E5E = 0;
    G_h01_451A = F_h00_4376();
    if (G_h01_451A & 0x80)
        return 1;
    switch (G_h01_451A & 0x3f) {
    case 1:
        (*py)--;
        G_h01_4522 = -1;
        G_h01_4520 = 0;
        break;
    case 2:
        (*py)--;
        *px += 2;
        G_h01_4522 = -1;
        G_h01_4520 = 1;
        break;
    case 3:
        (*px)++;
        G_h01_4520 = 1;
        G_h01_4522 = 0;
        break;
    case 4:
        (*py)++;
        *px += 2;
        G_h01_4522 = 1;
        G_h01_4520 = 1;
        break;
    case 5:
        (*py)++;
        G_h01_4522 = 1;
        G_h01_4520 = 0;
        break;
    case 6:
        (*py)++;
        *px -= 2;
        G_h01_4522 = 1;
        G_h01_4520 = -1;
        break;
    case 7:
        (*px)--;
        G_h01_4520 = -1;
        G_h01_4522 = 0;
        break;
    case 8:
        (*py)--;
        *px -= 2;
        G_h01_4520 = -1;
        G_h01_4522 = -1;
        break;
    case 0:
    default:
        G_h01_451C = 0;
        G_h01_451A = 0;
        G_h01_4522 = 0;
        G_h01_4520 = 0;
        G_h01_451E = 0;
        break;
    }
    if ((G_h01_451A & 0x3f) != 0 && G_h01_451C < 0x100) {
        if (G_h01_451C != 0) {
            switch (G_h01_451A & 0x3f) {
            case 2:
            case 4:
                G_h01_4520++;
                break;
            case 6:
            case 8:
                G_h01_4520--;
                break;
            }
        }
        G_h01_451C++;
    }
    if (G_h01_451C == 0) {
        G_h01_451C = 1;
        G_h01_451E = 1;
    }
    *px = *px + (G_h01_451C - 1) * G_h01_4520;
    *py = *py + (G_h01_451C - 1) * G_h01_4522;
    if (G_h01_451E) {
        G_h01_451C = 0;
        G_h01_451E = 0;
    }
    if (*px < 0x20)
        *px = 0x20;
    else if (*px > 0x11d)
        *px = 0x11d;
    if (*py < 0x1c)
        *py = 0x1c;
    else if (*py > 0x97)
        *py = 0x97;
    G_h01_A768.first = *px - 8;
    G_h01_A768.second = *py - 8;
    F_h00_34E0(&G_h01_A768);
    F_h00_435E();
    G_h01_5E5E = 1;
    return 0;
}
