/* Candidate v1 for resident_F_435E: discard the callee result, then clear the
   word global and the byte global in source order. */
extern int keyboard_direction_value;
extern char keyboard_fire_key_held;
extern long drain_input_key_queue();

recovered()
{
    drain_input_key_queue();
    keyboard_direction_value = 0;
    keyboard_fire_key_held = 0;
}
