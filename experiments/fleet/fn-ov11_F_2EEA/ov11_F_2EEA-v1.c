struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
struct Row { int field0; int field2; int field4; };
extern struct Record G_h01_9FCE[1];
extern int G_h01_1300[16];
extern struct Row G_h01_12C0[32];
extern int G_h01_34D8[16];
extern int G_h01_7A92;
extern int G_h01_8A3C;
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_A14E;
extern unsigned int F_h00_463E();
extern int F_h00_57D2();
extern int F_h11_25D6();
extern int F_h11_2E26();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_45EC();

recovered(index)
int index;
{
    int *object;
    int changed;
    int redraw;
    int near;
    object = (int *)&G_h01_9FCE[index];
    changed = 0;
    redraw = 0;
    near = F_h11_45EC(object + 1);
    object[31]--;
    switch (object[22]) {
    case 14:
        if (object[31] <= 0) {
            if (object[15] > G_h01_94BE && object[0] != 0 &&
                (int)F_h00_463E() % 100 < 75) {
                object[22] = 12; changed = 1; redraw = 1;
            } else if (object[15] > ((8 >> G_h01_94B0) + G_h01_94BE - 32) &&
                       (int)F_h00_463E() % 100 < 75) {
                object[22] = 16; object[16] = 8;
                G_h01_34D8[9] = (G_h01_94C0 - object[15] + 12) % 64;
                object[15] = object[17] + G_h01_34D8[9];
                changed = 1; redraw = 1;
            }
        }
        break;
    case 16:
        if (object[15] < ((8 >> G_h01_94B0) + G_h01_94BE - 64)) {
            object[22] = 14; object[15] = object[17];
            changed = 1; redraw = 1;
        } else if (object[23] == 0 &&
                   (int)F_h00_463E() % 100 < G_h01_1300[15]) {
            object[22] = 17; G_h01_7A92 = index;
            object[23] = 1; object[24] = 3;
            object[26] = object[30] = object[29] = object[16] + 28;
            object[25] = object[28] = object[27] = object[15] + 8;
            changed = 1; redraw = 1;
        }
        break;
    case 17:
        if (object[31] <= 0) {
            if (near) {
                object[22] = 14; changed = 1; redraw = 1;
            } else {
                if (object[4] == 2) F_h00_57D2(96);
                F_h11_4474(2, object + 1);
            }
        }
        break;
    case 12:
        if (object[31] <= 0) {
            if (near) {
                object[16] += 12;
                if (object[16] > 80 || object[16] + 28 >= G_h01_94C0 + 32)
                    object[22] = 13;
                changed = 1; redraw = 1;
            } else F_h11_4474(2, object + 1);
        }
        break;
    case 11:
        if (object[31] <= 0) {
            if (near) {
                object[16] -= 12;
                if (object[16] < 16)
                    object[22] = 14;
                else if (object[16] + 32 <= G_h01_94C0 + 32 &&
                         object[15] >= G_h01_94BE)
                    object[22] = 13;
                changed = 1; redraw = 1;
            } else F_h11_4474(2, object + 1);
        }
        break;
    case 13:
        if (object[31] <= 0) {
            if ((int)F_h00_463E() % 100 < G_h01_1300[13]) {
                if (object[23] == 0 &&
                    object[15] >= ((8 >> G_h01_94B0) + G_h01_94BE)) {
                    object[22] = 15; G_h01_12C0[16].field0 = 1;
                    changed = 1; redraw = 1; G_h01_7A92 = index;
                    G_h01_A14E = 0; object[23] = 1; object[24] = 0;
                    object[25] = object[28] = object[27] = object[15] + 8;
                    object[26] = object[30] = object[29] = object[16] + 28;
                }
            } else if ((int)F_h00_463E() % 100 < G_h01_1300[14]) {
                if (F_h11_25D6(object[15] - 32,
                               (8 >> G_h01_94B0) + G_h01_94BE,
                               object[15] + 32) != 0 || object[15] < G_h01_94BE) {
                    object[22] = 11; changed = 1; redraw = 1;
                } else if (object[16] + 20 < G_h01_94C0) {
                    if (object[16] < 80) { object[22] = 12; changed = 1; redraw = 1; }
                } else if (object[16] + 20 > G_h01_94C0 + 32) {
                    object[22] = 11; changed = 1; redraw = 1;
                }
            }
        }
        break;
    case 15:
        if (near) {
            object[22] = 13; changed = 1; redraw = 1;
        } else {
            if (object[4] == 1 && G_h01_12C0[16].field0 != 0) {
                F_h00_57D2(96); G_h01_12C0[16].field0 = 0;
            }
            F_h11_4474(2, object + 1);
        }
        break;
    case 18:
        if (near) { object[22] = 13; changed = 1; redraw = 1; }
        else F_h11_4474(2, object + 1);
        break;
    }
    if (G_h01_8A3C != 0 || changed) F_h11_2E26(index, 7);
    if (redraw) F_h11_41F6(2, object + 1, object[22], object[15], object[16]);
    if (object[31] <= 0) object[31] = G_h01_34D8[8];
}
