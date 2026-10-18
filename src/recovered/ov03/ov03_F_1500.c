extern long screen_rast_port;
extern char game_day;
extern long total_money;
extern long rival_unbanked_treasure_value;
extern long player_banked_cash;
extern long rival_banked_cash;
extern int switch_display_buffer();
extern int FreeSeg();
extern int SetRast();
extern int endgame_show_wealth_comparison();

recovered()
{
    SetRast(screen_rast_port,0L);
    player_banked_cash += total_money;
    if (game_day >= 30)
        rival_banked_cash += rival_unbanked_treasure_value;
    endgame_show_wealth_comparison();
    FreeSeg(endgame_show_wealth_comparison);
    total_money = 0L;
    SetRast(screen_rast_port,0L);
    switch_display_buffer();
}
