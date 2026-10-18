/* resident_F_3930 candidate: pointer range argument, long arithmetic for the end address; callees and DATA names are mechanical. */
extern int F_h00_701A();
extern int Deallocate();
extern int shutdown_av();
extern long tracked_memory_lower_bound;
extern long tracked_memory_upper_bound;

recovered(a, b, c)
long a;
char *b;
long c;
{
    if (b < tracked_memory_lower_bound || b > tracked_memory_upper_bound) {
        F_h00_701A("dealloc: %lx - %lx,  %ld ($%lx)\n", b, (long)b + c, c, c);
        shutdown_av("BAD POINTER\n");
    } else {
        Deallocate(a, b, c);
    }
}
