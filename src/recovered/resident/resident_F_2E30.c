/* Candidate v4 for resident_F_2E30 (v3 with the register long declarations swapped): K&R parameters (char arguments at +13 and +15),
   register locals for the long count, the long allocation result, the record
   pointer and the interior pointer. Callees use their mechanical F_h00 names. */
struct RecView { char pad0[8]; char field_8; char field_9; char *field_a; };

extern int strlen();
extern long AllocMem();
extern int strcpy();

struct RecView *recovered(p, c1, c2)
char *p;
char c1;
char c2;
{
    register long r;
    register long n;
    register struct RecView *rec;
    register char *t;

    n = (long)strlen(p) ? strlen(p) + 1L : 0L;
    rec = 0;
    r = AllocMem(n + 14, 0x10001L);
    if (r == 0)
        return 0;
    rec = (struct RecView *)r;
    if (n) {
        t = (char *)r + 14;
        strcpy(t, p);
        rec->field_a = t;
    }
    rec->field_8 = c1;
    rec->field_9 = c2;
    return rec;
}
