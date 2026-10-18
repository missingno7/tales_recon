/* Candidate for resident_F_04FE: structure follows the ov04_F_0104 sibling. */
extern long arc_file;
extern unsigned int F_h00_463E();
extern int request_disk();
extern long Open();
extern int arc_read_index();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_35DC();
extern int F_h00_3C0E();
extern int Close();

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
    saved = arc_file;
    request_disk(2);
    arc_file = Open("DT2:clues.arc", 1005L);
    arc_read_index(arc_file);
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
    Close(arc_file);
    arc_file = saved;
    arc_read_index(arc_file);
}
