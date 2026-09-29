struct ClusterRecord {
    int value0;
    int value2;
    char pad4[14];
    char pad18[26];
    int value2c;
    int value2e;
    int state30;
    int value32;
};

extern int G_h01_7A92;
extern int G_h01_8A3C;
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BA;
extern int G_h01_94C0;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_25F8();
extern int F_h11_37A0();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_5C42();

recovered(index)
int index;
{
    struct ClusterRecord *record;
    int x, y, update, state;

    record = &G_h01_8BEC[index];
    update = 0;
    state = record->state30;

    switch (record->state30) {
    case 1:
        if (((G_h01_94C0 + 14) >> 5) == ((int *)record)[1] &&
            ((int *)record)[0] == G_h01_94BA) {
            G_h01_94B4 = 1;
            G_h01_94D6 = index;
            state = 3;
            update = 1;
        }
        break;
    case 3:
        if (((int *)record)[0] == G_h01_94BA || G_h01_94AE == 18) {
            if (G_h01_94B6) {
                state = 1;
                G_h01_94B4 = 0;
                G_h01_94D6 = 0;
                G_h01_37F0 = 0;
                G_h01_37EE = 0;
                update = 1;
            } else {
                update = 1;
                F_h11_4474(24, &record->pad18[0]);
            }
        }
        break;
    }

    if (record->state30 != state) {
        record->state30 = state;
        F_h11_41F6(24, &record->pad18[0], state,
                   record->value2c, record->value2e);
    }

    if (G_h01_7A92) {
        F_h11_5C42(index, 0);
        return;
    }
    if (update) {
        F_h11_5C42(index, 3);
        return;
    }
    if (G_h01_8A3C &&
        F_h11_37A0(G_h01_8A3C, &x, &y) &&
        F_h11_25F8(record->value2c, record->value2e - 6,
                   x, y, record->value2c + 64,
                   record->value2e + 32)) {
        F_h11_5C42(index, 3);
    }
}
