/* Provisional source for normal ov11 layout evidence; never canonical by itself. */
struct Record {
    char pad0[12];
    int state;
    int value;
    char pad10[10];
    int x;
    int y;
    int first;
    int second;
    int third;
    char tail[4];
};
extern struct Record G_h01_3724[1];
extern int F_h11_4696();
extern int F_h11_5962();

recovered(index,mode)
int index,mode;
{
    struct Record *record;
    record=&G_h01_3724[index];
    record->state=2;
    if (record->value==0 || mode==5) record->value=mode;
    if (mode==5) {
        F_h11_4696(record->x,record->y,64,48,11);
        if (record->first) F_h11_5962(record->first,5);
        if (record->second) F_h11_5962(record->second,5);
        if (record->third) F_h11_5962(record->third,5);
    }
}
