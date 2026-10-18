/* aztec.h - the Aztec C 3.6 data model made explicit for the generated game code.
   Included first by every unit tools/port_gen.py writes (docs/sdl3-port.md). */
#ifndef AZTEC_H
#define AZTEC_H
#include <stdint.h>
#include <stddef.h>

/* A narrower view of a scalar - `((char *)&i)[1]`, the low byte of a 16-bit i on the 68000 -
   names the same value bits on a little-endian host when its index is counted from the
   other end. Structures, arrays and views as wide as the object are left as they are.
   port_gen.py rewrites every `((T *)&x)[k]` of the game code to BE_VIEW(T, x, k). */
/* the platform clock (port/main.c): busy-waits on interrupt state wait one frame per pass */
void platform_wait_ticks(int ticks);
void platform_spin_frame(void);
/* custom chip and CIA registers the game reads (port/m68k.c) */
uint16_t amiga_read16(uint32_t address);

#define BE_SCALAR(x) _Generic((x), int16_t: 1, uint16_t: 1, int32_t: 1, uint32_t: 1, default: 0)
#define BE_VIEW(T, x, k) (((T *)&(x))[BE_SCALAR(x) && sizeof(T) < sizeof(x) \
                                      ? (int)(sizeof(x) / sizeof(T)) - 1 - (k) : (k)])
#endif
