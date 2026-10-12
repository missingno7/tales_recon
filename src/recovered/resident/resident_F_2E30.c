/* Candidate v4 for resident_F_2E30 (v3 with the register long declarations swapped): K&R parameters (char arguments at +13 and +15),
   register locals for the long count, the long allocation result, the record
   pointer and the interior pointer. Callees use their mechanical F_h00 names. */
struct RecView { char pad0[8]; char field_8; char field_9; char *field_a; };

extern int F_h00_8044();
extern long F_h00_8926();
extern int F_h00_7AF0();

struct RecView *recovered(p, c1, c2)
char *p;
char c1;
char c2;
{
    register long r;
    register long n;
    register struct RecView *rec;
    register char *t;

    n = (long)F_h00_8044(p) ? F_h00_8044(p) + 1L : 0L;
    rec = 0;
    r = F_h00_8926(n + 14, 0x10001L);
    if (r == 0)
        return 0;
    rec = (struct RecView *)r;
    if (n) {
        t = (char *)r + 14;
        F_h00_7AF0(t, p);
        rec->field_a = t;
    }
    rec->field_8 = c1;
    rec->field_9 = c2;
    return rec;
}
