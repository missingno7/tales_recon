/* Direct reconstruction candidate for ov11_F_70DC. */
struct Record {
    int value0;
    int value2;
    int value4;
    int value6;
    char tail[2];
};

extern int G_h01_12FE;
extern int G_h01_94B0;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Record G_h01_A6A8[1];
extern int F_h11_25D6();
extern int F_h11_25F8();
extern int F_h11_717A();

recovered(a)
int a;
{
    struct Record *record;

    record = &G_h01_A6A8[a];
    if (F_h11_25D6(record->value0 - 2, G_h01_94BA,
                    record->value0 + 1)) {
        F_h11_717A(a, 9);
        if (F_h11_25F8(record->value6 + 30, record->value4 + 48,
                        (8 >> G_h01_94B0) + G_h01_94BE,
                        G_h01_94C0 + 16, record->value4, record->value6))
            G_h01_12FE = 1;
    }
}
