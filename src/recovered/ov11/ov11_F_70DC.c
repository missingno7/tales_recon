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
extern struct Record jg_end_trigger_records[1];
extern int integer_within_inclusive_range();
extern int point_inside_rectangle();
extern int jg_set_end_trigger_effect_state();

recovered(a)
int a;
{
    struct Record *record;

    record = &jg_end_trigger_records[a];
    if (integer_within_inclusive_range(record->value - 2, G_h01_94BA,
                    record->value + 1)) {
        jg_set_end_trigger_effect_state(a, 9);
        if (point_inside_rectangle(record->value4, record->value6,
                        (8 >> G_h01_94B0) + G_h01_94BE,
                        G_h01_94C0 + 16, record->value4 + 48,
                        record->value6 + 30))
            G_h01_12FE = 1;
    }
}
