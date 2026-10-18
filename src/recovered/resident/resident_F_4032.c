/* Baseline for resident_F_4032: a byte-sized argument is stored through an
   absolute-data char pointer that is post-incremented in place. */
extern char *lzw_output_cursor;

recovered(arg)
char arg;
{
    *lzw_output_cursor++ = arg;
}
