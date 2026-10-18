extern long F_h00_463E();
extern int F_h00_4EC6();
extern int request_disk();
extern int F_h00_4D04();
extern int load_scene_graphic();
extern int play_sound();
extern int arc_read_index();
extern int wait_for_fire_input();
extern long arc_file;

recovered(a)
int a;
{
    int value;

    if (a) {
        value=(unsigned)F_h00_463E()%3;
        F_h00_4EC6();
        request_disk(2);
        switch (value) {
        case 0:
            F_h00_4D04(9);
            break;
        case 2:
            F_h00_4D04(17);
            break;
        case 3:
            F_h00_4D04(18);
            break;
        }
        load_scene_graphic(12);
        play_sound(119);
        request_disk(1);
        arc_read_index(arc_file);
    } else {
        value=(F_h00_463E()&1) ? 15 : 16;
        F_h00_4EC6();
        request_disk(2);
        F_h00_4D04(value);
        load_scene_graphic(11);
        play_sound(119);
        request_disk(1);
        arc_read_index(arc_file);
    }
    wait_for_fire_input(100);
}
