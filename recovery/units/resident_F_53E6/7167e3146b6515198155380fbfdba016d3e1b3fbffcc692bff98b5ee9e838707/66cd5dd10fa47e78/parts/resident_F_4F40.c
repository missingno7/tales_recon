/* Candidate v1 for resident_F_4F40: spin while the first longword equals the
   second, then copy the second longword over the first. */
extern long G_h01_B1EC;
extern long G_h01_B396;

F_h00_4F40()
{
    while (G_h01_B396 == G_h01_B1EC)
        ;
    G_h01_B396 = G_h01_B1EC;
}
