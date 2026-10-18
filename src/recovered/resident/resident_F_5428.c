/* C-compatible small wrapper, ordinary parameter accesses establish types. */
extern char palette_cycle_word_index;
extern char palette_cycle_frame_countdown;
extern char palette_cycle_countdown_step;
extern long palette_cycle_callback_index;
recovered(p,n)
long p,n;
{
 palette_cycle_word_index=0;
 palette_cycle_frame_countdown=0;
 palette_cycle_countdown_step=n;
 palette_cycle_callback_index=p;
}
