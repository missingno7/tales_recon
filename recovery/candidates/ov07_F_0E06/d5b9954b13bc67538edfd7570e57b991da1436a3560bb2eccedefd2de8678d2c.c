struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern char G_h01_46E1;

recovered(p)
struct Header *p;
{
    p->first = 8;
    p->second = 175;
    F_h00_34E0(p);
    if (G_h01_46E1 < 10)
        F_h00_09C0(18, 182, G_h01_46E1, 7, 1, 0);
    else
        F_h00_09C0(14, 182, G_h01_46E1, 7, 1, 0);
}
