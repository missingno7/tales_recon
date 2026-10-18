/* Port version of src/recovered/resident/resident_F_8552.c (Aztec _exit).
   The original closes the game's files, frees the device table, runs the cleanup
   handler (_cln, G_h01_B3C8), closes the libraries the startup opened, resets the
   68881 in supervisor mode (inline assembly) and returns to the original stack. The port
   keeps the cleanup and the closes and ends the game through the platform; there is no
   FPU state and no Workbench message to reply to. */
#include "aztec.h"
#include "../amiga.h"

extern int32_t G_h01_B3C8;             /* _cln: cleanup handler */
extern int32_t G_h01_B3CE, MathBase, G_h01_B3D6;      /* libraries opened by the startup (B3D2 is MathBase) */
extern int16_t CloseLibrary();
void platform_exit(int code);

int16_t recovered_exit_8552(int16_t code)
{
    if (G_h01_B3C8)
        ((void (*)(void))(intptr_t)G_h01_B3C8)();
    if (G_h01_B3CE) CloseLibrary(G_h01_B3CE);
    if (MathBase) CloseLibrary(MathBase);
    if (G_h01_B3D6) CloseLibrary(G_h01_B3D6);
    platform_exit(code);
    return 0;
}
