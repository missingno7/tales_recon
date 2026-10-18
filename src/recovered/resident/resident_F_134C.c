extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int Delay();

recovered(n)
int n;
{
    unsigned char c;
    int i, result;

    result = 0;
    clear_input_direction_and_fire_state();
    for (i = 0; i < n; i++) {
        c = poll_controller_and_keyboard_input();
        if (c & 0x80) {
            result = 1;
            break;
        }
        Delay(5L);
    }
    return result;
}
