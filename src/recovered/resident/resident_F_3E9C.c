extern long Read();
extern unsigned short lzw_code_width_masks[1];
extern unsigned short lzw_bit_position;
extern unsigned short G_h01_A9C2;
extern unsigned short G_h01_A9C4;
extern unsigned short G_h01_A9C6;
extern unsigned short G_h01_A9C8;
extern unsigned char archive_read_buffer[1];
extern unsigned char G_h01_A9CB;
extern unsigned char G_h01_A9CC[1];
extern unsigned char G_h01_A9CD;
extern long lzw_input_file_handle;
extern unsigned short lzw_code_width;

recovered()
{
    unsigned long bits;

    G_h01_A9C2 = lzw_bit_position >> 3;
    G_h01_A9C8 = lzw_bit_position & 7;
    lzw_bit_position += lzw_code_width;
    if (G_h01_A9C2 >= 0x3fd) {
        lzw_bit_position = G_h01_A9C8 + lzw_code_width;
        G_h01_A9C6 = 0x400 - G_h01_A9C2;
        archive_read_buffer[0] = archive_read_buffer[G_h01_A9C2];
        G_h01_A9CB = archive_read_buffer[G_h01_A9C2 + 1];
        G_h01_A9CC[0] = archive_read_buffer[G_h01_A9C2 + 2];
        G_h01_A9CD = archive_read_buffer[G_h01_A9C2 + 3];
        Read(lzw_input_file_handle, archive_read_buffer + G_h01_A9C6, (unsigned long)G_h01_A9C2);
        G_h01_A9C2 = 0;
    }
    G_h01_A9C4 = archive_read_buffer[G_h01_A9C2 + 1];
    G_h01_A9C4 <<= 8;
    G_h01_A9C4 += archive_read_buffer[G_h01_A9C2];
    G_h01_A9C2 = G_h01_A9CC[G_h01_A9C2];
    bits = (((unsigned long)G_h01_A9C2 << 16) + G_h01_A9C4) >> G_h01_A9C8;
    return lzw_code_width_masks[(unsigned short)(lzw_code_width - 9)] & (unsigned short)bits;
}
