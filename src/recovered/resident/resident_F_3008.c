/* Candidate v1 for resident_F_3008: walks a list whose head pair lives in a
   local ring structure initialised by two callees, then calls the 7AC0 stub
   per entry until a hit is recorded. Callees use their mechanical F_h00 names. */
extern int F_h00_89A8();
extern int F_h00_2F24();
extern int F_h00_7AC0();
extern int F_h00_2FE2();

struct Entry {
    struct Entry *next;
    char pad4[6];
    long data;
};

struct Ring {
    struct Entry *head;
    long mid;
    struct Entry *last;
    short tail;
};

recovered(x)
long x;
{
    struct Ring s;
    struct Entry *p;
    unsigned char done;

    done = 0;
    F_h00_89A8(&s);
    F_h00_2F24(&s);
    if (s.last != (struct Entry *)&s) {
        for (p = s.head; p->next != 0 && !done; p = p->next) {
            if (!F_h00_7AC0(p->data, x))
                done = 1;
        }
    }
    F_h00_2FE2(&s);
    return done;
}
