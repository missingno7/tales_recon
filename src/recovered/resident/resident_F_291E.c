struct TextBlock {
    unsigned int length;
    char *data;
};
extern long arc_file;
extern unsigned int arc_record_kind;
extern unsigned int G_h01_A7DC;
extern unsigned int G_h01_A7DE;
extern unsigned int G_h01_A7E0;
extern unsigned int G_h01_A7E4;
extern unsigned int G_h01_A7D8;
extern long arc_record_stored_length;
extern long game_memory_header;
extern char G_h01_0971;
extern int read_arc_record_header();
extern int report_loader_error();
extern long allocate_bitmap();
extern long allocate_memory_or_report();
extern int allocate_bitmap_planes();
extern void decode_rle_bitmap();
extern void F_h00_4184();
extern int lzw_decode();
extern int shutdown_av();
extern long Read();
extern int printf();

long recovered(index, destination)
int index;
char *destination;
{
    unsigned int width;
    unsigned int stride;
    unsigned int height;
    unsigned int multiplier;
    int mode;
    unsigned int length;
    char *result;
    char *bitmap;
    char *graphic;
    struct TextBlock *block;

    if (read_arc_record_header(index, arc_file))
        report_loader_error(index + 1000);
    switch (arc_record_kind) {
    case 1:
        bitmap = destination;
        width = G_h01_A7DC;
        height = G_h01_A7DE;
        if (bitmap == 0) {
            bitmap = allocate_bitmap(width, height);
            if (bitmap == 0)
                report_loader_error(index + 2000);
        }
        decode_rle_bitmap(bitmap);
        result = bitmap;
        break;
    case 2:
        graphic = destination;
        width = G_h01_A7DC;
        height = G_h01_A7DE;
        multiplier = G_h01_A7E0;
        if (graphic == 0) {
            graphic = allocate_memory_or_report(&game_memory_header, 54L);
            if (graphic == 0)
                report_loader_error(index + 3000);
        }
        stride = width >> 3;
        *(int *)graphic = 0;
        *(int *)(graphic + 2) = 0;
        *(unsigned int *)(graphic + 4) = stride;
        *(unsigned int *)(graphic + 6) = height;
        *(unsigned int *)(graphic + 8) = stride * multiplier;
        *(unsigned int *)(graphic + 10) = height;
        *(char *)(graphic + 13) = G_h01_0971;
        allocate_bitmap_planes(graphic + 16, stride * multiplier, height);
        if (*(long *)(graphic + 16) == 0)
            report_loader_error(index + 4000);
        *(char *)(graphic + 52) = 0;
        decode_rle_bitmap(graphic + 8);
        result = graphic;
        break;
    case 3:
        result = 0;
        block = destination;
        if (block == 0) {
            block = allocate_memory_or_report(&game_memory_header, 6L);
            if (block == 0)
                shutdown_av("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7D8;
        block->length = length;
        block->data = allocate_memory_or_report(&game_memory_header, (unsigned long)length);
        Read(arc_file, block->data, arc_record_stored_length);
        break;
    case 4:
        result = 0;
        block = destination;
        if (block == 0) {
            block = allocate_memory_or_report(&game_memory_header, 6L);
            if (block == 0)
                shutdown_av("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7DC;
        block->length = length;
        block->data = allocate_memory_or_report(&game_memory_header, (unsigned long)length);
        mode = 1;
        lzw_decode(mode, arc_file, block->data, length);
        break;
    case 5:
        result = 0;
        block = destination;
        if (block == 0) {
            block = allocate_memory_or_report(&game_memory_header, 6L);
            if (block == 0)
                shutdown_av("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7DC;
        block->length = length;
        block->data = allocate_memory_or_report(&game_memory_header, (unsigned long)length);
        F_h00_4184(arc_record_stored_length, block->data);
        break;
    case 6:
        result = 0;
        block = destination;
        if (block == 0) {
            block = allocate_memory_or_report(&game_memory_header, 6L);
            if (block == 0)
                shutdown_av("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7E4;
        block->length = length;
        block->data = allocate_memory_or_report(&game_memory_header, (unsigned long)length);
        Read(arc_file, block->data, arc_record_stored_length);
        break;
    default:
        printf("LIT: #%d\n", index);
        report_loader_error(arc_record_kind + 5000);
        break;
    }
    return result;
}
