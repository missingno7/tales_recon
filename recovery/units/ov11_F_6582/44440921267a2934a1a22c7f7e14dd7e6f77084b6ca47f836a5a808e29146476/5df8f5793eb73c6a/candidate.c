struct Item {
    int value0;
    int value2;
    char pad4[6];
    int value10;
    char pad12[20];
    int state;
    int value34;
    int value36;
    char pad38[2];
};

extern struct Item G_h01_A464[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_8A3C;
extern int F_h11_25F8();
extern int F_h11_4B0C();
extern int F_h11_41F6();
extern int F_h00_57D2();

recovered(index)
int index;
{
    struct Item *item;
    int result;
    int y;
    int x;

    item = G_h01_A464 + index;
    result = 0;
    y = (8 >> G_h01_94B0) + G_h01_94BE;
    x = G_h01_94C0 + 16;
    if (G_h01_94AE == 19)
        x += 8;
    else if (G_h01_94AE == 18)
        y -= 16;

    if (item->state != 45 && G_h01_94AE != 2 &&
        G_h01_94AE != 6 && G_h01_94AE != 7) {
        if (F_h11_25F8(item->value34 + 16,
                       item->value36,
                       y,
                       x,
                       item->value34 + 48,
                       item->value36 + 56) != 0) {
            if (G_h01_94B6 != 0) {
                G_h01_94B6 = 0;
                G_h01_94D4 = 0;
            }
            G_h01_94AE = 45;
            F_h11_4B0C(G_h01_94AE);
            item->state = 45;
            F_h11_41F6(8, &item->value10, 45,
                       item->value34, item->value36);
            F_h00_57D2(98);
            G_h01_8A3C = 3;
            result = 1;
        } else if (item->value0 == G_h01_94BA &&
                   ((G_h01_94C0 + 14) >> 5) == item->value2 &&
                   (G_h01_94AE == 12 || G_h01_94AE == 1 || G_h01_94AE == 5)) {
            G_h01_94AE = 14;
            F_h11_4B0C(14);
        }
    }
    return result;
}