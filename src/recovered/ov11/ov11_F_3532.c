struct Record {
    int field0;
    char gap2[6];
    int field8;
    char gap10[14];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char gap36[8];
    int field44;
    int field46;
    int field48;
    int field50;
    int field52;
    char gap54[2];
    int field56;
    int field58;
    int field60;
    int field62;
};

struct TableCell {
    int value;
    char unused[12];
};

extern struct Record jg_actor_records[1];
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern struct TableCell G_h01_8A68[1];
extern int G_h01_A14E;
extern int jg_start_animation_sequence();
extern int jg_queue_background_restore_rectangle();
extern int jg_set_grid_states_in_rectangle();
extern int jg_set_p_section_object_state();

recovered(index)
int index;
{
    struct Record *record;
    int row;

    record = &jg_actor_records[index];
    if (record->field46 != 1)
        goto exit;
    if (record->field8 == 0)
        goto state_update;
    if (record->field48 != 0)
        goto state_update;
    if (record->field50 > G_h01_8A3E - 16)
        goto upper;

    record->field44 = 13;
    record->field46 = 0;
    G_h01_7A92 = 0;
    jg_start_animation_sequence(2, (char *)record + 2, 13,
               record->field30, record->field32);
    goto position_join;

upper:
    if (record->field50 < G_h01_8A3E + 320)
        goto adjust;
    record->field46 = 0;
    goto position_join;

adjust:
    if (G_h01_A14E)
        goto subtract_eight;
    G_h01_A14E = 1;
    record->field50 -= 32;
    goto position_join;

subtract_eight:
    record->field50 -= 8;
position_join:
    goto draw;

state_update:
    if (record->field48 != 3)
        goto draw;
    if (record->field8 <= 2)
        goto draw;
    record->field52 += 8;
    if (record->field52 < 169)
        goto draw;
    record->field44 = 16;
    record->field46 = 0;
    jg_start_animation_sequence(2, (char *)record + 2, 16,
               record->field30, record->field32);

draw:
    jg_queue_background_restore_rectangle(record->field56, record->field60, 24, 16,
               index + 12);
    jg_set_grid_states_in_rectangle(record->field56, record->field60, 24, 16, 11);
    row = record->field56 / 104;
    if (G_h01_8A68[row].value)
        jg_set_p_section_object_state(G_h01_8A68[row].value, 11);
exit:
    ;
}
