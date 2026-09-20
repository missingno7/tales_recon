F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }

extern int F_h11_25D6();
F_h11_25F8(a,b,c,d,e,f) int a,b,c,d,e,f; { return F_h11_25D6(a,c,e) && F_h11_25D6(b,d,f); }

/* Direct reconstruction candidate for ov11_F_70DC. */
struct Record {
    int value;
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
    if (F_h11_25D6(record->value - 2, G_h01_94BA,
                    record->value + 1)) {
        F_h11_717A(a, 9);
        if (F_h11_25F8(record->value4, record->value6,
                        (8 >> G_h01_94B0) + G_h01_94BE,
                        G_h01_94C0 + 16, record->value4 + 48,
                        record->value6 + 30))
            G_h01_12FE = 1;
    }
}

struct Record { int value; char tail[8]; };
extern struct Record G_h01_A6B0[36];
F_h11_717A(a) int a; { G_h01_A6B0[a].value=2; }

