/* resident_F_4676 candidate v1 (baseline, no parent).
   Mechanical access view: a word is read from the absolute custom-chip address
   0xdff004 and added to the longword G_h01_B1EC; the low word of the sum is
   stored to G_h01_3AB8. Names are mechanical offsets, not provenance. */
extern long G_h01_B1EC;
extern unsigned short G_h01_3AB8;

recovered()
{
	G_h01_3AB8 = *(unsigned short *)0xdff004 + G_h01_B1EC;
}
