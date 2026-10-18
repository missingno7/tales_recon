/* Port version of src/recovered/resident/resident_F_33E6.c (plane-union mask).
   The original clears the work buffer with BltClear, then runs the blitter once per
   plane with BLTCON0 0xDFC (D = B | C, B = the buffer, C = the plane), leaving in the
   buffer the union of all planes: a mask of every non-zero pixel. Same result here
   with a byte loop over rows x bytes. */
#include "aztec.h"

#pragma pack(push, 2)
struct BlitSrc {
    int16_t field_0;                 /* bytes per row */
    int16_t field_2;                 /* rows */
    char field_4;
    unsigned char field_5;           /* plane count */
    char field_6[2];
    int32_t field_8[1];              /* plane addresses */
};
#pragma pack(pop)

extern int16_t BltClear();

int16_t F_h00_33E6(struct BlitSrc *p, int32_t n)
{
    uint16_t a = (uint16_t)p->field_0, b = (uint16_t)p->field_2, count = p->field_5;
    uint8_t *mask = (uint8_t *)(intptr_t)n;
    BltClear(n, (int32_t)(b * a), 1L);
    for (uint16_t i = 0; i < count; i++) {
        const uint8_t *plane = (const uint8_t *)(intptr_t)p->field_8[i];
        for (uint32_t j = 0; j < (uint32_t)b * a; j++)
            mask[j] |= plane[j];
    }
    return 0;
}
