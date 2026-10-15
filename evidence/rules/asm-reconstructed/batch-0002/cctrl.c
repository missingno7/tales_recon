extern int (*C_handlers[44])();
int C_dispatch(p, i)
char *p;
unsigned i;
{
    if (i <= 43) return (*C_handlers[i])(*p++);
    return 0;
}
