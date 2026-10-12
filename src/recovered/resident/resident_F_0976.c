char *recovered(p, q)
char *p, *q;
{
    while (*p != '\n' && *p) {
        if (*p != '\r')
            *q = *p;
        q++;
        p++;
    }
    q--;
    *q = 0;
    return ++p;
}
