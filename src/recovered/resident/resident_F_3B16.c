/* resident_F_3B16: allocates a 40-byte bitmap header (error 7000) and its planes through 3A6E. u1..u3 are unused: the original 12-byte frame leaves 6 bytes between r and x. */
extern long allocate_memory_or_report();
extern int report_loader_error();
extern int allocate_bitmap_planes();
extern long game_memory_header;
extern char G_h01_0971;

recovered(c, e)
unsigned int c;
unsigned int e;
{
    char *r;
    unsigned int u1;
    unsigned int u2;
    unsigned int u3;
    unsigned int x;

    r = allocate_memory_or_report(&game_memory_header, 40L);
    if (r == 0)
        report_loader_error(7000);
    x = c >> 3;
    allocate_bitmap_planes(r + 8, x, e);
    *(unsigned int *)r = x;
    *(unsigned int *)(r + 2) = e;
    *(char *)(r + 5) = G_h01_0971;
    return r;
}
