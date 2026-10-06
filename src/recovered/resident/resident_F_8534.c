/* Reconstructed startup-called exit wrapper. The callback slot is proved
   only as an access view; original provider and TU ownership are unknown. */
extern long G_h01_B3C4;
extern int F_h00_8552();
recovered(code)
int code;
{
 if (G_h01_B3C4)
  (*(int (*)())G_h01_B3C4)();
 F_h00_8552(code);
}
