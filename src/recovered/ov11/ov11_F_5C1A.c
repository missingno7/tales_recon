struct MotionRecord {
    char pad[18];
    char motion;
    char remainder[33];
};

extern struct MotionRecord jg_platform_records[1];
extern int jg_advance_scheduled_sprite_motion();

recovered(n)
int n;
{
    struct MotionRecord *record;

    record = &jg_platform_records[n];
    jg_advance_scheduled_sprite_motion(&record->motion);
}
