/* Candidate for resident_F_04FE: structure follows the ov04_F_0104 sibling. */
extern long G_h01_46DA;
extern unsigned int F_h00_463E();
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_35DC();
extern int F_h00_3C0E();
extern int F_h00_868C();

recovered(a)
int a;
{
    long saved;
    long found;
    char buf[61];
    long state;
    unsigned int i;

    i = F_h00_463E() & 3;
    a = a * 4 + i;
    saved = G_h01_46DA;
    F_h00_0FDE(2);
    G_h01_46DA = F_h00_86DC("DT2:clues.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    found = 0;
    found = F_h00_291E(a, found);
    state = *(long *)((char *)found + 2);
    for (i = 0; i <= 61; i++)
        buf[i] = 0;
    state = F_h00_0976(state, buf);
    F_h00_35DC(20, 40, buf, 7, 0);
    state = F_h00_0976(state, buf);
    F_h00_35DC(20, 52, buf, 7, 0);
    state = F_h00_0976(state, buf);
    F_h00_35DC(20, 64, buf, 7, 0);
    F_h00_3C0E(found);
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}
