struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern long total_money;

recovered(p)
struct Header *p;
{
    p->first = 40;
    p->second = 172;
    F_h00_34E0(p);
    F_h00_09C0(176, 175, total_money, 1, 9, 1);
}
