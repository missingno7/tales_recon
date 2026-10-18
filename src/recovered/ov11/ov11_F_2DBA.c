struct MotionRecord {
    char pad0[2];
    char motion[28];
    short v30;
    short v32;
    short pad34;
    short v36;
    short v38;
    short v40;
    short v42;
    short state;
    char remainder[18];
};

extern struct MotionRecord jg_actor_records[1];
extern int jg_advance_scheduled_sprite_motion();

recovered(n)
int n;
{
    struct MotionRecord *record;

    record = &jg_actor_records[n];
    if (record->state != 14)
        jg_advance_scheduled_sprite_motion(record->motion);
    record->v38 = record->v36;
    record->v42 = record->v40;
    record->v40 = record->v32;
    record->v36 = record->v30;
}
