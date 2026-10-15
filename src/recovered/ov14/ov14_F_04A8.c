struct FlagEntry { char value; char pad[11]; };
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
    int cost;

    winner = 35;
    best = 16000;
    for (i = 1; i < 35; i++) {
        if (i != excluded && !G_h01_452E[i].value && !G_h01_452F[i].value) {
            cost = F_h03_154E(excluded, i);
            if (cost < best) {
                best = cost;
                winner = i;
            }
        }
    }
    return winner;
}
