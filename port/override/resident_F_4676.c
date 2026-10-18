/* Port version of src/recovered/resident/resident_F_4676.c (RNG seed).
   The original adds VPOSR (0xdff004, the beam position) to the game tick; the platform
   supplies the beam value (recorded and replayed, docs/sdl3-port.md). */
#include "aztec.h"
#include "../amiga.h"

extern int32_t G_h01_B1EC;
extern uint16_t G_h01_3AB8;

int16_t F_h00_4676(void)
{
    G_h01_3AB8 = (uint16_t)(platform_beam() + G_h01_B1EC);
    return 0;
}
