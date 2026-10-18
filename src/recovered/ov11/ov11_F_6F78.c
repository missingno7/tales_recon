/* Fingerprint-derived direct reconstruction candidate for ov11_F_6F78. */
struct DistanceRecord {
    char pad0[18];
    int value18;
    int value20;
    char tail[12];
};

extern char difficulty_level;
extern struct DistanceRecord jg_moving_object_records[1];
extern long squared_distance_long();

int recovered(index,x,y,scale)
int index;
int x;
int y;
int scale;
{
    struct DistanceRecord *record;

    record=&jg_moving_object_records[index];
    switch (difficulty_level) {
    case 0:
        scale*=3;
        break;
    case 1:
        scale*=2;
        break;
    case 2:
        break;
    }
    return index>0 && (long)scale>squared_distance_long(x,y,record->value18,record->value20);
}
