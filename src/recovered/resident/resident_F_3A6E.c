extern long allocate_memory_or_report();
extern int report_loader_error();
extern long game_memory_header;
extern int bitmap_plane_count;

recovered(p, c, e)
long *p;
unsigned int c;
unsigned int e;
{
    int i;
    long r;

    r = allocate_memory_or_report(&game_memory_header, (long)(unsigned int)(c * e * bitmap_plane_count));
    if (r == 0)
        report_loader_error(6000);
    for (i = 0; i < bitmap_plane_count; i++)
        p[i] = r + (unsigned int)(i * c * e);
}
