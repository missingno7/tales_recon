extern int G_h01_8A3E;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94B8;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_9F4C;
extern int G_h01_9FAA;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FC4;
extern int G_h01_9FC6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int G_h01_9FCC;
extern int rectangles_intersect();
extern int jg_draw_approaching_object();
extern int jg_finish_event_animation();
extern int jg_start_animation_sequence();
extern int jg_advance_animation_sequence();
extern int jg_select_player_animation();

recovered()
{
    int x;
    int y;

    switch (G_h01_9FCC) {
    case 0:
        if (G_h01_94B8 > G_h01_9F4C) {
            G_h01_9FCC = 1;
            G_h01_9FC0 = G_h01_8A3E + 318;
            G_h01_9FC2 = G_h01_94C0 + 12;
            G_h01_9FC4 = G_h01_9FC0;
            G_h01_9FC6 = G_h01_9FC2;
            G_h01_9FC8 = G_h01_9FC4;
            G_h01_9FCA = G_h01_9FC6;
            jg_draw_approaching_object(12);
            jg_start_animation_sequence(33, &G_h01_9FAA, G_h01_9FCC,
                G_h01_9FC0, G_h01_9FC2);
        }
        break;

    case 1:
        x = (8 >> G_h01_94B0) + G_h01_94BE;
        y = G_h01_94C0 + 16;
        switch (G_h01_94AE) {
        case 19:
            y += 8;
            break;
        case 6:
            x += 16;
            y += 8;
            break;
        }

        if (rectangles_intersect(x - 4, y - 6, x + 4, y + 6,
                G_h01_9FC0 + 8, G_h01_9FC2 + 8,
                G_h01_9FC0 + 18, G_h01_9FC2 + 20) &&
            G_h01_94AE != 2 && G_h01_94AE != 45) {
            if (G_h01_94B6) {
                jg_finish_event_animation(G_h01_94D4);
                G_h01_94B6 = 0;
            }
            G_h01_94AE = 2;
            jg_select_player_animation(2);
        }

        if (G_h01_9FC0 + 32 < G_h01_8A3E) {
            G_h01_9FCC = 0;
            G_h01_94B8 = 0;
        } else {
            G_h01_9FC0 -= 4;
            jg_advance_animation_sequence(33, &G_h01_9FAA);
        }
        jg_draw_approaching_object(12);
        break;
    }
}

