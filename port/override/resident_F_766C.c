/* Port version of src/recovered/resident/resident_F_766C.c (Aztec _main startup).
   The original allocates the device table, records the stack, parses the CLI line or
   takes the Workbench message, opens the standard streams, calls main(argc, argv) -
   the game's main is F_h03_0000 - and leaves through exit. The port is started like a
   CLI command without arguments; the streams are the host's. */
#include "aztec.h"

extern int16_t game_main();            /* F_h03_0000 */
extern int16_t recovered_exit_8534();  /* F_h00_8534: exit */

int16_t _main(int32_t alen, char *aptr)
{
    (void)alen; (void)aptr;
    game_main(1, (char **)0);
    recovered_exit_8534(0);
    return 0;
}
