extern int free_memory_checked();
extern short G_h01_0970;
extern long G_h01_542A;

recovered(p, x, y)
char **p;
short x;
short y;
{
    return free_memory_checked(&G_h01_542A, *p, (long)x * y * G_h01_0970);
}
