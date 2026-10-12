extern long G_h01_5392;
extern long G_h01_53E0;
extern long G_h01_53E4;

struct CopperBase { char pad[4]; char *field_4; };

recovered()
{
    char *p;
    char *q;
    short *src;
    unsigned int i;

    src = (short *)G_h01_5392;
    p = ((struct CopperBase *)G_h01_53E0)->field_4 + 4;
    q = ((struct CopperBase *)G_h01_53E4)->field_4 + 4;
    while (*(short *)p != 0x180)
        p += 4;
    while (*(short *)q != 0x180)
        q += 4;
    p += 2;
    q += 2;
    for (i = 0; i < 0x20; i++) {
        *(short *)p = *src;
        *(short *)q = *src;
        p += 4;
        q += 4;
        src++;
    }
}
