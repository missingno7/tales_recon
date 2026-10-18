/* One-factor change from v2: the assignment from the 8A06 stub is the tested
   expression, so the null test reads the value still held in d0 instead of
   reloading it from the pointer register. */
extern long RemTail();
extern int F_h00_2EE8();

recovered(arg)
char *arg;
{
	register char *p;

	for (;;) {
		if ((p = (char *)RemTail(arg)) == 0)
			break;
		F_h00_2EE8(p);
	}
}
