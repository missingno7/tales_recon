/* resident_F_4676 candidate v1 (baseline, no parent).
   Mechanical access view: a word is read from the absolute custom-chip address
   0xdff004 and added to the longword game_frame_tick; the low word of the sum is
   stored to random_state. Names are mechanical offsets, not provenance. */
extern long game_frame_tick;
extern unsigned short random_state;

recovered()
{
	random_state = *(unsigned short *)0xdff004 + game_frame_tick;
}
