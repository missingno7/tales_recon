struct MotionRecord {
    char pad[10];
    char motion;
    char remainder[29];
};

extern struct MotionRecord jg_contact_hazard_records[1];
extern int jg_advance_scheduled_sprite_motion();

recovered(n)
int n;
{
    struct MotionRecord *record;

    record = &jg_contact_hazard_records[n];
    jg_advance_scheduled_sprite_motion(&record->motion);
}
