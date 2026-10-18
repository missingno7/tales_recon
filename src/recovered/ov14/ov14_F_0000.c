struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
struct StringEntry { char *text; char pad[8]; };
extern struct FlagEntry rival_treasure_collected[35];
extern struct LinkEntry G_h01_4528[35];
extern struct StringEntry map_location_table[36];
extern char rival_current_location;
extern char G_h01_17A6[1];
extern long G_h01_2A16;
extern char rival_destination_location;
extern unsigned char G_h01_46C8;
extern long screen_rast_port;
extern char *palette_fade_target;
extern char difficulty_level;
extern char game_day;
extern char rival_day_counter;
extern long rival_unbanked_treasure_value;
extern long rival_banked_cash;
extern int load_scene_graphic();
extern int wait_for_fire_input();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int fade_palette_to_black();
extern int draw_text();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern unsigned int F_h00_463E();
extern int play_sound();
extern int mul36();
extern int strlen();
extern int Delay();
extern int SetRast();
extern int find_first_unclaimed_treasure_location();
extern char choose_highest_value_unclaimed_treasure();
extern char choose_nearest_unclaimed_treasure();
extern char choose_best_treasure_value_per_travel_day();
extern char calculate_travel_days();

recovered(a)
char a;
{
    unsigned int local_02;
    int local_04;
    int local_06;
    int local_08;
    int local_0a;
    int local_0c;
    int local_0e;
    int local_10;
    int local_12;

    if (rival_day_counter > game_day || game_day <= 1 || G_h01_46C8 == 0) {
        if (a == 0)
            return;
    }

    SetRast(screen_rast_port, 0L);

    if (a == 0) {
        switch ((long)difficulty_level) {
        case 0:
            if (rival_unbanked_treasure_value > 1000L)
                rival_destination_location = 0;
            else
                rival_destination_location = find_first_unclaimed_treasure_location(rival_current_location);
            break;
        case 1:
            if (rival_unbanked_treasure_value > 5000L) {
                rival_destination_location = 0;
            } else if (rival_day_counter & 1) {
                rival_destination_location = choose_nearest_unclaimed_treasure(rival_current_location);
            } else {
                rival_destination_location = choose_highest_value_unclaimed_treasure(rival_current_location);
            }
            break;
        case 2:
            if (rival_unbanked_treasure_value > 10000L)
                rival_destination_location = 0;
            else
                rival_destination_location = choose_best_treasure_value_per_travel_day(rival_current_location);
            break;
        }
    }

    rival_day_counter += calculate_travel_days(rival_current_location, rival_destination_location);
    if (rival_destination_location != 0) {
    local_02 = F_h00_463E() % 100;
    if (local_02 < 25)
        --rival_day_counter;
    else if (local_02 < 50)
        ++rival_day_counter;
    else if (local_02 < 55 && a == 0)
        rival_unbanked_treasure_value = 0L;

    local_02 = F_h00_463E();
    if ((local_02 & 1) || a) {
        ((struct FlagEntry *)((char *)&rival_treasure_collected + (long)rival_destination_location * 12L))->value = 1;
        rival_unbanked_treasure_value += ((int *)(((struct LinkEntry *)((char *)&G_h01_4528 + (long)rival_destination_location * 12L))->target))[1];
        load_scene_graphic(10);

        local_02 = F_h00_463E();
        if (local_02 & 1) {
            draw_text(0xa8, 0x3c, "Give it up,", 1, 0);
            draw_text(0xa8, 0x4c, "Scrooge!", 1, 0);
        } else {
            draw_text(0xa8, 0x3c, "You don't have a", 1, 0);
            draw_text(0xa8, 0x4c, "chance, McDuck!", 1, 0);
        }
        draw_text(0xa8, 0x64, "I've taken the", 1, 0);
        draw_text(0xa8, 0x74, "treasure from", 1, 0);

        local_10 = strlen(((struct StringEntry *)((char *)&map_location_table + (long)rival_destination_location * 12L))->text);
        local_10 <<= 2;
        draw_text(0xe0 - local_10, 0x84,
                   ((struct StringEntry *)((char *)&map_location_table + (long)rival_destination_location * 12L))->text,
                   1, 0);
        draw_text(0xe0 + local_10, 0x84, ".", 1, 0);
        play_sound(0x6e);
        switch_display_buffer();
        palette_fade_target = &G_h01_17A6[0];
        fade_palette_to_target(&G_h01_17A6[0]);
        clear_input_direction_and_fire_state();

        local_12 = 0;
        while (G_h01_2A16 != 0L) {
            local_12 = poll_controller_and_keyboard_input();
            if (local_12 & 0x80)
                break;
            Delay(10L);
            local_12 = 1;
        }
        if (local_12 == 0 && wait_for_fire_input(0x28))
            play_sound(0x24);
        fade_palette_to_black();
        play_sound(0x21);
    }
    } else {
        rival_banked_cash += rival_unbanked_treasure_value;
        rival_unbanked_treasure_value = 0L;
    }
    rival_current_location = rival_destination_location;
}
