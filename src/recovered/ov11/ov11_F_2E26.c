struct Record { int field0; char unused0[22]; int field24; int field26; int field28; int field30; int field32; int field34; char unused1[28]; };
extern struct Record jg_actor_records[1];
extern int jg_queue_background_restore_rectangle();
extern int jg_set_platform_record_state();

recovered(index, state)
int index;
int state;
{
    struct Record *record;

    record = &jg_actor_records[index];
    *(int *)((char *)record + 14) = 2;

    if (*(int *)((char *)record + 16) == 0 || state == 7)
        *(int *)((char *)record + 16) = state;

    if (state == 7) {
        jg_queue_background_restore_rectangle(*(int *)((char *)record + 38),
                   *(int *)((char *)record + 42), 64, 74, index + 1);
        if (*(int *)((char *)record + 24))
            jg_set_platform_record_state(*(int *)((char *)record + 24), 7);
        if (*(int *)((char *)record + 26))
            jg_set_platform_record_state(*(int *)((char *)record + 26), 7);
        if (*(int *)((char *)record + 28))
            jg_set_platform_record_state(*(int *)((char *)record + 28), 7);
    }
}

