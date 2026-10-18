struct Point { char reserved[36]; unsigned int value; };
struct PointRef { struct Point *point; char reserved[8]; };

extern struct PointRef map_location_table[36];
extern unsigned char G_h01_46C8;
extern int request_disk();
extern int show_clue_screen();
extern int LoadSeg();
extern int FreeSeg();
extern int run_grid_movement_minigame();
extern int run_timed_event_minigame();
extern int run_cave_maze_minigame();
extern int jg_run();

recovered(arg)
int arg;
{
    int result = 0;
    int unused;

    request_disk(1);
    switch (map_location_table[arg].point->value & 0x000f) {
    case 1:
        LoadSeg(jg_run);
        show_clue_screen(1);
        G_h01_46C8 |= 1;
        result = jg_run(map_location_table[arg].point->value >> 4);
        FreeSeg(jg_run);
        break;
    case 2:
        LoadSeg(run_grid_movement_minigame);
        show_clue_screen(2);
        G_h01_46C8 |= 2;
        result = run_grid_movement_minigame(map_location_table[arg].point->value >> 4);
        FreeSeg(run_grid_movement_minigame);
        break;
    case 8:
        LoadSeg(run_cave_maze_minigame);
        show_clue_screen(4);
        G_h01_46C8 |= 4;
        result = run_cave_maze_minigame(map_location_table[arg].point->value >> 4);
        FreeSeg(run_cave_maze_minigame);
        break;
    case 4:
        LoadSeg(run_timed_event_minigame);
        show_clue_screen(8);
        G_h01_46C8 |= 8;
        result = run_timed_event_minigame(map_location_table[arg].point->value >> 4);
        FreeSeg(run_timed_event_minigame);
        break;
    default:
        break;
    }
    return result;
}