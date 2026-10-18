extern int free_memory_checked();
extern long game_memory_header;

struct Rec { unsigned short size; char *ptr; };

recovered(p)
struct Rec *p;
{
    free_memory_checked(&game_memory_header, p->ptr, (long)p->size);
    free_memory_checked(&game_memory_header, p, 6L);
}
