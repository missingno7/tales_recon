/* Candidate v1 for resident_F_2F24: walks a BPTR-linked list reached from the
   absolute data word G_h01_A98E. BPTR values are converted with a left shift by
   two. Callees use their mechanical F_h00 names. */
struct Mid { char pad0[24]; long head; };
struct Top { char pad0[34]; struct Mid *mid; };
struct Head { char pad0[4]; long first; };
struct Node { long next; long kind; long flag; char pad12[28]; long name; };
struct Rec { char pad0[8]; char field_8; char field_9; char *field_a; };

extern struct Top *G_h01_A98E;
extern int Forbid();
extern int Permit();
extern int movmem();
extern int F_h00_2EAC();
extern long F_h00_2E30();
extern int AddTail();

recovered(x)
long x;
{
    struct Mid *mid;
    struct Head *head;
    char *name;
    char buf[32];
    register struct Node *node;
    register struct Rec *rec;

    mid = G_h01_A98E->mid;
    head = (struct Head *)(mid->head << 2);
    Forbid();
    for (node = (struct Node *)(head->first << 2); ((long)node << 2) != 0L;
         node = (struct Node *)(node->next << 2)) {
        if (node->kind == 2 || node->kind == 1) {
            if (node->flag != 0 && (node->name << 2) != 0L) {
                name = (char *)(node->name << 2);
                movmem(name, buf, *name + 1);
                F_h00_2EAC(buf);
                if ((rec = (struct Rec *)F_h00_2E30(buf, 0, 0)) != 0)
                    AddTail(x, rec);
            }
        }
    }
    Permit();
}
