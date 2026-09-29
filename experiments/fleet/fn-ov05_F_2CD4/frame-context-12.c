struct Lookup { int index; int pad; };
struct Record { char pad[4]; int value; char pad2[8]; };
struct Frame { struct Record *record; unsigned int chance; int transformed; char pad; char subtype; char pad2[2]; };

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
    struct Frame frame;


    if (G_h01_5E66[index].index == -1)
        return;
    frame.record = &G_h01_606C[G_h01_5E66[index].index];
    while ((unsigned char)frame.record->pad[0] == index) {
        switch (frame.record->pad2[6]) {
        case 33:
            frame.subtype = frame.record->pad2[7];
            *((int *)(&G_h01_5534 + (unsigned long)frame.subtype * 54)) = *((int *)&frame.record->pad[2]);
            *((int *)(&G_h01_5534 + (unsigned long)frame.subtype * 54 + 2)) = frame.record->value;
            F_h00_34E0(&G_h01_5534 + (unsigned long)frame.subtype * 54);
            break;
        case 40:
            frame.subtype = frame.record->pad2[7];
            *((int *)(&G_h01_57C0 + (unsigned long)frame.subtype * 54)) = *((int *)&frame.record->pad[2]);
            *((int *)(&G_h01_57C0 + (unsigned long)frame.subtype * 54 + 2)) = frame.record->value;
            F_h00_34E0(&G_h01_57C0 + (unsigned long)frame.subtype * 54);
            break;
        case 26:
            G_h01_54C8 = *((int *)&frame.record->pad[2]);
            G_h01_5500 = frame.record->value;
            F_h00_34E0(&G_h01_54C8);
            break;
        case 27:
            *((int *)&G_h01_54FE) = *((int *)&frame.record->pad[2]);
            G_h01_5500 = frame.record->value;
            F_h00_34E0(&G_h01_54FE);
            break;
        case 58:
            if (index == 0)
                G_h01_5D40 = *((int *)&frame.record->pad[2]) + 17;
            else
                G_h01_5D40 = *((int *)&frame.record->pad[2]) + 62;
            G_h01_5D42 = frame.record->value;
            if (frame.record->pad2[0]++ != 0)
                frame.record->pad2[0] = 0;
            else {
                G_h01_5D74 = frame.record->pad2[7];
                frame.record->pad2[7]++;
            }
            if (frame.record->pad2[7] > 2)
                frame.record->pad2[7] = (unsigned int)(((unsigned long)F_h00_463E() >> 16)) % 3;
            F_h00_34E0(&G_h01_5D40);
            break;
        case 42:
            frame.chance = (unsigned int)(((unsigned long)F_h00_463E() >> 16)) % 100;
            frame.transformed = F_h00_8D00(F_h00_8D0A(G_h01_5E34,
                F_h00_8D1E(*((int *)&frame.record->pad[2]))));
            if (frame.record->pad2[7] == 0 && ((char *)frame.record)[27] == 0 &&
                frame.chance < 10 && frame.transformed > -96 && frame.transformed < 96) {
                F_h00_57D2(54);
                frame.record->pad2[7]++;
            } else if (frame.record->pad2[7] <= 1 && frame.record->pad2[7] != 0) {
                frame.record->pad2[7]++;
                G_h01_582C = *((int *)&frame.record->pad[2]);
                G_h01_5862 = frame.record->value;
                F_h00_34E0(&G_h01_582C);
            }
            break;
        case 43:
            if (((char *)frame.record)[-1] > 1) {
                ((char *)frame.record)[-1] = 0;
                frame.record->pad2[7]++;
                G_h01_5862 = *((int *)&frame.record->pad[2]);
                G_h01_58EE = frame.record->value;
                F_h00_34E0(&G_h01_5862);
            } else if (frame.record->pad2[7] > 0 && frame.record->pad2[7] < 2) {
                frame.record->pad2[7]++;
                G_h01_5862 = *((int *)&frame.record->pad[2]);
                G_h01_58EE = frame.record->value;
                F_h00_34E0(&G_h01_5862);
                if (frame.record->pad2[7] == 2)
                    frame.record->pad2[7] = 0;
            }
            break;
        case 49:
            G_h01_2F1A = *((int *)&frame.record->pad[2]);
            G_h01_2F1C = *((int *)&frame.record->pad[2]) + *((int *)&frame.record->pad2[2]);
            G_h01_2F18 = frame.record->value + 16;
            if (G_h01_2F10 > G_h01_2F18 + 16 &&
                G_h01_2F14 > G_h01_2F1A && G_h01_2F16 < G_h01_2F1C)
                G_h01_0A7A = 1;
            else {
                G_h01_0A7A = 0;
                G_h01_0A7C = 0;
            }
            G_h01_58EE = *((int *)&frame.record->pad[2]);
            G_h01_5862 = frame.record->value;
            F_h00_34E0(&G_h01_58EE);
            break;
        default:
            break;
        }
        frame.record++;
    }
}