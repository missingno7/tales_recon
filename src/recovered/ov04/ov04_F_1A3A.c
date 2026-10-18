/* Direct reconstruction candidate for ov04_F_1A3A. */
extern long screen_rast_port;
extern int SetRast();
extern int F_h00_4EC6();
extern int request_disk();
extern int F_h00_4D04();
extern int load_scene_graphic();
extern int play_sound();
extern int clear_input_direction_and_fire_state();
extern int wait_for_fire_input();
extern int switch_display_buffer();

recovered(choice)
int choice;
{
    SetRast(screen_rast_port, 0L);
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(30);
    if (choice) load_scene_graphic(13);
    else load_scene_graphic(14);
    play_sound(119);
    clear_input_direction_and_fire_state();
    wait_for_fire_input(100);
    F_h00_4EC6();
    switch_display_buffer();
}
