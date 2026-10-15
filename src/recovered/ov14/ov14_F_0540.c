struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
extern struct LinkEntry G_h01_4528[35];
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];
extern char F_h03_154E();

char
recovered(excluded)
char excluded;
{
    char i;
    char winner;
    int best;
    int ratio;
    int cost;
    int value;

    winner = 35;
    best = 0;
    for (i = 1; i < 35; i++) {
        if (i != excluded && !G_h01_452E[i].value && !G_h01_452F[i].value) {
            cost = F_h03_154E(excluded, i);
            value = ((int *)G_h01_4528[i].target)[1];
            ratio = value / cost;
            if (ratio > best) {
                best = ratio;
                winner = i;
            }
        }
    }
    return winner;
}
