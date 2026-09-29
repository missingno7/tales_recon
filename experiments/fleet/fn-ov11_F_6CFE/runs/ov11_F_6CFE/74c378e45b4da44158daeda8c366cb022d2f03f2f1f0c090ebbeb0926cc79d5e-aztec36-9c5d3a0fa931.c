struct Record { int unused0, unused2; int left, right, top, bottom; int initial_x, initial_y, offset_y; int x, y, flags; int unused24, unused26, unused28; int step, active; };
extern int G_h01_94AE;
extern int G_h01_94D8;
extern struct Record G_h01_A554[10];
extern int F_h00_57D2();
extern int F_h11_4696();
extern int F_h11_5962();
extern int F_h11_727A();
extern int F_h11_729C();

recovered(index)
int index;
{
    struct Record *record;
    int dx;
    int dy;

    record = &G_h01_A554[index];
    record->flags += record->unused28;
    if (record->flags > record->unused26) {
        record->unused28 = record->unused28 * -1;
        if (G_h01_94AE == 8 && index == G_h01_94D8)
            F_h00_57D2(0x5a);
    } else {
        if (record->flags < record->unused24) {
            record->unused28 = record->unused28 * -1;
            if (G_h01_94AE == 8 && index == G_h01_94D8)
                F_h00_57D2(0x5d);
        }
    }

    record->x = record->initial_x +
        (F_h11_729C(record->flags - 0x80) * record->offset_y) / 0x100;
    record->y = record->initial_y +
        (F_h11_727A(record->flags - 0x80) * record->offset_y) / 0x100;

    if (record->initial_x > record->right) {
        dx = record->initial_x - record->right + 0x10;
    } else {
        dx = record->right - record->initial_x;
        record->right = record->initial_x;
    }
    dy = record->bottom - record->initial_y + 1;
    F_h11_4696(record->right, record->initial_y, dx, dy, index + 0x1c);

    if (record->unused0)
        F_h11_5962(record->unused0, 4);
    if (record->unused2)
        F_h11_5962(record->unused2, 4);
}
