/* Candidate for resident_F_3A06: the two referenced printable runs are written as
   string literals (PC-relative in the code hunk), the list head stays an absolute
   long global. Callee and DATA names are mechanical. */
extern long tracked_allocation_list_head;
extern int F_h00_701A();

recovered()
{
    long node;

    F_h00_701A("\nMEM LIST\n");
    node = tracked_allocation_list_head;
    while (node != 0) {
        F_h00_701A("%lx:  %ld ($%lx)\n", node, *(long *)((char *)node + 4), *(long *)((char *)node + 4));
        node = *(long *)node;
    }
}
