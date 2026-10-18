struct Record { int unused0, unused2; int left, right, top, bottom; int initial_x, initial_y, offset_y; int x, y, flags; int unused24, unused26, unused28; int step, active; };
extern int G_h01_94AE;
extern int G_h01_94D8;
extern struct Record jg_moving_object_records[10];
extern int play_sound();
extern int jg_queue_background_restore_rectangle();
extern int jg_set_platform_record_state();
extern int jg_lookup_motion_vertical_component();
extern int jg_lookup_motion_horizontal_component();

recovered(index)
int index;
{
    struct Record *record;
    int dx;
    int dy;

    record = &jg_moving_object_records[index];
    record->flags += record->unused28;
    if (record->flags > record->unused26) {
        record->unused28 *= -1;
        if (G_h01_94AE == 8 && index == G_h01_94D8)
            play_sound(0x5a);
    } else {
        if (record->flags < record->unused24) {
            record->unused28 *= -1;
            if (G_h01_94AE == 8 && index == G_h01_94D8)
                play_sound(0x5d);
        }
    }

    record->x = record->initial_x +
        (jg_lookup_motion_horizontal_component(record->flags - 0x80) * record->offset_y) / 0x100;
    record->y = record->initial_y +
        (jg_lookup_motion_vertical_component(record->flags - 0x80) * record->offset_y) / 0x100;

    if (record->initial_x <= record->right) {
        dx = record->right - record->initial_x;
        record->right = record->initial_x;
    } else {
        dx = record->initial_x - record->right;
    }
    dx += 0x10;
    dy = record->bottom - record->initial_y + 1;
    jg_queue_background_restore_rectangle(record->right, record->initial_y, dx, dy, index + 0x1c);

    if (record->unused0)
        jg_set_platform_record_state(record->unused0, 4);
    if (record->unused2)
        jg_set_platform_record_state(record->unused2, 4);
}
