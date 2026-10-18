/* ov09_F_1B1C v1: plain structured C, canonical declaration views where they exist. */
extern long F_h00_463E();
extern int spawn_timed_scene_event();
extern int place_timed_scene_event_sprite();
extern int draw_timed_scene_event_art();
extern char timed_scene_active_events;
extern char timed_scene_event_spawn_chance_percent;
extern char difficulty_level;
extern unsigned char timed_scene_elapsed_round_count;
extern char G_h01_3D88;
extern char G_h01_3DBE;
extern char G_h01_3DF4;
extern char G_h01_3E2A;
extern char G_h01_3E60;
extern char G_h01_3E96;
extern char G_h01_3ECC;
extern char G_h01_3F02;
extern char G_h01_3F38;
extern char G_h01_3F6E;
extern char G_h01_3FA4;
extern char G_h01_3FDA;
extern char G_h01_4010;
extern char G_h01_4046;
extern char G_h01_407C;
extern char G_h01_40B2;
extern char G_h01_40E8;

struct State {
    unsigned char kind;
    char pad1;
    unsigned int type;
    unsigned char mode;
    unsigned char step;
    char ticks;
    char pad7;
    int first;
    int second;
};

recovered()
{
    int i;
    int f0;
    int f1;
    int f2;
    int thr;
    register struct State *p;

    f0 = 0;
    f1 = 0;
    f2 = 0;
    for (i = 0; i < 3; i++) {
        if (((struct State *)&timed_scene_active_events)[i].kind) {
            if (i == 0)
                f0 = 1;
            else if (i == 1)
                f1 = 1;
            else
                f2 = 1;
        }
    }

    if (timed_scene_elapsed_round_count > 8) {
        if (difficulty_level < 2) {
            timed_scene_event_spawn_chance_percent = 25;
            thr = 90;
        } else {
            timed_scene_event_spawn_chance_percent = 15;
            thr = 80;
        }
    } else if (timed_scene_elapsed_round_count > 2) {
        if (difficulty_level < 2) {
            timed_scene_event_spawn_chance_percent = 40;
            thr = 35;
        } else {
            timed_scene_event_spawn_chance_percent = 20;
            thr = 20;
        }
    } else {
        if (difficulty_level < 2) {
            timed_scene_event_spawn_chance_percent = 50;
            thr = 15;
        } else {
            timed_scene_event_spawn_chance_percent = 25;
            thr = 8;
        }
    }

    if (!f0 && (unsigned)F_h00_463E() % 100 < thr)
        spawn_timed_scene_event(0);
    if (!f2 && (unsigned)F_h00_463E() % 100 < thr)
        spawn_timed_scene_event(2);
    if (!f1 && (unsigned)F_h00_463E() % 100 < thr)
        spawn_timed_scene_event(1);

    p = (struct State *)&timed_scene_active_events;
    for (i = 0; i < 3; i++, p++) {
        if (!p->kind)
            continue;
        switch (p->type) {
        case 14:
        case 30:
            if (p->type == 14)
                place_timed_scene_event_sprite(p, &G_h01_3D88);
            else
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step > 0)
                        p->mode = 1;
                    else
                        p->kind = 0;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    p->ticks = 1;
                    if (p->step == 2 && timed_scene_elapsed_round_count > 5)
                        p->kind = 0;
                    else if (p->step == 2) {
                        p->step = 0;
                        p->mode = 0;
                    } else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 2;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 15:
        case 31:
            place_timed_scene_event_sprite(p, &G_h01_3DBE);
            if (p->type == 31)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2)
                        p->kind = 0;
                    else
                        p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 0;
                    p->step = 2;
                }
                break;
            case 2:
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 7;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 16:
        case 32:
            place_timed_scene_event_sprite(p, &G_h01_3DF4);
            if (p->type == 32)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2 && timed_scene_elapsed_round_count > 5)
                        p->kind = 0;
                    else if (p->step == 2)
                        p->mode = 3;
                    else if (p->step == 3) {
                        p->mode = 2;
                        p->step = 4;
                    } else if (p->step == 5)
                        p->kind = 0;
                    else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->step = 2;
                        p->mode = 1;
                    } else if (p->step == 4) {
                        p->step = 5;
                        p->mode = 1;
                    }
                }
                break;
            case 3:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 3;
                }
                break;
            case 4:
            case 5:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 5)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 17:
        case 18:
        case 33:
        case 34:
            if (p->type == 18)
                place_timed_scene_event_sprite(p, &G_h01_3E60);
            else if (p->type == 34)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            else if (p->type == 17)
                place_timed_scene_event_sprite(p, &G_h01_3E2A);
            else
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->mode = 1;
                        p->step = 2;
                        if (timed_scene_elapsed_round_count > 5)
                            p->kind = 0;
                    } else
                        p->kind = 0;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 19:
        case 35:
            if (p->type == 19)
                place_timed_scene_event_sprite(p, &G_h01_3E96);
            else
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2)
                        p->mode = 2;
                    else
                        p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->mode = 0;
                        p->step = 2;
                    } else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0)
                    p->kind = 0;
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 0;
                    if (++p->mode > 4) {
                        p->mode = 3;
                        if (++p->step > 7)
                            p->kind = 0;
                    }
                }
                break;
            }
            break;
        case 20:
        case 21:
        case 36:
        case 37:
            if (p->type == 20 || p->type == 36) {
                place_timed_scene_event_sprite(p, &G_h01_3ECC);
                if (p->type == 36)
                    place_timed_scene_event_sprite(p, &G_h01_40E8);
            } else {
                place_timed_scene_event_sprite(p, &G_h01_3F02);
                if (p->type == 37)
                    place_timed_scene_event_sprite(p, &G_h01_40E8);
            }
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 4)
                        p->step = 5;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step > 1 && timed_scene_elapsed_round_count > 5)
                        p->kind = 0;
                    else if (p->step == 3) {
                        p->mode = 0;
                        p->step = 4;
                    } else if (p->step == 5)
                        p->kind = 0;
                    else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step++;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 22:
        case 23:
        case 38:
        case 39:
            if (p->type == 22 || p->type == 38) {
                place_timed_scene_event_sprite(p, &G_h01_3F38);
                if (p->type == 38)
                    place_timed_scene_event_sprite(p, &G_h01_40E8);
            } else {
                place_timed_scene_event_sprite(p, &G_h01_3F6E);
                if (p->type == 39)
                    place_timed_scene_event_sprite(p, &G_h01_40E8);
            }
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step > 0)
                        p->mode = 1;
                    else
                        p->kind = 0;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    p->ticks = 1;
                    if (p->step > 1 && timed_scene_elapsed_round_count > 5)
                        p->kind = 0;
                    else if (p->step == 2) {
                        p->step = 0;
                        p->mode = 0;
                    } else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 2;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 24:
        case 25:
        case 28:
        case 29:
        case 40:
        case 41:
        case 44:
        case 45:
            if (p->type == 25)
                place_timed_scene_event_sprite(p, &G_h01_3FDA);
            else if (p->type == 41)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            else if (p->type == 24)
                place_timed_scene_event_sprite(p, &G_h01_3FA4);
            else if (p->type == 40)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            else if (p->type == 28)
                place_timed_scene_event_sprite(p, &G_h01_407C);
            else if (p->type == 44)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            else if (p->type == 29)
                place_timed_scene_event_sprite(p, &G_h01_40B2);
            else
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2)
                        p->kind = 0;
                    else
                        p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    p->ticks = 1;
                    if (p->step > 1 && timed_scene_elapsed_round_count > 5)
                        p->kind = 0;
                    else if (p->step == 2)
                        p->mode = 0;
                    else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 2;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 26:
        case 27:
        case 42:
        case 43:
            if (p->type == 27)
                place_timed_scene_event_sprite(p, &G_h01_4046);
            else if (p->type == 43)
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            else if (p->type == 26)
                place_timed_scene_event_sprite(p, &G_h01_4010);
            else
                place_timed_scene_event_sprite(p, &G_h01_40E8);
            draw_timed_scene_event_art(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    if (p->step == 2 && timed_scene_elapsed_round_count > 5)
                        p->kind = 0;
                    p->ticks = 1;
                    p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->mode = 1;
                        p->step = 2;
                    } else
                        p->kind = 0;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        default:
            break;
        }
    }
}
