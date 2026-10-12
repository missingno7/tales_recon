/* Candidate v4 for resident_F_2EE8: one-factor change from v3. The true arm of the
   conditional expression is converted to long, so the 16-bit sum F_h00_8044(field)+1
   is sign-extended inside that arm rather than after the join. Calls, operands and
   accumulator are unchanged. */
struct R2EE8View { char unknown_before_a[10]; long field_a; };
extern int F_h00_8044();
extern int F_h00_897C();

recovered(p)
struct R2EE8View *p;
{
	register long n;

	n = 14;
	n += p->field_a ? (long)(F_h00_8044(p->field_a) + 1) : 0;
	return F_h00_897C(p, n);
}
