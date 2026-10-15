struct FlagEntry { char value; char pad[11]; };
struct LinkEntry { char *target; char pad[8]; };
extern struct LinkEntry G_h01_4528[35];
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];

char
recovered(excluded)
char excluded;
{
    char i;
    char winner;
    int best;
    int value;

    best = 0;
    winner = 35;
    for (i = 1; i < 35; i++) {
        if (i != excluded && !G_h01_452E[i].value && !G_h01_452F[i].value) {
            value = ((int *)G_h01_4528[i].target)[1];
            if (value > best) {
                best = value;
                winner = i;
            }
        }
    }
    return winner;
}
