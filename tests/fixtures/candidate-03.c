struct Object {
    char pad00[0x1e];
    int value1e;
    int value20;
    char pad24[10];
    int state2c;
    int gate2e;
    int state30;
    int y32;
    int x34;
    char pad36[2];
    int value38;
    char pad3a[2];
    int value3c;
    char pad3e[2];
};

extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern struct Object G_h01_9FCE[1];
extern int F_h11_262E();
extern int F_h11_41F6();
extern int F_h11_4B0C();
extern int F_h11_4696();
extern int F_h11_407C();

recovered(index)
int index;
{
    int left;
    int top;
    struct Object *object;
    int hit;

    left = (8 >> G_h01_94B0) + G_h01_94BE;
    top = G_h01_94C0 + 16;
    object = &G_h01_9FCE[index];
    hit = 0;
    if (object->gate2e != 0) {
        hit = F_h11_262E(left - 4, top - 6, left + 4, top + 6,
                         object->y32 + 4, object->x34 + 2,
                         object->y32 + 8, object->x34 + 12);
    }
    if (hit != 0) {
        if (object->state30 == 0) {
            object->state2c = 0x12;
            F_h11_41F6(2, (char *)object + 2, 0x12,
                       object->value1e, object->value20);
        } else if (G_h01_94B6 != 0) {
            F_h11_407C(G_h01_94D4);
            G_h01_94B6 = 0;
        }
        G_h01_94AE = 2;
        F_h11_4B0C(2);
        object->gate2e = 0;
        F_h11_4696(object->value38, object->value3c, 0x18, 0x10,
                   index + 12);
    }
    return hit;
}