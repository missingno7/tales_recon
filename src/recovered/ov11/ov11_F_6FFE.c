/* Direct reconstruction candidate for ov11_F_6FFE. */
struct InitRecord { int value0; int value2; int value4; int value6; int pad8; };
struct Target { char pad0[52]; char value52; };
extern struct InitRecord jg_end_trigger_records[1];
extern struct Target *G_h01_9F76;
extern int jg_set_end_trigger_effect_state();
recovered()
{
    struct InitRecord *record;
    int i;
    for (i = 1, record = jg_end_trigger_records; i < 3; i++, record++) {
        record->value4 = record->value0 * 53 + 12;
        record->value6 = (record->value2 << 5) + 21;
        jg_set_end_trigger_effect_state(i, 9);
    }
    G_h01_9F76->value52 = 0;
}