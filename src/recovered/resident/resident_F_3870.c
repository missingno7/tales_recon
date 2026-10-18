/* resident_F_3870 candidate: alloc-side sibling of resident_F_3930. The allocation
   result is a long; the failure report prints the range and size. Callee and DATA
   names are mechanical. */
extern int F_h00_701A();
extern long Allocate();
extern int dump_memory_list();
extern int shutdown_av();
extern long tracked_free_memory_bytes;

long recovered(a, c)
long a;
long c;
{
    long r;

    r = Allocate(a, c);
    if (r == 0) {
        F_h00_701A("alloc: %lx - %lx,  %ld ($%lx)\n", r, r + c, c, c);
        F_h00_701A("FAILED:  %ld ($%lx) bytes free\n", tracked_free_memory_bytes, tracked_free_memory_bytes);
        dump_memory_list();
        shutdown_av("Memory Alloc Failure");
    }
    return r;
}
