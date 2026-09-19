/* Direct reconstruction candidate for ov11_F_6FFE. */
struct InitRecord { int value0; int value2; int value4; int value6; int pad8; };
struct Target { char pad0[52]; char value52; };
extern struct InitRecord G_h01_A6A8[1];
extern struct Target *G_h01_9F76;
extern int F_h11_717A();
recovered()
{
    struct InitRecord *record;
    int i;
    for (i = 1, record = G_h01_A6A8; i < 3; i++, record++) {
        record->value4 = record->value0 * 53 + 12;
        record->value6 = (record->value2 << 5) + 21;
        F_h11_717A(i, 9);
    }
    G_h01_9F76->value52 = 0;
}