/* Port version of src/recovered/resident/resident_F_2D66.c (read_le16).
   The original reads two bytes of a little-endian file field and swaps them in memory
   so the 68000 sees the value; on a little-endian host that swap would undo itself.
   The value is assembled from the bytes instead, so it is right on any host: the result
   is in buf (as a native short) and in G_h01_A7E8, as in the original. */
#include "aztec.h"

extern int32_t Read();               /* F_h00_86F6: Read glue */
extern int16_t G_h01_A7E8;

int16_t F_h00_2D66(int32_t fh, uint8_t *buf)
{
    int16_t value;
    Read(fh, buf, 2L);
    value = (int16_t)(buf[0] | buf[1] << 8);
    *(int16_t *)buf = value;
    G_h01_A7E8 = value;
    return value;
}
