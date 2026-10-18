struct Header {
    int first;
    int second;
};

extern int F_h00_34E0();
extern int F_h00_09C0();
extern char game_day;

recovered(p)
struct Header *p;
{
    int unused1;
    int unused2;

    p->first = 8;
    p->second = 175;
    F_h00_34E0(p);
    if (game_day < 10)
        F_h00_09C0(18, 182, (long)game_day, 7, 1, 0);
    else
        F_h00_09C0(14, 182, (long)game_day, 7, 1, 0);
}
