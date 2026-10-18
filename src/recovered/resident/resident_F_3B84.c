/* resident_F_3B84: frees a block (size = w2 * w0 * G_h01_0970, zero-extended) and then its 40-byte header. */
struct R3B84 { unsigned short w0; unsigned short w2; char f4[4]; long l8; };

extern int free_memory_checked();
extern long G_h01_542A;
extern short G_h01_0970;

recovered(p)
struct R3B84 *p;
{
    free_memory_checked(&G_h01_542A, p->l8, (long)(unsigned short)(p->w2 * p->w0 * G_h01_0970));
    free_memory_checked(&G_h01_542A, p, 40L);
}
