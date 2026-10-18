extern long Seek();
extern long read_le16();
extern long read_le32();
extern long arc_offsets[104];

long recovered(fh)
long fh;
{
    unsigned short n;
    unsigned short i;

    Seek(fh, 0L, -1L);
    read_le16(fh, &n);
    if (n > 104) {
        return -1;
    }
    for (i = 0; i < n; i++) {
        read_le32(fh, &arc_offsets[i]);
    }
    return 0;
}
