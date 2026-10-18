/* Direct recovery candidate for a 40-byte motion record dispatch. */
struct MotionRecord {
    char bytes[40];
};

extern struct MotionRecord jg_scenery_object_records[1];
extern int jg_advance_scheduled_sprite_motion();

recovered(n)
int n;
{
    struct MotionRecord *record;

    record = &jg_scenery_object_records[n];
    jg_advance_scheduled_sprite_motion(record);
}
