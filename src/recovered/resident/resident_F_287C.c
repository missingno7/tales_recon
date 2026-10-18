extern long Seek();
extern long read_le32();
extern long read_le16();
extern long arc_offsets[104];
extern long G_h01_A7D6;
extern int G_h01_A7DA;
extern int G_h01_A7DC;
extern int G_h01_A7DE;
extern int G_h01_A7E0;
extern int G_h01_A7E2;
extern int G_h01_A7E4;

recovered(index, fh)
int index;
long fh;
{
    long offset;
    offset = arc_offsets[index];
    Seek(fh, offset, -1L);
    read_le32(fh, &G_h01_A7D6);
    read_le16(fh, &G_h01_A7DA);
    read_le16(fh, &G_h01_A7DC);
    read_le16(fh, &G_h01_A7DE);
    read_le16(fh, &G_h01_A7E0);
    read_le16(fh, &G_h01_A7E2);
    read_le16(fh, &G_h01_A7E4);
    return 0;
}

