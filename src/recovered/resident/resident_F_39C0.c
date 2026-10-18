extern long tracked_free_memory_bytes;
extern int F_h00_701A();
recovered(label)
long label;
{
 F_h00_701A("%s  mem=%ld (%lx)\n",label,tracked_free_memory_bytes,tracked_free_memory_bytes);
}
