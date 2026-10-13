extern int F_h00_3930();
extern long G_h01_542A;

struct Rec { unsigned short size; char *ptr; };

recovered(p)
struct Rec *p;
{
    F_h00_3930(&G_h01_542A, p->ptr, (long)p->size);
    F_h00_3930(&G_h01_542A, p, 6L);
}
