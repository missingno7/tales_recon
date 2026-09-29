struct Record {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};

struct Slot { long value; char unused[12]; };

extern char G_h01_46E0;
extern char G_h01_9D2C[1];
extern char G_h01_9D4C[1];
extern char G_h01_9D6C[1];
extern char G_h01_9D9C[1];
extern char G_h01_9E5C[1];
extern long G_h01_9F6A;
extern struct Record G_h01_9FCE[1];
extern int G_h01_1300[16];
extern int G_h01_34D8[16];

extern int G_h01_9D30;
extern int G_h01_9D40;
extern int G_h01_9D4A;
extern int G_h01_9D50;
extern int G_h01_9D5A;
extern int G_h01_9D60;
extern int G_h01_9D6A;
extern int G_h01_9D70;
extern int G_h01_9D72;
extern int G_h01_9D80;
extern int G_h01_9D82;
extern int G_h01_9D90;
extern int G_h01_9DA0;
extern int G_h01_9DB0;
extern int G_h01_9DB2;
extern int G_h01_9DC0;
extern int G_h01_9DD0;
extern int G_h01_9DD2;
extern int G_h01_9DE0;
extern int G_h01_9DF0;
extern int G_h01_9DF2;
extern int G_h01_9E00;
extern int G_h01_9E10;
extern int G_h01_9E12;
extern int G_h01_9E20;
extern int G_h01_9E30;
extern int G_h01_9E32;
extern int G_h01_9E40;
extern int G_h01_9E50;
extern int G_h01_9E52;
extern int G_h01_9E60;
extern int G_h01_9E62;
extern int G_h01_9E70;
extern int G_h01_9E72;
extern int G_h01_9E80;
extern int G_h01_9E82;
extern int G_h01_9E90;
extern int G_h01_9E92;
extern int G_h01_9EA0;
extern int G_h01_9EA2;

extern int F_h11_2E26();
extern int F_h11_41F6();

recovered()
{
    int i;
    struct Record *record;

    for (i = 0; i < 2; i++) {
        ((struct Slot *)G_h01_9D4C)[i].value = G_h01_9F6A;
        ((struct Slot *)G_h01_9D2C)[i].value = G_h01_9F6A;
    }

    G_h01_9D50 = 0;
    G_h01_9D5A = 0;
    G_h01_9D60 = 1;
    G_h01_9D6A = 12;
    G_h01_9D30 = 0;
    G_h01_9D40 = 1;
    G_h01_9D4A = 12;

    for (i = 0; i < 3; i++)
        ((struct Slot *)G_h01_9D6C)[i].value = G_h01_9F6A;

    G_h01_9D70 = 2;
    G_h01_9D72 = 5;
    G_h01_9D80 = 3;
    G_h01_9D82 = 128;
    G_h01_9D90 = 1;

    for (i = 0; i < 12; i++)
        ((struct Slot *)G_h01_9D9C)[i].value = G_h01_9F6A;

    G_h01_9DA0 = 4;
    G_h01_9DB0 = 5;
    G_h01_9DB2 = 2;
    G_h01_9DC0 = 4;
    G_h01_9DD0 = 5;
    G_h01_9DD2 = 2;
    G_h01_9DE0 = 4;
    G_h01_9DF0 = 5;
    G_h01_9DF2 = 2;
    G_h01_9E00 = 4;
    G_h01_9E10 = 5;
    G_h01_9E12 = 2;
    G_h01_9E20 = 4;
    G_h01_9E30 = 5;
    G_h01_9E32 = 2;
    G_h01_9E40 = 4;
    G_h01_9E50 = 5;
    G_h01_9E52 = 2;

    for (i = 0; i < 5; i++)
        ((struct Slot *)G_h01_9E5C)[i].value = G_h01_9F6A;

    G_h01_9E60 = 6;
    G_h01_9E62 = 3;
    G_h01_9E70 = 7;
    G_h01_9E72 = 0;
    G_h01_9E80 = 7;
    G_h01_9E82 = 0;
    G_h01_9E90 = 7;
    G_h01_9E92 = 64;
    G_h01_9EA0 = 6;
    G_h01_9EA2 = 3;

    switch (G_h01_46E0) {
    case 0:
        G_h01_34D8[8] = 6;
        break;
    case 1:
        G_h01_1300[13] = 50;
        G_h01_1300[14] = 75;
        G_h01_1300[15] = 75;
        G_h01_34D8[8] = 3;
        break;
    case 2:
        G_h01_1300[13] = 75;
        G_h01_1300[14] = 75;
        G_h01_1300[15] = 85;
        G_h01_34D8[8] = 2;
        break;
    }

    for (i = 0; i < 6; i++) {
        record = &G_h01_9FCE[i];
        record->field30 = record->field34;
        *(int *)((char *)record + 44) = 14;
        *(int *)((char *)record + 46) = 0;
        *(int *)((char *)record + 62) = G_h01_34D8[8];
        F_h11_2E26(i, 7);
        F_h11_41F6(2, (char *)record + 2, 14,
                   *(int *)((char *)record + 30),
                   *(int *)((char *)record + 32));
    }
}
