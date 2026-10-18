extern long allocate_memory_or_report();
extern int report_loader_error();
extern long G_h01_542A;
extern int G_h01_0970;

recovered(p, c, e)
long *p;
unsigned int c;
unsigned int e;
{
    int i;
    long r;

    r = allocate_memory_or_report(&G_h01_542A, (long)(unsigned int)(c * e * G_h01_0970));
    if (r == 0)
        report_loader_error(6000);
    for (i = 0; i < G_h01_0970; i++)
        p[i] = r + (unsigned int)(i * c * e);
}
