struct Record { int amount; char reserved[4]; int category; char rest[38]; };
extern struct Record investment_market_state[16];
extern unsigned char market_price_history[16][31];
extern char game_day;
recovered(n) int n;
{
    int result, amount, percent;
    amount = investment_market_state[n].amount;
    percent = market_price_history[investment_market_state[n].category][game_day-1];
    result = amount * percent / 100;
    if (result <= 0 && percent > 0) result = 1;
    return result;
}
