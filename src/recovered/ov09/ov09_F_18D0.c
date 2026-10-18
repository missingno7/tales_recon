struct Row { int values[5]; };
extern struct Row G_h01_12C0[32];
extern int timed_scene_bonus_event_type;
extern int timed_scene_route_point_indices[6];
recovered(n) int n;
{
    unsigned int i;
    timed_scene_route_point_indices[0] = timed_scene_bonus_event_type - 16;
    i = 1;
    do {
        timed_scene_route_point_indices[i] = G_h01_12C0[n-1].values[i-1];
        ++i;
    } while (i < 6);
}
