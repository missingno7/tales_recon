/* resident_F_3930 candidate: pointer range argument, long arithmetic for the end address; callees and DATA names are mechanical. */
extern int F_h00_701A();
extern int F_h00_8938();
extern int F_h04_27FE();
extern long G_h01_543E;
extern long G_h01_5442;

recovered(a, b, c)
long a;
char *b;
long c;
{
    if (b < G_h01_543E || b > G_h01_5442) {
        F_h00_701A("dealloc: %lx - %lx,  %ld ($%lx)\n", b, (long)b + c, c, c);
        F_h04_27FE("BAD POINTER\n");
    } else {
        F_h00_8938(a, b, c);
    }
}
