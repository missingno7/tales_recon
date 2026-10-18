/* ov11_F_5FB2: per-record scroll delta from float position math (m.lib FFP). */
struct ClusterRecord {
    char f0[8];
    int value8;
    int value10;
    char f12[2];
    int value14;
    int value16;
    char f18[12];
    int state30;
    int value32;
    int *ref34;
    char f38[2];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37EE;
extern int G_h01_37F0;
extern struct ClusterRecord jg_platform_records[1];
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;

recovered(index)
int index;
{
    struct ClusterRecord *record;
    int delta;
    int shift;

    record = &jg_platform_records[index];
    delta = (int)(((float)G_h01_94BE - (float)record->value2c)
                  * (float)record->ref34[4] / 104.0);
    shift = 0;
    if (record->ref34[2] == 2) {
        if ((8 >> G_h01_94B0) + G_h01_94BE - G_h01_37F0 - record->value2c > 45) {
            delta += 5;
            shift = -5;
        }
    }
    G_h01_94C0 += delta - G_h01_37EE;
    G_h01_94BE += shift - G_h01_37F0;
    G_h01_37EE = delta;
    G_h01_37F0 = shift;
}
