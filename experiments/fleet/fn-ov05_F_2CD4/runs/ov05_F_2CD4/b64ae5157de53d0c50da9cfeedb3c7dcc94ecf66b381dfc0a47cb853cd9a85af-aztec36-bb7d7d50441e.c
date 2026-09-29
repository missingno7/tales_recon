struct Lookup { int index; int pad; };
struct Record { char pad[4]; int value; char pad2[8]; };

extern struct Lookup G_h01_5E66[16];
extern struct Record G_h01_606C[16];
extern char G_h01_54FE;
extern int G_h01_54C8;
extern int G_h01_5500;
extern char G_h01_5534;
extern char G_h01_57C0;
extern int G_h01_582C;
extern int G_h01_5862;
extern int G_h01_58EE;
extern int G_h01_2F10;
extern int G_h01_2F14;
extern int G_h01_2F16;
extern int G_h01_2F18;
extern int G_h01_2F1A;
extern int G_h01_2F1C;
extern int G_h01_0A7A;
extern int G_h01_0A7C;
extern long G_h01_5E34;
extern int G_h01_5D40;
extern int G_h01_5D42;
extern char G_h01_5D74;
extern int F_h00_34E0();
extern unsigned long F_h00_463E();
extern int F_h00_57D2();
extern long F_h00_8D1E();
extern long F_h00_8D0A();
extern int F_h00_8D00();

void recovered(index)
int index;
{
    struct Record *record;
    unsigned int chance;
    int transformed;
    signed char subtype;

    if (G_h01_5E66[index].index == -1)
        return;
    record = &G_h01_606C[G_h01_5E66[index].index];
    while ((unsigned char)record->pad[0] == index) {
        switch (record->pad2[6]) {
        case 26:
            G_h01_54C8 = *((int *)&record->pad[2]);
            G_h01_5500 = record->value;
            F_h00_34E0(&G_h01_54C8);
            break;
        case 27:
            *((int *)&G_h01_54FE) = *((int *)&record->pad[2]);
            G_h01_5500 = record->value;
            F_h00_34E0(&G_h01_54FE);
            break;
        case 33:
            subtype = record->pad2[7];
            *((int *)(&G_h01_5534 + subtype * 54)) = *((int *)&record->pad[2]);
            *((int *)(&G_h01_5534 + subtype * 54 + 2)) = record->value;
            F_h00_34E0(&G_h01_5534 + subtype * 54);
            break;
        case 40:
            subtype = record->pad2[7];
            *((int *)(&G_h01_57C0 + subtype * 54)) = *((int *)&record->pad[2]);
            *((int *)(&G_h01_57C0 + subtype * 54 + 2)) = record->value;
            F_h00_34E0(&G_h01_57C0 + subtype * 54);
            break;
        case 42:
            chance = ((unsigned long)F_h00_463E() >> 16) % 100;
            transformed = F_h00_8D00(F_h00_8D0A(G_h01_5E34,
                F_h00_8D1E(*((int *)&record->pad[2]))));
            if (record->pad2[7] == 0 && ((char *)record)[27] == 0 &&
                chance < 10 && transformed > -96 && transformed < 96) {
                F_h00_57D2(54);
                record->pad2[7]++;
            } else if (record->pad2[7] <= 1 && record->pad2[7] != 0) {
                record->pad2[7]++;
                G_h01_582C = *((int *)&record->pad[2]);
                G_h01_5862 = record->value;
                F_h00_34E0(&G_h01_582C);
            }
            break;
        case 43:
            if (((char *)record)[-1] > 1) {
                ((char *)record)[-1] = 0;
                record->pad2[7]++;
                G_h01_5862 = *((int *)&record->pad[2]);
                G_h01_58EE = record->value;
                F_h00_34E0(&G_h01_5862);
            } else if (record->pad2[7] > 0 && record->pad2[7] < 2) {
                record->pad2[7]++;
                G_h01_5862 = *((int *)&record->pad[2]);
                G_h01_58EE = record->value;
                F_h00_34E0(&G_h01_5862);
                if (record->pad2[7] == 2)
                    record->pad2[7] = 0;
            }
            break;
        case 49:
            G_h01_2F1A = *((int *)&record->pad[2]);
            G_h01_2F1C = *((int *)&record->pad[2]) + *((int *)&record->pad2[2]);
            G_h01_2F18 = record->value + 16;
            if (G_h01_2F10 > G_h01_2F18 + 16 &&
                G_h01_2F14 > G_h01_2F1A && G_h01_2F16 < G_h01_2F1C)
                G_h01_0A7A = 1;
            else {
                G_h01_0A7A = 0;
                G_h01_0A7C = 0;
            }
            G_h01_58EE = *((int *)&record->pad[2]);
            G_h01_5862 = record->value;
            F_h00_34E0(&G_h01_58EE);
            break;
        case 58:
            if (index == 0)
                G_h01_5D40 = *((int *)&record->pad[2]) + 17;
            else
                G_h01_5D40 = *((int *)&record->pad[2]) + 62;
            G_h01_5D42 = record->value;
            if (record->pad2[0]++ != 0)
                record->pad2[0] = 0;
            else {
                G_h01_5D74 = record->pad2[7];
                record->pad2[7]++;
            }
            if (record->pad2[7] > 2)
                record->pad2[7] = ((unsigned long)F_h00_463E() >> 16) % 3;
            F_h00_34E0(&G_h01_5D40);
            break;
        default:
            break;
        }
        record++;
    }
}