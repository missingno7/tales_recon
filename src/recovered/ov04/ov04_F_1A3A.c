/* Direct reconstruction candidate for ov04_F_1A3A. */
extern long screen_rast_port;
extern int SetRast();
extern int F_h00_4EC6();
extern int request_disk();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int play_sound();
extern int clear_input_direction_and_fire_state();
extern int wait_for_fire_input();
extern int F_h00_307C();

recovered(choice)
int choice;
{
    SetRast(screen_rast_port, 0L);
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(30);
    if (choice) F_h00_0640(13);
    else F_h00_0640(14);
    play_sound(119);
    clear_input_direction_and_fire_state();
    wait_for_fire_input(100);
    F_h00_4EC6();
    F_h00_307C();
}
