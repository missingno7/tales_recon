extern long F_h00_86F6();
extern long G_h01_A7EA;

long recovered(fh, buf)
long fh;
char *buf;
{
    char *p;
    char c;

    F_h00_86F6(fh, buf, 4L);
    G_h01_A7EA = *(long *)buf;
    p = buf;
    c = *p;
    p[0] = p[3];
    p[3] = c;
    c = p[1];
    p[1] = p[2];
    p[2] = c;
    G_h01_A7EA = *(long *)buf;
}
