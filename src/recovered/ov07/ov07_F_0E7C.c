struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern long G_h01_46E6;

recovered(p)
struct Header *p;
{
    p->first = 40;
    p->second = 172;
    F_h00_34E0(p);
    F_h00_09C0(176, 175, G_h01_46E6, 1, 9, 1);
}
