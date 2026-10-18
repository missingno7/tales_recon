/* Port version of src/recovered/resident/resident_F_2DBA.c (read_le32).
   As read_le16: the original swaps the four bytes in memory for the 68000; here the
   little-endian value is assembled from the bytes. Result in buf and in G_h01_A7EA. */
#include "aztec.h"

extern int32_t Read();               /* F_h00_86F6: Read glue */
extern int32_t G_h01_A7EA;

int32_t F_h00_2DBA(int32_t fh, uint8_t *buf)
{
    int32_t value;
    Read(fh, buf, 4L);
    value = (int32_t)((uint32_t)buf[0] | (uint32_t)buf[1] << 8 | (uint32_t)buf[2] << 16 | (uint32_t)buf[3] << 24);
    *(int32_t *)buf = value;
    G_h01_A7EA = value;
    return value;
}
