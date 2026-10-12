/* Baseline for resident_F_4032: a byte-sized argument is stored through an
   absolute-data char pointer that is post-incremented in place. */
extern char *G_h01_A9BE;

recovered(arg)
char arg;
{
    *G_h01_A9BE++ = arg;
}
