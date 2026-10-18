extern int free_memory_checked();
extern long G_h01_542A;

struct Rec { unsigned short size; char *ptr; };

recovered(p)
struct Rec *p;
{
    free_memory_checked(&G_h01_542A, p->ptr, (long)p->size);
    free_memory_checked(&G_h01_542A, p, 6L);
}
