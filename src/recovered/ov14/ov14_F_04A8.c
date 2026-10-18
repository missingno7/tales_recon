struct FlagEntry { char value; char pad[11]; };
extern struct FlagEntry player_treasure_collected[35];
extern struct FlagEntry rival_treasure_collected[35];
extern char calculate_travel_days();

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
        if (i != excluded && !player_treasure_collected[i].value && !rival_treasure_collected[i].value) {
            cost = calculate_travel_days(excluded, i);
            if (cost < best) {
                best = cost;
                winner = i;
            }
        }
    }
    return winner;
}
