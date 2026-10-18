extern int free_bitmap_planes();
extern int free_memory_checked();
extern long game_memory_header;

recovered(p)
char *p;
{
    free_bitmap_planes(p + 16, *(short *)(p + 8), *(short *)(p + 10));
    return free_memory_checked(&game_memory_header, p, 54L);
}
