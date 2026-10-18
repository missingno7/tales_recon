extern int F_h00_3AE4();
extern int free_memory_checked();
extern long G_h01_542A;

recovered(p)
char *p;
{
    F_h00_3AE4(p + 16, *(short *)(p + 8), *(short *)(p + 10));
    return free_memory_checked(&G_h01_542A, p, 54L);
}
