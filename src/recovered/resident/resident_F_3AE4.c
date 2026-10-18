extern int free_memory_checked();
extern short bitmap_plane_count;
extern long game_memory_header;

recovered(p, x, y)
char **p;
short x;
short y;
{
    return free_memory_checked(&game_memory_header, *p, (long)x * y * bitmap_plane_count);
}
