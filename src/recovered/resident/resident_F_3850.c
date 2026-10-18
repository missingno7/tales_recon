/* Baseline for resident_F_3850: a 32-bit absolute-data flag gates one call to a
   mechanically named A4 jump-table callee; the long argument is forwarded as the
   second argument. Declarations follow the canonical ov04 view for the same
   global and callee. */
extern long chip_memory_pool_base;
extern int F_h00_897C();

recovered(arg)
long arg;
{
    if (chip_memory_pool_base)
        F_h00_897C(chip_memory_pool_base, arg);
}
