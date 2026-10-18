/* Plain structured transcription of ov11_F_0000 (worker haiku-fn-ov11_F_0000). */
struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };

extern int G_h01_12FE;
extern long palette_cycle_callback_index;
extern char palette_cycle_countdown_step;
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern long arc_file;
extern int G_h01_7A94;
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern int G_h01_8A42;
extern struct Record jg_entity_row_dispatch_records[1];
extern int jg_grid_tile_indices[41][4];
extern short jg_tile_reward_available_flags[1];
extern int G_h01_94AC;
extern int G_h01_94AE;
extern int G_h01_94B8;
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_94E6;
extern long G_h01_9FA6;
extern char G_h01_16E6[1];

extern int request_disk();
extern int arc_read_index();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int fade_palette_to_black();
extern int clear_input_direction_and_fire_state();
extern int F_h00_4D04();
extern int F_h00_4EC6();
extern int play_sound();
extern int Close();
extern int Delay();
extern int BltBitMap();
extern int SetRast();

recovered(arg)
int arg;
{
    int i;
    int aux;
    int j;
    int lim;
    struct Record *p;
    int flag;
    char scratch[200];

    flag = 1;
    G_h01_7A94 = arg;
    SetRast(screen_rast_port, 0L);
    jg_load_level_resources(1);
    jg_initialize_actor_states();
    jg_initialize_p_section_objects();
    jg_initialize_moving_objects();
    jg_initialize_events();
    F_h11_21F8();
    jg_initialize_hazards();
    jg_initialize_end_triggers();
    jg_begin_attempt(1);
    palette_cycle_callback_index = 0;
    palette_cycle_countdown_step = 0;
    fade_palette_to_black();
    G_h01_12FE = 0;
    SetRast(screen_rast_port, 0L);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 0x140L, 0xC8L, 0xC0L, 0xFFL, 0L);
    jg_initialize_platform_map(1);
    F_h00_4EC6();
    request_disk(2);
    F_h00_4D04(8);
    play_sound(0x5C);
    jg_tile_reward_available_flags[jg_grid_tile_indices[G_h01_94BA][G_h01_94BC]] = 0;
    G_h01_94B8 = 0;
    clear_input_direction_and_fire_state();

    while (G_h01_12FE == 0) {
        if (G_h01_8A3C == 0) {
            jg_prepare_player_redraw();
        }
        G_h01_94E6 = 0;
        jg_handle_player_input();
        jg_collect_tile_reward_and_check_fall();
        if (G_h01_12FE != 0) continue;
        if (G_h01_94AE == 7) {
            play_sound(0);
            Delay(0x32L);
            fade_palette_to_black();
            if (G_h01_94AC < 3) {
                G_h01_8A3C = 3;
                flag = 1;
                jg_reset_camera_scroll();
                jg_load_level_resources(0);
                jg_begin_attempt(0);
                jg_initialize_actor_states();
                jg_initialize_platform_map(0);
                jg_initialize_events();
                F_h11_21F8();
                Delay(0x64L);
                G_h01_94B8 = 0;
                play_sound(0x5C);
            } else {
                break;
            }
        }
        jg_update_camera_scroll();
        if (G_h01_8A42) {
            G_h01_8A3C = 3;
        }
        j = G_h01_8A3E / 104;
        lim = (G_h01_8A42 ? 4 : 3) + j;

        for (i = j; i < lim; i++) {
            p = &jg_entity_row_dispatch_records[i];
            if (p->ignored) {
                jg_update_player_platform_attachment(p->ignored);
            }
            if (p->value1) {
                jg_update_p_section_object(p->value1);
            }
            if (p->value2) {
                jg_update_moving_object(p->value2);
                if (p->value3) {
                    jg_update_moving_object(p->value3);
                }
            }
            if (p->value5) {
                jg_update_actor_behavior(p->value5);
            }
            if (p->value5) {
                jg_update_actor_position_and_animation(p->value5);
            }
            if (p->value4) {
                jg_update_hazard_state(p->value4);
                jg_check_player_hazard_collision(p->value4);
            }
            if (p->value6) {
                jg_check_end_trigger_collision(p->value6);
            }
        }

        jg_advance_event_records();
        jg_update_timed_approaching_object();
        jg_update_player_attachment();
        jg_update_player_state();
        if (G_h01_8A3C > 1) {
            jg_clear_background_restore_queue();
        }
        if (G_h01_8A3C > 0) {
            jg_redraw_scrolled_scene_region(G_h01_8A3E, 0, 0x140, G_h01_8A3C == 1);
            G_h01_8A3C--;
        } else {
            jg_restore_background_rectangles();
        }

        for (i = j; i < lim; i++) {
            p = &jg_entity_row_dispatch_records[i];
            if (p->ignored) {
                jg_update_platform_motion(p->ignored);
            }
            if (p->value5) {
                jg_update_actor_motion_history(p->value5);
            }
        }

        jg_update_visible_events();

        for (i = j; i < lim; i++) {
            p = &jg_entity_row_dispatch_records[i];
            if (p->value1) {
                jg_advance_p_section_motion(p->value1);
            }
            if (p->value5) {
                jg_draw_actor_sprite(p->value5);
                jg_check_actor_collision(p->value5);
            }
            if (p->value2) {
                jg_draw_moving_object_segment(p->value2);
                if (p->value3) {
                    jg_draw_moving_object_segment(p->value3);
                }
            }
            if (p->value4 && G_h01_94AE == 45) {
                jg_advance_hazard_motion(p->value4);
            }
            if (p->value6) {
                jg_draw_end_trigger(p->value6);
            }
        }

        jg_update_player_world_position();
        jg_update_approaching_object_history();
        jg_draw_status_bar();
        if (flag) {
            fade_palette_to_black();
            switch_display_buffer();
            palette_fade_target = G_h01_16E6;
            fade_palette_to_target(G_h01_16E6);
            flag = 0;
            clear_input_direction_and_fire_state();
        } else {
            switch_display_buffer();
        }
    }

    jg_release_loaded_resources();
    F_h11_4A92();
    fade_palette_to_black();
    Close(arc_file);
    arc_file = G_h01_9FA6;
    arc_read_index(arc_file);
    play_sound(0);
    F_h00_4EC6();
    return G_h01_12FE;
}
