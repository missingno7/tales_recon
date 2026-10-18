/* Direct reconstruction candidate for ov11_F_407C. */
struct Record {
    char pad0[12];
    int value12;
    int value14;
    char pad2[6];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};

extern struct Record jg_event_records[1];
extern int jg_set_event_draw_state();

recovered(index)
int index;
{
    jg_event_records[index].value12 = jg_event_records[index].value14;
    jg_set_event_draw_state(index, 6);
}