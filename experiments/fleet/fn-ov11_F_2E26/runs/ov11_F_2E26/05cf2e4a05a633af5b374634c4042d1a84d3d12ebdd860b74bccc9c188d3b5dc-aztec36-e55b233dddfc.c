struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
extern struct Record G_h01_9FCE[1];
extern int F_h11_4696();
extern int F_h11_5962();

recovered(index, state)
int index;
int state;
{
    struct Record *record;

    record = &G_h01_9FCE[index];
    *(int *)((char *)record + 14) = 2;

    if (*(int *)((char *)record + 16) == 0 || state == 7)
        *(int *)((char *)record + 16) = state;

    if (state != 7) {
        F_h11_4696(*(int *)((char *)record + 38),
                   *(int *)((char *)record + 42), 64, 74, index + 1);
        if (record->field24)
            F_h11_5962(record->field24, 7);
        if (record->field26)
            F_h11_5962(record->field26, 7);
        if (record->field28)
            F_h11_5962(record->field28, 7);
    }
}
