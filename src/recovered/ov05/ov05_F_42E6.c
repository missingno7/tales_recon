/* Declarations already used by canonical sources: candidate views, not provenance. */
extern unsigned int F_h00_463E();
extern int G_h01_5E64[1][2];

recovered(delta, kind, p)
int delta;
char kind;
int *p;
{
    int i;
    unsigned int r;

    i = *p;
    *p = *p + delta;
    if (i == 0)
        i = 2;
    if (kind == 21) {
        for (; i < *p; i++) {
            if (G_h01_5E64[i - 1][0] != 12 && G_h01_5E64[i - 1][0] != 14)
                G_h01_5E64[i][0] = 14;
            else
                G_h01_5E64[i][0] = 12;
        }
    } else {
        for (; i < *p; i++) {
            if (G_h01_5E64[i - 1][0] == 12) {
                G_h01_5E64[i][0] = 13;
                continue;
            }
            G_h01_5E64[i][0] = 0;
            r = F_h00_463E() % 100;
            if (G_h01_5E64[i - 1][0] == 1)
                G_h01_5E64[i][0] = 2;
            else if (G_h01_5E64[i - 1][0] == 3)
                G_h01_5E64[i][0] = 4;
            else if (G_h01_5E64[i - 1][0] == 5)
                G_h01_5E64[i][0] = 6;
            else if (G_h01_5E64[i - 1][0] == 7)
                G_h01_5E64[i][0] = 11;
            else if (G_h01_5E64[i - 1][0] == 11)
                G_h01_5E64[i][0] = 8;
            else if (G_h01_5E64[i - 1][0] == 9)
                G_h01_5E64[i][0] = 10;
            else if (kind == 7 && i < *p - 2 && F_h00_463E() % 100 < 95)
                G_h01_5E64[i][0] = 7;
            else if (kind == 3 && i < *p - 2 && F_h00_463E() % 100 < 75)
                G_h01_5E64[i][0] = 3;
            else if (kind == 1 && i < *p - 2 && F_h00_463E() % 100 < 75)
                G_h01_5E64[i][0] = 1;
            else if (r < 80) {
                if (i < *p - 2 && kind == 20) {
                    r = F_h00_463E() % 5;
                    switch (r) {
                    case 0:
                        G_h01_5E64[i][0] = 1;
                        break;
                    case 1:
                        G_h01_5E64[i][0] = 3;
                        break;
                    case 2:
                        G_h01_5E64[i][0] = 5;
                        break;
                    case 3:
                        G_h01_5E64[i][0] = 7;
                        break;
                    case 4:
                        G_h01_5E64[i][0] = 9;
                        break;
                    default:
                        break;
                    }
                }
            }
        }
    }
}
