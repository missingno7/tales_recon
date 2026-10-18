extern long drain_input_key_queue();
extern int play_sound();
extern int confirm_quit_game();
extern int pause_game();
extern unsigned char joystick_action_translation_table[32];
extern int keyboard_direction_value;
extern char keyboard_direction_input_enabled;
extern char input_fire_action_capture_enabled;
extern char input_fire_action_pending;
extern char G_h01_A7CC;
extern char G_h01_A7CD;
extern char input_quit_key_seen;
extern char keyboard_fire_key_held;
extern int sound_toggle_state;

int recovered()
{
    unsigned int s;
    long p0;
    long p1;
    unsigned int c;
    int e;

    p0 = 0xdff00c;
    p1 = 0xbfe0fe;
    s = ((*(unsigned short *)p1 & 0x80) ^ 0x80) >> 3;
    s |= (*(unsigned short *)p0 & 0x2) << 2;
    s |= (*(unsigned short *)p0 & 0x200) >> 7;
    s |= ((*(unsigned short *)p0 & 0x1) << 1) ^ (*(unsigned short *)p0 & 0x2);
    s |= ((*(unsigned short *)p0 & 0x200) >> 9) ^ ((*(unsigned short *)p0 & 0x100) >> 8);
    e = joystick_action_translation_table[s];
    c = drain_input_key_queue();
    switch (c & 0x7f) {
    case 27:
    case 113:
        input_quit_key_seen = 1;
        if (G_h01_A7CC == 0 && G_h01_A7CD == 0) {
            confirm_quit_game();
            e = 0;
        } else {
            e = 0x71;
        }
        break;
    case 13:
    case 32:
        e = keyboard_direction_value;
        break;
    case 1:
        e = 6;
        keyboard_direction_value = 6;
        break;
    case 2:
    case 109:
        e = 5;
        keyboard_direction_value = 5;
        break;
    case 3:
        e = 4;
        keyboard_direction_value = 4;
        break;
    case 4:
    case 106:
        e = 7;
        keyboard_direction_value = 7;
        break;
    case 5:
        e = 0;
        keyboard_direction_value = 0;
        break;
    case 6:
    case 107:
        e = 3;
        keyboard_direction_value = 3;
        break;
    case 7:
        e = 8;
        keyboard_direction_value = 8;
        break;
    case 8:
    case 105:
        e = 1;
        keyboard_direction_value = 1;
        break;
    case 9:
        e = 2;
        keyboard_direction_value = 2;
        break;
    case 112:
        if (G_h01_A7CD == 0 && G_h01_A7CC == 0) {
            pause_game();
            e = 0;
        } else {
            e = 0x70;
        }
        break;
    case 115:
        if (sound_toggle_state == 0) {
            sound_toggle_state = 1;
            play_sound(0x7f);
        } else {
            sound_toggle_state = 0;
            play_sound(0x7e);
        }
        break;
    case 78:
    case 89:
    case 110:
    case 121:
        e = c;
        break;
    default:
        keyboard_direction_value = 0;
        break;
    }
    if (keyboard_direction_input_enabled == 0)
        keyboard_direction_value = 0;
    if (keyboard_fire_key_held)
        e |= 0x80;
    if (input_fire_action_capture_enabled && (e & 0x80))
        input_fire_action_pending = 1;
    return e;
}
