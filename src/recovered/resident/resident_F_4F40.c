/* Candidate v1 for resident_F_4F40: spin while the first longword equals the
   second, then copy the second longword over the first. */
extern long game_frame_tick;
extern long G_h01_B396;

recovered()
{
    while (G_h01_B396 == game_frame_tick)
        ;
    G_h01_B396 = game_frame_tick;
}
