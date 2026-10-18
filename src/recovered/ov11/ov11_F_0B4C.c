extern int G_h01_94AE;
extern int G_h01_94B4;
extern int G_h01_94B6;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_94D6;
extern int jg_follow_moving_platform();
extern int F_h11_405A();
extern int jg_select_player_animation();
extern int jg_advance_event_track();
extern int jg_set_event_draw_state();

recovered()
{
    if (G_h01_94B4) {
        jg_follow_moving_platform(G_h01_94D6, &G_h01_94C0);
    } else if (G_h01_94B6) {
        if (F_h11_405A(G_h01_94D4)) {
            G_h01_94AE = 2;
            jg_select_player_animation(2);
            G_h01_94B6 = 0;
        } else {
            jg_advance_event_track(G_h01_94D4, &G_h01_94BE, &G_h01_94C0);
            jg_set_event_draw_state(G_h01_94D4, 10);
        }
    }
}
