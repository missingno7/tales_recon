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

extern struct Item G_h01_2466[1];
extern int G_h01_14B0;
extern int G_h01_14B2;
extern int G_h01_14B8;
extern int G_h01_14BC;
extern int G_h01_14C0;
extern int G_h01_14C2;
extern int G_h01_14D6;
extern int G_h01_0A3E;
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

    item = G_h01_2466 + index;
    result = 0;
    y = (8 >> G_h01_14B2) + G_h01_14C0;
    x = G_h01_14C2 + 16;
    if (G_h01_14B0 == 19)
        x += 8;
    else if (G_h01_14B0 == 18)
        y -= 16;

    if (item->state != 45 && G_h01_14B0 != 2 &&
        G_h01_14B0 != 6 && G_h01_14B0 != 7) {
        if (F_h11_25F8(item->value34 + 16,
                       item->value36,
                       y,
                       x,
                       item->value34 + 48,
                       item->value36 + 56) != 0) {
            if (G_h01_14B8 != 0) {
                G_h01_14B8 = 0;
                G_h01_14D6 = 0;
            }
            G_h01_14B0 = 45;
            F_h11_4B0C(45);
            item->state = 45;
            F_h11_41F6(8, &item->value10, 45,
                       item->value34, item->value36);
            F_h00_57D2(98);
            G_h01_0A3E = 3;
            result = 1;
        } else if (item->value0 == G_h01_14BC &&
                   ((G_h01_14C2 + 14) >> 5) == item->value2 &&
                   (G_h01_14B0 == 12 || G_h01_14B0 == 1 || G_h01_14B0 == 5)) {
            G_h01_14B0 = 14;
            F_h11_4B0C(14);
        }
    }
    return result;
}