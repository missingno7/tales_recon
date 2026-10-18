/* resident_F_3B84: frees a block (size = w2 * w0 * bitmap_plane_count, zero-extended) and then its 40-byte header. */
struct R3B84 { unsigned short w0; unsigned short w2; char f4[4]; long l8; };

extern int free_memory_checked();
extern long game_memory_header;
extern short bitmap_plane_count;

recovered(p)
struct R3B84 *p;
{
    free_memory_checked(&game_memory_header, p->l8, (long)(unsigned short)(p->w2 * p->w0 * bitmap_plane_count));
    free_memory_checked(&game_memory_header, p, 40L);
}
