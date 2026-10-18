struct MotionRecord {
    char prefix[32];
    int field20;
    int field22;
    int field24;
    int field26;
};
extern struct MotionRecord jg_contact_hazard_records[1];
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int F_h11_45EC();
extern int jg_set_hazard_record_state();
extern int jg_start_animation_sequence();
extern int jg_select_player_animation();
extern int jg_advance_animation_sequence();

recovered(index)
int index;
{
    struct MotionRecord *state;
    state = &jg_contact_hazard_records[index];
    state->field26--;
    switch (state->field20) {
    case 20:
        break;
    case 45:
        G_h01_8A3C = 3;
        if (F_h11_45EC((char *)state + 10)) {
            state->field20 = 20;
            jg_set_hazard_record_state(index, 8);
            jg_start_animation_sequence(8, (char *)state + 10, 20, state->field22, state->field24);
            G_h01_94AE = 2;
            jg_select_player_animation(2);
        } else {
            jg_set_hazard_record_state(index, 8);
            jg_advance_animation_sequence(8, (char *)state + 10);
        }
        break;
    }
    if (G_h01_8A3C != 0)
        jg_set_hazard_record_state(index, 8);
    if (state->field26 <= 0)
        state->field26 = 20;
}
