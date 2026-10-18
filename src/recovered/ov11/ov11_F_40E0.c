/* Direct reconstruction candidate for ov11_F_40E0. */
struct Record {
    char pad0[22];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};

extern struct Record jg_event_records[1];
extern int jg_queue_background_restore_rectangle();

recovered(index, mode)
int index;
int mode;
{
    struct Record *record;

    record = &jg_event_records[index];
    record->state = 2;
    if (record->value30 == 0 || mode == 6)
        record->value30 = mode;
    if (mode == 6)
        jg_queue_background_restore_rectangle(record->value22, record->value26, 88, 30,
                   index % 4 + 18);
}