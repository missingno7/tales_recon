struct Entry { unsigned char kind; unsigned char active; int pos; char rest[2]; };
extern long G_h01_46CE;
extern long G_h01_46D2;
extern struct Entry *G_h01_6F3C;
extern struct Entry G_h01_12B4;
extern struct Entry G_h01_12BA;
extern int G_h01_34E2;
extern int G_h01_34E4;
extern int G_h01_704E;
extern int BltBitMap();

recovered(P)
int P;
{
    int x, y, w, h, x2, y2, u1, u2, i, flag;
    struct Entry *p;

    for (i = P; i < P + 5 && i < 25; i++) {
        p = G_h01_6F3C + i;
        flag = 0;
        switch (p->kind) {
        case 4:
            x = p->pos;
            y = 160 - (i - P) * 40 - 20;
            if (y < 0)
                y = 0;
            switch (p->active) {
            case 0:
                x2 = G_h01_704E + 16;
                y2 = 160 - (i - P) * 40 - 16;
                if (y2 < 0)
                    y2 = 0;
                BltBitMap(G_h01_46CE, (long)x2, (long)y2, G_h01_46D2, (long)x2, (long)y2, 32L, 16L, 192L, 255L, 0L);
                w = 64;
                h = 24;
                flag = 1;
                break;
            case 1:
            case 2:
                w = 64;
                h = 24;
                flag = 1;
                break;
            case 3:
                x2 = G_h01_704E + 16;
                y2 = 160 - (i - P) * 40 - 16;
                if (y2 < 0)
                    y2 = 0;
                BltBitMap(G_h01_46CE, (long)x2, (long)y2, G_h01_46D2, (long)x2, (long)y2, 32L, 16L, 192L, 255L, 0L);
                w = 64;
                h = 24;
                flag = 1;
                break;
            }
            if (flag)
                BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, (long)w, (long)h, 192L, 255L, 0L);
            break;
        case 2:
            y = 160 - (i - P) * 40 - 30;
            if (y < 0)
                y = 0;
            x = p->active < 10 ? p->pos + 14 : p->pos - 20;
            w = 48;
            h = 33;
            BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, (long)w, (long)h, 192L, 255L, 0L);
            break;
        case 3:
            y = 160 - (i - P) * 40 - 36;
            if (y < 0)
                y = 0;
            x = p->pos;
            w = 40;
            h = 40;
            BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, (long)w, (long)h, 192L, 255L, 0L);
            break;
        case 6:
            x = p->pos;
            y = 160 - (i - P) * 40 - 36;
            if (y < 0)
                y = 0;
            w = 64;
            h = 40;
            BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, (long)w, (long)h, 192L, 255L, 0L);
            break;
        case 9:
            if (p->active == 1 || p->active == 2) {
                y = 160 - (i - P) * 40 - 12;
                x = p->pos;
                BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, 16L, 16L, 192L, 255L, 0L);
                p->active++;
            }
            break;
        case 0:
        case 1:
        case 5:
        case 7:
        case 8:
        default:
            break;
        }
    }

    flag = 0;
    p = &G_h01_12B4;
    y = 0;
    x = p->pos - 16;
    if (x < 0)
        x = 0;
    switch (p->active) {
    case 0:
        if (x + 56 > 319)
            BltBitMap(G_h01_46CE, (long)(x + 8), 136L, G_h01_46D2, (long)(x + 8), 136L, (long)(320 - (x + 8)), 32L, 192L, 255L, 0L);
        else
            BltBitMap(G_h01_46CE, (long)(x + 8), 136L, G_h01_46D2, (long)(x + 8), 136L, 48L, 32L, 192L, 255L, 0L);
        w = 72;
        h = 32;
        flag = 1;
        break;
    case 1:
    case 2:
        w = 72;
        h = 32;
        flag = 1;
        break;
    case 4:
        w = 72;
        h = 32;
        flag = 1;
        x2 = p->pos + 18;
        y2 = 40;
        BltBitMap(G_h01_46CE, (long)x2, (long)y2, G_h01_46D2, (long)x2, (long)y2, 16L, 16L, 192L, 255L, 0L);
        break;
    case 5:
        w = 72;
        h = 32;
        flag = 1;
        x2 = p->pos + 18;
        BltBitMap(G_h01_46CE, (long)x2, 0L, G_h01_46D2, (long)x2, 0L, 24L, 168L, 192L, 255L, 0L);
        break;
    }
    BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, (long)w, (long)h, 192L, 255L, 0L);

    p = &G_h01_12BA;
    switch (p->active) {
    case 0:
        break;
    case 1:
        x = p->pos;
        y = 160 - (G_h01_34E2 - P) * 40 - G_h01_34E4 - 22;
        break;
    case 2:
        x = p->pos - 2;
        y = 160 - (G_h01_34E2 - P) * 40 - G_h01_34E4 - 14;
        break;
    case 3:
        x = p->pos + 2;
        y = 160 - (G_h01_34E2 - P) * 40 - G_h01_34E4 - 14;
        break;
    }

    if (P == 0) {
        BltBitMap(G_h01_46CE, 0L, 148L, G_h01_46D2, 0L, 148L, 32L, 20L, 192L, 255L, 0L);
        BltBitMap(G_h01_46CE, 288L, 148L, G_h01_46D2, 288L, 148L, 32L, 20L, 192L, 255L, 0L);
    }

    x -= 8;
    y -= 8;
    w = 32;
    h = 32;
    if (y + h > 0 && y < 168) {
        if (y < 0) {
            h += y;
            y = 0;
        } else if (y + h > 168) {
            h = 168 - y;
        }
        if (x + w > 0 && x < 320) {
            if (x < 0) {
                x = 0;
            } else if (x + w > 319) {
                x = 287;
            }
            BltBitMap(G_h01_46CE, (long)x, (long)y, G_h01_46D2, (long)x, (long)y, (long)w, (long)h, 192L, 255L, 0L);
        }
    }
}
