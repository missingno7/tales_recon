struct resident_entry {
    unsigned short word0;
    unsigned char byte2;
    unsigned char byte3;
};

extern long Read();
extern int lzw_read_code();
extern int lzw_append_output_byte();
extern unsigned short lzw_bit_position;
extern unsigned short G_h01_B1D8;
extern unsigned short lzw_code_width;
extern unsigned short lzw_next_code_width_threshold;
extern unsigned short G_h01_B1E4;
extern unsigned short G_h01_B1E6;
extern long lzw_output_start;
extern long lzw_input_file_handle;
extern long lzw_dictionary_storage;
extern char *lzw_output_cursor;
extern unsigned short G_h01_A9C2;
extern unsigned char G_h01_A9C3;
extern unsigned char archive_read_buffer[1];
extern unsigned short lzw_dictionary_walk_code;
extern unsigned char G_h01_ADCF;
extern unsigned short lzw_previous_code;
extern unsigned short lzw_current_code;
extern unsigned short lzw_next_dictionary_code;
extern unsigned short lzw_expansion_stack_length;
extern unsigned char lzw_expansion_stack[1];
extern unsigned char lzw_current_string_first_byte;

long recovered(p1, p2, p3, p4)
unsigned short p1;
long p2;
long p3;
unsigned short p4;
{
    G_h01_B1E6 = p4;
    G_h01_B1E4 = p1;
    lzw_input_file_handle = p2;
    lzw_output_start = p3;
    lzw_output_cursor = (char *)p3;
    G_h01_B1D8 = 0;
    lzw_next_dictionary_code = 0x102;
    lzw_expansion_stack_length = 0;
    lzw_code_width = 9;
    lzw_next_code_width_threshold = 0x200;
    lzw_bit_position = 0;
    Read(lzw_input_file_handle, archive_read_buffer, (unsigned long)0x400);

    while ((G_h01_A9C2 = lzw_read_code()) != 0x101) {
        if (G_h01_A9C2 == 0x100) {
            lzw_code_width = 9;
            lzw_next_code_width_threshold = 0x200;
            lzw_next_dictionary_code = 0x102;
            G_h01_A9C2 = lzw_read_code();
            lzw_previous_code = G_h01_A9C2;
            lzw_dictionary_walk_code = G_h01_A9C2;
            lzw_current_string_first_byte = G_h01_A9C3;
            lzw_append_output_byte(lzw_current_string_first_byte);
            continue;
        }
        lzw_current_code = G_h01_A9C2;
        lzw_dictionary_walk_code = G_h01_A9C2;
        if (G_h01_A9C2 >= lzw_next_dictionary_code) {
            lzw_dictionary_walk_code = lzw_previous_code;
            lzw_expansion_stack[lzw_expansion_stack_length++] = lzw_current_string_first_byte;
        }
        while (lzw_dictionary_walk_code > 0xff) {
            lzw_expansion_stack[lzw_expansion_stack_length++] = ((unsigned char *)(lzw_dictionary_storage + ((unsigned long)lzw_dictionary_walk_code << 2)))[2];
            lzw_dictionary_walk_code = ((struct resident_entry *)lzw_dictionary_storage)[lzw_dictionary_walk_code].word0;
        }
        lzw_current_string_first_byte = G_h01_ADCF;
        lzw_expansion_stack[lzw_expansion_stack_length++] = lzw_current_string_first_byte;
        while (lzw_expansion_stack_length != 0) {
            lzw_expansion_stack_length--;
            lzw_append_output_byte(lzw_expansion_stack[lzw_expansion_stack_length]);
        }
        ((unsigned char *)(lzw_dictionary_storage + ((unsigned long)lzw_next_dictionary_code << 2)))[2] = lzw_current_string_first_byte;
        ((struct resident_entry *)lzw_dictionary_storage)[lzw_next_dictionary_code].word0 = lzw_previous_code;
        lzw_next_dictionary_code++;
        lzw_previous_code = lzw_current_code;
        if (lzw_next_dictionary_code >= lzw_next_code_width_threshold && lzw_code_width < 0xc) {
            lzw_code_width++;
            lzw_next_code_width_threshold *= 2;
        }
    }
    return (long)lzw_output_cursor - lzw_output_start;
}
