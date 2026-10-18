extern int input_key_ring;
extern int input_key_ring_read_index;
extern char keyboard_fire_key_held;
extern char input_key_ring_bytes[1];
extern char raw_key_code_translation_table[1];

long recovered()
{
    char c;
    long l;
    long p;

    p = 0xbfe0fe;
    if (input_key_ring_read_index == input_key_ring)
        return 0;
    while (input_key_ring_read_index != input_key_ring) {
        c = input_key_ring_bytes[input_key_ring_read_index++];
        if (c == 'D' || c == '@' || c == 'C')
            keyboard_fire_key_held = 1;
        else if (c == (char)0xC4 || c == (char)0xC0 || c == (char)0xC3)
            keyboard_fire_key_held = 0;
        input_key_ring_read_index &= 0x7f;
    }
    c &= 0xff;
    c = (c < 0x70 && c > 0) ? raw_key_code_translation_table[c] : -1;
    return c;
}
