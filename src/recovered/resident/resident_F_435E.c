/* Candidate v1 for resident_F_435E: discard the callee result, then clear the
   word global and the byte global in source order. */
extern int G_h01_1F34;
extern char G_h01_B1EB;
extern long F_h00_4F62();

recovered()
{
    F_h00_4F62();
    G_h01_1F34 = 0;
    G_h01_B1EB = 0;
}
