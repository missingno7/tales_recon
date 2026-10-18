/* Candidate for resident_F_37C8: the baseline with one extra long local declared
   before the int status local, so the status word sits at the lower frame slot.
   Callee and DATA names are mechanical. */
extern long AllocMem();
extern long chip_memory_pool_base;
extern long tracked_allocation_list_head;
extern long tracked_memory_lower_bound;
extern long tracked_memory_upper_bound;
extern long tracked_free_memory_bytes;
extern long G_h01_53E8;

int recovered(arg)
long arg;
{
    long tmp;
    int result;

    chip_memory_pool_base = AllocMem(arg, 0x10002L);
    if (chip_memory_pool_base == 0) {
        result = -1;
    } else {
        tracked_allocation_list_head = chip_memory_pool_base;
        tracked_memory_lower_bound = chip_memory_pool_base;
        tracked_memory_upper_bound = (long)((char *)arg + chip_memory_pool_base + 1);
        tracked_free_memory_bytes = arg - 8;
        G_h01_53E8 = chip_memory_pool_base;
        *(long *)G_h01_53E8 = 0L;
        *((long *)G_h01_53E8 + 1) = tracked_free_memory_bytes;
        result = 0;
    }
    return result;
}
