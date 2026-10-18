extern long Read();
extern short G_h01_A7E8;

recovered(fh, buf)
long fh;
char *buf;
{
    char *p;
    char c;

    Read(fh, buf, 2L);
    G_h01_A7E8 = *(short *)buf;
    p = buf;
    c = *p;
    *p = p[1];
    p[1] = c;
    G_h01_A7E8 = *(short *)buf;
}
